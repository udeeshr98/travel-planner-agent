import json
import re
import requests
import streamlit as st


SERPAPI_API_KEY = st.secrets["SERPAPI_API_KEY"]
YOUTUBE_API_KEY = st.secrets["YOUTUBE_API_KEY"]
OLLAMA_URL = "http://localhost:11434/api/generate"
OLLAMA_MODEL = "qwen2.5:3b"

ALLOWED_PLACE_CATEGORIES = [
    "Beach", "Culture", "Nature", "Food", "Shopping", "Museum",
    "Nightlife", "Landmark", "Market", "Sports"
]
ALLOWED_WEATHER_SENSITIVITY = ["Low", "Moderate", "High"]
ALLOWED_TRAVELER_SENTIMENT = ["Positive", "Mixed", "Cautious"]
ALLOWED_BUDGET_FIT = ["Low", "Moderate", "High", "Luxury", "Budget-friendly", "Affordable"]
ALLOWED_INTERESTS = ["Beaches", "Food", "Culture", "Nature", "Shopping", "Nightlife", "Temples", "Museums"]


# ---------------------------------------------------------------------------
# Core HTTP helpers
# ---------------------------------------------------------------------------

def safe_get_json(url, params=None, timeout=30):
    response = requests.get(url, params=params, timeout=timeout)
    response.raise_for_status()
    return response.json()


def safe_post_json(url, payload, timeout=60):
    response = requests.post(url, json=payload, timeout=timeout)
    response.raise_for_status()
    return response.json()


# ---------------------------------------------------------------------------
# Text helpers
# ---------------------------------------------------------------------------

def clean_text(value):
    return str(value).strip() if value is not None else ""


def ensure_list(value):
    if isinstance(value, list):
        return [clean_text(v) for v in value if clean_text(v)]
    if isinstance(value, str) and clean_text(value):
        return [clean_text(value)]
    return []


def normalize_whitespace(text):
    return re.sub(r"\s+", " ", clean_text(text))


def dedupe_results(results):
    seen = set()
    cleaned = []
    for item in results:
        link = item.get("link") or item.get("video_url") or item.get("title")
        if link and link not in seen:
            seen.add(link)
            cleaned.append(item)
    return cleaned


# ---------------------------------------------------------------------------
# Geocoding
# ---------------------------------------------------------------------------

def get_location_options(city_or_region):
    url = "https://geocoding-api.open-meteo.com/v1/search"
    params = {"name": city_or_region, "count": 5, "language": "en", "format": "json"}
    data = safe_get_json(url, params=params, timeout=30)
    return data.get("results", [])


# ---------------------------------------------------------------------------
# Weather helpers  (anchor location only)
# ---------------------------------------------------------------------------

def get_weather_details(latitude, longitude, timezone):
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": latitude,
        "longitude": longitude,
        "current": "temperature_2m,weather_code,wind_speed_10m",
        "daily": "temperature_2m_max,temperature_2m_min",
        "timezone": timezone,
        "forecast_days": 1,
    }
    return safe_get_json(url, params=params, timeout=30)


def get_weather_description(weather_code):
    weather_code_map = {
        0: "Clear sky", 1: "Mainly clear", 2: "Partly cloudy", 3: "Overcast",
        45: "Fog", 48: "Depositing rime fog", 51: "Light drizzle", 53: "Moderate drizzle",
        55: "Dense drizzle", 56: "Light freezing drizzle", 57: "Dense freezing drizzle",
        61: "Slight rain", 63: "Moderate rain", 65: "Heavy rain", 66: "Light freezing rain",
        67: "Heavy freezing rain", 71: "Slight snow fall", 73: "Moderate snow fall",
        75: "Heavy snow fall", 77: "Snow grains", 80: "Slight rain showers",
        81: "Moderate rain showers", 82: "Violent rain showers", 85: "Slight snow showers",
        86: "Heavy snow showers", 95: "Thunderstorm", 96: "Thunderstorm with slight hail",
        99: "Thunderstorm with heavy hail"
    }
    return weather_code_map.get(weather_code, "Unknown weather")


def get_temperature_feel(temp_c):
    if temp_c is None:
        return "Unknown"
    if temp_c >= 32:
        return "Hot"
    if temp_c >= 20:
        return "Mild"
    return "Cool"


def get_wind_feel(wind_speed):
    if wind_speed is None:
        return "Unknown"
    if wind_speed >= 20:
        return "Windy"
    return "Calm"


def get_activity_suitability(weather_code, temp_c, wind_speed):
    indoor_codes = {
        45, 48, 53, 55, 56, 57, 63, 65, 66, 67, 73, 75, 77, 81, 82, 86, 95, 96, 99
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

    return {
        "weather_description": get_weather_description(weather_code),
        "temperature_now_c": current_temp,
        "temperature_feel": get_temperature_feel(current_temp),
        "wind_speed_kmh": wind_speed,
        "wind_feel": get_wind_feel(wind_speed),
        "today_max_c": max_temp,
        "today_min_c": min_temp,
        "activity_suitability": get_activity_suitability(weather_code, current_temp, wind_speed),
    }


# ---------------------------------------------------------------------------
# Search helpers
# ---------------------------------------------------------------------------

def serpapi_search(query, num_results=3):
    url = "https://serpapi.com/search.json"
    params = {"engine": "google", "q": query, "api_key": SERPAPI_API_KEY, "num": num_results}
    data = safe_get_json(url, params=params, timeout=60)
    results = []
    for item in data.get("organic_results", [])[:num_results]:
        results.append({
            "title": item.get("title", ""),
            "link": item.get("link", ""),
            "snippet": item.get("snippet", ""),
        })
    return results


def youtube_search(query, max_results=2):
    url = "https://www.googleapis.com/youtube/v3/search"
    params = {
        "key": YOUTUBE_API_KEY,
        "part": "snippet",
        "q": query,
        "type": "video",
        "maxResults": max_results,
    }
    data = safe_get_json(url, params=params, timeout=60)
    results = []
    for item in data.get("items", []):
        snippet = item.get("snippet", {})
        video_id = item.get("id", {}).get("videoId", "")
        results.append({
            "title": snippet.get("title", ""),
            "channel": snippet.get("channelTitle", ""),
            "description": snippet.get("description", ""),
            "video_url": f"https://www.youtube.com/watch?v={video_id}" if video_id else "",
        })
    return results


# ---------------------------------------------------------------------------
# CITY-LEVEL research  (runs once per selected city)
# ---------------------------------------------------------------------------

def build_city_research(city, country, parsed_profile):
    """
    Collects web + YouTube research specifically for one city.
    All search queries are city-specific so the intel is never generic.
    """
    destination = f"{city}, {country}"
    interests_text = ", ".join(parsed_profile.get("interests", []))
    hotel_category = parsed_profile.get("hotel_category", "")
    food_preference = parsed_profile.get("food_preference", "")
    budget = parsed_profile.get("budget", "")

    search_plan = {
        "best_areas_to_stay": [
            f"best areas to stay in {destination} for tourists",
            f"{destination} best neighborhoods for visitors",
        ],
        "must_visit_places": [
            f"must visit places in {destination}",
            f"top tourist attractions in {destination}",
        ],
        "suggested_places_by_interest": [
            f"best {interests_text} spots in {destination}",
            f"{destination} things to do {interests_text}",
        ],
        "hotels": [
            f"best {hotel_category} hotels in {destination} {budget}",
            f"recommended {hotel_category} hotels in {city} {country} for tourists",
        ],
        "food": [
            f"best {food_preference} food restaurants in {destination}",
            f"famous local food spots in {city} must try dishes {food_preference}",
        ],
        "local_transport": [
            f"how to get around {destination} for tourists",
            f"{destination} local transport options tuk tuk taxi songthaew",
        ],
    }

    web_research = {}
    total_web_results = 0
    for section, queries in search_plan.items():
        section_results = []
        for query in queries:
            section_results.extend(serpapi_search(query, num_results=3))
        section_results = dedupe_results(section_results)[:6]
        web_research[section] = section_results
        total_web_results += len(section_results)

    youtube_queries = [
        f"{destination} travel guide",
        f"best hotels in {destination}",
        f"{destination} food guide must try",
    ]
    youtube_results = []
    for query in youtube_queries:
        youtube_results.extend(youtube_search(query, max_results=2))
    youtube_results = dedupe_results(youtube_results)[:6]

    return {
        "city": city,
        "country": country,
        "destination_label": destination,
        "web_research": web_research,
        "youtube_research": youtube_results,
        "source_counts": {
            "web_results_count": total_web_results,
            "youtube_results_count": len(youtube_results),
        },
    }


# ---------------------------------------------------------------------------
# COUNTRY-LEVEL research  (runs once for the whole trip)
# ---------------------------------------------------------------------------

def build_country_research(country, selected_cities, parsed_profile):
    """
    Collects country-level context: climate/season, visa, etiquette, safety,
    and inter-city transport between the user's specific selected cities.
    """
    cities_text = " and ".join(selected_cities) if selected_cities else country
    cities_joined = ", ".join(selected_cities) if selected_cities else country

    search_plan = {
        "best_season_climate": [
            f"best time to visit {country} for tourists weather season",
            f"{country} climate travel seasons when to go",
        ],
        "visa_entry": [
            f"{country} visa requirements for Indian tourists",
            f"entry requirements for visiting {country}",
        ],
        "country_etiquette": [
            f"{country} culture etiquette for tourists dos and donts",
            f"customs and traditions in {country} for visitors",
        ],
        "country_safety": [
            f"{country} tourist safety tips general",
            f"is {country} safe for tourists travel advice",
        ],
        "intercity_transport": [
            f"how to travel between {cities_text} in {country}",
            f"{cities_joined} travel options bus train flight {country}",
            f"getting from {selected_cities[0]} to {selected_cities[-1]} {country}" if len(selected_cities) >= 2 else f"transport within {country}",
        ],
    }

    web_research = {}
    total_web_results = 0
    for section, queries in search_plan.items():
        section_results = []
        for query in queries:
            section_results.extend(serpapi_search(query, num_results=3))
        section_results = dedupe_results(section_results)[:6]
        web_research[section] = section_results
        total_web_results += len(section_results)

    return {
        "country": country,
        "selected_cities": selected_cities,
        "web_research": web_research,
        "source_counts": {
            "web_results_count": total_web_results,
        },
    }


# ---------------------------------------------------------------------------
# Master research builder  (replaces old build_live_research_context)
# ---------------------------------------------------------------------------

def build_live_research_context(parsed_profile, selected_location):
    """
    Builds a structured multi-city research context:
    - country_context: climate, visa, etiquette, safety, inter-city transport
    - city_research: per-city intel for every selected city
    - anchor_location: geocoded anchor details
    """
    country = parsed_profile.get("destination_country", "")
    selected_cities = parsed_profile.get("selected_cities", [])
    custom_city = clean_text(parsed_profile.get("custom_city_region", ""))

    # Build the full city list (selected + custom, deduplicated)
    all_cities = list(dict.fromkeys(selected_cities + ([custom_city] if custom_city else [])))

    # Fallback: if no cities were explicitly selected, use anchor
    if not all_cities:
        anchor_name = clean_text(selected_location.get("name", ""))
        if anchor_name:
            all_cities = [anchor_name]

    # Country-level research
    country_research = build_country_research(country, all_cities, parsed_profile)

    # City-level research for every selected city
    city_research = {}
    total_city_web = 0
    total_city_youtube = 0
    for city in all_cities:
        city_data = build_city_research(city, country, parsed_profile)
        city_research[city] = city_data
        total_city_web += city_data["source_counts"]["web_results_count"]
        total_city_youtube += city_data["source_counts"]["youtube_results_count"]

    return {
        "anchor_location": {
            "name": clean_text(selected_location.get("name")),
            "country": clean_text(selected_location.get("country")),
            "latitude": selected_location.get("latitude"),
            "longitude": selected_location.get("longitude"),
            "timezone": clean_text(selected_location.get("timezone")),
        },
        "all_cities": all_cities,
        "country_research": country_research,
        "city_research": city_research,
        "source_counts": {
            "country_web_results": country_research["source_counts"]["web_results_count"],
            "city_web_results": total_city_web,
            "city_youtube_results": total_city_youtube,
        },
    }


# ---------------------------------------------------------------------------
# JSON Schema builders
# ---------------------------------------------------------------------------

def get_city_schema(city, country, user_interests):
    """
    Schema for one city's intel block. Used inside the multi-city schema.
    """
    return {
        "type": "object",
        "properties": {
            "city_fit_summary": {
                "type": "string",
                "description": f"One sentence describing what {city} is best for (e.g. best for beaches and nightlife)."
            },
            "best_areas_to_stay": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "area_name": {"type": "string"},
                        "best_for": {"type": "array", "items": {"type": "string"}},
                        "why_recommended": {"type": "string"},
                        "pros": {"type": "array", "items": {"type": "string"}},
                        "cons": {"type": "array", "items": {"type": "string"}},
                        "budget_fit": {"type": "string", "enum": ALLOWED_BUDGET_FIT},
                        "connectivity_notes": {"type": "string"},
                        "traveler_sentiment": {"type": "string", "enum": ALLOWED_TRAVELER_SENTIMENT},
                    },
                    "required": [
                        "area_name", "best_for", "why_recommended", "pros", "cons",
                        "budget_fit", "connectivity_notes", "traveler_sentiment",
                    ],
                },
            },
            "must_visit_places": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "name": {"type": "string"},
                        "category": {"type": "string", "enum": ALLOWED_PLACE_CATEGORIES},
                        "why_visit": {"type": "string"},
                        "best_for": {"type": "array", "items": {"type": "string"}},
                        "time_needed": {"type": "string"},
                        "best_time_to_visit": {"type": "string"},
                        "weather_sensitivity": {"type": "string", "enum": ALLOWED_WEATHER_SENSITIVITY},
                    },
                    "required": [
                        "name", "category", "why_visit", "best_for",
                        "time_needed", "best_time_to_visit", "weather_sensitivity",
                    ],
                },
            },
            "suggested_places_by_interest": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "name": {"type": "string"},
                        "matched_interest": {"type": "string", "enum": user_interests},
                        "why_suggested": {"type": "string"},
                        "indoor_outdoor": {"type": "string", "enum": ["Indoor", "Outdoor", "Mixed"]},
                        "time_needed": {"type": "string"},
                    },
                    "required": [
                        "name", "matched_interest", "why_suggested",
                        "indoor_outdoor", "time_needed",
                    ],
                },
            },
            "hotel_recommendations": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "hotel_name": {"type": "string"},
                        "area": {"type": "string"},
                        "hotel_category": {"type": "string"},
                        "budget_fit": {"type": "string"},
                        "why_it_matches": {"type": "string"},
                        "review_highlights": {"type": "array", "items": {"type": "string"}},
                        "cautions": {"type": "array", "items": {"type": "string"}},
                        "pricing_note": {"type": "string"},
                        "location_logic": {"type": "string"},
                    },
                    "required": [
                        "hotel_name", "area", "hotel_category", "budget_fit",
                        "why_it_matches", "review_highlights", "cautions",
                        "pricing_note", "location_logic",
                    ],
                },
            },
            "food_recommendations": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "place_name": {"type": "string"},
                        "category": {"type": "string"},
                        "cuisine": {"type": "string"},
                        "area": {"type": "string"},
                        "why_recommended": {"type": "string"},
                        "signature_items": {"type": "array", "items": {"type": "string"}},
                        "price_level": {"type": "string"},
                        "vibe": {"type": "string"},
                        "notes": {"type": "string"},
                    },
                    "required": [
                        "place_name", "category", "cuisine", "area",
                        "why_recommended", "signature_items", "price_level",
                        "vibe", "notes",
                    ],
                },
            },
            "local_transport": {
                "type": "object",
                "properties": {
                    "summary": {"type": "string"},
                    "common_modes": {"type": "array", "items": {"type": "string"}},
                    "best_options_for_tourists": {"type": "array", "items": {"type": "string"}},
                    "cost_notes": {"type": "array", "items": {"type": "string"}},
                    "practical_tips": {"type": "array", "items": {"type": "string"}},
                },
                "required": [
                    "summary", "common_modes", "best_options_for_tourists",
                    "cost_notes", "practical_tips",
                ],
            },
        },
        "required": [
            "city_fit_summary",
            "best_areas_to_stay",
            "must_visit_places",
            "suggested_places_by_interest",
            "hotel_recommendations",
            "food_recommendations",
            "local_transport",
        ],
    }


def get_country_context_schema():
    return {
        "type": "object",
        "properties": {
            "best_season_climate": {
                "type": "object",
                "properties": {
                    "summary": {"type": "string"},
                    "best_months_to_visit": {"type": "array", "items": {"type": "string"}},
                    "months_to_avoid": {"type": "array", "items": {"type": "string"}},
                    "climate_notes": {"type": "string"},
                },
                "required": ["summary", "best_months_to_visit", "months_to_avoid", "climate_notes"],
            },
            "visa_entry": {
                "type": "object",
                "properties": {
                    "summary": {"type": "string"},
                    "visa_on_arrival": {"type": "string"},
                    "duration_allowed": {"type": "string"},
                    "key_requirements": {"type": "array", "items": {"type": "string"}},
                    "notes": {"type": "string"},
                },
                "required": ["summary", "visa_on_arrival", "duration_allowed", "key_requirements", "notes"],
            },
            "country_etiquette": {
                "type": "object",
                "properties": {
                    "people_and_social_norms": {"type": "string"},
                    "dress_code": {"type": "string"},
                    "dining_etiquette": {"type": "string"},
                    "religious_site_etiquette": {"type": "string"},
                    "dos": {"type": "array", "items": {"type": "string"}},
                    "donts": {"type": "array", "items": {"type": "string"}},
                },
                "required": [
                    "people_and_social_norms", "dress_code", "dining_etiquette",
                    "religious_site_etiquette", "dos", "donts",
                ],
            },
            "country_safety": {
                "type": "object",
                "properties": {
                    "overall_note": {"type": "string"},
                    "safe_areas": {"type": "array", "items": {"type": "string"}},
                    "caution_areas": {"type": "array", "items": {"type": "string"}},
                    "common_issues": {"type": "array", "items": {"type": "string"}},
                    "emergency_numbers": {"type": "string"},
                },
                "required": [
                    "overall_note", "safe_areas", "caution_areas",
                    "common_issues", "emergency_numbers",
                ],
            },
            "intercity_transport": {
                "type": "object",
                "properties": {
                    "summary": {"type": "string"},
                    "routes": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "from_city": {"type": "string"},
                                "to_city": {"type": "string"},
                                "options": {"type": "array", "items": {"type": "string"}},
                                "estimated_duration": {"type": "string"},
                                "cost_estimate": {"type": "string"},
                                "recommended_mode": {"type": "string"},
                            },
                            "required": [
                                "from_city", "to_city", "options",
                                "estimated_duration", "cost_estimate", "recommended_mode",
                            ],
                        },
                    },
                    "practical_tips": {"type": "array", "items": {"type": "string"}},
                },
                "required": ["summary", "routes", "practical_tips"],
            },
        },
        "required": [
            "best_season_climate",
            "visa_entry",
            "country_etiquette",
            "country_safety",
            "intercity_transport",
        ],
    }


def get_multi_city_schema(all_cities, country, user_interests):
    """
    Top-level schema: country_context + one city block per selected city.
    """
    cities_properties = {}
    for city in all_cities:
        cities_properties[city] = get_city_schema(city, country, user_interests)

    return {
        "type": "object",
        "properties": {
            "country_context": get_country_context_schema(),
            "city_intel": {
                "type": "object",
                "properties": cities_properties,
                "required": all_cities,
            },
        },
        "required": ["country_context", "city_intel"],
    }


# ---------------------------------------------------------------------------
# Inference helpers  (same as before)
# ---------------------------------------------------------------------------

def destination_text_is_valid(text, selected_city, selected_country):
    text = clean_text(text).lower()
    selected_city = clean_text(selected_city).lower()
    selected_country = clean_text(selected_country).lower()
    return selected_city in text or selected_country in text


def contains_placeholder_text(text):
    text = clean_text(text).lower()
    markers = [
        "local_identities_and_culture_influence_on_traveler_experience",
        "insert",
        "placeholder",
        "lorem ipsum",
    ]
    return any(marker in text for marker in markers)


def infer_place_category(name, text_blob):
    value = f"{clean_text(name)} {clean_text(text_blob)}".lower()
    if any(word in value for word in ["beach", "coast", "bay", "surf"]):
        return "Beach"
    if any(word in value for word in ["museum", "gallery", "exhibition"]):
        return "Museum"
    if any(word in value for word in ["opera", "bridge", "harbour", "harbor", "tower", "landmark"]):
        return "Landmark"
    if any(word in value for word in ["club", "bar", "pub", "nightlife", "music", "distillery"]):
        return "Nightlife"
    if any(word in value for word in ["market", "bazaar"]):
        return "Market"
    if any(word in value for word in ["park", "garden", "botanic", "trail", "reserve", "nature"]):
        return "Nature"
    if any(word in value for word in ["food", "restaurant", "cafe", "dining"]):
        return "Food"
    if any(word in value for word in ["shop", "shopping", "mall"]):
        return "Shopping"
    if any(word in value for word in ["stadium", "cricket", "football", "sports"]):
        return "Sports"
    return "Culture"


def infer_indoor_outdoor(name, text_blob):
    value = f"{clean_text(name)} {clean_text(text_blob)}".lower()
    if any(word in value for word in ["beach", "park", "garden", "walk", "harbour", "bridge"]):
        return "Outdoor"
    if any(word in value for word in ["museum", "gallery", "aquarium", "indoor", "theatre", "opera"]):
        return "Indoor"
    return "Mixed"


def classify_interest_fit(name, text_blob, user_interests):
    value = f"{clean_text(name)} {clean_text(text_blob)}".lower()
    for interest in user_interests:
        interest_lower = interest.lower()
        if interest_lower == "beaches" and any(word in value for word in ["beach", "coast", "surf"]):
            return interest
        if interest_lower == "nightlife" and any(word in value for word in ["bar", "club", "pub", "nightlife", "music", "party"]):
            return interest
        if interest_lower == "food" and any(word in value for word in ["restaurant", "cafe", "food", "dining"]):
            return interest
        if interest_lower == "culture" and any(word in value for word in ["opera", "museum", "gallery", "historic", "heritage"]):
            return interest
        if interest_lower == "nature" and any(word in value for word in ["park", "garden", "trail", "reserve"]):
            return interest
        if interest_lower == "shopping" and any(word in value for word in ["shop", "market", "mall"]):
            return interest
        if interest_lower == "museums" and any(word in value for word in ["museum", "gallery", "exhibition"]):
            return interest
        if interest_lower == "temples" and any(word in value for word in ["temple", "shrine"]):
            return interest
    return user_interests[0] if user_interests else "Culture"


# ---------------------------------------------------------------------------
# Per-city cleaning helpers
# ---------------------------------------------------------------------------

def clean_best_area_items(items):
    cleaned, seen = [], set()
    for item in items:
        area_name = normalize_whitespace(item.get("area_name"))
        if not area_name:
            continue
        key = area_name.lower()
        if key in seen:
            continue
        seen.add(key)
        cleaned.append({
            "area_name": area_name,
            "best_for": ensure_list(item.get("best_for")),
            "why_recommended": normalize_whitespace(item.get("why_recommended")),
            "pros": ensure_list(item.get("pros")),
            "cons": ensure_list(item.get("cons")),
            "budget_fit": normalize_whitespace(item.get("budget_fit")),
            "connectivity_notes": normalize_whitespace(item.get("connectivity_notes")),
            "traveler_sentiment": normalize_whitespace(item.get("traveler_sentiment")),
        })
    return cleaned[:4]


def clean_must_visit_items(items):
    cleaned, seen = [], set()
    for item in items:
        name = normalize_whitespace(item.get("name"))
        if not name:
            continue
        key = name.lower()
        if key in seen:
            continue
        seen.add(key)
        why_visit = normalize_whitespace(item.get("why_visit"))
        category = normalize_whitespace(item.get("category"))
        if category not in ALLOWED_PLACE_CATEGORIES:
            category = infer_place_category(name, why_visit)
        weather_sensitivity = normalize_whitespace(item.get("weather_sensitivity"))
        if weather_sensitivity not in ALLOWED_WEATHER_SENSITIVITY:
            weather_sensitivity = "Moderate"
        cleaned.append({
            "name": name,
            "category": category,
            "why_visit": why_visit,
            "best_for": ensure_list(item.get("best_for")),
            "time_needed": normalize_whitespace(item.get("time_needed")),
            "best_time_to_visit": normalize_whitespace(item.get("best_time_to_visit")),
            "weather_sensitivity": weather_sensitivity,
        })
    return cleaned[:6]


def clean_interest_items(items, parsed_profile):
    user_interests = parsed_profile.get("interests", [])
    cleaned, seen = [], set()
    for item in items:
        name = normalize_whitespace(item.get("name"))
        if not name:
            continue
        key = name.lower()
        if key in seen:
            continue
        seen.add(key)
        why_suggested = normalize_whitespace(item.get("why_suggested"))
        matched_interest = normalize_whitespace(item.get("matched_interest"))
        if matched_interest not in user_interests:
            matched_interest = classify_interest_fit(name, why_suggested, user_interests)
        indoor_outdoor = normalize_whitespace(item.get("indoor_outdoor"))
        if indoor_outdoor not in ["Indoor", "Outdoor", "Mixed"]:
            indoor_outdoor = infer_indoor_outdoor(name, why_suggested)
        cleaned.append({
            "name": name,
            "matched_interest": matched_interest,
            "why_suggested": why_suggested,
            "indoor_outdoor": indoor_outdoor,
            "time_needed": normalize_whitespace(item.get("time_needed")),
        })
    return cleaned[:6]


def clean_hotel_items(items):
    cleaned, seen = [], set()
    for item in items:
        hotel_name = normalize_whitespace(item.get("hotel_name"))
        if not hotel_name:
            continue
        key = hotel_name.lower()
        if key in seen:
            continue
        seen.add(key)
        cleaned.append({
            "hotel_name": hotel_name,
            "area": normalize_whitespace(item.get("area")),
            "hotel_category": normalize_whitespace(item.get("hotel_category")),
            "budget_fit": normalize_whitespace(item.get("budget_fit")),
            "why_it_matches": normalize_whitespace(item.get("why_it_matches")),
            "review_highlights": ensure_list(item.get("review_highlights")),
            "cautions": ensure_list(item.get("cautions")),
            "pricing_note": normalize_whitespace(item.get("pricing_note")),
            "location_logic": normalize_whitespace(item.get("location_logic")),
        })
    return cleaned[:5]


def clean_food_items(items, hotel_names):
    cleaned, seen = [], set()
    for item in items:
        place_name = normalize_whitespace(item.get("place_name"))
        if not place_name:
            continue
        if place_name.lower() in hotel_names:
            continue
        key = place_name.lower()
        if key in seen:
            continue
        seen.add(key)
        cleaned.append({
            "place_name": place_name,
            "category": normalize_whitespace(item.get("category")),
            "cuisine": normalize_whitespace(item.get("cuisine")),
            "area": normalize_whitespace(item.get("area")),
            "why_recommended": normalize_whitespace(item.get("why_recommended")),
            "signature_items": ensure_list(item.get("signature_items")),
            "price_level": normalize_whitespace(item.get("price_level")),
            "vibe": normalize_whitespace(item.get("vibe")),
            "notes": normalize_whitespace(item.get("notes")),
        })
    return cleaned[:5]


def clean_local_transport(transport):
    return {
        "summary": normalize_whitespace(transport.get("summary")),
        "common_modes": ensure_list(transport.get("common_modes")),
        "best_options_for_tourists": ensure_list(transport.get("best_options_for_tourists")),
        "cost_notes": ensure_list(transport.get("cost_notes")),
        "practical_tips": ensure_list(transport.get("practical_tips")),
    }


# ---------------------------------------------------------------------------
# City-level fallbacks
# ---------------------------------------------------------------------------

def apply_city_safe_fallbacks(city_data, city, country, parsed_profile, warnings):
    user_interests = parsed_profile.get("interests", [])

    city_fit = normalize_whitespace(city_data.get("city_fit_summary", ""))
    if not city_fit or contains_placeholder_text(city_fit):
        city_data["city_fit_summary"] = f"{city} is a popular destination in {country} known for its unique attractions and local experiences."
        warnings.append(f"[{city}] Added fallback city_fit_summary.")

    best_areas = clean_best_area_items(city_data.get("best_areas_to_stay", []))
    must_visit = clean_must_visit_items(city_data.get("must_visit_places", []))
    by_interest = clean_interest_items(city_data.get("suggested_places_by_interest", []), parsed_profile)
    hotels = clean_hotel_items(city_data.get("hotel_recommendations", []))
    hotel_names = {item["hotel_name"].lower() for item in hotels}
    food = clean_food_items(city_data.get("food_recommendations", []), hotel_names)
    transport = clean_local_transport(city_data.get("local_transport", {}))

    if not must_visit:
        must_visit = [{
            "name": f"{city} city centre",
            "category": "Landmark",
            "why_visit": f"The central areas of {city} are home to its best-known landmarks and public spaces.",
            "best_for": ["Sightseeing"],
            "time_needed": "2-4 hours",
            "best_time_to_visit": "Morning or late afternoon",
            "weather_sensitivity": "Moderate",
        }]
        warnings.append(f"[{city}] Added fallback must_visit_places entry.")

    if not by_interest and user_interests:
        fallback_interest = user_interests[0]
        by_interest = [{
            "name": f"{city} {fallback_interest.lower()} area",
            "matched_interest": fallback_interest,
            "why_suggested": f"A suggestion aligned with {fallback_interest.lower()} experiences in {city}.",
            "indoor_outdoor": "Mixed",
            "time_needed": "2-3 hours",
        }]
        warnings.append(f"[{city}] Added fallback suggested_places_by_interest entry.")

    if not transport["summary"]:
        transport["summary"] = f"{city} has standard local transport options including taxis and ride-hailing services."
        warnings.append(f"[{city}] Added fallback local transport summary.")

    city_data["best_areas_to_stay"] = best_areas
    city_data["must_visit_places"] = must_visit
    city_data["suggested_places_by_interest"] = by_interest
    city_data["hotel_recommendations"] = hotels
    city_data["food_recommendations"] = food
    city_data["local_transport"] = transport

    return city_data


# ---------------------------------------------------------------------------
# Country-level fallbacks
# ---------------------------------------------------------------------------

def apply_country_safe_fallbacks(country_context, country, selected_cities, warnings):
    season = country_context.get("best_season_climate", {})
    if not normalize_whitespace(season.get("summary", "")):
        country_context["best_season_climate"] = {
            "summary": f"{country} generally has a tropical or subtropical climate. Check specific seasonal conditions before travel.",
            "best_months_to_visit": ["November", "December", "January", "February"],
            "months_to_avoid": [],
            "climate_notes": "Weather can vary significantly by region and season.",
        }
        warnings.append(f"[{country}] Added fallback best_season_climate.")

    visa = country_context.get("visa_entry", {})
    if not normalize_whitespace(visa.get("summary", "")):
        country_context["visa_entry"] = {
            "summary": f"Check current visa requirements for {country} based on your nationality before travel.",
            "visa_on_arrival": "Check with official embassy or consulate",
            "duration_allowed": "Varies by nationality",
            "key_requirements": ["Valid passport", "Return ticket", "Proof of funds"],
            "notes": "Always verify with official government sources before travelling.",
        }
        warnings.append(f"[{country}] Added fallback visa_entry.")

    etiquette = country_context.get("country_etiquette", {})
    if not normalize_whitespace(etiquette.get("people_and_social_norms", "")):
        country_context["country_etiquette"] = {
            "people_and_social_norms": f"Locals in {country} are generally welcoming to tourists. Be respectful of local customs.",
            "dress_code": "Dress modestly when visiting temples or religious sites.",
            "dining_etiquette": "Follow local dining customs and be respectful at meal times.",
            "religious_site_etiquette": "Remove shoes before entering temples. Dress modestly and keep noise low.",
            "dos": ["Greet locals politely", "Respect religious sites", "Follow local rules"],
            "donts": ["Avoid public displays of disrespect", "Do not litter", "Do not touch religious objects without permission"],
        }
        warnings.append(f"[{country}] Added fallback country_etiquette.")

    safety = country_context.get("country_safety", {})
    if not normalize_whitespace(safety.get("overall_note", "")):
        country_context["country_safety"] = {
            "overall_note": f"{country} is generally safe for tourists. Exercise normal caution as you would in any travel destination.",
            "safe_areas": ["Tourist zones and city centres are generally well-monitored."],
            "caution_areas": ["Avoid poorly lit or isolated areas at night."],
            "common_issues": ["Petty theft in crowded areas", "Taxi overcharging"],
            "emergency_numbers": "Check local emergency numbers before travel.",
        }
        warnings.append(f"[{country}] Added fallback country_safety.")

    intercity = country_context.get("intercity_transport", {})
    if not normalize_whitespace(intercity.get("summary", "")):
        routes = []
        for i in range(len(selected_cities) - 1):
            routes.append({
                "from_city": selected_cities[i],
                "to_city": selected_cities[i + 1],
                "options": ["Domestic flight", "Bus", "Train"],
                "estimated_duration": "Varies - check current schedules",
                "cost_estimate": "Varies by mode and booking time",
                "recommended_mode": "Domestic flight for long distances, bus for shorter routes",
            })
        country_context["intercity_transport"] = {
            "summary": f"Travel between {', '.join(selected_cities)} in {country} is possible via multiple transport modes.",
            "routes": routes,
            "practical_tips": [
                "Book transport in advance especially during peak season.",
                "Compare bus, train, and flight options for cost and time.",
            ],
        }
        warnings.append(f"[{country}] Added fallback intercity_transport.")

    return country_context


# ---------------------------------------------------------------------------
# Consistency validation
# ---------------------------------------------------------------------------

def validate_multi_city_consistency(report, all_cities, country):
    issues = []
    city_intel = report.get("city_intel", {})
    for city in all_cities:
        if city not in city_intel:
            issues.append(f"city_intel is missing a block for selected city: {city}.")
        else:
            city_block = city_intel[city]
            if not city_block.get("must_visit_places"):
                issues.append(f"[{city}] must_visit_places is empty.")
            if not city_block.get("hotel_recommendations"):
                issues.append(f"[{city}] hotel_recommendations is empty.")
            if not city_block.get("food_recommendations"):
                issues.append(f"[{city}] food_recommendations is empty.")
    if not report.get("country_context"):
        issues.append("country_context block is missing from the report.")
    return issues


# ---------------------------------------------------------------------------
# Output cleaner
# ---------------------------------------------------------------------------

def clean_multi_city_output(data, parsed_profile, selected_location, weather_summary, live_research):
    warnings = []
    country = parsed_profile.get("destination_country", clean_text(selected_location.get("country")))
    all_cities = live_research.get("all_cities", [])
    selected_cities = parsed_profile.get("selected_cities", [])

    # Clean country context
    country_context = data.get("country_context", {})
    country_context = apply_country_safe_fallbacks(country_context, country, selected_cities or all_cities, warnings)
    data["country_context"] = country_context

    # Clean city intel for each selected city
    city_intel = data.get("city_intel", {})
    cleaned_city_intel = {}
    for city in all_cities:
        city_data = city_intel.get(city, {})
        city_data = apply_city_safe_fallbacks(city_data, city, country, parsed_profile, warnings)
        cleaned_city_intel[city] = city_data
    data["city_intel"] = cleaned_city_intel

    combined_output = {
        "destination_context": {
            "country": country,
            "all_cities": all_cities,
            "anchor_city": clean_text(selected_location.get("name")),
            "timezone": clean_text(selected_location.get("timezone")),
            "latitude": selected_location.get("latitude"),
            "longitude": selected_location.get("longitude"),
        },
        "traveler_profile": parsed_profile,
        "weather_summary": weather_summary,
        "research_summary": {
            "country_web_results": int(live_research.get("source_counts", {}).get("country_web_results", 0)),
            "city_web_results": int(live_research.get("source_counts", {}).get("city_web_results", 0)),
            "city_youtube_results": int(live_research.get("source_counts", {}).get("city_youtube_results", 0)),
        },
        "final_report": {
            "country_context": data.get("country_context", {}),
            "city_intel": data.get("city_intel", {}),
        },
    }

    consistency_issues = validate_multi_city_consistency(combined_output["final_report"], all_cities, country)
    return combined_output, warnings, consistency_issues


# ---------------------------------------------------------------------------
# Ollama generation  (multi-city aware)
# ---------------------------------------------------------------------------

def get_research_from_ollama(parsed_profile, selected_location, weather_summary, live_research):
    country = parsed_profile.get("destination_country", clean_text(selected_location.get("country")))
    all_cities = live_research.get("all_cities", [])
    user_interests = parsed_profile.get("interests", []) or ALLOWED_INTERESTS[:2]

    schema = get_multi_city_schema(all_cities, country, user_interests)

    cities_instruction = ", ".join(all_cities)
    intercity_pairs = ""
    if len(all_cities) >= 2:
        pairs = [f"{all_cities[i]} to {all_cities[i+1]}" for i in range(len(all_cities)-1)]
        intercity_pairs = " and ".join(pairs)

    prompt = (
        "You are a multi-city travel research synthesis agent.\n"
        "Return only valid JSON matching the provided schema.\n"
        "Do not include markdown. Do not include any explanation outside JSON.\n"
        "MANDATORY: Every city in city_intel must have its own complete, city-specific data block.\n"
        "MANDATORY LANGUAGE RULES:\n"
        "- The entire response must be written in English only.\n"
        "- Every JSON field value must be in English only.\n"
        "- Translate any non-English evidence into English before writing the JSON.\n\n"
        f"Selected country: {country}\n"
        f"Selected cities for this trip: {cities_instruction}\n"
        f"Traveler interests: {json.dumps(user_interests)}\n"
        f"Hotel preference: {parsed_profile.get('hotel_category', '')}\n"
        f"Food preference: {parsed_profile.get('food_preference', '')}\n"
        f"Budget: {parsed_profile.get('budget', '')}\n"
        f"Trip days: {parsed_profile.get('days', '')}\n\n"
        "RULES FOR city_intel:\n"
        f"- You MUST generate a separate complete block for EACH of these cities: {cities_instruction}\n"
        "- Each city's best_areas_to_stay, must_visit_places, suggested_places_by_interest, hotel_recommendations, food_recommendations, and local_transport must be specific to THAT city only.\n"
        "- Do NOT mix recommendations between cities.\n"
        "- Hotel recommendations must match the traveler's hotel_category preference and budget.\n"
        "- Food recommendations must match the traveler's food_preference (veg/non-veg/both) and must include the specific restaurant or food spot name.\n"
        "- suggested_places_by_interest.matched_interest must exactly match one of the traveler's interests.\n\n"
        "RULES FOR country_context:\n"
        "- best_season_climate must reflect the actual climate of the country and best travel months.\n"
        "- visa_entry must reflect current general entry requirements.\n"
        "- intercity_transport.routes must cover travel between the selected cities.\n"
        f"- Specifically include route details for: {intercity_pairs if intercity_pairs else cities_instruction}\n\n"
        f"Traveler profile:\n{json.dumps(parsed_profile, indent=2)}\n\n"
        f"Anchor location details:\n{json.dumps(selected_location, indent=2)}\n\n"
        f"Weather summary (for anchor city):\n{json.dumps(weather_summary, indent=2)}\n\n"
        f"City-specific live research:\n{json.dumps(live_research.get('city_research', {}), indent=2)}\n\n"
        f"Country-level live research:\n{json.dumps(live_research.get('country_research', {}), indent=2)}\n\n"
        f"JSON Schema:\n{json.dumps(schema, indent=2)}\n"
    )

    payload = {
        "model": OLLAMA_MODEL,
        "prompt": prompt,
        "stream": False,
        "format": schema,
    }

    data = safe_post_json(OLLAMA_URL, payload, timeout=300)
    response_text = data.get("response", "").strip()
    if not response_text:
        raise ValueError("Ollama returned an empty response.")

    parsed = json.loads(response_text)
    return clean_multi_city_output(parsed, parsed_profile, selected_location, weather_summary, live_research)
