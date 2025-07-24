import pytest
import requests
import os

# It's a good practice to have the base URL configurable
BASE_URL = os.environ.get("API_BASE_URL", "http://localhost:8000")

def get_cluster_for_place(place_name, processed_data):
    """
    Finds the cluster key for a given place name in the processed_data.
    """
    for cluster_key, places in processed_data.items():
        for place in places:
            if place.get('name') == place_name:
                return cluster_key
    return None

def test_create_3_day_travel_plan_with_clustering():
    """
    Tests the /plan endpoint to ensure that for a multi-day plan where clustering
    is active, the itinerary for each day consists of places from the same cluster.
    """
    # Define the query parameters for the request
    params = {
        "lat": 48.8575,
        "lon": 2.3514,
        "radius_km": 20,
        "rating": 3,
        "number_of_days": 3,
        "city_id": 1,
        "user_id": 1
    }

    # Make the GET request to the /plan endpoint
    response = requests.get(f"{BASE_URL}/plan", params=params)

    # 1. Check for a successful response
    assert response.status_code == 200, f"Expected status code 200, but got {response.status_code}. Response: {response.text}"

    # 2. Parse the JSON response
    data = response.json()
    assert "travel_plan" in data, "Response JSON must contain 'travel_plan'"
    assert "processed_data" in data, "Response JSON must contain 'processed_data'"

    travel_plan = data["travel_plan"]
    processed_data = data["processed_data"]

    # 3. Verify the plan is for the correct number of days
    assert len(travel_plan) == params["number_of_days"], f"Expected a {params['number_of_days']}-day plan, but got {len(travel_plan)} days."
    
    # 4. Verify the clustering rule for each day's itinerary
    for day, day_plan in travel_plan.items():
        itinerary = day_plan.get("itinerary", [])
        
        # Skip days with no itinerary
        if not itinerary:
            continue

        # Get the cluster for the first place in the itinerary
        first_place_name = itinerary[0].get("name")
        expected_cluster = get_cluster_for_place(first_place_name, processed_data)

        # It's possible the LLM hallucinates a place not in the processed data.
        # While not ideal for the app, the test should handle this gracefully.
        assert expected_cluster is not None, f"Place '{first_place_name}' from itinerary not found in processed_data."

        # Check that all other places in the itinerary belong to the same cluster
        for i in range(1, len(itinerary)):
            place_name = itinerary[i].get("name")
            
            # We only care about places that are in our source data
            if get_cluster_for_place(place_name, processed_data) is None:
                print(f"Warning: Place '{place_name}' in itinerary for {day} not found in processed_data. Skipping check for this item.")
                continue

            current_cluster = get_cluster_for_place(place_name, processed_data)
            
            assert current_cluster == expected_cluster, (
                f"Clustering rule violated on {day}. "
                f"Place '{place_name}' is in cluster '{current_cluster}', "
                f"but expected cluster '{expected_cluster}' (based on '{first_place_name}')."
            )
        
        print(f"Successfully validated {day}: All places are in cluster '{expected_cluster}'.")

