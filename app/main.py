from collections import defaultdict
from contextlib import asynccontextmanager
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
from sqlmodel import Session, asc, desc, distinct, func, select
from app.clustering import cluster_places_by_location
from app.database import create_db_and_tables, get_session
from app.models import Category, NewUserVisit, PlacesQuery, PlanQuery, TravelPlan, User, UserFrequency, Place, PlanPlace
import json
from app.places import Location, PlaceResult, UnifiedGooglePlacesAPI, execute_search_queries, filter_and_sort_places, get_llm_queries, get_places_for_plan
from app.utils import generate_llm_response
import time as time_module
import requests

load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("Creating tables...")
    try:
        create_db_and_tables()
    except Exception as e:
        logger.error(f"❌ Application startup failed: {e}")
        raise
    yield
    # Shutdown
    logger.info("🛑 Application shutting down...")

        
app = FastAPI(
    title="Travel Planner",
    description="A travel planner app backend with POI search capabilities and Yelp ratings",
    lifespan=lifespan
)

def calculate_distance_meters(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """
    Calculate distance between two points in meters using geodesic distance
    """
    try:
        distance = geodesic((lat1, lon1), (lat2, lon2)).meters
        return round(distance, 2)
    except Exception as e:
        logger.error(f"Error calculating distance: {e}")
        return 0.0

async def get_plan_for_one_day(
    city: str,
    country: str,
    start_date: datetime,
    start_day: str,
    intent: str,
    user_activity: str,
    places_data: Any,
    exclude_places: str,
    clustering: bool = False,
    api_key: str = "",
):
    
    system_prompt = f"""You are a travel planner assistant. 
    You will be provided with a user's past activity, user's travel intent, start date, number of days and places data fetched from Google Maps Places API (new).
    Your task is to generate a travel plan for the user based on the provided data.
    Keep in mind following constraints:
    {"- If you are given places API data in clusters like cluster_0, cluster_1 and so on then choose all the places from a cluster with all the most popular places. Always recommend places from only one cluster." if clustering else ""}
    - Never recommend closed places, check for opening times of locations
    - Develop a natural plan according to times of day and account for travel times between places
    - Include meals and food in the plan according to user's preferences
    - Stay within the places API data provided by the user
    - Respect user intent, the stated intent should be clearly addressable in your plan
    - **Ensure minimum 6 places per day and include sufficient meals. Never recommend less than 6 places per day!**
    - **Local food or local cuisine means that country's food, disregard other countries' food if user asks for local food**
    - Try to include snacks, coffee or other light food if there is in the places data
    - ## Always include a specific place from the places data, don't recommend some generic recommendation like "a local restaurant" or "a local cafe"
    - ## Always recommend places from places data provided, NEVER recommend places from your own
    - ## Always use correct place names from the places data provided including special characters from original place name
    - **Respect user's food preferences like trying local food or some particular cuisine, don't recommend any other cuisine if user explitly mentioned one**
    - **Ensure at least 2 meals per day but ONLY SUGGEST PLACES FROM DATA GIVEN**
    - **Never recommend places user asks to exclude**
    - Always make sure that the duration of each place in the itninerary feels natural.
    {"- Always recommend places from only one cluster." if clustering else ""}
    
    Your response should be a JSON object in the following format:
    {{
        "overview": {{
            "duration": "", # timespan covered (e.g. "09:00 AM - 10:00 PM")
            "theme": "", # Brief description of the overall experience
            "personalization_notes": "" # How this plan reflects user's past preferences
        }},
        "itinerary": [
            {{
                "name": "", # Name of the place (must match exactly from places data)
                "place_id": "", # Google Places ID from the places data
                "duration": "", # Time of visit (e.g., "10:00 AM - 12:00 PM")
                "reason": "", # Why this place is included in the plan
                "practical_notes": "" # Operating hours etc.
            }},
            {{...}} # More places can be added here
        ],
        "considerations": "" # anything the user should consider
    }}
    """

    user_message = f"""
    city: {city}
    country: {country}
    start date: {start_date.strftime('%Y-%m-%d')}
    start day: {start_day}
    number of days: 1
    user intent: {intent}
    past activity: {user_activity}
    places data: {json.dumps(places_data, indent=2)}
    exclude places: {exclude_places or "none"}
    generate a travel plan in the json format provided in the system prompt.
    """

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_message}
    ]
    response = generate_llm_response(
        messages=messages,
        model_name="llama",
        temperature=0,
        api_key=api_key,
    )

    travel_plan = {}
    if response:
        travel_plan = json.loads(response) or {}

    return travel_plan

@app.get("/plan")
async def get_plan(
    user_id: int = Query(1, description="User ID"),
    city_id: int = Query(1, description="City ID"),
    lat: float = Query(65.0121, description="Latitude", ge=-90, le=90),
    lon: float = Query(25.4651, description="Longitude", ge=-180, le=180),
    radius_km: int = Query(2, description="Search radius in kilometers", gt=0, le=50),
    rating: float = Query(3, description="Minimum Yelp rating", ge=0, le=5),
    intent: str = Query("travel, sight seeing and trying local food", description="Intent of the plan"),
    start_date: datetime = Query(datetime.now(), description="Travel plan start date"),
    number_of_days: int = Query(1, description="Number of days for the travel plan", ge=1, le=5),
    model: str = Query("llama", description="LLM model to use for generating the plan"),
    api_key: str = Query("", description="Provide your own api key for LLMs"),
    places_api_key: str = Query("", description="Provide your own Google Places API key"),
    session: Session = Depends(get_session)
):
    try:
        # Get user activity data
        if user_id <= 125000:
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
        else:
            unique_place_types_query = select(distinct(NewUserVisit.place_type)).where(
                NewUserVisit.user_id == user_id
            )
            results = session.exec(unique_place_types_query).all()

        user_activity = ", ".join(results)

        result = ox.geocoder.geocode_to_gdf(
            f"{lat}, {lon}", 
            which_result=1
        )
        
        city = "Unknown"
        country = "Unknown"
        if not result.empty:
            # Get the display name which contains location info
            display_name = result.iloc[0]['display_name']
            system_prompt = f"""
            You are a tool to extract the city and country from a display name.
            You should return a JSON object with the keys "city" and "country".
            Example output: {{"city": "Paris", "country": "France"}}
            """
            user_prompt = f"Display name: {display_name}"
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ]
            response = generate_llm_response(
                messages=messages,
                model_name="llama",
                temperature=0,
                api_key=api_key
            )

            if response:
                try:
                    location_data = json.loads(response or "{}")
                    city = location_data.get("city", "Unknown City")
                    country = location_data.get("country", "Unknown Country")
                except json.JSONDecodeError:
                    logger.error(f"Failed to parse location data: {response}")
                    city = display_name
                    country = ""
            
        print(f"City: {city}, Country: {country}")
        # Create travel plan in db
        plan = TravelPlan(
            user_id=user_id,
            city_id=city_id,
            city=city,
            country=country or "",
            intent=intent,
            lat=lat,
            long=lon,
            radius_km=radius_km,
            rating=rating,
            model=model,
            travel_date=start_date,
            number_of_days=number_of_days,
            created_at=datetime.now()
        )
        session.add(plan)
        session.commit()


        # Step 1: Get queries from LLM
        print("Step 1: Getting search queries from LLM...")
        queries = get_llm_queries(
            user_activity=user_activity,
            country=country,
            city=city,
            intent=intent,
            model=model,
            api_key=api_key,
        )
        
        if not queries:
            print("Failed to get queries from LLM. Exiting.")
            return
        
        print(f"Generated {len(queries)} queries:")
        for i, query in enumerate(queries, 1):
            print(f"  {i}. {query}")

        
        # Step 2: Execute search queries
        print("\nStep 2: Executing search queries...")

        location = Location(latitude=lat, longitude=lon)
        try:
            results = execute_search_queries(
                queries=queries,
                plan_id=plan.id,
                location=location,
                session=session,
                city=city,
                country=country,
                radius_km=radius_km,
                max_results_per_query=20,
                places_api_key=places_api_key
            )
        except Exception as e:
            if "API_KEY_INVALID" in str(e) or "INVALID_REQUEST" in str(e):
                raise HTTPException(status_code=400, detail=f"Invalid Places API key: {str(e)}")
            else:
                raise HTTPException(status_code=500, detail=f"Places API error: {str(e)}")

        should_use_clustering = number_of_days > 1 and radius_km > 2
        if should_use_clustering:
            clustered_places = cluster_places_by_location(results, number_of_days)
            print(clustered_places)
            results = clustered_places

        day_name = start_date.strftime('%A')
        count = 0
        processed_data = {}
        seen_places = set()  # Track place names we've already seen
        
        for search_category, places in results.items():
            filtered_places = filter_and_sort_places(places)
            
            # Remove duplicates based on place name
            unique_places = []
            for place in filtered_places:
                place_name = place.get("name")
                if place_name and place_name not in seen_places and (place.get("rating") or 0) >= rating:
                    unique_places.append(place)
                    seen_places.add(place_name)
                    count += 1
            
            processed_data[search_category] = unique_places

        places_data = json.dumps(processed_data, indent=2, ensure_ascii=False)
        print("Processed data:", places_data)
        print(f"Total unique places found: {count}")

        travel_plan = {}
        excluded_places = []
        for i in range(number_of_days):
            day_number = i + 1
            print("Making plan for day", day_number)
            plan_per_day = await get_plan_for_one_day(city, country, start_date, day_name, intent, user_activity, places_data, ", ".join(excluded_places), clustering=should_use_clustering)
            for place in plan_per_day.get("itinerary", {}):
                excluded_places.append(place.get("name", ""))
            
            travel_plan[f"day_{day_number}"] = plan_per_day
        
        plan.travel_plan = travel_plan
        session.add(plan)
        session.commit()

        # NEW: Get places from database and enrich the travel plan using place_id
        plan_places = get_places_for_plan(session, plan.id)
        
        # Create lookup dictionary for fast matching using place_id
        place_lookup = {}
        for place in plan_places:
            place_lookup[place.place_id] = {
                "name": place.name,
                "location": {"latitude": place.latitude, "longitude": place.longitude},
                "photos": place.photos or [],
                "rating": place.rating,
                "address": place.address,
                "opening_hours": place.opening_hours,
                "types": place.types or []
            }

        # Update each place in the travel plan with location data and distance using place_id
        for _, day_data in travel_plan.items():
            itinerary = day_data.get("itinerary", [])
            for place in itinerary:
                place_id = place.get("place_id")
                matched = place_lookup.get(place_id) if place_id else None

                if matched:
                    place["location"] = matched["location"]
                    place["photos"] = matched["photos"]
                    place["rating"] = matched["rating"]
                    place["address"] = matched["address"]
                    place["opening_hours"] = matched["opening_hours"]
                    place["types"] = matched["types"]
                    
                    # Calculate distance from user location to this place
                    place_lat = matched["location"].get("latitude")
                    place_lon = matched["location"].get("longitude")
                    if place_lat is not None and place_lon is not None:
                        distance = calculate_distance_meters(lat, lon, place_lat, place_lon)
                        place["distance"] = distance
                    else:
                        place["distance"] = None
                else:
                    place["distance"] = None

        return {
            "travel_plan_id": plan.id,
            "travel_plan": travel_plan,
            "unique_places_count": count,
            "processed_data": processed_data,
            "start_date": start_date.strftime('%Y-%m-%d'),
            "number_of_days": number_of_days,
            "day_name": day_name,
            "city": city,
            "country": country,
            "queries": queries,
            "user_activity": user_activity,
        }
        

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error in get_plan: {e}")
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")


async def update_plan_for_one_day(
    city: str,
    country: str,
    plan: dict,
    start_date: datetime,
    start_day: str,
    message: str,
    places_data: Any,
    exclude_places: str = "",
    clustering: bool = False,
    api_key: str = "",
):
    
    system_prompt = f"""You are a travel planner assistant. 
    You will be provided with a travel plan for one day, user message to update the travel plan and new data from places API according to user message.
    Your task is to generate a travel plan for the user based on the provided data.
    Keep in mind following constraints:
    {"- If you are given places API data in clusters like cluster_0, cluster_1 and so on then choose all the places from the same cluster close to places in the existing plan." if clustering else ""}
    - Never recommend closed places, check for opening times of locations
    - Develop a natural plan according to times of day and account for travel times between places
    - Stay within the places API data provided by the user
    - ## Always include a specific place from the places data, don't recommend some generic recommendation like "a local restaurant" or "a local cafe"
    - ## Always recommend places from places data provided, NEVER recommend places from your own
    - ## Always use correct place names from the places data provided including special characters from original place name
    - Try to incorporate the new data according to the user message. Change original plan as per user requirement.
    - **Ensure at least 2 meals per day but ONLY SUGGEST PLACES FROM DATA GIVEN**
    - **Never recommend places user asks to exclude**
    - Always make sure that the duration of each place in the itninerary feels natural.
    {"- Always recommend places from only one cluster." if clustering else ""}
    
    Your response should be a JSON object in the following format:
    {{
        "overview": {{
            "duration": "", // timespan covered (e.g. "09:00 AM - 10:00 PM")
            "theme": "", // Brief description of the overall experience
            "personalization_notes": "" // How this plan reflects user's past preferences
        }},
        "itinerary": [
            {{
                "name": "", // Name of the place (must match exactly from places data)
                "place_id": "", // Google Places ID from the places data
                "duration": "", // Time of visit (e.g., "10:00 AM - 12:00 PM")
                "reason": "", // Why this place is included in the plan
                "practical_notes": "" // Operating hours etc.
            }},
            {{...}} // More places can be added here
        ],
        "considerations": "" // anything the user should consider
    }}
    """

    user_message = f"""
    city: {city}
    country: {country}
    start date: {start_date.strftime('%Y-%m-%d')}
    start day: {start_day}
    number of days: 1
    existing plan: {json.dumps(plan, indent=2)}
    user message: {message}
    new places data: {json.dumps(places_data, indent=2)}
    exclude places: {exclude_places or "none"}
    generate a travel plan in the json format provided in the system prompt.
    """

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_message}
    ]
    response = generate_llm_response(
        messages=messages,
        model_name="llama",
        temperature=0,
        api_key=api_key,
    )

    travel_plan = {}
    if response:
        travel_plan = json.loads(response) or {}

    return travel_plan


@app.get("/update-plan")
async def update_plan(
    user_id: int = Query(1, description="User ID"),
    plan_id: int = Query(description="Plan ID"),
    message: str = Query(description="Message from user"),
    model: str = Query("llama", description="LLM model to use for generating the plan"),
    api_key: str = Query("", description="Provide your own api key for LLMs"),
    places_api_key: str = Query("", description="Provide your own Google Places API key"),
    session: Session = Depends(get_session)
):
    try:
        query = (
            select(TravelPlan)
            .where(TravelPlan.user_id == user_id)
            .where(TravelPlan.id == plan_id)
        )

        original_plan = session.exec(query).first()
        
        if not original_plan:
            raise HTTPException(404, "Travel plan not found")
        
        travel_plan = original_plan.travel_plan


        system_prompt = """
        You are a decision making system. You have to decide if the initial params of a travel plan need to be changed based on revision request by the user.
        You will be provided with initial params of the travel plan and new message from the user. The initial params will be in the format:
        { "radius_km": 2, "rating": 3.2, "number_of_days": 2}
        radius_km is between 0 and 50 and rating is between 0 and 5 and number of days is between 1 and 5. Do not output values outside these ranges.
        you have to output a boolean variable "params_changed" if the params need to be changed. You also need to provide any additional user intent in the "intent" key.
        Your output should be in the following json format:
        { "params_changed": true, "radius_km": 3, "rating": 4.0, "number_of_days": 3, "intent": "any new message by the user other than the initial params" }
        """
        params_dict = {
            "radius_km": original_plan.radius_km,
            "rating": original_plan.rating,
            "number_of_days": original_plan.number_of_days
        }
        user_message = f"""
        Initial Params: {params_dict}
        Revision message from user: {message}
        """
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message}
        ]

        response = generate_llm_response(
            messages=messages,
            model_name="llama",
            temperature=0,
            api_key=api_key,
        )

        if response:
            data = json.loads(response) or {}
            params_changed = data.get("params_changed", False)
            if params_changed:
                intent = data.get("intent", "")
                new_intent = original_plan.intent
                if intent:
                    new_intent += f", {intent}"
                
                new_plan_response = await get_plan(
                    original_plan.user_id, 
                    city_id=original_plan.city_id, 
                    lat=original_plan.lat, 
                    lon=original_plan.long, 
                    radius_km=data.get("radius_km", original_plan.radius_km), 
                    rating=data.get("rating", original_plan.rating), 
                    intent=new_intent, 
                    start_date=original_plan.travel_date, 
                    number_of_days=data.get("number_of_days", original_plan.number_of_days), 
                    model=model, 
                    api_key=api_key, 
                    places_api_key=places_api_key,
                    session=session
                )
                
                # Get the new plan ID from the response
                new_plan_id = new_plan_response.get("travel_plan_id")
                
                # Update the new plan's update_for column to reference the original plan
                if new_plan_id:
                    # Find the original plan ID (if current plan is already an update)
                    original_plan_id = original_plan.update_for if original_plan.update_for else original_plan.id
                    
                    # Update the new plan
                    update_query = (
                        select(TravelPlan)
                        .where(TravelPlan.id == new_plan_id)
                    )
                    new_plan = session.exec(update_query).first()
                    
                    if new_plan:
                        new_plan.update_for = original_plan_id
                        session.add(new_plan)
                        session.commit()
                        
                        # Update the response to include the original plan reference
                        new_plan_response["original_plan_id"] = original_plan_id
                
                return new_plan_response 
        else:
            print("Failed to get response from LLM for initial params check")

        statement = (
            select(PlacesQuery.query_type, PlacesQuery.query)
            .select_from(PlacesQuery, PlanQuery)
            .where(
                PlacesQuery.id == PlanQuery.query_id,
                PlanQuery.plan_id == plan_id
            )
        )
        
        queries = session.exec(statement).all()
        query_texts = []
        for query in queries:
            query_texts.append(f"{query[0]}: {query[1]}")
        queries = ", ".join(query_texts)

        print("Existing queries", queries)

        system_prompt = """
        You are a decision making system. You have to decide if there is a need to fetch new data for a travel plan based on revision request by the user.
        You will be provided with existing queries to the google places api and new message from the user. You have to respond in the following json format:
        { "fetch_data": "true" } or { "fetch_data": "false" }
        Make your decision based on the fact that if the user's revision request might need data outside existing queries or not.
        """
        user_message = f"""
        Existing queries: {queries}
        Revision message from user: {message}
        """
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message}
        ]

        print("Step 1: Checking if need to fetch data again")
        response = generate_llm_response(
            messages=messages,
            model_name="llama",
            temperature=0,
            api_key=api_key,
        )

        if response:
            fetch_data = json.loads(response) or {"fetch_data": False}
            fetch_data = fetch_data["fetch_data"]
            
            # Create new travel plan record (common for both paths)
            new_plan = TravelPlan(
                user_id=original_plan.user_id,
                city_id=original_plan.city_id,
                update_for=original_plan.id,  # Reference to original plan
                lat=original_plan.lat,
                long=original_plan.long,
                radius_km=original_plan.radius_km,
                rating=original_plan.rating,
                intent=f"{original_plan.intent}, {message}",  # Include update message in intent
                model=model,
                city=original_plan.city,
                country=original_plan.country,
                travel_date=original_plan.travel_date,
                number_of_days=original_plan.number_of_days,
                created_at=datetime.now()
            )
            session.add(new_plan)
            session.commit()
            session.refresh(new_plan)

            # Copy all existing places from original plan to new plan (common for both paths)
            original_plan_places = get_places_for_plan(session, original_plan.id)
            for place in original_plan_places:
                from app.places import link_place_to_plan
                link_place_to_plan(session, new_plan.id, place.place_id)
            session.commit()
            
            if fetch_data == "true":
                print("Need to fetch new data")

                # Get user activity data
                if user_id <= 125000:
                    query = (
                        select(Category.category_name)
                        .select_from(UserFrequency)
                        .join(Category)
                        .where(UserFrequency.poi_category_id == Category.category_id)
                        .where(UserFrequency.user_id == user_id)
                        .group_by(Category.category_name)
                        .order_by(desc(func.sum(UserFrequency.count)))
                    )

                    # Execute query
                    results = session.exec(query).all()
                else:
                    unique_place_types_query = select(distinct(NewUserVisit.place_type)).where(
                        NewUserVisit.user_id == user_id
                    )
                    results = session.exec(unique_place_types_query).all()

                user_activity = ", ".join(results)

                print("Step 2: Getting search queries from LLM...")
                queries = get_llm_queries(
                    user_activity=user_activity,
                    country=original_plan.country,
                    city=original_plan.city,
                    intent=message,
                    model=model,
                    api_key=api_key,
                    exclude_queries=queries,
                )

                if not queries:
                    return HTTPException(500, "Failed to get queries from LLM")
                
                print(f"Generated {len(queries)} queries:")
                for i, query in enumerate(queries, 1):
                    print(f"  {i}. {query}")

                # Step 2: Execute search queries with new plan ID
                print("\nStep 2: Executing search queries...")

                location = Location(latitude=original_plan.lat, longitude=original_plan.long)
                try:
                    results = execute_search_queries(
                        queries=queries,
                        plan_id=new_plan.id,  # Use new plan ID
                        location=location,
                        session=session,
                        city=original_plan.city,
                        country=original_plan.country,
                        radius_km=int(original_plan.radius_km),
                        max_results_per_query=20,
                        places_api_key=places_api_key
                    )
                except Exception as e:
                    if "API_KEY_INVALID" in str(e) or "INVALID_REQUEST" in str(e):
                        raise HTTPException(status_code=400, detail=f"Invalid Places API key: {str(e)}")
                    else:
                        raise HTTPException(status_code=500, detail=f"Places API error: {str(e)}")

                should_use_clustering = original_plan.number_of_days > 1 and original_plan.radius_km > 2
                if should_use_clustering:
                    clustered_places = cluster_places_by_location(results, original_plan.number_of_days)
                    results = clustered_places

                day_name = original_plan.travel_date.strftime('%A')
                count = 0
                processed_data = {}
                seen_places = set()  # Track place names we've already seen
                
                for search_category, places in results.items():
                    filtered_places = filter_and_sort_places(places)
                    
                    # Remove duplicates based on place name
                    unique_places = []
                    for place in filtered_places:
                        place_name = place.get("name")
                        if place_name and place_name not in seen_places and (place.get("rating") or 0) >= original_plan.rating:
                            unique_places.append(place)
                            seen_places.add(place_name)
                            count += 1
                    
                    processed_data[search_category] = unique_places

                places_data = json.dumps(processed_data, indent=2, ensure_ascii=False)
                print("Processed data:", places_data)
                print(f"Total unique places found: {count}")

                updated_travel_plan = {}
                excluded_places = []
                if isinstance(travel_plan, dict):
                    for key in travel_plan:
                        print("Making plan for", key)
                        plan_per_day = await update_plan_for_one_day(original_plan.city, original_plan.country, travel_plan, original_plan.travel_date, day_name, message, places_data, ", ".join(excluded_places), clustering=should_use_clustering)
                        for place in plan_per_day.get("itinerary", {}):
                            excluded_places.append(place.get("name", ""))
                        
                        updated_travel_plan[key] = plan_per_day
                else:
                    print("travel_plan is not a dictionary")
                    
            else:
                print("No need to fetch new data")
                
                system_prompt = """
                You are a decision making system. You have to decide if there is a need to retrieve existing places data for a travel plan based on revision request by the user.
                You will be provided with existing queries to the places API, a travel plan and new message from the user. 
                You have to respond with the queries to fetch existing data if it is needed to update the travel plan.
                You have to respond in the following json format:
                {{ "queries": ["nearby: restaurant", "text": "local cuisine", ...]}}
                Make your decision based on the fact that if the user's revision request might need places data or if it can be implemented without retrieving the data.
                If there is no need to retrieve the data respond like this:
                {{ "queries": [] }}
                """
                user_message = f"""
                Existing queries: {queries}
                Travel Plan: {json.dumps(travel_plan, indent=2)}
                Revision message from user: {message}
                """
                messages = [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_message}
                ]

                print("Checking if need to retrieve places data")
                response = generate_llm_response(
                    messages=messages,
                    model_name="llama",
                    temperature=0,
                    api_key=api_key,
                )

                places = []
                if response:
                    retrieve_queries = json.loads(response)["queries"] or []
                    print("Retrieve queries", retrieve_queries)
                    for q in retrieve_queries:
                        split = q.split(": ")
                        query_type = split[0]
                        query_value = split[1]

                        print("Searching for", query_type, query_value)

                        statement = (
                            select(PlacesQuery.places, PlacesQuery.query_type, PlacesQuery.query)
                            .join(PlanQuery)
                            .where(PlacesQuery.id == PlanQuery.query_id)
                            .where(PlanQuery.plan_id == plan_id)  # Still use original plan_id for data retrieval
                            .where(PlacesQuery.query_type == query_type)
                            .where(PlacesQuery.query == query_value)
                        )
            
                        result = session.exec(statement).first()
                        if result:
                            for place_dict in result.places: # type: ignore
                                places.append(PlaceResult.from_dict(place_dict))

                    # Link existing places to new plan
                    for place_result in places:
                        from app.places import upsert_place, link_place_to_plan
                        upsert_place(session, place_result)
                        link_place_to_plan(session, new_plan.id, place_result.id)

                    day_name = original_plan.travel_date.strftime('%A')
                    count = 0
                    processed_data = {}
                    seen_places = set()  # Track place names we've already seen
                    filtered_places = filter_and_sort_places(places)
                
                    # Remove duplicates based on place name
                    unique_places = []
                    for place in filtered_places:
                        place_name = place.get("name")
                        if place_name and place_name not in seen_places and (place.get("rating") or 0) >= original_plan.rating:
                            unique_places.append(place)
                            seen_places.add(place_name)
                            count += 1
                    
                    processed_data = unique_places

                updated_travel_plan = {}
                excluded_places = []
                if isinstance(travel_plan, dict):
                    for key in travel_plan:
                        print("Making plan for", key)
                        plan_per_day = await update_plan_for_one_day(original_plan.city, original_plan.country, travel_plan, original_plan.travel_date, day_name, message, processed_data, exclude_places=", ".join(excluded_places))
                        for place in plan_per_day.get("itinerary", {}):
                            excluded_places.append(place.get("name", ""))
                        updated_travel_plan[key] = plan_per_day
                else:
                    print("travel_plan is not a dictionary")

            # Common logic for saving and enriching the travel plan
            new_plan.travel_plan = updated_travel_plan
            session.add(new_plan)
            session.commit()

            # NEW: Get places from database and enrich the travel plan using place_id
            plan_places = get_places_for_plan(session, new_plan.id)
            
            # Create lookup dictionary for fast matching using place_id
            place_lookup = {}
            for place in plan_places:
                place_lookup[place.place_id] = {
                    "name": place.name,
                    "location": {"latitude": place.latitude, "longitude": place.longitude},
                    "photos": place.photos or [],
                    "rating": place.rating,
                    "address": place.address,
                    "opening_hours": place.opening_hours,
                    "types": place.types or []
                }

            # Update each place in the travel plan with location data and distance using place_id
            for _, day_data in updated_travel_plan.items():
                itinerary = day_data.get("itinerary", [])
                for place in itinerary:
                    place_id = place.get("place_id")
                    matched = place_lookup.get(place_id) if place_id else None

                    if matched:
                        place["location"] = matched["location"]
                        place["photos"] = matched["photos"]
                        place["rating"] = matched["rating"]
                        place["address"] = matched["address"]
                        place["opening_hours"] = matched["opening_hours"]
                        place["types"] = matched["types"]
                        
                        # Calculate distance from user location to this place
                        place_lat = matched["location"].get("latitude")
                        place_lon = matched["location"].get("longitude")
                        if place_lat is not None and place_lon is not None:
                            distance = calculate_distance_meters(original_plan.lat, original_plan.long, place_lat, place_lon)
                            place["distance"] = distance
                        else:
                            place["distance"] = None
                    else:
                        place["distance"] = None

            return {
                "travel_plan_id": new_plan.id,
                "original_plan_id": original_plan.id,
                "travel_plan": updated_travel_plan,
                "new_places": processed_data if 'processed_data' in locals() else {}
            }


        return HTTPException(500, f"Error: {response}")
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error in get_plan: {e}")
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")


@app.get("/get-nearby-places")
async def get_nearby_places(
    lat: float = Query(65.00978049249451, description="Latitude"),
    long: float = Query(25.502957692471355, description="Longitude"),
    places_api_key: str = Query("", description="Provide your own Google Places API key"),
):
    try:
        # Use provided API key or fall back to environment variable
        api_key = places_api_key if places_api_key else os.getenv("PLACES_API_KEY", "")
        if not api_key:
            raise HTTPException(status_code=400, detail="Places API key is required")
            
        places_api = UnifiedGooglePlacesAPI(api_key)
        location = Location(latitude=lat, longitude=long)
        places = places_api.search_places_nearby(
            location,
            radius=180,
            max_results=5,
            sort_by_popularity=False
        )

        display_places = []
        for place in places:
            display_places.append({
                "name": place.name,
                "location": place.location,
                "rating": place.rating,
                "address": place.address,
                "types": place.types,
                "photos": place.photos,
            })

        return {
            "places": places,
        }
    except Exception as e:
        if "API_KEY_INVALID" in str(e) or "INVALID_REQUEST" in str(e):
            raise HTTPException(status_code=400, detail=f"Invalid Places API key: {str(e)}")
        else:
            raise HTTPException(status_code=500, detail=f"Places API error: {str(e)}")
    

@app.get("/user-visits")
async def create_user_visit(
    user_id: int = Query(125001),
    lat: float = Query(65.00951909999999, description="Latitude"),
    long: float = Query(25.5040852, description="Longitude"),
    name: str = Query("City Biljard", description="Place name"),
    place_type: str = Query("Sports Complex", description="Place type"),
    address: Optional[str] = Query("Ylioppilaantie 4c, 90130 Oulu, Finland", description="Place address"),
    created_at: Optional[datetime] = Query(None, description="created at time"),
    session: Session = Depends(get_session)
):
    try:
        # Create new user visit instance
        new_visit = NewUserVisit(
            user_id=user_id,
            lat=lat,
            long=long,
            name=name,
            place_type=place_type,
            address=address,
            created_at=created_at if created_at is not None else datetime.utcnow()
        )
        
        # Add to session and commit
        session.add(new_visit)
        session.commit()
        session.refresh(new_visit)

        unique_place_types_query = select(distinct(NewUserVisit.place_type)).where(
            NewUserVisit.user_id == user_id
        )
        unique_place_types = session.exec(unique_place_types_query).all()
        
        return {"success": True, "id": new_visit.id, "history": unique_place_types}
        
    except Exception as e:
        session.rollback()
        print(f"Error creating user visit: {str(e)}")
        
        raise HTTPException(
            status_code=500,
            detail="Failed to create user visit"
        )
    

# Add this endpoint to your FastAPI app
@app.get("/autocomplete")
async def get_autocomplete_suggestions(
    query: str = Query(..., description="Search query for place autocomplete", min_length=1),
    session_token: Optional[str] = Query(None, description="Session token for billing optimization"),
    places_api_key: str = Query("", description="Provide your own Google Places API key")
):
    """
    Get autocomplete suggestions for places using Google Places Autocomplete API
    """
    try:
        # Use provided API key or fall back to environment variable
        api_key = places_api_key if places_api_key else os.getenv("PLACES_API_KEY", "")
        if not api_key:
            raise HTTPException(status_code=400, detail="Places API key is required")
        
        url = "https://places.googleapis.com/v1/places:autocomplete"
        
        # Prepare the request payload
        payload = {
            "input": query,
            "includeQueryPredictions": True
        }
        
        # Add session token if provided (helps with billing)
        if session_token:
            payload["sessionToken"] = session_token
        
        headers = {
            "Content-Type": "application/json",
            "X-Goog-Api-Key": api_key
        }
        
        # Make the API request
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=payload, headers=headers) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    # Parse and format the suggestions
                    suggestions = []
                    predictions = data.get("suggestions", [])
                    
                    # Limit to 5 results
                    for prediction in predictions[:5]:
                        place_prediction = prediction.get("placePrediction")
                        if place_prediction:
                            suggestion = {
                                "place_id": place_prediction.get("placeId"),
                                "text": place_prediction.get("text", {}).get("text", ""),
                                "structured_formatting": {
                                    "main_text": place_prediction.get("structuredFormat", {}).get("mainText", {}).get("text", ""),
                                    "secondary_text": place_prediction.get("structuredFormat", {}).get("secondaryText", {}).get("text", "")
                                },
                                "types": place_prediction.get("types", []),
                            }
                            suggestions.append(suggestion)
                    
                    return {
                        "suggestions": suggestions,
                        "status": "success",
                        "query": query
                    }
                
                else:
                    error_text = await response.text()
                    logger.error(f"Autocomplete API failed with status {response.status}: {error_text}")
                    if response.status == 400:
                        raise HTTPException(
                            status_code=400,
                            detail=f"Invalid Places API key or request: {error_text}"
                        )
                    else:
                        raise HTTPException(
                            status_code=response.status,
                            detail=f"Places API error: {error_text}"
                        )
                    
    except aiohttp.ClientError as e:
        logger.error(f"Network error in autocomplete: {e}")
        raise HTTPException(status_code=503, detail="Network error connecting to Places API")
    
    except Exception as e:
        logger.error(f"Unexpected error in autocomplete: {e}")
        if "API_KEY_INVALID" in str(e) or "INVALID_REQUEST" in str(e):
            raise HTTPException(status_code=400, detail=f"Invalid Places API key: {str(e)}")
        else:
            raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@app.get("/place-details")
async def get_place_details(
    place_id: str = Query(..., description="Google Places ID"),
    fields: Optional[str] = Query(
        "id,displayName,location,rating,userRatingCount,primaryTypeDisplayName,types,formattedAddress,regularOpeningHours",
        description="Comma-separated list of fields to return"
    ),
    places_api_key: str = Query("", description="Provide your own Google Places API key")
):
    """
    Get detailed information about a place using its place_id
    """
    try:
        # Use provided API key or fall back to environment variable
        api_key = places_api_key if places_api_key else os.getenv("PLACES_API_KEY", "")
        if not api_key:
            raise HTTPException(status_code=400, detail="Places API key is required")
        
        url = f"https://places.googleapis.com/v1/places/{place_id}"
        
        headers = {
            "Content-Type": "application/json",
            "X-Goog-Api-Key": api_key,
            "X-Goog-FieldMask": fields
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    # Parse the place details similar to your existing _parse_place_data method
                    location_data = data.get("location", {})
                    
                    place_details = {
                        "id": data.get("id"),
                        "name": data.get("displayName", {}).get("text", ""),
                        "location": {
                            "latitude": location_data.get("latitude"),
                            "longitude": location_data.get("longitude")
                        },
                        "rating": data.get("rating"),
                        "user_rating_count": data.get("userRatingCount"),
                        "primary_type": data.get("primaryTypeDisplayName", {}).get("text", ""),
                        "types": data.get("types", []),
                        "address": data.get("formattedAddress"),
                        "opening_hours": data.get("regularOpeningHours")
                    }
                    
                    return {
                        "place": place_details,
                        "status": "success"
                    }
                
                else:
                    error_text = await response.text()
                    logger.error(f"Place details API failed with status {response.status}: {error_text}")
                    if response.status == 400:
                        raise HTTPException(
                            status_code=400,
                            detail=f"Invalid Places API key or request: {error_text}"
                        )
                    else:
                        raise HTTPException(
                            status_code=response.status,
                            detail=f"Places API error: {error_text}"
                        )
                    
    except aiohttp.ClientError as e:
        logger.error(f"Network error in place details: {e}")
        raise HTTPException(status_code=503, detail="Network error connecting to Places API")
    
    except Exception as e:
        logger.error(f"Unexpected error in place details: {e}")
        if "API_KEY_INVALID" in str(e) or "INVALID_REQUEST" in str(e):
            raise HTTPException(status_code=400, detail=f"Invalid Places API key: {str(e)}")
        else:
            raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@app.get("/create-user")
def create_user(
   email: str = Query(..., description="User email"),
   name: str = Query(..., description="User name"),
   session: Session = Depends(get_session)
):
   try:
       # Try to find existing user by email
       statement = select(User).where(User.email == email)
       existing_user = session.exec(statement).first()
       
       if existing_user:
           return {"user_id": existing_user.user_id}
       
       # Create new user
       new_user = User(
           name=name,
           email=email,
           created_at=datetime.utcnow(),
           updated_at=datetime.utcnow()
       )
       
       session.add(new_user)
       session.commit()
       session.refresh(new_user)
       
       return {"user_id": new_user.user_id,}
       
   except Exception as e:
       logger.error(f"Error creating/fetching user: {e}")
       raise HTTPException(status_code=500, detail="Failed to create or fetch user")

@app.get("/user-plans")
async def get_user_plans(
   user_id: int = Query(..., description="User ID"),
   session: Session = Depends(get_session)
):
   """
   Get all original travel plans for a user (excludes updated plans)
   """
   try:
       # Query for original plans only (where update_for is null)
       query = (
            select(TravelPlan)
            .where(TravelPlan.user_id == user_id)
            .where(TravelPlan.update_for.is_(None)) # type: ignore
            .order_by(desc(TravelPlan.created_at))
        )
       
       plans = session.exec(query).all()
       
       # Format response
       plans_data = []
       for plan in plans:
           plans_data.append({
               "travel_plan_id": plan.id,
               "city": plan.city,
               "country": plan.country,
               "intent": plan.intent,
               "travel_date": plan.travel_date.isoformat() if plan.travel_date else None,
               "number_of_days": plan.number_of_days,
               "rating": plan.rating,
               "radius_km": plan.radius_km,
               "created_at": plan.created_at.isoformat() if plan.created_at else None,
               "model": plan.model
           })
       
       return {
           "plans": plans_data,
           "total_count": len(plans_data)
       }
       
   except Exception as e:
       logger.error(f"Error fetching user plans: {e}")
       raise HTTPException(status_code=500, detail="Failed to fetch user plans")

@app.get("/plan/{plan_id}")
async def get_plan_by_id(
   plan_id: int,
   user_id: int = Query(..., description="User ID for authorization"),
   session: Session = Depends(get_session)
):
   """
   Get a specific travel plan by ID along with all its updates
   """
   try:
       # Query for the main plan with user authorization
       query = (
           select(TravelPlan)
           .where(TravelPlan.id == plan_id)
           .where(TravelPlan.user_id == user_id)  # Ensure user owns the plan
       )
       
       plan = session.exec(query).first()
       
       if not plan:
           raise HTTPException(status_code=404, detail="Travel plan not found")
       
       # Get all update plans for this plan (including nested updates)
       def get_all_updates(original_plan_id: int) -> list:
           updates_query = (
               select(TravelPlan)
               .where(TravelPlan.update_for == original_plan_id)
               .where(TravelPlan.user_id == user_id)
               .order_by(asc(TravelPlan.created_at))
           )
           updates = session.exec(updates_query).all()
           
           all_updates = []
           for update in updates:
               all_updates.append(update)
               # Recursively get updates of updates
               nested_updates = get_all_updates(update.id)
               all_updates.extend(nested_updates)
           
           return all_updates
       
       # Get all updates (if this is an original plan) or find the original plan
       if plan.update_for is None:
           # This is an original plan, get all its updates
           original_plan = plan
           update_plans = get_all_updates(plan.id)
       else:
           # This is an update plan, find the original and all updates
           original_query = (
               select(TravelPlan)
               .where(TravelPlan.id == plan.update_for)
               .where(TravelPlan.user_id == user_id)
           )
           original_plan = session.exec(original_query).first()
           
           if not original_plan:
               raise HTTPException(status_code=404, detail="Original plan not found")
           
           update_plans = get_all_updates(original_plan.id)
       
       # Function to enrich a single plan with place data using place_id
       def enrich_plan_with_places(travel_plan_data, plan_obj):
           # Get places from database for this plan
           plan_places = get_places_for_plan(session, plan_obj.id)
           
           # Create lookup dictionary for fast matching using place_id
           place_lookup = {}
           for place in plan_places:
               place_lookup[place.place_id] = {
                   "name": place.name,
                   "location": {"latitude": place.latitude, "longitude": place.longitude},
                   "photos": place.photos or [],
                   "rating": place.rating,
                   "address": place.address,
                   "opening_hours": place.opening_hours,
                   "types": place.types or []
               }

           # Enrich travel plan with place data and distances using place_id
           enriched_travel_plan = travel_plan_data
           if enriched_travel_plan and isinstance(enriched_travel_plan, dict):
               for _, day_data in enriched_travel_plan.items():
                   itinerary = day_data.get("itinerary", [])
                   for place in itinerary:
                       place_id = place.get("place_id")
                       matched = place_lookup.get(place_id) if place_id else None

                       if matched:
                           place["location"] = matched["location"]
                           place["photos"] = matched["photos"]
                           place["rating"] = matched["rating"]
                           place["address"] = matched["address"]
                           place["opening_hours"] = matched["opening_hours"]
                           place["types"] = matched["types"]
                           
                           # Calculate distance from user location to this place
                           place_lat = matched["location"].get("latitude")
                           place_lon = matched["location"].get("longitude")
                           if place_lat is not None and place_lon is not None:
                               distance = calculate_distance_meters(plan_obj.lat, plan_obj.long, place_lat, place_lon)
                               place["distance"] = distance
                           else:
                               place["distance"] = None
                       else:
                           place["distance"] = None
           
           return enriched_travel_plan
       
       # Enrich original plan
       enriched_original_plan = enrich_plan_with_places(original_plan.travel_plan, original_plan)
       
       # Build original plan response
       original_plan_data = {
           "travel_plan_id": original_plan.id,
           "travel_plan": enriched_original_plan,
           "city": original_plan.city,
           "country": original_plan.country,
           "intent": original_plan.intent,
           "start_date": original_plan.travel_date.isoformat() if original_plan.travel_date else None,
           "number_of_days": original_plan.number_of_days,
           "rating": original_plan.rating,
           "radius_km": original_plan.radius_km,
           "lat": original_plan.lat,
           "lon": original_plan.long,
           "model": original_plan.model,
           "created_at": original_plan.created_at.isoformat() if original_plan.created_at else None,
           "update_for": original_plan.update_for,
           "day_name": original_plan.travel_date.strftime('%A') if original_plan.travel_date else None
       }
       
       # Build update plans response
       update_plans_data = []
       for update_plan in update_plans:
           enriched_update_plan = enrich_plan_with_places(update_plan.travel_plan, update_plan)
           
           update_plan_data = {
               "travel_plan_id": update_plan.id,
               "travel_plan": enriched_update_plan,
               "city": update_plan.city,
               "country": update_plan.country,
               "intent": update_plan.intent,
               "start_date": update_plan.travel_date.isoformat() if update_plan.travel_date else None,
               "number_of_days": update_plan.number_of_days,
               "rating": update_plan.rating,
               "radius_km": update_plan.radius_km,
               "lat": update_plan.lat,
               "lon": update_plan.long,
               "model": update_plan.model,
               "created_at": update_plan.created_at.isoformat() if update_plan.created_at else None,
               "update_for": update_plan.update_for,
               "day_name": update_plan.travel_date.strftime('%A') if update_plan.travel_date else None
           }
           update_plans_data.append(update_plan_data)
       
       return {
           "original_plan": original_plan_data,
           "update_plans": update_plans_data,
           "total_updates": len(update_plans_data),
           "requested_plan_id": plan_id,
           "is_original": plan.update_for is None
       }
       
   except HTTPException:
       raise
   except Exception as e:
       logger.error(f"Error fetching plan by ID: {e}")
       raise HTTPException(status_code=500, detail="Failed to fetch travel plan")
   
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)