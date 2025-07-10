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
from sqlmodel import Session, asc, desc, func, select
from app.database import get_session
from app.models import Category, UserFrequency
import json
from app.utils import generate_llm_response
import time as time_module

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
                try:
                    error_data = await response.json()
                    logger.warning(f"Yelp API error for {business_id}: {response.status} - {error_data}")
                except:
                    error_text = await response.text()
                    logger.warning(f"Yelp API error for {business_id}: {response.status} - {error_text}")
                
                
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
                try:
                    error_data = await response.json()
                    logger.warning(f"Yelp API error for {name}: {response.status} - {error_data}")
                except:
                    error_text = await response.text()
                    logger.warning(f"Yelp API error for {name}: {response.status} - {error_text}")
                
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
        batch_size = 3  # Reduced batch size due to additional API calls
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


            # Approximate popularity by tag richness
            pois["tag_count"] = pois.apply(lambda row: len(row.dropna()), axis=1)

            # Get top 100
            pois = pois.sort_values(by="tag_count", ascending=False).head(100)

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
                if distance <= radius_km + 1:
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
        
        # Limit to top 20 results if more than 20
        if len(enriched_poi_list) > 20:
            enriched_poi_list = enriched_poi_list[:20]

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
    radius_km: float = Query(10, description="Search radius in kilometers", gt=0, le=50),
    sort_by: str = Query("closing_time", description="Sort by: 'closing_time', 'rating', 'distance', 'review_count'")
):
    """
    Search for Points of Interest (POI) within a specified radius with Yelp ratings and hours
    """
    return await search_poi_for_ai({'amenity': True}, lat, lon, radius_km, 0, sort_by)

@app.get("/plan")
async def get_plan(
    user_id: int = Query(1, description="User ID"),
    city_id: int = Query(1, description="City ID"),
    lat: float = Query(48.8575, description="Latitude", ge=-90, le=90),
    lon: float = Query(2.3514, description="Longitude", ge=-180, le=180),
    radius_km: float = Query(2, description="Search radius in kilometers", gt=0, le=50),
    rating: float = Query(3, description="Minimum Yelp rating", ge=0, le=5),
    intent: str = Query("travel, sight seeing and trying local food", description="Intent of the plan"),
    model: str = Query("llama", description="LLM model to use for generating the plan"),
    session: Session = Depends(get_session)
):
    try:
        # Get user activity data
        query = (
            select(Category.category_name)
            .select_from(UserFrequency)
            .join(Category)
            .where(UserFrequency.poi_category_id == Category.category_id)
            .where(UserFrequency.user_id == user_id)
            .group_by(Category.category_name)
            .order_by(desc(func.sum(UserFrequency.count)))
        )

        # Add city filter if provided
        if city_id is not None:
            query = query.where(UserFrequency.city_id == city_id)

        # Execute query
        results = session.exec(query).all()
        
        if not results:
            raise HTTPException(status_code=404, detail=f"No activity found for user {user_id}")
        
        user_activity = results

        print("Fetching POIs within radius:", radius_km, "km from coordinates:", lat, lon)
        pois = await search_poi_for_ai(
            search_tag={'amenity': True},
            lat=lat,
            lon=lon,
            radius_km=radius_km,
            rating=rating,
            sort_by="closing_time"
        )

        print(f"Found {pois['count']} POIs after filtering. Here are the details:", pois)
        system_prompt = """
            # Travel Planner System Prompt

            You are an expert travel planner AI that creates personalized, realistic, and enjoyable travel itineraries. You will be provided with three key inputs:

            1. **User's Past Activity**: Historical data showing places the user has frequently visited, categorized by type (Restaurant, Park, Church, Real Estate, Shopping, Museums, Entertainment, etc.)
            2. **Available POIs**: Points of interest near the target location, filtered by user preferences (radius, rating, etc.)
            3. **User Intent**: A string describing what the user wants to see, do, or experience during their visit

            ## Your Primary Objectives

            Create a comprehensive travel plan that:
            - **Personalizes** the experience based on the user's demonstrated preferences from their past activity
            - **Fulfills** the user's stated intent and desires
            - **Includes 8-10 diverse locations** to visit throughout the day/trip
            - **Feels natural and realistic** with proper pacing, transitions, and logical flow
            - **Accounts for practical constraints** like opening hours, meal times, and travel logistics

            ## Planning Principles

            ### 1. Personalization Based on Past Activity
            - **Identify patterns** in the user's historical visits (e.g., frequent park visits suggest outdoor preferences, regular church attendance indicates cultural/spiritual interests)
            - **Weight recommendations** toward categories the user has shown preference for
            - **Balance familiarity with novelty** - include some types of places they know they enjoy, but also introduce new experiences that align with their interests
            - **Consider frequency and recency** of past visits when making recommendations

            ### 2. Intent Integration
            - **Prioritize locations and activities** that directly address the user's stated intent
            - **Interpret intent broadly** - if they want "local culture," consider museums, markets, historic sites, local neighborhoods
            - **Fill gaps** where intent is vague by leveraging their past activity patterns
            - **Ensure coherence** between stated intent and planned activities

            ### 3. Practical Logistics
            - **Respect operating hours** - never schedule visits to closed venues
            - **Plan strategic meal times** - include breakfast, lunch, and dinner at appropriate intervals (typically 7-9am, 12-2pm, 6-8pm)
            - **Consider travel time** between locations and group nearby attractions
            - **Account for energy levels** - alternate high-energy activities with more relaxed ones
            - **Factor in seasonal considerations** and weather-appropriate activities

            ### 4. Natural Flow and Pacing
            - **Start with easier, welcoming activities** to build momentum
            - **Peak experiences** should be scheduled when the user is most alert and engaged
            - **Include downtime** - coffee breaks, scenic spots for rest, leisurely walks
            - **End thoughtfully** - conclude with memorable but not overwhelming experiences
            - **Logical geography** - minimize backtracking and excessive travel time

            ### 5. Diverse Experience Design
            - **Mix activity types**: active/passive, indoor/outdoor, cultural/recreational, social/solitary
            - **Include local specialties** - food, attractions, or experiences unique to the area
            - **Balance popular and hidden gems** based on available POI data
            - **Consider group dynamics** if applicable (family-friendly, romantic, solo travel, etc.)

            ## Output Format

            Structure your travel plan as follows:

            ### Travel Plan Overview
            - **Duration**: [Time span covered]
            - **Theme**: [Brief description of the overall experience]
            - **Personalization Notes**: [How this plan reflects their past preferences]

            ### Detailed Itinerary

            For each location/activity:
            - **Time**: [Specific time window]
            - **Location**: [Name and brief description]
            - **Duration**: [How long to spend here]
            - **Why This Choice**: [Brief explanation connecting to their past activity and/or intent]
            - **Practical Notes**: [Operating hours, reservations needed, etc.]

            ### Meal Planning
            - **Breakfast**: [Location and reasoning]
            - **Lunch**: [Location and reasoning]
            - **Dinner**: [Location and reasoning]
            - **Snacks/Coffee**: [Any planned refreshment stops]

            ### Logistics Summary
            - **Total locations**: [Count]
            - **Travel considerations**: [Transportation notes, walking distances, etc.]
            - **Timing buffer**: [How breaks/flexibility are built in]
            - **Weather backup**: [Alternative indoor options if needed]

            ## Important Constraints

            - **Never recommend closed venues** - always verify and respect operating hours
            - **Maintain realistic timing** - account for travel time, lines, and natural pace
            - **Include meal solutions** - don't leave users without food options during meal times
            - **Stay within provided POI data** - only recommend from the available filtered options
            - **Respect user intent** - the stated intent should be clearly addressable in your plan
            - **Ensure minimum 8 locations** - but prioritize quality over quantity if needed for better experience

            ## Quality Checks

            Before finalizing, verify:
            - [ ] All venues are open during planned visit times
            - [ ] Meals are appropriately spaced and included
            - [ ] Travel between locations is feasible within time constraints
            - [ ] Plan reflects user's demonstrated preferences from past activity
            - [ ] User's stated intent is clearly addressed
            - [ ] Experience has natural flow and good pacing
            - [ ] Minimum 8-10 locations are included
            - [ ] Mix of activity types provides variety

            Remember: A great travel plan feels effortless to the user while being meticulously planned behind the scenes. Focus on creating experiences that feel both personally meaningful and practically seamless.
            """
        
        user_message = f"""User Activity History:
        {json.dumps(user_activity, indent=2)}
        User Intent: {intent}
        POI Search Results:
        {json.dumps(pois, indent=2)}

        Please create a personalized travel plan for this user based on their activity history and travel intent."""

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message}
        ]

        llm_start = time_module.perf_counter()
        response = generate_llm_response(
                    messages=messages,
                    model_name=model,
                    temperature=0.7,
                )
        llm_time = (time_module.perf_counter() - llm_start) * 1000
        
        print("Generated travel plan response:", response)
        
        return {
            "plan": response,
            "user_activity": user_activity,
            "pois": pois,
            "llm_time_ms": llm_time
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error in get_plan: {e}")
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)