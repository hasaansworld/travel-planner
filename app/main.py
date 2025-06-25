from fastapi import FastAPI, HTTPException, Query
from datetime import datetime
from typing import List, Dict, Any, Optional
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

# POI category mapping for OSM tags
POI_CATEGORIES = {
    # Food categories
    "food": {"amenity": "restaurant"},
    "japanese restaurant": {"amenity": "restaurant", "cuisine": "japanese"},
    "western restaurant": {"amenity": "restaurant", "cuisine": ["american", "european", "french", "italian"]},
    "eat all you can restaurant": {"amenity": "restaurant", "diet": "buffet"},
    "chinese restaurant": {"amenity": "restaurant", "cuisine": "chinese"},
    "indian restaurant": {"amenity": "restaurant", "cuisine": "indian"},
    "ramen restaurant": {"amenity": "restaurant", "cuisine": "ramen"},
    "curry restaurant": {"amenity": "restaurant", "cuisine": "curry"},
    "bbq restaurant": {"amenity": "restaurant", "cuisine": "barbecue"},
    "hot pot restaurant": {"amenity": "restaurant", "cuisine": "hot_pot"},
    "bar": {"amenity": "bar"},
    "diner": {"amenity": "restaurant", "restaurant": "diner"},
    "creative cuisine": {"amenity": "restaurant", "cuisine": "fusion"},
    "organic cuisine": {"amenity": "restaurant", "organic": "yes"},
    "pizza": {"amenity": "restaurant", "cuisine": "pizza"},
    "café": {"amenity": "cafe"},
    "tea salon": {"amenity": "cafe", "cuisine": "tea"},
    "bakery": {"shop": "bakery"},
    "sweets": {"shop": "confectionery"},
    "wine bar": {"amenity": "bar", "bar": "wine_bar"},
    "pub": {"amenity": "pub"},
    "disco": {"amenity": "nightclub"},
    "beer garden": {"amenity": "biergarten"},
    "fast food": {"amenity": "fast_food"},
    "karaoke": {"amenity": "karaoke_box"},
    "cruising": {"tourism": "attraction", "attraction": "cruise"},
    "theme park restaurant": {"amenity": "restaurant", "tourism": "theme_park"},
    "amusement restaurant": {"amenity": "restaurant", "leisure": "amusement_arcade"},
    "other restaurants": {"amenity": "restaurant"},

    # Shopping categories
    "shopping": {"shop": True},
    "glasses": {"shop": "optician"},
    "drug store": {"shop": "chemist"},
    "electronics store": {"shop": "electronics"},
    "diy store": {"shop": "doityourself"},
    "convenience store": {"shop": "convenience"},
    "recycle shop": {"shop": "second_hand"},
    "interior shop": {"shop": "interior_decoration"},
    "sports store": {"shop": "sports"},
    "clothes store": {"shop": "clothes"},
    "grocery store": {"shop": "supermarket"},
    "online grocery store": {"shop": "supermarket", "service": "online"},
    "retail store": {"shop": True},

    # Entertainment categories
    "entertainment": {"leisure": True},
    "sports recreation": {"leisure": "sports_centre"},
    "game arcade": {"leisure": "amusement_arcade"},
    "swimming pool": {"leisure": "swimming_pool"},
    "casino": {"amenity": "casino"},

    # Accommodation & Transport
    "hotel": {"tourism": "hotel"},
    "park": {"leisure": "park"},
    "transit station": {"public_transport": "station"},
    "parking area": {"amenity": "parking"},

    # Healthcare
    "hospital": {"amenity": "hospital"},
    "pharmacy": {"amenity": "pharmacy"},
    "chiropractic": {"healthcare": "chiropractic"},
    "elderly care home": {"amenity": "social_facility", "social_facility": "nursing_home"},
    "vet": {"amenity": "veterinary"},

    # Education
    "school": {"amenity": "school"},
    "cram school": {"amenity": "school", "school:type": "cramming"},
    "kindergarten": {"amenity": "kindergarten"},
    "driving school": {"amenity": "driving_school"},

    # Services
    "real estate": {"office": "estate_agent"},
    "home appliances": {"shop": "houseware"},
    "post office": {"amenity": "post_office"},
    "laundry": {"shop": "laundry"},
    "wedding ceremony": {"amenity": "place_of_worship"},
    "cemetary": {"landuse": "cemetery"},
    "bank": {"amenity": "bank"},
    "hot spring": {"leisure": "resort", "resort": "hot_spring"},
    "hair salon": {"shop": "hairdresser"},
    "lawyer office": {"office": "lawyer"},
    "recruitment office": {"office": "employment_agency"},
    "city hall": {"amenity": "townhall"},
    "community center": {"amenity": "community_centre"},
    "church": {"amenity": "place_of_worship", "religion": "christian"},
    "accountant office": {"office": "accountant"},
    "it office": {"office": "it"},
    "publisher office": {"office": "publisher"},

    # Industry & Specialized
    "building material": {"shop": "trade"},
    "gardening": {"shop": "garden_centre"},
    "heavy industry": {"landuse": "industrial"},
    "npo": {"office": "ngo"},
    "utility copany": {"office": "company", "operator:type": "public"},
    "port": {"landuse": "port"},
    "research facility": {"amenity": "research_institute"},
    "fishing": {"leisure": "fishing"},
}

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
                    return {
                        "yelp_id": best_match.get("id", ""),
                        "yelp_name": best_match.get("name", ""),
                        "yelp_rating": best_match.get("rating", 0),
                        "yelp_review_count": best_match.get("review_count", 0),
                        "yelp_price": best_match.get("price", ""),
                        "yelp_url": best_match.get("url", ""),
                        "yelp_image_url": best_match.get("image_url", ""),
                        "yelp_categories": [cat.get("title", "") for cat in best_match.get("categories", [])],
                        "yelp_phone": best_match.get("display_phone", ""),
                        "yelp_is_closed": best_match.get("is_closed", False),
                        "match_score": round(best_score, 2)
                    }
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
        batch_size = 5
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
                else:
                    # Default values for POIs without Yelp data
                    enhanced_poi.update({
                        "yelp_rating": 0,
                        "yelp_review_count": 0,
                        "yelp_price": "",
                        "yelp_url": "",
                        "yelp_image_url": "",
                        "yelp_categories": [],
                        "yelp_phone": "",
                        "yelp_is_closed": False,
                        "sort_score": 0
                    })
                
                enriched_pois.append(enhanced_poi)
            
            # Small delay between batches to respect rate limits
            if i + batch_size < len(poi_list):
                await asyncio.sleep(0.1)
    
    return enriched_pois

@app.get("/")
async def root():
    return "Hello World! This is a travel planner with Yelp integration"

@app.get("/poi/categories")
async def get_poi_categories():
    """Get list of available POI categories"""
    return {
        "categories": list(POI_CATEGORIES.keys()),
        "total": len(POI_CATEGORIES),
        "yelp_integration": YELP_API_KEY is not None
    }

@app.get("/poi/search")
async def search_poi(
    lat: float = Query(..., description="Latitude", ge=-90, le=90),
    lon: float = Query(..., description="Longitude", ge=-180, le=180),
    category: str = Query(..., description="POI category (e.g., 'restaurant', 'park')"),
    radius_km: float = Query(10, description="Search radius in kilometers", gt=0, le=50),
    sort_by: str = Query("rating", description="Sort by: 'rating', 'distance', 'review_count'")
):
    """
    Search for Points of Interest (POI) within a specified radius with Yelp ratings
    
    Args:
        lat: Latitude of the search center
        lon: Longitude of the search center
        category: POI category to search for
        radius_km: Search radius in kilometers (max 50km)
        sort_by: Sort results by 'rating', 'distance', or 'review_count'
    
    Returns:
        List of POIs with their details and Yelp ratings
    """
    try:
        # Validate category
        category_lower = category.lower().strip()
        if category_lower not in POI_CATEGORIES:
            raise HTTPException(
                status_code=400, 
                detail=f"Category '{category}' not supported. Use /poi/categories to see available categories."
            )
        
        # Validate sort_by parameter
        valid_sort_options = ["rating", "distance", "review_count"]
        if sort_by not in valid_sort_options:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid sort_by parameter. Must be one of: {valid_sort_options}"
            )
        
        logger.info(f"Searching for {category_lower} near ({lat}, {lon}) within {radius_km}km")
        
        # Get OSM tags for the category
        tags = POI_CATEGORIES[category_lower]
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
                "message": f"No {category_lower} found within {radius_km}km of the specified location"
            }
        
        if pois.empty:
            return {
                "pois": [],
                "count": 0,
                "message": f"No {category_lower} found within {radius_km}km"
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
                        "category": category_lower,
                        "address": str(address),
                        "phone": str(phone),
                        "website": str(website),
                        "opening_hours": str(opening_hours),
                        "osm_id": str(idx) if idx is not None else "unknown"
                    }
                    
                    # Add category-specific fields with validation
                    if "restaurant" in category_lower or category_lower in ["food"]:
                        cuisine = poi.get("cuisine", "")
                        if isinstance(cuisine, float) and math.isnan(cuisine):
                            cuisine = ""
                        poi_data["cuisine"] = str(cuisine)
                        
                        diet = poi.get("diet", "")
                        if isinstance(diet, float) and math.isnan(diet):
                            diet = ""
                        poi_data["diet"] = str(diet)
                        
                    elif category_lower == "hotel":
                        stars = poi.get("stars", "")
                        if isinstance(stars, float) and math.isnan(stars):
                            stars = ""
                        poi_data["stars"] = str(stars)
                        
                    elif category_lower == "church":
                        religion = poi.get("religion", "")
                        if isinstance(religion, float) and math.isnan(religion):
                            religion = ""
                        poi_data["religion"] = str(religion)
                        
                    elif "store" in category_lower or "shop" in category_lower or category_lower == "shopping":
                        shop_type = poi.get("shop", "")
                        if isinstance(shop_type, float) and math.isnan(shop_type):
                            shop_type = ""
                        poi_data["shop_type"] = str(shop_type)
                        
                    elif category_lower in ["hospital", "pharmacy", "chiropractic", "elderly care home"]:
                        healthcare = poi.get("healthcare", "")
                        if isinstance(healthcare, float) and math.isnan(healthcare):
                            healthcare = ""
                        poi_data["healthcare_type"] = str(healthcare)
                        
                    elif "office" in category_lower:
                        office_type = poi.get("office", "")
                        if isinstance(office_type, float) and math.isnan(office_type):
                            office_type = ""
                        poi_data["office_type"] = str(office_type)
                    
                    poi_list.append(poi_data)
                    
            except Exception as e:
                logger.warning(f"Error processing POI {idx}: {e}")
                continue
        
        # Enrich with Yelp data
        enriched_poi_list = await enrich_pois_with_yelp(poi_list)
        
        # Sort based on the requested criteria
        if sort_by == "rating":
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
            "search_params": {
                "latitude": lat,
                "longitude": lon,
                "category": category_lower,
                "radius_km": radius_km,
                "sort_by": sort_by
            },
            "yelp_integration_enabled": YELP_API_KEY is not None,
            "total_with_yelp_data": sum(1 for poi in enriched_poi_list if poi.get("yelp_rating", 0) > 0)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error in POI search: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)