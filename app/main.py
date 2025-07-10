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
                    "yelp_transactions": data.get("transactions", []),
                    "yelp_location": data.get("location", {}),
                    "yelp_coordinates": data.get("coordinates", {})
                }
            else:
                logger.warning(f"Yelp API error for business {business_id}: {response.status}, {response.text}")
                
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
                        # "yelp_review_count": best_match.get("review_count", 0),
                        # "yelp_price": best_match.get("price", ""),
                        # "yelp_url": best_match.get("url", ""),
                        # "yelp_image_url": best_match.get("image_url", ""),
                        "yelp_categories": [cat.get("title", "") for cat in best_match.get("categories", [])],
                        # "yelp_phone": best_match.get("display_phone", ""),
                        "yelp_is_closed": best_match.get("is_closed", False),
                        # "match_score": round(best_score, 2)
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
                        })
                    
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
        batch_size = 2  # Reduced batch size due to additional API calls
        for i in range(0, len(poi_list), batch_size):
            batch = poi_list[i:i + batch_size]
            tasks = []
            
            for poi in batch:
                task = search_yelp_business(
                    session=session,
                    name=poi["name"],
                    latitude=poi["latitude"],
                    longitude=poi["longitude"],
                    category=poi["category"]
                )
                tasks.append(task)
            
            # Execute batch requests
            yelp_results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Merge results
            for poi, yelp_data in zip(batch, yelp_results):
                enhanced_poi = poi.copy()
                
                if isinstance(yelp_data, dict) and yelp_data:
                    enhanced_poi.update(yelp_data)
                    # Add sorting priority based on rating and review count
                    rating = yelp_data.get("yelp_rating", 0)
                    review_count = yelp_data.get("yelp_review_count", 0)
                    # Weighted score: rating * log(review_count + 1) to balance rating and popularity
                    enhanced_poi["sort_score"] = rating * math.log(review_count + 1)
                    
                    # Add closing time sort value (minutes from midnight)
                    closing_time = yelp_data.get("yelp_closing_time_today")
                    if closing_time:
                        enhanced_poi["closing_time_minutes"] = closing_time.hour * 60 + closing_time.minute
                    else:
                        enhanced_poi["closing_time_minutes"] = 9999  # Places without hours go to end
                        
                else:
                    # Default values for POIs without Yelp data
                    enhanced_poi.update({
                        "yelp_rating": 0,
                        # "yelp_review_count": 0,
                        # "yelp_price": "", 
                        # "yelp_url": "",
                        # "yelp_image_url": "",
                        # "yelp_categories": [],
                        # "yelp_phone": "",
                        "yelp_is_closed": False,
                        "yelp_hours": "Hours not available",
                        "yelp_closing_time_today": None,
                        "yelp_is_open_now": None,
                        # "sort_score": 0,
                        # "closing_time_minutes": 9999
                    })
                
                enriched_pois.append(enhanced_poi)
            
            # Small delay between batches to respect rate limits
            if i + batch_size < len(poi_list):
                await asyncio.sleep(0.2)  # Increased delay due to additional API calls
    
    return enriched_pois

@app.get("/")
async def root():
    return "Hello World! This is a travel planner with Yelp integration"

# @app.get("/poi/categories")
# async def get_poi_categories():
#     """Get list of available POI categories"""
#     return {
#         "categories": list(POI_CATEGORIES.keys()),
#         "total": len(POI_CATEGORIES),
#         "yelp_integration": YELP_API_KEY is not None
#     }

@app.get("/poi/search")
async def search_poi(
    lat: float = Query(..., description="Latitude", ge=-90, le=90),
    lon: float = Query(..., description="Longitude", ge=-180, le=180),
    search_tag: dict[str, bool | str | list[str]] = Query(..., description="Search tags for osmnx search"),
    radius_km: float = Query(10, description="Search radius in kilometers", gt=0, le=50),
    sort_by: str = Query("closing_time", description="Sort by: 'closing_time', 'rating', 'distance', 'review_count'")
):
    """
    Search for Points of Interest (POI) within a specified radius with Yelp ratings and hours
    
    Args:
        lat: Latitude of the search center
        lon: Longitude of the search center
        search_tag: Search tags for osmnx search
        radius_km: Search radius in kilometers (max 50km)
        sort_by: Sort results by 'closing_time', 'rating', 'distance', or 'review_count'
    
    Returns:
        List of POIs with their details, Yelp ratings, and hours information
    """
    try:
        # Validate category
        # category_lower = category.lower().strip()
        # if category_lower not in POI_CATEGORIES:
        #     raise HTTPException(
        #         status_code=400, 
        #         detail=f"Category '{category}' not supported. Use /poi/categories to see available categories."
        #     )
        
        # Validate sort_by parameter
        valid_sort_options = ["closing_time", "rating", "distance", "review_count"]
        if sort_by not in valid_sort_options:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid sort_by parameter. Must be one of: {valid_sort_options}"
            )
        
        # logger.info(f"Searching for {category_lower} near ({lat}, {lon}) within {radius_km}km")
        
        # Get OSM tags for the category
        tags = search_tag
        print(f"Using tags: {tags}")
        
        # Use point-based query which is more efficient and respects the radius better
        try:
            pois = ox.features_from_point(
                center_point=(lat, lon),
                tags=tags,
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
                    logger.warning(f"Invalid coordinates for POI {idx}: ({lat_coord}, {lon_coord})")
                    continue
                
                poi_coords = (lat_coord, lon_coord)
                
                # Calculate distance
                distance = geodesic(center_point, poi_coords).kilometers
                
                # Validate distance
                if math.isnan(distance) or math.isinf(distance):
                    logger.warning(f"Invalid distance calculated for POI {idx}")
                    continue
                
                # Filter by radius
                if distance <= radius_km:
                    # Get and validate name
                    name = poi.get("name", "Unknown")
                    if isinstance(name, float) and math.isnan(name):
                        name = "Unknown"
                    
                    # Get and validate other fields
                    address = poi.get("addr:full") or poi.get("addr:street", "")
                    if isinstance(address, float) and math.isnan(address):
                        address = ""
                    
                    phone = poi.get("phone", "")
                    if isinstance(phone, float) and math.isnan(phone):
                        phone = ""
                    
                    website = poi.get("website", "")
                    if isinstance(website, float) and math.isnan(website):
                        website = ""
                    
                    opening_hours = poi.get("opening_hours", "")
                    if isinstance(opening_hours, float) and math.isnan(opening_hours):
                        opening_hours = ""
                    
                    poi_data = {
                        "name": str(name),
                        "latitude": round(float(lat_coord), 6),
                        "longitude": round(float(lon_coord), 6),
                        "distance_km": round(float(distance), 2),
                        # "category": category_lower,
                        # "address": str(address),
                        # "phone": str(phone),
                        # "website": str(website),
                        "opening_hours": str(opening_hours),
                        # "osm_id": str(idx) if idx is not None else "unknown"
                    }
                    
                    
            except Exception as e:
                logger.warning(f"Error processing POI {idx}: {e}")
                continue
        
        # Enrich with Yelp data
        enriched_poi_list = await enrich_pois_with_yelp(poi_list)
        
        # Sort based on the requested criteria
        if sort_by == "closing_time":
            # Sort by closing time (earliest closing first), then by rating, then by distance
            enriched_poi_list.sort(key=lambda x: (x.get("closing_time_minutes", 9999), -x.get("yelp_rating", 0), x["distance_km"]))
        elif sort_by == "rating":
            # Sort by sort_score (weighted rating), then by rating, then by distance
            enriched_poi_list.sort(key=lambda x: (-x.get("sort_score", 0), -x.get("yelp_rating", 0), x["distance_km"]))
        elif sort_by == "review_count":
            # Sort by review count, then by rating, then by distance
            enriched_poi_list.sort(key=lambda x: (-x.get("yelp_review_count", 0), -x.get("yelp_rating", 0), x["distance_km"]))
        else:  # sort_by == "distance"
            # Sort by distance, then by rating
            enriched_poi_list.sort(key=lambda x: (x["distance_km"], -x.get("yelp_rating", 0)))
        
        return {
            "pois": enriched_poi_list,
            "count": len(enriched_poi_list),
            # "search_params": {
            #     "latitude": lat,
            #     "longitude": lon,
            #     "category": category_lower,
            #     "radius_km": radius_km,
            #     "sort_by": sort_by
            # },
            # "yelp_integration_enabled": YELP_API_KEY is not None,
            # "total_with_yelp_data": sum(1 for poi in enriched_poi_list if poi.get("yelp_rating", 0) > 0)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error in POI search: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


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
        # Build the query with join
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
        result = dict(sorted(time_slot_categories.items()))
        
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)