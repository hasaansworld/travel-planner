import json
import os
import openai
from groq import Groq
from dotenv import load_dotenv
import requests
import time
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime

from sqlmodel import Session, select

from app.models import PlacesQuery, PlanQuery, Place, PlanPlace
from app.utils import generate_llm_response

load_dotenv()

@dataclass
class Location:
    latitude: float
    longitude: float

@dataclass
class PlaceResult:
    id: str
    name: str
    location: Location
    rating: Optional[float] = None
    user_rating_count: Optional[int] = None
    primary_type: str = ""
    types: Optional[List[str]] = None
    address: Optional[str] = None
    opening_hours: Optional[Dict] = None
    search_type: Optional[str] = None  
    photos: Optional[List[str]] = None 
    
    def to_dict(self) -> Dict:
        """Convert PlaceResult to dictionary for JSON serialization"""
        return {
            "id": self.id,
            "name": self.name,
            "location": {"latitude": self.location.latitude, "longitude": self.location.longitude},
            "rating": self.rating,
            "user_rating_count": self.user_rating_count,
            "primary_type": self.primary_type,
            "types": self.types,
            "address": self.address,
            "opening_hours": self.opening_hours,
            "search_type": self.search_type,
            "photos": self.photos
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'PlaceResult':
        """Create PlaceResult from dictionary"""
        location_data = data.get("location", {})
        location = Location(
            latitude=location_data.get("latitude", 0),
            longitude=location_data.get("longitude", 0)
        )
        
        return cls(
            id=data.get("id", ""),
            name=data.get("name", ""),
            location=location,
            rating=data.get("rating"),
            user_rating_count=data.get("user_rating_count"),
            primary_type=data.get("primary_type", ""),
            types=data.get("types"),
            address=data.get("address"),
            opening_hours=data.get("opening_hours"),
            search_type=data.get("search_type"),
            photos=data.get("photos", [])
        )

def upsert_place(session: Session, place_result: PlaceResult) -> Place:
    """Insert a new place or update existing one in the database"""
    
    # Check if place already exists
    existing_place = session.exec(
        select(Place).where(Place.place_id == place_result.id)
    ).first()
    
    if existing_place:
        # Update existing place
        existing_place.name = place_result.name
        existing_place.latitude = place_result.location.latitude
        existing_place.longitude = place_result.location.longitude
        existing_place.rating = place_result.rating
        existing_place.user_rating_count = place_result.user_rating_count
        existing_place.primary_type = place_result.primary_type
        existing_place.types = place_result.types
        existing_place.address = place_result.address
        existing_place.opening_hours = place_result.opening_hours
        existing_place.photos = place_result.photos
        existing_place.search_type = place_result.search_type
        existing_place.updated_at = datetime.utcnow()
        
        session.add(existing_place)
        return existing_place
    else:
        # Create new place
        new_place = Place(
            place_id=place_result.id,
            name=place_result.name,
            latitude=place_result.location.latitude,
            longitude=place_result.location.longitude,
            rating=place_result.rating,
            user_rating_count=place_result.user_rating_count,
            primary_type=place_result.primary_type,
            types=place_result.types,
            address=place_result.address,
            opening_hours=place_result.opening_hours,
            photos=place_result.photos,
            search_type=place_result.search_type
        )
        
        session.add(new_place)
        return new_place

def link_place_to_plan(session: Session, plan_id: int, place_id: str) -> None:
    """Create a link between a plan and a place"""
    
    # Check if the relationship already exists
    existing_link = session.exec(
        select(PlanPlace).where(
            PlanPlace.plan_id == plan_id,
            PlanPlace.place_id == place_id
        )
    ).first()
    
    if not existing_link:
        plan_place = PlanPlace(
            plan_id=plan_id,
            place_id=place_id
        )
        session.add(plan_place)

def get_places_for_plan(session: Session, plan_id: int) -> List[Place]:
    """Get all places associated with a specific plan"""
    
    statement = (
        select(Place)
        .join(PlanPlace)
        .where(PlanPlace.plan_id == plan_id)
    )
    
    places = session.exec(statement).all()
    return list(places)

class UnifiedGooglePlacesAPI:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.nearby_url = "https://places.googleapis.com/v1/places:searchNearby"
        self.text_search_url = "https://places.googleapis.com/v1/places:searchText"
        self.session = requests.Session()
        
    def search_places_nearby(
        self, 
        location: Location, 
        radius: int = 1000,
        place_types: Optional[List[str]] = None,
        max_results: int = 100,
        sort_by_popularity: bool = True
    ) -> List[PlaceResult]:
        """
        Search for places near a location using the Nearby Search API
        """
        all_places = []
        next_page_token = None
        requests_made = 0
        max_requests = 10
        
        field_mask = (
            "places.id,"
            "places.displayName,"
            "places.location,"
            "places.rating,"
            "places.userRatingCount,"
            "places.primaryTypeDisplayName,"
            "places.types,"
            "places.formattedAddress,"
            "places.regularOpeningHours,"
            "places.photos"
        )
        
        while len(all_places) < max_results and requests_made < max_requests:
            payload = {
                "maxResultCount": min(20, max_results - len(all_places)),
                "locationRestriction": {
                    "circle": {
                        "center": {
                            "latitude": location.latitude,
                            "longitude": location.longitude
                        },
                        "radius": radius
                    }
                },
                "rankPreference": "POPULARITY" if sort_by_popularity else "DISTANCE"
            }
            
            if place_types:
                payload["includedTypes"] = place_types
            
            if next_page_token:
                payload["pageToken"] = next_page_token
            
            try:
                response = self._make_request(self.nearby_url, payload, field_mask)
                
                if response.status_code == 200:
                    data = response.json()
                    places = data.get("places", [])
                    
                    for place_data in places:
                        place = self._parse_place_data(place_data, search_type="nearby")
                        if place:
                            all_places.append(place)
                    
                    next_page_token = data.get("nextPageToken")
                    print(f"Nearby search - Fetched {len(places)} places (Total: {len(all_places)})")
                    
                    if not next_page_token:
                        break
                else:
                    print(f"Nearby API request failed with status {response.status_code}")
                    print(f"Response: {response.text}")
                    break
                    
            except Exception as e:
                print(f"Error in nearby search: {e}")
                break
            
            requests_made += 1
            if next_page_token:
                time.sleep(1)
        
        return all_places[:max_results]
    
    def search_places_by_text(
        self, 
        text_query: str,
        location: Optional[Location] = None,
        radius: Optional[int] = None,
        max_results: int = 100,
        sort_by_popularity: bool = True
    ) -> List[PlaceResult]:
        """
        Search for places using text query with the Text Search API
        """
        all_places = []
        next_page_token = None
        requests_made = 0
        max_requests = 10
        
        field_mask = (
            "places.id,"
            "places.displayName,"
            "places.location,"
            "places.rating,"
            "places.userRatingCount,"
            "places.primaryTypeDisplayName,"
            "places.types,"
            "places.formattedAddress,"
            "places.regularOpeningHours,"
            "places.photos"
        )
        
        while len(all_places) < max_results and requests_made < max_requests:
            payload = {
                "textQuery": text_query,
                "pageSize": min(20, max_results - len(all_places)),
                "rankPreference": "RELEVANCE" if sort_by_popularity else "DISTANCE"
            }
            
            if location:
                payload["locationBias"] = {
                    "circle": {
                        "center": {
                            "latitude": location.latitude,
                            "longitude": location.longitude
                        },
                        "radius": radius or 10000
                    }
                }
            
            if next_page_token:
                payload["pageToken"] = next_page_token
            
            try:
                response = self._make_request(self.text_search_url, payload, field_mask)
                
                if response.status_code == 200:
                    data = response.json()
                    places = data.get("places", [])
                    
                    for place_data in places:
                        place = self._parse_place_data(place_data, search_type="text")
                        if place:
                            all_places.append(place)
                    
                    next_page_token = data.get("nextPageToken")
                    print(f"Text search - Fetched {len(places)} places (Total: {len(all_places)})")
                    
                    if not next_page_token:
                        break
                else:
                    print(f"Text API request failed with status {response.status_code}")
                    print(f"Response: {response.text}")
                    break
                    
            except Exception as e:
                print(f"Error in text search: {e}")
                break
            
            requests_made += 1
            if next_page_token:
                time.sleep(1)
        
        return all_places[:max_results]
    
    def _make_request(self, url: str, payload: dict, field_mask: str) -> requests.Response:
        """Make API request with proper headers"""
        headers = {
            "Content-Type": "application/json",
            "X-Goog-Api-Key": self.api_key,
            "X-Goog-FieldMask": field_mask
        }
        
        return self.session.post(
            url,
            headers=headers,
            json=payload,
            timeout=30
        )
    
    def _parse_place_data(self, place_data: dict, search_type: str) -> Optional[PlaceResult]:
        """Parse place data from API response"""
        try:
            place_id = place_data.get("id")
            display_name = place_data.get("displayName", {}).get("text", "")
            location_data = place_data.get("location", {})
            
            if not place_id or not display_name or not location_data:
                return None
            
            location = Location(
                latitude=location_data.get("latitude", 0),
                longitude=location_data.get("longitude", 0)
            )
            
            rating = place_data.get("rating")
            user_rating_count = place_data.get("userRatingCount")
            primary_type = place_data.get("primaryTypeDisplayName", "")
            if primary_type:
                primary_type = primary_type.get("text", "")
            types = place_data.get("types", [])
            address = place_data.get("formattedAddress")
            opening_hours = place_data.get("regularOpeningHours")
            photos = place_data.get("photos", [])
            first_photo_name = photos[0].get("name") if photos and photos[0].get("name") else None
            print("Extracted photos:", photos)
            
            return PlaceResult(
                id=place_id,
                name=display_name,
                location=location,
                rating=rating,
                user_rating_count=user_rating_count,
                primary_type=primary_type,
                types=types,
                address=address,
                opening_hours=opening_hours,
                search_type=search_type,
                photos=[first_photo_name] if first_photo_name else []
            )
            
        except Exception as e:
            print(f"Error parsing place data: {e}")
            return None

def get_llm_queries(
    user_activity: str,
    country: str = "Finland",
    city: str = "Oulu",
    intent: str = "travel, sight seeing and trying local food",
    exclude_queries: str = "",
    model: str = "llama"
) -> List[Dict]:
    """Get search queries from LLM based on user preferences"""
    
    # Determine number of queries based on whether we're excluding some
    num_queries = "1-3" if exclude_queries else "6-8"
    
    system_prompt = f"""
    You are a helpful assistant that creates travel plans based on user preferences and location.
    Your job is to query the Google Places API (new) to find places of interest based on the user's past activity and travel intent.
    You can suggest two types of queries:
    1. Nearby search: You have to suggest one category of places to search for, such as restaurants, parks, museums, etc.
    2. Text search: If you need to search for something that doesn't fall into any category for nearby search API, you can use a text query to find places that match the user's intent.

    You must suggest between {num_queries} queries of either type using your own knowledge and judgment.
    You must never suggest two text queries that are similar to each other.
    Try to use nearby search API as much as possible, use text search only when a category is not available for nearby search.
    Try to match the text queries with user's intent.
    {"## You must always make at least 2 queries for places to eat like restaurants and cafes." if exclude_queries else ""}
    Your output should be a JSON object with the following structure:
    {{
        "queries": [
            {{
                "type": "nearby" or "text",
                "category": "the category for nearby search, if type is nearby. Only use categories from Nearby Search API (new)"
                "query": "the query string",
            }}
            {{...}},{{...}}
        ]
    }}
    here's an example response:
    {{    "queries": [
            {{
                "type": "nearby",
                "category": "restaurant",
            }},
            {{
                "type": "nearby",
                "category": "tourist_attraction"
            }},
            {{
                "type": "nearby",
                "category": "park"
            }},
            {{
                "type": "text",
                "query": "local food markets"
            }},
            {{
                "type": "text",
                "query": "Pakistani restaurants"
            }}
        ]
    }}
    """

    user_message = f"""
        **User Activity History:**
        {json.dumps(user_activity, indent=2)}
        **User Intent:** {intent}
        **Country:** {country}
        **City:** {city}
        Please give queries in json format as described in the system prompt.
    """

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_message}
    ]

    if len(exclude_queries) > 0:
        messages.append({
            "role": "user",
            "content": f"Please exclude these queries for which I already have data: {exclude_queries}. **Suggest only 1-3 queries at max**."
        })

    print("Getting queries from LLM...")
    response = generate_llm_response(
        messages=messages,
        model_name=model,
        temperature=0,
    )
    
    try:
        response_data = json.loads(response or "{}")
        return response_data.get("queries", [])
    except json.JSONDecodeError as e:
        print(f"Error parsing LLM response: {e}")
        print(f"Response: {response}")
        return []

def execute_search_queries(
    queries: List[Dict],
    location: Location,
    session: Session,
    plan_id: int,
    city: str = "",
    country: str = "",
    radius_km: int = 5,
    max_results_per_query: int = 20
) -> Dict[str, List[PlaceResult]]:
    """Execute search queries using the appropriate API endpoints and store places in database"""
    
    api_key = os.getenv("PLACES_API_KEY", "")
    places_api = UnifiedGooglePlacesAPI(api_key)
    results = {}
    
    for i, query in enumerate(queries):

        query_type = query.get("type")
        query_value = query.get("category") or query.get("query")
        query_key = f"{query_type} search: {query_value}"
        tolerance = 0.0001

        db_query = (
            select(PlacesQuery)
            .where(PlacesQuery.lat >= location.latitude - tolerance)
            .where(PlacesQuery.lat <= location.latitude + tolerance)
            .where(PlacesQuery.long >= location.longitude - tolerance)
            .where(PlacesQuery.long <= location.longitude + tolerance)
            .where(PlacesQuery.radius_km == radius_km)
            .where(PlacesQuery.query_type == query_type)
            .where(PlacesQuery.query == query_value)
        )

        place_query = session.exec(db_query).first()
        
        if place_query:
            print(f"Using cached results for query {i+1}: {query_key}")
            # Convert stored dictionary data back to PlaceResult objects
            cached_places = []
            if place_query.places:
                for place_dict in place_query.places:
                    cached_places.append(PlaceResult.from_dict(place_dict))
            results[query_key] = cached_places

            # Store places in new database structure and link to plan
            for place_result in cached_places:
                # Upsert place into places table
                upsert_place(session, place_result)
                # Link place to plan
                link_place_to_plan(session, plan_id, place_result.id)

            plan_query = PlanQuery(
                plan_id=plan_id,
                query_id=place_query.id
            )
            session.add(plan_query)
            session.commit()
            continue
        
        else:
            print(f"\nExecuting query {i+1}: {query}")
            places = []

            if query_type == "nearby":
                category = query.get("category")
                if category:
                    places = places_api.search_places_nearby(
                        location=location,
                        radius=radius_km * 1000,
                        place_types=[category],
                        max_results=max_results_per_query,
                        sort_by_popularity=True
                    )
                    print(f"Found {len(places)} places for nearby search: {category}")
            
            elif query_type == "text":
                text_query = query.get("query")
                if text_query:
                    places = places_api.search_places_by_text(
                        text_query=text_query,
                        location=location,
                        radius=radius_km * 1000,
                        max_results=max_results_per_query,
                        sort_by_popularity=True
                    )
                    print(f"Found {len(places)} places for text search: {text_query}")
            
            results[query_key] = places

            if places:
                # Store places in new database structure
                for place_result in places:
                    # Upsert place into places table
                    upsert_place(session, place_result)
                    # Link place to plan
                    link_place_to_plan(session, plan_id, place_result.id)

                # Convert PlaceResult objects to dictionaries for legacy database storage
                places_dict_list = [place.to_dict() for place in places]

                places_query = PlacesQuery(
                    lat=location.latitude,
                    long=location.longitude,
                    radius_km=radius_km,
                    query_type=query_type or "",
                    query=query_value or "",
                    city=city,
                    country=country,
                    places=places_dict_list
                )
                session.add(places_query)
                session.commit()

                plan_query = PlanQuery(
                    plan_id=plan_id,
                    query_id=places_query.id
                )
                session.add(plan_query)
                session.commit()
            # Add delay between queries to avoid rate limiting
            time.sleep(0.5)
    
    return results


def filter_and_sort_places(places):
    # Filter each place to only include required fields
    filtered_places = []
    for place in places:
        weekday_descriptions = "Open 24 hours"
        opening_hours = place.opening_hours
        if opening_hours:
            weekday_descriptions = opening_hours.get("weekdayDescriptions", [])
            
        filtered_place = {
            "name": place.name,
            "rating": place.rating,
            "opening_hours": weekday_descriptions
        }
        filtered_places.append(filtered_place)
    
    # Sort by rating in descending order (highest rating first)
    filtered_places.sort(key=lambda x: x.get("rating") or 0, reverse=True)
    
    return filtered_places
