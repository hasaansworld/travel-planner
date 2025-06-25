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
    "restaurant": {"amenity": "restaurant"},
    "japanese restaurant": {"amenity": "restaurant", "cuisine": "japanese"},
    "italian restaurant": {"amenity": "restaurant", "cuisine": "italian"},
    "chinese restaurant": {"amenity": "restaurant", "cuisine": "chinese"},
    "park": {"leisure": "park"},
    "hospital": {"amenity": "hospital"},
    "school": {"amenity": "school"},
    "bank": {"amenity": "bank"},
    "pharmacy": {"amenity": "pharmacy"},
    "gas station": {"amenity": "fuel"},
    "hotel": {"tourism": "hotel"},
    "museum": {"tourism": "museum"},
    "attraction": {"tourism": "attraction"},
    "cafe": {"amenity": "cafe"},
    "bar": {"amenity": "bar"},
    "pub": {"amenity": "pub"},
    "supermarket": {"shop": "supermarket"},
    "mall": {"shop": "mall"},
    "gym": {"leisure": "fitness_centre"},
    "library": {"amenity": "library"},
    "cinema": {"amenity": "cinema"},
    "theatre": {"amenity": "theatre"},
    "church": {"amenity": "place_of_worship", "religion": "christian"},
    "mosque": {"amenity": "place_of_worship", "religion": "muslim"},
    "temple": {"amenity": "place_of_worship", "religion": "buddhist"},
    "atm": {"amenity": "atm"},
    "post office": {"amenity": "post_office"},
    "police": {"amenity": "police"},
    "fire station": {"amenity": "fire_station"},
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
                    if category_lower in ["restaurant", "japanese restaurant", "italian restaurant", "chinese restaurant"]:
                        cuisine = poi.get("cuisine", "")
                        if isinstance(cuisine, float) and math.isnan(cuisine):
                            cuisine = ""
                        poi_data["cuisine"] = str(cuisine)
                    elif category_lower == "hotel":
                        stars = poi.get("stars", "")
                        if isinstance(stars, float) and math.isnan(stars):
                            stars = ""
                        poi_data["stars"] = str(stars)
                    elif category_lower in ["church", "mosque", "temple"]:
                        religion = poi.get("religion", "")
                        if isinstance(religion, float) and math.isnan(religion):
                            religion = ""
                        poi_data["religion"] = str(religion)
                    
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