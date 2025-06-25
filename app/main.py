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

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Travel Planner",
    description="A travel planner app backend with POI search capabilities",
)

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

@app.get("/")
async def root():
    return "Hello World! This is a travel planner"

@app.get("/poi/categories")
async def get_poi_categories():
    """Get list of available POI categories"""
    return {
        "categories": list(POI_CATEGORIES.keys()),
        "total": len(POI_CATEGORIES)
    }

@app.get("/poi/search")
async def search_poi(
    lat: float = Query(..., description="Latitude", ge=-90, le=90),
    lon: float = Query(..., description="Longitude", ge=-180, le=180),
    category: str = Query(..., description="POI category (e.g., 'restaurant', 'park')"),
    radius_km: float = Query(10, description="Search radius in kilometers", gt=0, le=50)
):
    """
    Search for Points of Interest (POI) within a specified radius
    
    Args:
        lat: Latitude of the search center
        lon: Longitude of the search center
        category: POI category to search for
        radius_km: Search radius in kilometers (max 50km)
    
    Returns:
        List of POIs with their details
    """
    try:
        # Validate category
        category_lower = category.lower().strip()
        if category_lower not in POI_CATEGORIES:
            raise HTTPException(
                status_code=400, 
                detail=f"Category '{category}' not supported. Use /poi/categories to see available categories."
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
        
        # Sort by distance
        poi_list.sort(key=lambda x: x["distance_km"])
        
        return {
            "pois": poi_list,
            "count": len(poi_list),
            "search_params": {
                "latitude": lat,
                "longitude": lon,
                "category": category_lower,
                "radius_km": radius_km
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error in POI search: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)