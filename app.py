import streamlit as st
import requests
from datetime import datetime
import folium
from streamlit_folium import folium_static
from mapbox import Geocoder
import os

'''
# Taxi Fare Interface
'''

st.markdown('''
Welcome to the Taxi Fare Prediction App!
''')

'''
## Enter Your Ride Details:
'''
'''
## Enter Your Ride Details:
'''
# Initialize coordinates with default values
pickup_longitude = -73.9798156
pickup_latitude = 40.7614327
dropoff_longitude = -73.9630000
dropoff_latitude = 40.8030000

pickup_datetime = st.text_input("Date and Time (YYYY-MM-DD HH:MM)", value=datetime.now().strftime("%Y-%m-%d %H:%M"))

# Get pickup location from user
pickup_address = st.text_input("Pickup Location (Address)")

# Get dropoff location from user
dropoff_address = st.text_input("Dropoff Location (Address)")

passenger_count = st.number_input("Passenger Count", min_value=1, step=1, value=1)

# Your Mapbox access token
MAPBOX_ACCESS_TOKEN = os.environ.get("MAPBOX_PK")


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


# 5. Display Map
if response.status_code == 200:
    # ... (Display prediction) ...

    # Create a Folium map centered on the pickup location
    m = folium.Map(location=[pickup_latitude, pickup_longitude], zoom_start=13)

    # Add markers for pickup and dropoff locations using COORDINATES
    folium.Marker([pickup_latitude, pickup_longitude],
                  popup="Pickup Location",
                  icon=folium.Icon(color='blue')).add_to(m)
    folium.Marker([dropoff_latitude, dropoff_longitude],
                  popup="Dropoff Location",
                  icon=folium.Icon(color='red')).add_to(m)

    # Display the map
    folium_static(m)
