from collections import defaultdict
from fastapi import Depends, FastAPI, HTTPException, Query
from datetime import datetime, time
from typing import List, Dict, Any, Optional, Union
import click
import osmnx as ox
import geopandas as gpd
from geopy.distance import geodesic
import logging
import numpy as np
import math
import os
import aiohttp
import asyncio
from urllib.parse import quote
from dotenv import load_dotenv
from sqlmodel import Session, asc, desc, select
from app.database import get_session
from app.models import Category, UserFrequency
import json
from app.utils import generate_llm_response

load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Travel Planner",
    description="A travel planner app backend with POI search capabilities and Yelp ratings",
)

# Yelp API configuration
YELP_API_KEY = os.getenv("YELP_API_KEY")
YELP_CLIENT_ID = os.getenv("YELP_CLIENT_ID")
YELP_API_BASE = "https://api.yelp.com/v3"

if not YELP_API_KEY:
    logger.warning("YELP_API_KEY environment variable not set. Yelp integration will be disabled.")

def parse_yelp_hours(hours_data: List[Dict]) -> Dict[str, Any]:
    """
    Parse Yelp hours data to extract today's closing time and formatted hours
    
    Args:
        hours_data: List of hours data from Yelp API
    
    Returns:
        Dict with closing_time_today (as time object), formatted_hours, and is_open_now
    """
    if not hours_data:
        return {
            "closing_time_today": None,
            "formatted_hours": "Hours not available",
            "is_open_now": None
        }
    
    # Get today's day of week (0=Monday, 6=Sunday)
    today = datetime.now().weekday()
    
    # Yelp uses 0=Monday, 6=Sunday format
    day_names = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    
    formatted_hours = {}
    closing_time_today = None
    is_open_now = None
    
    for hour_info in hours_data:
        if hour_info.get("hours_type") == "REGULAR":
            open_times = hour_info.get("open", [])
            is_open_now = hour_info.get("is_open_now", False)
            
            # Process each day's hours
            for day_hours in open_times:
                day = day_hours.get("day", -1)
                start = day_hours.get("start", "")
                end = day_hours.get("end", "")
                
                if 0 <= day <= 6:
                    day_name = day_names[day]
                    
                    # Format times (Yelp uses 24-hour format like "1000" for 10:00)
                    if start and end:
                        try:
                            start_time = f"{start[:2]}:{start[2:]}" if len(start) == 4 else start
                            end_time = f"{end[:2]}:{end[2:]}" if len(end) == 4 else end
                            formatted_hours[day_name] = f"{start_time} - {end_time}"
                            
                            # If this is today, extract closing time
                            if day == today:
                                # Convert end time to time object
                                if len(end) == 4:
                                    hour = int(end[:2])
                                    minute = int(end[2:])
                                    # Handle 24:00 format (midnight)
                                    if hour == 24:
                                        hour = 0
                                    elif hour > 23:
                                        hour = hour - 24
                                    closing_time_today = time(hour, minute)
                        except (ValueError, IndexError) as e:
                            logger.warning(f"Error parsing Yelp hours: {e}")
                            formatted_hours[day_name] = "Hours format error"
                    else:
                        formatted_hours[day_name] = "Closed"
            
            break  # Only process the first regular hours entry
    
    # Format hours for display
    hours_display = []
    for day in day_names:
        if day in formatted_hours:
            hours_display.append(f"{day}: {formatted_hours[day]}")
    
    return {
        "closing_time_today": closing_time_today,
        "formatted_hours": " | ".join(hours_display) if hours_display else "Hours not available",
        "is_open_now": is_open_now
    }

async def get_yelp_business_details(session: aiohttp.ClientSession, business_id: str) -> Dict[str, Any]:
    """
    Get detailed business information from Yelp including hours
    
    Args:
        session: aiohttp session
        business_id: Yelp business ID
    
    Returns:
        Dict with detailed business info including hours
    """
    if not YELP_API_KEY or not business_id:
        return {}
    
    try:
        headers = {
            "Authorization": f"Bearer {YELP_API_KEY}",
            "Accept": "application/json"
        }
        
        async with session.get(f"{YELP_API_BASE}/businesses/{business_id}", headers=headers) as response:
            if response.status == 200:
                data = await response.json()
                
                # Parse hours information
                hours_data = data.get("hours", [])
                hours_info = parse_yelp_hours(hours_data)
                
                return {
                    "yelp_hours": hours_info["formatted_hours"],
                    "yelp_closing_time_today": hours_info["closing_time_today"],
                    "yelp_is_open_now": hours_info["is_open_now"],
                    # "yelp_transactions": data.get("transactions", []),
                    # "yelp_location": data.get("location", {}),
                    # "yelp_coordinates": data.get("coordinates", {})
                }
            else:
                logger.warning(f"Yelp API error for business {business_id}: {response.status}")
                
    except Exception as e:
        logger.error(f"Error getting Yelp business details for {business_id}: {e}")
    
    return {}

async def search_yelp_business(session: aiohttp.ClientSession, name: str, latitude: float, longitude: float, category: str = "") -> Dict[str, Any]:
    """
    Search for a business on Yelp using name and location
    
    Args:
        session: aiohttp session
        name: Business name
        latitude: Business latitude
        longitude: Business longitude
        category: Business category for better matching
    
    Returns:
        Dict with Yelp business data or empty dict if not found
    """
    if not YELP_API_KEY:
        return {}
    
    try:
        print(f"Searching Yelp for business: {name} at ({latitude}, {longitude}) with category '{category}'")
        # Clean up the name for search
        search_name = name.replace("Unknown", "").strip()
        if not search_name:
            return {}
        
        # Prepare search parameters
        params = {
            "term": search_name,
            "latitude": latitude,
            "longitude": longitude,
            "radius": 100,  # 100 meter radius for precise matching
            "limit": 5,
            "sort_by": "distance"
        }
        
        # Add category if available and relevant
        if category and any(cat in category.lower() for cat in ["restaurant", "food", "bar", "cafe", "hotel"]):
            if "restaurant" in category.lower() or "food" in category.lower():
                params["categories"] = "restaurants"
            elif "bar" in category.lower():
                params["categories"] = "bars"
            elif "cafe" in category.lower():
                params["categories"] = "coffee"
            elif "hotel" in category.lower():
                params["categories"] = "hotels"
        
        headers = {
            "Authorization": f"Bearer {YELP_API_KEY}",
            "Accept": "application/json"
        }
        
        async with session.get(f"{YELP_API_BASE}/businesses/search", params=params, headers=headers) as response:
            if response.status == 200:
                data = await response.json()
                businesses = data.get("businesses", [])
                
                # Find the best match based on name similarity and distance
                best_match = None
                best_score = 0
                
                for business in businesses:
                    # Calculate name similarity (simple approach)
                    business_name = business.get("name", "").lower()
                    search_name_lower = search_name.lower()
                    
                    # Simple name matching score
                    if search_name_lower in business_name or business_name in search_name_lower:
                        name_score = 0.8
                    elif any(word in business_name for word in search_name_lower.split()):
                        name_score = 0.6
                    else:
                        name_score = 0.3
                    
                    # Distance score (closer is better)
                    business_coords = business.get("coordinates", {})
                    if business_coords:
                        business_lat = business_coords.get("latitude")
                        business_lon = business_coords.get("longitude")
                        if business_lat and business_lon:
                            distance = geodesic((latitude, longitude), (business_lat, business_lon)).meters
                            distance_score = max(0, 1 - (distance / 100))  # Within 100m gets full score
                        else:
                            distance_score = 0
                    else:
                        distance_score = 0
                    
                    total_score = (name_score * 0.7) + (distance_score * 0.3)
                    
                    if total_score > best_score and total_score > 0.4:  # Minimum threshold
                        best_score = total_score
                        best_match = business
                
                if best_match:
                    basic_info = {
                        "yelp_id": best_match.get("id", ""),
                        "yelp_name": best_match.get("name", ""),
                        "yelp_rating": best_match.get("rating", 0),
                        "yelp_categories": [cat.get("title", "") for cat in best_match.get("categories", [])],
                        "yelp_is_closed": best_match.get("is_closed", False),
                    }
                    
                    # Get detailed info including hours
                    business_id = best_match.get("id", "")
                    if business_id:
                        detailed_info = await get_yelp_business_details(session, business_id)
                        basic_info.update(detailed_info)
                    
                    # Add default values for missing hour info
                    if "yelp_hours" not in basic_info:
                        basic_info.update({
                            "yelp_hours": "Hours not available",
                            "yelp_closing_time_today": None,
                            "yelp_is_open_now": None
                        })  # Small delay to respect rate limits
                    
                    return basic_info
                    
            else:
                logger.warning(f"Yelp API error for {name}: {response.status}")
                
    except Exception as e:
        logger.error(f"Error searching Yelp for {name}: {e}")
    
    return {}

async def enrich_pois_with_yelp(poi_list: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Enrich POI list with Yelp data
    
    Args:
        poi_list: List of POI dictionaries
    
    Returns:
        Enhanced POI list with Yelp data
    """
    if not YELP_API_KEY or not poi_list:
        return poi_list
    
    enriched_pois = []
    
    async with aiohttp.ClientSession() as session:
        # Process POIs in batches to respect rate limits
        batch_size = 1  # Reduced batch size due to additional API calls
        for i in range(0, len(poi_list), batch_size):
            batch = poi_list[i:i + batch_size]
            tasks = []
            
            for poi in batch:
                task = search_yelp_business(
                    session=session,
                    name=poi["name"],
                    latitude=poi["latitude"],
                    longitude=poi["longitude"],
                    category=poi.get("category", "")
                )
                tasks.append(task)
            
            # Execute batch requests
            yelp_results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Merge results
            for poi, yelp_data in zip(batch, yelp_results):
                enhanced_poi = poi.copy()
                
                if isinstance(yelp_data, dict) and yelp_data:
                    # Convert time object to string before adding to enhanced_poi
                    if 'yelp_closing_time_today' in yelp_data and yelp_data['yelp_closing_time_today']:
                        yelp_data['yelp_closing_time_today'] = yelp_data['yelp_closing_time_today'].strftime('%H:%M')
    
                    enhanced_poi.update(yelp_data)
                    # Add sorting priority based on rating and review count
                    rating = yelp_data.get("yelp_rating", 0)
                    review_count = yelp_data.get("yelp_review_count", 0)
                    # Weighted score: rating * log(review_count + 1) to balance rating and popularity
                    enhanced_poi["sort_score"] = rating * math.log(review_count + 1)
                    
                    # Add closing time sort value (minutes from midnight)
                    closing_time = yelp_data.get("yelp_closing_time_today")
                    if closing_time:
                        if isinstance(closing_time, str):
                            hour, minute = map(int, closing_time.split(':'))
                            enhanced_poi["closing_time_minutes"] = hour * 60 + minute
                        else:
                            enhanced_poi["closing_time_minutes"] = closing_time.hour * 60 + closing_time.minute
                    else:
                        enhanced_poi["closing_time_minutes"] = 9999  # Places without hours go to end
                        
                else:
                    # Default values for POIs without Yelp data
                    enhanced_poi.update({
                        "yelp_rating": 0,
                        "yelp_is_closed": False,
                        "yelp_hours": "Hours not available",
                        "yelp_closing_time_today": None,
                        "yelp_is_open_now": None,
                    })
                
                enriched_pois.append(enhanced_poi)
            
            # Small delay between batches to respect rate limits
            if i + batch_size < len(poi_list):
                await asyncio.sleep(0.4)  # Increased delay due to additional API calls
    
    return enriched_pois

# Function that will be available to OpenAI for function calling
async def search_poi_for_ai(
    search_tag: dict,
    lat: float,
    lon: float,
    radius_km: float = 10,
    rating: float = 4.0,
    sort_by: str = "closing_time"
) -> Dict[str, Any]:
    """
    Search for POIs - this function will be called by OpenAI
    """
    try:
        # Get OSM tags for the search
        print(f"Params received: search_tag={search_tag}, lat={lat}, lon={lon}, radius_km={radius_km}, rating={rating}, sort_by={sort_by}")
        print("Searching for POIs with tags:", search_tag, type(search_tag))
        # Use point-based query
        try:
            pois = ox.features_from_point(
                center_point=(lat, lon),
                tags=search_tag,
                dist=radius_km * 1000  # Convert to meters
            )
        except Exception as e:
            logger.error(f"Failed to fetch POIs: {e}")
            return {
                "pois": [],
                "count": 0,
                "message": f"No POI found within {radius_km}km of the specified location"
            }
        
        if pois.empty:
            return {
                "pois": [],
                "count": 0,
                "message": f"No POI found within {radius_km}km"
            }
        
        # Process POIs and filter by distance
        poi_list = []
        center_point = (lat, lon)
        
        for idx, poi in pois.iterrows():
            try:
                # Get coordinates and validate them
                poi_coords = None
                
                if hasattr(poi.geometry, 'centroid'):
                    # For polygons, use centroid
                    centroid = poi.geometry.centroid
                    if hasattr(centroid, 'y') and hasattr(centroid, 'x'):
                        lat_coord = centroid.y
                        lon_coord = centroid.x
                elif hasattr(poi.geometry, 'y') and hasattr(poi.geometry, 'x'):
                    # For points
                    lat_coord = poi.geometry.y
                    lon_coord = poi.geometry.x
                else:
                    continue
                
                # Validate coordinates are not NaN or infinite
                if (math.isnan(lat_coord) or math.isnan(lon_coord) or 
                    math.isinf(lat_coord) or math.isinf(lon_coord)):
                    continue
                
                poi_coords = (lat_coord, lon_coord)
                
                # Calculate distance
                distance = geodesic(center_point, poi_coords).kilometers
                
                # Validate distance
                if math.isnan(distance) or math.isinf(distance):
                    continue
                
                # Filter by radius
                if distance <= radius_km:
                    # Get and validate name
                    name = poi.get("name", "Unknown")
                    if isinstance(name, float) and math.isnan(name):
                        name = "Unknown"
                    
                    # Get and validate other fields
                    opening_hours = poi.get("opening_hours", "")
                    if isinstance(opening_hours, float) and math.isnan(opening_hours):
                        opening_hours = ""
                    
                    poi_data = {
                        "name": str(name),
                        "latitude": round(float(lat_coord), 6),
                        "longitude": round(float(lon_coord), 6),
                        "distance_km": round(float(distance), 2),
                        "opening_hours": str(opening_hours),
                    }
                    
                    poi_list.append(poi_data)
                    
            except Exception as e:
                logger.warning(f"Error processing POI {idx}: {e}")
                continue
        
        print(f"Found {len(poi_list)} POIs within {radius_km}km of ({lat}, {lon}). Here are the details:", poi_list)
        # Enrich with Yelp data
        enriched_poi_list = await enrich_pois_with_yelp(poi_list)
        
        # Filter by rating if specified
        if rating > 0:
            enriched_poi_list = [poi for poi in enriched_poi_list if poi.get("yelp_rating", 0) >= rating]
        
        # Sort based on the requested criteria
        if sort_by == "closing_time":
            enriched_poi_list.sort(key=lambda x: (x.get("closing_time_minutes", 9999), -x.get("yelp_rating", 0), x["distance_km"]))
        elif sort_by == "rating":
            enriched_poi_list.sort(key=lambda x: (-x.get("yelp_rating", 0), x["distance_km"]))
        elif sort_by == "distance":
            enriched_poi_list.sort(key=lambda x: (x["distance_km"], -x.get("yelp_rating", 0)))
        
        return {
            "pois": enriched_poi_list,
            "count": len(enriched_poi_list)
        }
        
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid JSON format for search_tag")
    
    except Exception as e:
        logger.error(f"Error in search_poi_for_ai: {e}")
        return {
            "pois": [],
            "count": 0,
            "message": f"Error: {str(e)}"
        }

@app.get("/")
async def root():
    return "Hello World! This is a travel planner with Yelp integration"

@app.get("/poi/search")
async def search_poi(
    lat: float = Query(..., description="Latitude", ge=-90, le=90),
    lon: float = Query(..., description="Longitude", ge=-180, le=180),
    search_tag: str = Query(..., description="Search tags for osmnx search"),
    radius_km: float = Query(10, description="Search radius in kilometers", gt=0, le=50),
    sort_by: str = Query("closing_time", description="Sort by: 'closing_time', 'rating', 'distance', 'review_count'")
):
    """
    Search for Points of Interest (POI) within a specified radius with Yelp ratings and hours
    """
    return await search_poi_for_ai(search_tag, lat, lon, radius_km, 0, sort_by)

@app.get("/plan")
async def get_plan(
    user_id: int = Query(1, description="User ID"),
    city_id: int = Query(1, description="City ID"),
    lat: float = Query(..., description="Latitude", ge=-90, le=90),
    lon: float = Query(..., description="Longitude", ge=-180, le=180),
    radius_km: float = Query(10, description="Search radius in kilometers", gt=0, le=50),
    rating: float = Query(4, description="Minimum Yelp rating", ge=0, le=5),
    intent: str = Query("travel", description="Intent of the plan"),
    session: Session = Depends(get_session)
):
    try:
        # Get user activity data
        query = (
            select(
                UserFrequency.time_slot,
                Category.category_name,
                UserFrequency.count
            )
            .join(Category)
            .where(UserFrequency.poi_category_id == Category.category_id)
            .where(UserFrequency.user_id == user_id)
        )
        
        # Add city filter if provided
        if city_id is not None:
            query = query.where(UserFrequency.city_id == city_id)
        
        # Order by count descending for easier processing
        query = query.order_by(asc(UserFrequency.time_slot), desc(UserFrequency.count))
        
        # Execute query
        results = session.exec(query).all()
        
        if not results:
            raise HTTPException(status_code=404, detail=f"No activity found for user {user_id}")
        
        # Group results by time_slot and get top 3 for each
        time_slot_categories = defaultdict(list)
        
        for time_slot, category_name, count in results:
            if len(time_slot_categories[time_slot]) < 3:
                time_slot_categories[time_slot].append(category_name)
        
        # Convert defaultdict to regular dict and ensure consistent ordering
        user_activity = dict(sorted(time_slot_categories.items()))
        
        # Define the function schema for OpenAI
        function_schema = {
            "name": "search_poi",
            "description": "Search for Points of Interest using OSM tags. Use this to find specific types of places like restaurants, shops, attractions, etc.",
            "parameters": {
                "type": "object",
                "properties": {
                    "search_tag": {
                        "type": "string",
                        "description": "Pass json object as string. OSM tags to search for. Examples: {'amenity': 'restaurant'}, {'shop': 'supermarket'}, {'tourism': 'attraction'}, {'leisure': 'park'}, {'amenity': ['cafe', 'bar']}"
                    },
                    "sort_by": {
                        "type": "string",
                        "enum": ["closing_time", "rating", "distance"],
                        "description": "How to sort the results. Use 'closing_time' to prioritize places that close soon."
                    }
                },
                "required": ["search_tag"]
            }
        }
        
        # Prepare the system message
        system_message = """You are a comprehensive travel planner AI that creates diverse, full-day itineraries. You will receive a user's mobility history showing their top 3 preferred activity categories for each 30-minute time slot throughout the day (48 time slots total).

            ## Core Requirements:

            ### 1. Activity Pattern Analysis
            - Analyze the user's activity patterns across all 48 time slots (0-47, each representing 30 minutes)
            - Identify peak activity times, preferred categories, and natural flow patterns
            - Consider the user's stated intent alongside their historical preferences

            ### 2. Diverse POI Search Strategy
            **RECOMMENDED**: Unless the user specifies otherwise, search for AT LEAST 6 different POI categories using multiple search_poi calls:
            - **Food & Dining**: restaurants, cafes, bars, food trucks, bakeries
            - **Entertainment**: cinemas, theaters, music venues, gaming centers
            - **Shopping**: malls, markets, boutiques, specialty stores
            - **Culture & Tourism**: museums, galleries, historical sites, landmarks
            - **Recreation**: parks, sports facilities, beaches, outdoor activities
            - **Services**: spas, fitness centers, libraries, co-working spaces

            **Search Strategy**:
            - Make 6-8 separate search_poi calls with different tags
            - Use varied OSM format tags for each category:
            - Food: {'amenity': 'restaurant'}, {'amenity': 'cafe'}, {'amenity': 'bar'}
            - Shopping: {'shop': 'mall'}, {'shop': 'supermarket'}, {'shop': 'clothes'}
            - Culture: {'tourism': 'attraction'}, {'tourism': 'museum'}, {'amenity': 'library'}
            - Recreation: {'leisure': 'park'}, {'leisure': 'sports_centre'}, {'natural': 'beach'}
            - Entertainment: {'amenity': 'cinema'}, {'amenity': 'theatre'}
            - Services: {'leisure': 'spa'}, {'amenity': 'gym'}

            ### 3. Comprehensive Plan Requirements
            - **Minimum 12-15 places** (unless user specifies fewer)
            - **Balanced distribution**: When searching multiple categories, no single category should dominate (max 30% of total places)
            - **Respect user intent**: If user specifies particular focus areas, prioritize those while still providing some variety
            - **Time-appropriate activities**: Match activities to typical operating hours and user patterns
            - **Logical flow**: Consider travel time and geographic proximity
            - **Complete day coverage**: Include breakfast, lunch, dinner, and activities throughout the day

            ### 4. Enhanced Recommendation Logic
            - **Priority factors** (in order):
            1. User's stated intent and goals
            2. Historical activity patterns from mobility data
            3. Time-appropriate venue hours
            4. Geographic proximity and travel efficiency
            5. Venue popularity and ratings

            ### 5. Markdown Format (STRICT)
            For each place, use exactly this format:

            ## [Place Name]
            **Time:** [Recommended visit time]
            **Distance:** [Distance from previous location]
            **Yelp Rating:** [Rating/5 stars]
            **Reason:** [Why this place matches user preferences and fits the itinerary]

            ### 6. Quality Assurance Checklist
            Before finalizing, ensure:
            - [ ] Multiple POI categories represented (aim for 6+ unless user specifies otherwise)
            - [ ] 12-15 total places recommended (adjust based on user needs)
            - [ ] When using multiple categories, no category exceeds 30% of total recommendations
            - [ ] User's specific requests are prioritized
            - [ ] Logical time progression throughout the day
            - [ ] Includes meals (breakfast, lunch, dinner)
            - [ ] Activities match user's historical patterns
            - [ ] All places have proper formatting

            ## Example Search Sequence:
            1. search_poi({'amenity': 'restaurant'}) 
            2. search_poi({'tourism': 'attraction'})
            3. search_poi({'shop': 'mall'})
            4. search_poi({'leisure': 'park'})
            5. search_poi({'amenity': 'cafe'})
            6. search_poi({'amenity': 'cinema'})
            7. search_poi({'amenity': 'bar'})
            8. search_poi({'tourism': 'museum'})

            Remember: Diversity is encouraged to create rich, varied experiences, but always prioritize the user's stated preferences and intent. When no specific focus is given, aim for variety that goes beyond the user's top preferences to introduce them to new experiences while respecting their core interests."""

        # Prepare the user message
        user_message = f"""User Activity History:
            {json.dumps(user_activity, indent=2)}

            Location: Latitude {lat}, Longitude {lon}
            Search radius: {radius_km} km
            Minimum rating: {rating}
            Intent: {intent}

            Please create a personalized travel plan for this user based on their activity history and travel intent. Use the search_poi function to find relevant places."""

        # Create the messages for OpenAI
        messages = [
            {"role": "system", "content": system_message},
            {"role": "user", "content": user_message}
        ]
        
        print(f"Messages for OpenAI: {json.dumps(messages, indent=2)}")

        # Make the initial call to OpenAI
        try:
            response = generate_llm_response(
                messages=messages,
                model_name="gpt-4.1",
                temperature=0.7,
                function_schema=function_schema,
            )

            print(f"Raw response from OpenAI: {response}")
            
            # Check if the AI wants to make function calls
            if "function_call" in response:
                # Handle function calls
                function_results = []
                
                func_call = response["function_call"]
                print(f"Function call detected: {func_call}")
                if func_call["name"] == "search_poi":
                    search_params = func_call["arguments"]
                    
                    # Add default sort_by if not provided
                    if "sort_by" not in search_params:
                        search_params["sort_by"] = "closing_time"
                    
                    print(f"Calling search_poi with params: {search_params}")
                    # Call the search function
                    search_result = await search_poi_for_ai(
                        search_tag=json.loads(search_params["search_tag"].replace("'", "\"")),
                        lat=lat,
                        lon=lon,
                        radius_km=radius_km,
                        rating=rating,
                        sort_by=search_params.get("sort_by", "closing_time")
                    )

                    print(f"Search result: {search_result}")
                    
                    function_results.append({
                        "function_name": "search_poi",
                        "parameters": search_params,
                        "result": search_result
                    })
                
                # Send the function results back to OpenAI for final plan generation
                messages.append({"role": "assistant", "content": json.dumps(response)})
                messages.append({
                    "role": "user", 
                    "content": f"Function call results: {json.dumps(function_results, indent=2)}\n\nNow generate the final travel plan in markdown format."
                })
                
                # Get the final response
                final_response = generate_llm_response(
                    messages=messages,
                    model_name="gpt-4-turbo",
                    temperature=0.7,
                    function_schema=function_schema,
                )
                
                print(f"Final response from OpenAI: {final_response}")
                travel_plan = final_response
                
            else:
                # If no function calls, the AI provided a direct response
                travel_plan = response_data.get("travel_plan", "Plan generation failed")
            
            return {
                "user_id": user_id,
                "city_id": city_id,
                "user_activity": user_activity,
                "travel_plan": travel_plan,
                "location": {"latitude": lat, "longitude": lon},
                "parameters": {
                    "radius_km": radius_km,
                    "rating": rating,
                    "intent": intent
                }
            }
            
        except Exception as e:
            logger.error(f"Error generating travel plan: {e}")
            raise HTTPException(status_code=500, detail=f"Error generating travel plan: {str(e)}")
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error in get_plan: {e}")
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)