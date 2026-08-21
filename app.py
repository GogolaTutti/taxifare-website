import streamlit as st
import requests
import datetime
import pandas as pd
import pydeck as pdk

st.markdown('# 🚕 TaxiFare')


# Ask for Date and time
st.markdown('#### ⌚ When would you like to be picked up?')

# 2 Columns to ask for date and time
date_col, time_col = st.columns(2)
pickup_date = date_col.date_input('Pickup Date', value=datetime.date.today())
pickup_time = time_col.time_input('Pickup Time', value=datetime.time(12, 0))

combined_datetime = datetime.datetime.combine(pickup_date, pickup_time)
pickup_datetime = combined_datetime.strftime("%Y-%m-%d %H:%M:%S")

# Ask for pickup coordinats
st.markdown('#### 🧭 Enter your pickup coordinates')

## creating 2 equal columns for pick up coordinates
columns = st.columns(2)
pickup_longitude = columns[0].number_input('Pickup longitude', value=-73.7, min_value=-74.3, max_value=-73.7, format="%.6f", key="pickup_lon")
pickup_latitude = columns[1].number_input('Pickup longitude', value=40.7, min_value=40.5, max_value=40.9, format="%.6f", key="pickup_lat")

# Ask for dropoff coordinats
st.markdown('#### 🧭 your drop off coordinates')

## creating 2 equal columns for drop off coordinates
columns = st.columns(2)
dropoff_longitude = columns[0].number_input('Dropoff longitude', value=-74.3, min_value=-74.3, max_value=-73.7, format="%.6f", key="dropoff_lon")
dropoff_latitude = columns[1].number_input('Dropoff longitude', value=40.9, min_value=40.5, max_value=40.9, format="%.6f", key="dropoff_lat")

# Ask for passanger count
st.markdown('#### 🧍‍♂️ Number of passangers')
passenger_count = st.number_input('Passenger number please', min_value=1, max_value=8, value=1, step=1, key="passenger_count")

# Creating a map showing where passangers are to be picked up and dropped off
st.markdown('#### Route Map')
## Let's create a dataframe with the coordinates
#map_df = pd.DataFrame([
 #   {"lat": pickup_latitude, "lon": pickup_longitude},  # Punto de recogida
  #  {"lat": dropoff_latitude, "lon": dropoff_longitude}   # Punto de destino
#])
## Showing the coordinates in the map
#st.map(map_df)

st.markdown('### 🗺️ Trip Route Map')

# Creating a database with the structure that pydeck needs to draw the route lines
# Uniting pickup to dropoff
route_data = pd.DataFrame([{
    "from_lat": pickup_latitude,
    "from_lon": pickup_longitude,
    "to_lat": dropoff_latitude,
    "to_lon": dropoff_longitude,
    "tooltip": "Your Taxi Route"
}])

# Configuring the line layer with ArcLayer
layer = pdk.Layer(
    "ArcLayer",
    data=route_data,
    get_source_position=["from_lon", "from_lat"],
    get_target_position=["to_lon", "to_lat"],
    get_source_color=[255, 165, 0, 200],  # Color naranja de inicio (RGBA)
    get_target_color=[255, 0, 0, 200],    # Color rojo de llegada (RGBA)
    stroke_width=5,                       # Grosor de la línea
)

# Centering the view with respect to the coordinates of the user
view_state = pdk.ViewState(
    latitude=(pickup_latitude + dropoff_latitude) / 2,
    longitude=(pickup_longitude + dropoff_longitude) / 2,
    zoom=11,
    pitch=45,  # Ángulo de inclinación 3D para apreciar el arco
)

# Showing the interactive map in the screen
st.pydeck_chart(pdk.Deck(
    layers=[layer],
    initial_view_state=view_state,
    tooltip={"text": "{tooltip}"}
))



############################# Calling the API
# Defining the url for my api
API_URL = 'https://taxifare.lewagon.ai/predict'

st.markdown('### 💸 Price Calculation')

# Let's build a dictionary with the parameters (from the user) for our API to use
params = {
    "pickup_datetime": pickup_datetime,
    "pickup_longitude": pickup_longitude,
    "pickup_latitude": pickup_latitude,
    "dropoff_longitude": dropoff_longitude,
    "dropoff_latitude": dropoff_latitude,
    "passenger_count": passenger_count
}

# Activating the price prediction
if st.button('Calculate fare'):

    with st.spinner('Calling your API...'):
        try:
            # Calling the API with request
            response = requests.get(API_URL, params=params)

            # Did we have a good anwer, is the status code 200?
            if response.status_code == 200:

                # Get the json answer from th epi
                data = response.json()

                # Acceder a la clave del JSON (asumiendo que tu API devuelve {"prediction": valor})
                prediction = data.get("fare", data.get("prediction", 0.0))

                # Conveying the price info to user
                st.success(f"The predicted taxi fare is: ${prediction:.2f}")

            else:
                st.error(f"Calculation Error. Status code: {response.status_code}")

        except requests.exceptions.RequestException as e:
            st.error(f"Could not connect to the API. Error: {e}")
