from sklearn.cluster import KMeans
import numpy as np
from typing import Dict, List, Any

def cluster_places_by_location(results: Dict[str, List[Any]], number_of_days: int) -> Dict[str, List[Any]]:
    
    # Step 1: Combine all places from all queries into one array
    all_places = []
    for query_key, places_array in results.items():
        all_places.extend(places_array)
    
    # Step 2: Remove duplicates based on place ID
    unique_places = {}
    for place in all_places:
        place_id = place.id if hasattr(place, 'id') else place['id']
        if place_id not in unique_places:
            unique_places[place_id] = place
    
    places_list = list(unique_places.values())
    
    # Step 3: Extract coordinates for clustering
    coordinates = []
    for place in places_list:
        if hasattr(place, 'location'):
            # If it's an object with location attribute
            lat = place.location.latitude
            lon = place.location.longitude
        else:
            # If it's a dictionary
            lat = place['location']['latitude']
            lon = place['location']['longitude']
        coordinates.append([lat, lon])
    
    # Step 4: Handle edge cases
    if len(places_list) == 0:
        return {}
    
    if len(places_list) <= number_of_days:
        # If we have fewer places than days, put each place in its own cluster
        clustered_results = {}
        for i, place in enumerate(places_list):
            clustered_results[f"cluster_{i}"] = [place]
        return clustered_results
    
    # Step 5: Perform k-means clustering
    coordinates_array = np.array(coordinates)
    
    # Use k-means++ initialization for better results
    kmeans = KMeans(
        n_clusters=number_of_days, 
        init='k-means++', 
        n_init=10,
        random_state=42
    )
    
    cluster_labels = kmeans.fit_predict(coordinates_array)
    
    # Step 6: Organize places by cluster
    clustered_results = {}
    for i in range(number_of_days):
        clustered_results[f"cluster_{i}"] = []
    
    for place, cluster_label in zip(places_list, cluster_labels):
        cluster_key = f"cluster_{cluster_label}"
        clustered_results[cluster_key].append(place)
    
    return clustered_results