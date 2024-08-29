import streamlit as st
import requests
from datetime import datetime
import folium
from streamlit_folium import folium_static
from mapbox import Geocoder
import os

st.markdown('''
Welcome to the Taxi Fare Prediction App!
''')

'''
## Enter Your Ride Details:
'''
# Initialize coordinates with default values
pickup_longitude = -73.9798156
pickup_latitude = 40.7614327
dropoff_longitude = -73.9630000
dropoff_latitude = 40.8030000

pickup_datetime = st.text_input("Date and Time (YYYY-MM-DD HH:MM)", value=datetime.now().strftime("%Y-%m-%d %H:%M"))

# Add this function after the imports
def get_address_suggestions(query):
    url = f"https://api.mapbox.com/geocoding/v5/mapbox.places/{query}.json"
    params = {
        "access_token": st.secrets["mapbox"]["MAPBOX_PK"],
        "autocomplete": True,
        "types": "address"
    }
    response = requests.get(url, params=params)
    if response.status_code == 200:
        suggestions = [feature['place_name'] for feature in response.json()['features']]
        return suggestions
    return []

# Replace the pickup and dropoff address input sections with these:
pickup_address = st.text_input("Pickup Location (Address)", key="pickup")
if pickup_address:
    pickup_suggestions = get_address_suggestions(pickup_address)
    pickup_address = st.selectbox("Select pickup address", options=pickup_suggestions, key="pickup_select")

dropoff_address = st.text_input("Dropoff Location (Address)", key="dropoff")
if dropoff_address:
    dropoff_suggestions = get_address_suggestions(dropoff_address)
    dropoff_address = st.selectbox("Select dropoff address", options=dropoff_suggestions, key="dropoff_select")

passenger_count = st.number_input("Passenger Count", min_value=1, step=1, value=1)

try:
    # Try to get the token from Streamlit secrets
    MAPBOX_ACCESS_TOKEN = st.secrets["mapbox"]["MAPBOX_PK"]
except FileNotFoundError:
    # If running locally and secrets.toml is not set up, fall back to environment variable
    MAPBOX_ACCESS_TOKEN = os.environ.get("MAPBOX_PK")

if not MAPBOX_ACCESS_TOKEN:
    st.error("Mapbox access token not found. Please set it up in secrets.toml or as an environment variable.")
    st.stop()

# Your Mapbox access token
MAPBOX_ACCESS_TOKEN = st.secrets["mapbox"]["MAPBOX_PK"]


geocoder = Geocoder(access_token=MAPBOX_ACCESS_TOKEN)

# 2. Geocode Pickup and Dropoff Locations
if pickup_address:
    response_pickup = geocoder.forward(pickup_address)
    if response_pickup.status_code == 200:
        pickup_coordinates = response_pickup.geojson()['features'][0]['geometry']['coordinates']
        pickup_longitude, pickup_latitude = pickup_coordinates
    else:
        st.error(f"Error geocoding pickup address: {response_pickup.status_code}")

if dropoff_address:
    response_dropoff = geocoder.forward(dropoff_address)
    if response_dropoff.status_code == 200:
        dropoff_coordinates = response_dropoff.geojson()['features'][0]['geometry']['coordinates']
        dropoff_longitude, dropoff_latitude = dropoff_coordinates
    else:
        st.error(f"Error geocoding dropoff address: {response_dropoff.status_code}")
'''
## Get Your Fare Prediction:
'''

url = 'https://taxifare.lewagon.ai/predict'  # You can change this to your API endpoint

if url == 'https://taxifare.lewagon.ai/predict':
    st.markdown('**Note:** Using the Le Wagon API for prediction.')

# 2. Create dictionary for API parameters
params = {
    "pickup_datetime": pickup_datetime,
    "pickup_longitude": pickup_longitude,
    "pickup_latitude": pickup_latitude,
    "dropoff_longitude": dropoff_longitude,
    "dropoff_latitude": dropoff_latitude,
    "passenger_count": passenger_count
}

# 3. Call API using requests
response = requests.get(url, params=params)

# 4. Retrieve prediction from JSON response
if response.status_code == 200:
    prediction = response.json()['fare']
    st.success(f'## Your Estimated Fare: ${prediction:.2f}')
else:
    st.error('Error fetching prediction. Please check your inputs or the API endpoint.')

# Add this function after the other functions
def get_route(start_lon, start_lat, end_lon, end_lat):
    url = f"https://api.mapbox.com/directions/v5/mapbox/driving/{start_lon},{start_lat};{end_lon},{end_lat}"
    params = {
        "access_token": st.secrets["mapbox"]["MAPBOX_PK"],
        "geometries": "geojson",
        "overview": "full"
    }
    response = requests.get(url, params=params)
    if response.status_code == 200:
        route = response.json()['routes'][0]['geometry']['coordinates']
        return route
    return None

# Replace the map creation part with this
if response.status_code == 200:
    # Get the route
    route = get_route(pickup_longitude, pickup_latitude, dropoff_longitude, dropoff_latitude)

    if route:
        # Create a Folium map centered on the pickup location
        m = folium.Map(location=[pickup_latitude, pickup_longitude], zoom_start=12)

        # Add markers for pickup and dropoff locations
        folium.Marker([pickup_latitude, pickup_longitude],
                      popup="Pickup Location",
                      icon=folium.Icon(color='blue')).add_to(m)
        folium.Marker([dropoff_latitude, dropoff_latitude],
                      popup="Dropoff Location",
                      icon=folium.Icon(color='red')).add_to(m)

        # Add the route line
        folium.PolyLine(
            locations=[[coord[1], coord[0]] for coord in route],  # Note the coordinate order swap
            color="red",
            weight=2,
            opacity=0.8
        ).add_to(m)

        # Adjust the map view to show the entire route
        sw = min(coord[1] for coord in route), min(coord[0] for coord in route)
        ne = max(coord[1] for coord in route), max(coord[0] for coord in route)
        m.fit_bounds([sw, ne])

        # Display the map
        folium_static(m)
    else:
        st.error("Unable to fetch route. Please check your inputs and try again.")
