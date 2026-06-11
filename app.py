import streamlit as st
import requests
import json


st.set_page_config(page_title="Travel Planner Agent", page_icon="✈️")


st.title("✈️ Travel Planner - Input & Preference Agent")
st.write("Fill in your travel preferences below and generate a structured travel profile.")


def get_location_options(city_or_region):
    url = "https://geocoding-api.open-meteo.com/v1/search"
    params = {
        "name": city_or_region,
        "count": 5,
        "language": "en",
        "format": "json"
    }
    response = requests.get(url, params=params, timeout=30)
    data = response.json()

    if "results" in data and len(data["results"]) > 0:
        return data["results"]
    return []


def get_weather_details(latitude, longitude, timezone):
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": latitude,
        "longitude": longitude,
        "current": "temperature_2m,weather_code,wind_speed_10m",
        "daily": "temperature_2m_max,temperature_2m_min",
        "timezone": timezone,
        "forecast_days": 1
    }
    response = requests.get(url, params=params, timeout=30)
    return response.json()


def get_weather_description(weather_code):
    weather_code_map = {
        0: "Clear sky",
        1: "Mainly clear",
        2: "Partly cloudy",
        3: "Overcast",
        45: "Fog",
        48: "Depositing rime fog",
        51: "Light drizzle",
        53: "Moderate drizzle",
        55: "Dense drizzle",
        56: "Light freezing drizzle",
        57: "Dense freezing drizzle",
        61: "Slight rain",
        63: "Moderate rain",
        65: "Heavy rain",
        66: "Light freezing rain",
        67: "Heavy freezing rain",
        71: "Slight snow fall",
        73: "Moderate snow fall",
        75: "Heavy snow fall",
        77: "Snow grains",
        80: "Slight rain showers",
        81: "Moderate rain showers",
        82: "Violent rain showers",
        85: "Slight snow showers",
        86: "Heavy snow showers",
        95: "Thunderstorm",
        96: "Thunderstorm with slight hail",
        99: "Thunderstorm with heavy hail"
    }
    return weather_code_map.get(weather_code, "Unknown weather")


def get_temperature_feel(temp_c):
    if temp_c is None:
        return "Unknown"
    if temp_c >= 32:
        return "Hot"
    elif temp_c >= 20:
        return "Mild"
    else:
        return "Cool"


def get_wind_feel(wind_speed):
    if wind_speed is None:
        return "Unknown"
    if wind_speed >= 20:
        return "Windy"
    else:
        return "Calm"


def get_activity_suitability(weather_code, temp_c, wind_speed):
    indoor_codes = {
        45, 48, 53, 55, 56, 57,
        63, 65, 66, 67,
        73, 75, 77,
        81, 82, 86,
        95, 96, 99
    }

    if weather_code in indoor_codes:
        return "Better for indoor activities"

    if temp_c is not None and temp_c >= 35:
        return "Better for indoor activities during peak afternoon; outdoor is okay in morning/evening"

    if wind_speed is not None and wind_speed >= 25:
        return "Outdoor possible, but windy conditions require caution"

    return "Good for outdoor activities"


def build_weather_summary(weather):
    current = weather.get("current", {})
    daily = weather.get("daily", {})

    current_temp = current.get("temperature_2m")
    wind_speed = current.get("wind_speed_10m")
    weather_code = current.get("weather_code")
    max_temp = daily.get("temperature_2m_max", [None])[0]
    min_temp = daily.get("temperature_2m_min", [None])[0]

    description = get_weather_description(weather_code)
    temperature_feel = get_temperature_feel(current_temp)
    wind_feel = get_wind_feel(wind_speed)
    activity_suitability = get_activity_suitability(weather_code, current_temp, wind_speed)

    summary = {
        "weather_description": description,
        "temperature_now_c": current_temp,
        "temperature_feel": temperature_feel,
        "wind_speed_kmh": wind_speed,
        "wind_feel": wind_feel,
        "today_max_c": max_temp,
        "today_min_c": min_temp,
        "activity_suitability": activity_suitability
    }

    return summary


def get_travel_profile_from_ollama(user_data):
    prompt = (
        "You are a travel preference structuring assistant.\n"
        "Return only valid JSON.\n"
        "Do not include markdown.\n"
        "Do not include explanation text.\n\n"
        f"User input:\n{json.dumps(user_data, indent=2)}\n\n"
        "Return JSON with exactly these keys:\n"
        "origin, destination_country, destination_city_region, days, travelers, budget, "
        "hotel_category, food_preference, travel_style, pace, interests"
    )

    response = requests.post(
        "http://localhost:11434/api/generate",
        json={
            "model": "qwen2.5:3b",
            "prompt": prompt,
            "stream": False,
            "format": "json"
        },
        timeout=60
    )

    return response.json()["response"]


with st.form("travel_form"):
    origin = st.text_input("Origin city")
    destination_country = st.text_input("Destination country")
    destination_city_region = st.text_input("Destination city / region")
    days = st.number_input("Number of days", min_value=1, max_value=30, value=4)
    travelers = st.number_input("Number of travelers", min_value=1, max_value=10, value=2)
    budget = st.selectbox("Budget", ["Low", "Moderate", "High", "Luxury"])
    hotel_category = st.selectbox("Hotel preference", ["3-star", "4-star", "5-star"])
    food_preference = st.selectbox("Food preference", ["Veg", "Non-veg", "Both"])
    travel_style = st.selectbox("Travel style", ["Leisure", "Adventure", "Cultural", "Family", "Mixed"])
    pace = st.selectbox("Trip pace", ["Relaxed", "Moderate", "Packed"])
    interests = st.multiselect(
        "Interests",
        ["Beaches", "Food", "Culture", "Nature", "Shopping", "Nightlife", "Temples", "Museums"]
    )

    submitted = st.form_submit_button("Create Travel Profile")


if submitted:
    errors = []

    if not origin.strip():
        errors.append("Origin city is required.")
    if not destination_country.strip():
        errors.append("Destination country is required.")
    if not destination_city_region.strip():
        errors.append("Destination city / region is required.")
    if len(interests) == 0:
        errors.append("Please select at least one interest.")

    if errors:
        for error in errors:
            st.error(error)
    else:
        user_data = {
            "origin": origin,
            "destination_country": destination_country,
            "destination_city_region": destination_city_region,
            "days": int(days),
            "travelers": int(travelers),
            "budget": budget,
            "hotel_category": hotel_category,
            "food_preference": food_preference,
            "travel_style": travel_style,
            "pace": pace,
            "interests": interests
        }

        st.subheader("Submitted Form Data")
        st.json(user_data)

        try:
            structured_profile = get_travel_profile_from_ollama(user_data)
            parsed_profile = json.loads(structured_profile)

            st.subheader("LLM-Structured Travel Profile")
            st.json(parsed_profile)

            summary_text = (
                f"{parsed_profile['travelers']} traveler(s) planning a "
                f"{parsed_profile['days']}-day "
                f"{str(parsed_profile['travel_style']).lower()} trip from "
                f"{parsed_profile['origin']} to "
                f"{str(parsed_profile['destination_city_region']).title()}, "
                f"{str(parsed_profile['destination_country']).title()} "
                f"with a {str(parsed_profile['budget']).lower()} budget."
            )

            st.subheader("Quick Summary")
            st.success(summary_text)

            st.subheader("Destination Research")

            location_options = get_location_options(parsed_profile["destination_city_region"])

            if location_options:
                filtered_options = []

                for loc in location_options:
                    loc_country = str(loc.get("country", "")).lower()
                    user_country = str(parsed_profile["destination_country"]).lower()

                    if user_country in loc_country or loc_country in user_country:
                        filtered_options.append(loc)

                if len(filtered_options) == 0:
                    filtered_options = location_options

                option_labels = []
                for loc in filtered_options:
                    name = loc.get("name", "Unknown")
                    country = loc.get("country", "Unknown Country")
                    timezone = loc.get("timezone", "Unknown Timezone")
                    label = f"{name}, {country} ({timezone})"
                    option_labels.append(label)

                selected_label = st.selectbox("Select the correct destination", option_labels)
                selected_index = option_labels.index(selected_label)
                selected_location = filtered_options[selected_index]

                st.write("### Location Details")
                st.json({
                    "name": selected_location.get("name"),
                    "country": selected_location.get("country"),
                    "latitude": selected_location.get("latitude"),
                    "longitude": selected_location.get("longitude"),
                    "timezone": selected_location.get("timezone")
                })

                weather = get_weather_details(
                    selected_location.get("latitude"),
                    selected_location.get("longitude"),
                    selected_location.get("timezone")
                )

                st.write("### Raw Weather Details")
                st.json({
                    "current_temperature": weather.get("current", {}).get("temperature_2m"),
                    "wind_speed": weather.get("current", {}).get("wind_speed_10m"),
                    "weather_code": weather.get("current", {}).get("weather_code"),
                    "max_temperature": weather.get("daily", {}).get("temperature_2m_max", [None])[0],
                    "min_temperature": weather.get("daily", {}).get("temperature_2m_min", [None])[0]
                })

                weather_summary = build_weather_summary(weather)

                st.write("### Weather Summary for Planning")
                st.json(weather_summary)

                st.info(
                    f"Today's weather is {weather_summary['weather_description'].lower()}. "
                    f"It feels {weather_summary['temperature_feel'].lower()} with "
                    f"{weather_summary['wind_feel'].lower()} conditions. "
                    f"{weather_summary['activity_suitability']}."
                )

            else:
                st.warning("Could not find destination details.")

        except Exception as e:
            st.error("Something went wrong while getting the travel profile from Ollama.")
            st.code(str(e))