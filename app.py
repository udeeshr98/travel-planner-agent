import json
import re
import requests
import streamlit as st


st.set_page_config(page_title="Travel Planner Agent", page_icon="✈️", layout="wide")

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


def inject_custom_css():
    st.markdown(
        """
        <style>
        .block-container {
            padding-top: 1.5rem;
            padding-bottom: 3rem;
            max-width: 1400px;
        }

        .app-hero {
            padding: 1.2rem 1.4rem;
            border-radius: 18px;
            background: linear-gradient(135deg, #0f172a 0%, #1e293b 55%, #334155 100%);
            color: white;
            margin-bottom: 1rem;
            border: 1px solid rgba(255,255,255,0.08);
        }

        .app-hero h1 {
            margin: 0 0 0.35rem 0;
            font-size: 2rem;
            line-height: 1.1;
        }

        .app-hero p {
            margin: 0;
            color: rgba(255,255,255,0.88);
            font-size: 0.98rem;
        }

        .section-title {
            font-size: 1.05rem;
            font-weight: 700;
            margin: 0.4rem 0 0.8rem 0;
        }

        .mini-note {
            color: #64748b;
            font-size: 0.9rem;
            margin-top: -0.25rem;
            margin-bottom: 0.8rem;
        }

        .summary-card {
            border: 1px solid rgba(148, 163, 184, 0.25);
            border-radius: 18px;
            padding: 1rem 1rem 0.85rem 1rem;
            background: linear-gradient(180deg, rgba(248,250,252,0.95), rgba(241,245,249,0.92));
            min-height: 142px;
            box-shadow: 0 10px 28px rgba(15, 23, 42, 0.05);
        }

        .summary-card .label {
            font-size: 0.82rem;
            color: #64748b;
            text-transform: uppercase;
            letter-spacing: 0.04em;
            margin-bottom: 0.35rem;
            font-weight: 700;
        }

        .summary-card .value {
            font-size: 1.35rem;
            font-weight: 800;
            color: #0f172a;
            line-height: 1.2;
            margin-bottom: 0.4rem;
        }

        .summary-card .sub {
            font-size: 0.92rem;
            color: #475569;
            line-height: 1.45;
        }

        .pill {
            display: inline-block;
            padding: 0.28rem 0.58rem;
            border-radius: 999px;
            background: #e2e8f0;
            color: #0f172a;
            font-size: 0.78rem;
            font-weight: 700;
            margin-right: 0.35rem;
            margin-bottom: 0.35rem;
        }

        .recommendation-card {
            border: 1px solid rgba(148, 163, 184, 0.25);
            border-radius: 18px;
            padding: 1rem;
            background: white;
            box-shadow: 0 8px 22px rgba(15, 23, 42, 0.04);
            margin-bottom: 0.9rem;
        }

        .recommendation-card h4 {
            margin: 0 0 0.4rem 0;
            font-size: 1.08rem;
            color: #0f172a;
        }

        .recommendation-meta {
            color: #475569;
            font-size: 0.9rem;
            margin-bottom: 0.55rem;
        }

        .recommendation-body {
            color: #334155;
            font-size: 0.94rem;
            line-height: 1.55;
        }

        .info-banner {
            border: 1px solid rgba(148, 163, 184, 0.22);
            background: #f8fafc;
            border-radius: 16px;
            padding: 0.9rem 1rem;
            margin-bottom: 0.85rem;
        }

        .source-link a {
            text-decoration: none;
        }

        .muted {
            color: #64748b;
            font-size: 0.9rem;
        }

        .divider-space {
            margin-top: 0.3rem;
            margin-bottom: 0.8rem;
        }

        .stTabs [data-baseweb="tab-list"] {
            gap: 0.45rem;
        }

        .stTabs [data-baseweb="tab"] {
            border-radius: 12px;
            padding: 0.6rem 1rem;
        }

        .stButton > button {
            border-radius: 12px;
            font-weight: 600;
        }

        .source-chip {
            display: inline-block;
            padding: 0.28rem 0.55rem;
            border-radius: 999px;
            background: #eef2ff;
            color: #3730a3;
            font-size: 0.76rem;
            font-weight: 700;
            margin-right: 0.35rem;
            margin-bottom: 0.35rem;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def safe_get_json(url, params=None, timeout=30):
    response = requests.get(url, params=params, timeout=timeout)
    response.raise_for_status()
    return response.json()


def safe_post_json(url, payload, timeout=60):
    response = requests.post(url, json=payload, timeout=timeout)
    response.raise_for_status()
    return response.json()


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


def get_location_options(city_or_region):
    url = "https://geocoding-api.open-meteo.com/v1/search"
    params = {"name": city_or_region, "count": 5, "language": "en", "format": "json"}
    data = safe_get_json(url, params=params, timeout=30)
    return data.get("results", [])


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
        "activity_suitability": get_activity_suitability(weather_code, current_temp, wind_speed)
    }


def serpapi_search(query, num_results=3):
    url = "https://serpapi.com/search.json"
    params = {"engine": "google", "q": query, "api_key": SERPAPI_API_KEY, "num": num_results}
    data = safe_get_json(url, params=params, timeout=60)
    results = []
    for item in data.get("organic_results", [])[:num_results]:
        results.append({
            "title": item.get("title", ""),
            "link": item.get("link", ""),
            "snippet": item.get("snippet", "")
        })
    return results


def youtube_search(query, max_results=2):
    url = "https://www.googleapis.com/youtube/v3/search"
    params = {
        "key": YOUTUBE_API_KEY,
        "part": "snippet",
        "q": query,
        "type": "video",
        "maxResults": max_results
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
            "video_url": f"https://www.youtube.com/watch?v={video_id}" if video_id else ""
        })
    return results


def build_live_research_context(parsed_profile, selected_location):
    destination = f"{parsed_profile['destination_city_region']}, {parsed_profile['destination_country']}"
    interests_text = ", ".join(parsed_profile.get("interests", []))
    hotel_category = parsed_profile.get("hotel_category", "")
    food_preference = parsed_profile.get("food_preference", "")

    search_plan = {
        "best_areas_to_stay": [
            f"best areas to stay in {destination}",
            f"{destination} neighborhoods for tourists"
        ],
        "must_visit_places": [
            f"must visit places in {destination}",
            f"top attractions in {destination}"
        ],
        "suggested_places_by_interest": [
            f"best {interests_text} in {destination}",
            f"{destination} hidden gems {interests_text}"
        ],
        "hotels": [
            f"best {hotel_category} hotels in {destination}",
            f"where to stay in {destination} hotels {parsed_profile['budget']}"
        ],
        "food": [
            f"best {food_preference} food in {destination}",
            f"top restaurants in {destination} {food_preference}"
        ],
        "transport": [
            f"how to get around {destination}",
            f"{destination} public transport for tourists"
        ],
        "culture": [
            f"{destination} culture etiquette for tourists"
        ],
        "safety": [
            f"{destination} tourist safety tips",
            f"{destination} areas to avoid tourists"
        ]
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
        f"{destination} where to stay",
        f"{destination} food guide"
    ]
    youtube_results = []
    for query in youtube_queries:
        youtube_results.extend(youtube_search(query, max_results=2))
    youtube_results = dedupe_results(youtube_results)[:6]

    return {
        "destination": destination,
        "selected_location": {
            "name": clean_text(selected_location.get("name")),
            "country": clean_text(selected_location.get("country")),
            "latitude": selected_location.get("latitude"),
            "longitude": selected_location.get("longitude"),
            "timezone": clean_text(selected_location.get("timezone"))
        },
        "web_research": web_research,
        "youtube_research": youtube_results,
        "source_counts": {
            "web_results_count": total_web_results,
            "youtube_results_count": len(youtube_results)
        }
    }


def get_research_schema(selected_city, selected_country, user_interests):
    return {
        "type": "object",
        "properties": {
            "destination_guardrails": {
                "type": "object",
                "properties": {
                    "selected_city": {"type": "string", "const": selected_city},
                    "selected_country": {"type": "string", "const": selected_country}
                },
                "required": ["selected_city", "selected_country"]
            },
            "destination_snapshot": {
                "type": "object",
                "properties": {
                    "summary": {"type": "string"},
                    "traveler_fit": {"type": "string"},
                    "key_characteristics": {
                        "type": "array",
                        "items": {"type": "string"},
                        "minItems": 3,
                        "maxItems": 5
                    }
                },
                "required": ["summary", "traveler_fit", "key_characteristics"]
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
                        "traveler_sentiment": {"type": "string", "enum": ALLOWED_TRAVELER_SENTIMENT}
                    },
                    "required": [
                        "area_name", "best_for", "why_recommended", "pros", "cons",
                        "budget_fit", "connectivity_notes", "traveler_sentiment"
                    ]
                }
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
                        "weather_sensitivity": {"type": "string", "enum": ALLOWED_WEATHER_SENSITIVITY}
                    },
                    "required": [
                        "name", "category", "why_visit", "best_for",
                        "time_needed", "best_time_to_visit", "weather_sensitivity"
                    ]
                }
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
                        "time_needed": {"type": "string"}
                    },
                    "required": [
                        "name", "matched_interest", "why_suggested",
                        "indoor_outdoor", "time_needed"
                    ]
                }
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
                        "location_logic": {"type": "string"}
                    },
                    "required": [
                        "hotel_name", "area", "hotel_category", "budget_fit",
                        "why_it_matches", "review_highlights", "cautions",
                        "pricing_note", "location_logic"
                    ]
                }
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
                        "notes": {"type": "string"}
                    },
                    "required": [
                        "place_name", "category", "cuisine", "area",
                        "why_recommended", "signature_items", "price_level",
                        "vibe", "notes"
                    ]
                }
            },
            "weather_climate": {
                "type": "object",
                "properties": {
                    "summary": {"type": "string"},
                    "comfort_level": {"type": "string"},
                    "travel_impact": {"type": "string"},
                    "planning_advice": {"type": "array", "items": {"type": "string"}}
                },
                "required": ["summary", "comfort_level", "travel_impact", "planning_advice"]
            },
            "local_transport": {
                "type": "object",
                "properties": {
                    "summary": {"type": "string"},
                    "common_modes": {"type": "array", "items": {"type": "string"}},
                    "best_options_for_tourists": {"type": "array", "items": {"type": "string"}},
                    "cost_notes": {"type": "array", "items": {"type": "string"}},
                    "area_connectivity": {"type": "string"},
                    "practical_tips": {"type": "array", "items": {"type": "string"}}
                },
                "required": [
                    "summary", "common_modes", "best_options_for_tourists",
                    "cost_notes", "area_connectivity", "practical_tips"
                ]
            },
            "culture_etiquette": {
                "type": "object",
                "properties": {
                    "people_and_social_norms": {"type": "string"},
                    "dress_code": {"type": "string"},
                    "dining_etiquette": {"type": "string"},
                    "religious_site_etiquette": {"type": "string"},
                    "dos": {"type": "array", "items": {"type": "string"}},
                    "donts": {"type": "array", "items": {"type": "string"}}
                },
                "required": [
                    "people_and_social_norms", "dress_code", "dining_etiquette",
                    "religious_site_etiquette", "dos", "donts"
                ]
            },
            "safety_and_cautions": {
                "type": "object",
                "properties": {
                    "overall_note": {"type": "string"},
                    "safe_areas": {"type": "array", "items": {"type": "string"}},
                    "caution_areas": {"type": "array", "items": {"type": "string"}},
                    "common_issues": {"type": "array", "items": {"type": "string"}},
                    "transport_cautions": {"type": "array", "items": {"type": "string"}},
                    "food_hygiene_notes": {"type": "array", "items": {"type": "string"}}
                },
                "required": [
                    "overall_note", "safe_areas", "caution_areas",
                    "common_issues", "transport_cautions", "food_hygiene_notes"
                ]
            },
            "planning_tradeoffs": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "topic": {"type": "string"},
                        "tradeoff": {"type": "string"},
                        "who_should_choose_this": {"type": "string"}
                    },
                    "required": ["topic", "tradeoff", "who_should_choose_this"]
                }
            }
        },
        "required": [
            "destination_guardrails", "destination_snapshot", "best_areas_to_stay",
            "must_visit_places", "suggested_places_by_interest", "hotel_recommendations",
            "food_recommendations", "weather_climate", "local_transport",
            "culture_etiquette", "safety_and_cautions", "planning_tradeoffs"
        ]
    }


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
        "lorem ipsum"
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
        if interest_lower == "beaches" and any(word in value for word in ["beach", "bondi", "manly", "coast", "surf"]):
            return interest
        if interest_lower == "nightlife" and any(word in value for word in ["bar", "club", "pub", "nightlife", "music", "late-night", "distillery", "party"]):
            return interest
        if interest_lower == "food" and any(word in value for word in ["restaurant", "cafe", "food", "vegan", "vegetarian", "dining"]):
            return interest
        if interest_lower == "culture" and any(word in value for word in ["opera", "museum", "gallery", "historic", "heritage", "theatre"]):
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


def validate_destination_consistency(report, selected_location):
    issues = []
    selected_city = clean_text(selected_location.get("name"))
    selected_country = clean_text(selected_location.get("country"))

    guardrails = report.get("destination_guardrails", {})
    if clean_text(guardrails.get("selected_city")) != selected_city:
        issues.append("destination_guardrails.selected_city does not match selected destination.")
    if clean_text(guardrails.get("selected_country")) != selected_country:
        issues.append("destination_guardrails.selected_country does not match selected country.")

    snapshot = report.get("destination_snapshot", {})
    if not destination_text_is_valid(snapshot.get("summary", ""), selected_city, selected_country):
        issues.append("destination_snapshot.summary does not mention the selected city or country.")
    if not destination_text_is_valid(snapshot.get("traveler_fit", ""), selected_city, selected_country):
        issues.append("destination_snapshot.traveler_fit does not mention the selected city or country.")
    if len(ensure_list(snapshot.get("key_characteristics"))) < 3:
        issues.append("destination_snapshot.key_characteristics has fewer than 3 items.")

    return issues


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
            "traveler_sentiment": normalize_whitespace(item.get("traveler_sentiment"))
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
            "weather_sensitivity": weather_sensitivity
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
            "time_needed": normalize_whitespace(item.get("time_needed"))
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
            "location_logic": normalize_whitespace(item.get("location_logic"))
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
            "notes": normalize_whitespace(item.get("notes"))
        })
    return cleaned[:5]


def apply_destination_safe_fallbacks(data, parsed_profile, selected_location, weather_summary, live_research):
    warnings = []
    selected_city = clean_text(selected_location.get("name"))
    selected_country = clean_text(selected_location.get("country"))
    user_interests = parsed_profile.get("interests", [])

    snapshot = data.get("destination_snapshot", {})
    summary = normalize_whitespace(snapshot.get("summary"))
    traveler_fit = normalize_whitespace(snapshot.get("traveler_fit"))
    key_characteristics = ensure_list(snapshot.get("key_characteristics"))

    if not summary or contains_placeholder_text(summary) or not destination_text_is_valid(summary, selected_city, selected_country):
        summary = (
            f"{selected_city}, {selected_country} is a major city destination with iconic sights, diverse neighborhoods, "
            f"and a mix of coastal and urban experiences that work well for a short leisure trip."
        )
        warnings.append("Replaced weak destination summary with destination-safe fallback.")

    if not traveler_fit or contains_placeholder_text(traveler_fit) or not destination_text_is_valid(traveler_fit, selected_city, selected_country):
        traveler_fit = (
            f"For this {parsed_profile.get('days')} day trip, {selected_city} fits travelers seeking "
            f"{', '.join(user_interests).lower()} experiences on a {parsed_profile.get('budget', '').lower()} budget."
        )
        warnings.append("Replaced weak traveler_fit with destination-safe fallback.")

    cleaned_characteristics = []
    for item in key_characteristics:
        item = normalize_whitespace(item)
        if item and not contains_placeholder_text(item):
            cleaned_characteristics.append(item)

    if len(cleaned_characteristics) < 3:
        cleaned_characteristics = [
            f"{selected_city} combines waterfront attractions, major landmarks, and varied neighborhoods.",
            f"Current conditions suggest {weather_summary.get('activity_suitability', '').lower()}.",
            f"This plan is tuned to {', '.join(user_interests).lower()} preferences."
        ]
        warnings.append("Rebuilt destination key_characteristics with fallback values.")

    data["destination_snapshot"] = {
        "summary": summary,
        "traveler_fit": traveler_fit,
        "key_characteristics": cleaned_characteristics[:5]
    }

    best_areas = clean_best_area_items(data.get("best_areas_to_stay", []))
    must_visit = clean_must_visit_items(data.get("must_visit_places", []))
    by_interest = clean_interest_items(data.get("suggested_places_by_interest", []), parsed_profile)
    hotels = clean_hotel_items(data.get("hotel_recommendations", []))
    hotel_names = {item["hotel_name"].lower() for item in hotels}
    food_items = clean_food_items(data.get("food_recommendations", []), hotel_names)

    if not must_visit:
        must_visit = [{
            "name": selected_city,
            "category": "Landmark",
            "why_visit": f"Central areas of {selected_city} provide easy access to its best-known landmarks and public spaces.",
            "best_for": ["Sightseeing"],
            "time_needed": "2-4 hours",
            "best_time_to_visit": "Morning or late afternoon",
            "weather_sensitivity": "Moderate"
        }]
        warnings.append("Added fallback must_visit_places entry.")

    if not by_interest and user_interests:
        fallback_interest = user_interests[0]
        by_interest = [{
            "name": f"{selected_city} nightlife district",
            "matched_interest": fallback_interest,
            "why_suggested": f"A destination-relevant suggestion aligned with {fallback_interest.lower()} preferences.",
            "indoor_outdoor": "Mixed",
            "time_needed": "2-3 hours"
        }]
        warnings.append("Added fallback suggested_places_by_interest entry.")

    data["best_areas_to_stay"] = best_areas
    data["must_visit_places"] = must_visit
    data["suggested_places_by_interest"] = by_interest
    data["hotel_recommendations"] = hotels
    data["food_recommendations"] = food_items

    weather_block = data.get("weather_climate", {})
    weather_block["summary"] = normalize_whitespace(weather_block.get("summary"))
    weather_block["comfort_level"] = normalize_whitespace(weather_block.get("comfort_level"))
    weather_block["travel_impact"] = normalize_whitespace(weather_block.get("travel_impact"))
    weather_block["planning_advice"] = ensure_list(weather_block.get("planning_advice"))

    if not weather_block["summary"] or contains_placeholder_text(weather_block["summary"]):
        weather_block["summary"] = (
            f"Current conditions in {selected_city} are {weather_summary.get('weather_description', '').lower()} "
            f"with temperatures around {weather_summary.get('temperature_now_c')}°C."
        )
        warnings.append("Replaced weak weather summary with actual weather fallback.")
    data["weather_climate"] = weather_block

    transport = data.get("local_transport", {})
    transport["summary"] = normalize_whitespace(transport.get("summary"))
    transport["common_modes"] = ensure_list(transport.get("common_modes"))
    transport["best_options_for_tourists"] = ensure_list(transport.get("best_options_for_tourists"))
    transport["cost_notes"] = ensure_list(transport.get("cost_notes"))
    transport["area_connectivity"] = normalize_whitespace(transport.get("area_connectivity"))
    transport["practical_tips"] = ensure_list(transport.get("practical_tips"))

    safe_cost_notes = []
    for note in transport["cost_notes"]:
        if "free" in note.lower() and "ferr" in note.lower():
            continue
        safe_cost_notes.append(note)
    transport["cost_notes"] = safe_cost_notes

    if not transport["summary"]:
        transport["summary"] = f"{selected_city} has a well-connected public transport network with trains, buses, ferries, and light rail."
        warnings.append("Added fallback local transport summary.")

    if not transport["cost_notes"]:
        transport["cost_notes"] = [
            "Public transport costs vary by route, distance, and payment method.",
            "Ferries are scenic but typically paid rather than free."
        ]
        warnings.append("Replaced unsupported transport cost notes with safer fallback.")

    data["local_transport"] = transport

    culture = data.get("culture_etiquette", {})
    culture["people_and_social_norms"] = normalize_whitespace(culture.get("people_and_social_norms"))
    culture["dress_code"] = normalize_whitespace(culture.get("dress_code"))
    culture["dining_etiquette"] = normalize_whitespace(culture.get("dining_etiquette"))
    culture["religious_site_etiquette"] = normalize_whitespace(culture.get("religious_site_etiquette"))
    culture["dos"] = ensure_list(culture.get("dos"))
    culture["donts"] = ensure_list(culture.get("donts"))

    if not culture["religious_site_etiquette"]:
        culture["religious_site_etiquette"] = "Be respectful, keep noise low, and follow any local dress or photography guidance at religious sites."
        warnings.append("Added fallback religious_site_etiquette guidance.")
    data["culture_etiquette"] = culture

    safety = data.get("safety_and_cautions", {})
    safety["overall_note"] = normalize_whitespace(safety.get("overall_note"))
    safety["safe_areas"] = ensure_list(safety.get("safe_areas"))
    safety["caution_areas"] = ensure_list(safety.get("caution_areas"))
    safety["common_issues"] = ensure_list(safety.get("common_issues"))
    safety["transport_cautions"] = ensure_list(safety.get("transport_cautions"))
    safety["food_hygiene_notes"] = ensure_list(safety.get("food_hygiene_notes"))

    if "always some level of risk" in safety["overall_note"].lower():
        safety["overall_note"] = f"{selected_city} is generally safe for visitors, with normal care recommended in busy urban areas."
        warnings.append("Softened generic alarmist safety wording.")
    data["safety_and_cautions"] = safety

    tradeoffs = []
    for item in data.get("planning_tradeoffs", []):
        topic = normalize_whitespace(item.get("topic"))
        tradeoff = normalize_whitespace(item.get("tradeoff"))
        who = normalize_whitespace(item.get("who_should_choose_this"))
        if topic and tradeoff and who:
            tradeoffs.append({
                "topic": topic,
                "tradeoff": tradeoff,
                "who_should_choose_this": who
            })
    data["planning_tradeoffs"] = tradeoffs[:4]

    return data, warnings


def clean_research_output(data, parsed_profile, selected_location, weather_summary, live_research):
    warnings = []
    selected_city = clean_text(selected_location.get("name"))
    selected_country = clean_text(selected_location.get("country"))

    data["destination_guardrails"] = {
        "selected_city": selected_city,
        "selected_country": selected_country
    }

    data, fallback_warnings = apply_destination_safe_fallbacks(
        data, parsed_profile, selected_location, weather_summary, live_research
    )
    warnings.extend(fallback_warnings)

    combined_output = {
        "destination_context": {
            "city": selected_city,
            "country": selected_country,
            "timezone": clean_text(selected_location.get("timezone")),
            "latitude": selected_location.get("latitude"),
            "longitude": selected_location.get("longitude")
        },
        "traveler_profile": parsed_profile,
        "weather_summary": weather_summary,
        "research_summary": {
            "web_results_count": int(live_research.get("source_counts", {}).get("web_results_count", 0)),
            "youtube_results_count": int(live_research.get("source_counts", {}).get("youtube_results_count", 0)),
            "top_web_sources": {
                section: results[:2]
                for section, results in live_research.get("web_research", {}).items()
            },
            "top_youtube_sources": live_research.get("youtube_research", [])[:3]
        },
        "final_report": {
            "destination_guardrails": data["destination_guardrails"],
            "destination_snapshot": data.get("destination_snapshot", {}),
            "best_areas_to_stay": data.get("best_areas_to_stay", []),
            "must_visit_places": data.get("must_visit_places", []),
            "suggested_places_by_interest": data.get("suggested_places_by_interest", []),
            "hotel_recommendations": data.get("hotel_recommendations", []),
            "food_recommendations": data.get("food_recommendations", []),
            "weather_climate": data.get("weather_climate", {}),
            "local_transport": data.get("local_transport", {}),
            "culture_etiquette": data.get("culture_etiquette", {}),
            "safety_and_cautions": data.get("safety_and_cautions", {}),
            "planning_tradeoffs": data.get("planning_tradeoffs", [])
        }
    }

    consistency_issues = validate_destination_consistency(combined_output["final_report"], selected_location)
    return combined_output, warnings, consistency_issues


def get_research_from_ollama(parsed_profile, selected_location, weather_summary, live_research):
    selected_city = clean_text(selected_location.get("name"))
    selected_country = clean_text(selected_location.get("country"))
    user_interests = parsed_profile.get("interests", []) or ALLOWED_INTERESTS[:2]
    schema = get_research_schema(selected_city, selected_country, user_interests)

    prompt = (
        "You are a travel research synthesis agent.\n"
        "Return only valid JSON matching the provided schema.\n"
        "Do not include markdown.\n"
        "Do not include explanation outside JSON.\n"
        "Use only the supplied evidence.\n"
        "Never change the destination.\n"
        f"Selected city: {selected_city}\n"
        f"Selected country: {selected_country}\n"
        f"Allowed interests for matched_interest: {json.dumps(user_interests)}\n"
        f"Allowed categories for must_visit_places.category: {json.dumps(ALLOWED_PLACE_CATEGORIES)}\n"
        f"Allowed values for weather_sensitivity: {json.dumps(ALLOWED_WEATHER_SENSITIVITY)}\n"
        "Do not invent free transport, fake hotel names, placeholder text, or unsupported safety claims.\n"
        "Do not reuse hotels as restaurants unless clearly supported.\n"
        "Rules:\n"
        f"- destination_guardrails.selected_city must be exactly '{selected_city}'.\n"
        f"- destination_guardrails.selected_country must be exactly '{selected_country}'.\n"
        "- destination_snapshot.summary must explicitly mention the selected city or country.\n"
        "- destination_snapshot.traveler_fit must explicitly mention the selected city or country.\n"
        "- key_characteristics must have 3 to 5 clean natural-language items.\n"
        "- suggested_places_by_interest.matched_interest must exactly match one user interest.\n"
        "- local_transport.cost_notes must avoid claiming ferries are free unless clearly supported.\n"
        "- culture_etiquette.religious_site_etiquette must never be blank.\n"
        "- Keep attractions, hotels, and food recommendations in appropriate sections.\n\n"
        f"Traveler profile:\n{json.dumps(parsed_profile, indent=2)}\n\n"
        f"Selected destination details:\n{json.dumps(selected_location, indent=2)}\n\n"
        f"Weather summary:\n{json.dumps(weather_summary, indent=2)}\n\n"
        f"Live research context:\n{json.dumps(live_research, indent=2)}\n\n"
        f"JSON Schema:\n{json.dumps(schema, indent=2)}\n"
    )

    payload = {
        "model": OLLAMA_MODEL,
        "prompt": prompt,
        "stream": False,
        "format": schema
    }

    data = safe_post_json(OLLAMA_URL, payload, timeout=180)
    response_text = data.get("response", "").strip()
    if not response_text:
        raise ValueError("Ollama returned an empty response.")

    parsed = json.loads(response_text)
    return clean_research_output(parsed, parsed_profile, selected_location, weather_summary, live_research)


def init_state():
    defaults = {
        "selected_location": None,
        "generated_report": None,
        "quality_warnings": [],
        "consistency_issues": [],
        "location_options": [],
        "pending_profile": None,
        "debug_mode": False
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def pill_row(items):
    if not items:
        st.write("—")
        return
    html = "".join([f'<span class="pill">{item}</span>' for item in items])
    st.markdown(html, unsafe_allow_html=True)


def render_summary_cards(report):
    destination = report["destination_context"]
    traveler = report["traveler_profile"]
    weather = report["weather_summary"]

    c1, c2, c3, c4 = st.columns(4)

    with c1:
        st.markdown(
            f"""
            <div class="summary-card">
                <div class="label">Destination</div>
                <div class="value">{destination["city"]}, {destination["country"]}</div>
                <div class="sub">{traveler["days"]} days • {traveler["travelers"]} traveler(s)<br>{destination["timezone"]}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with c2:
        st.markdown(
            f"""
            <div class="summary-card">
                <div class="label">Weather now</div>
                <div class="value">{weather["temperature_now_c"]}°C • {weather["weather_description"]}</div>
                <div class="sub">Feels {weather["temperature_feel"].lower()} • Wind {weather["wind_speed_kmh"]} km/h<br>{weather["activity_suitability"]}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with c3:
        st.markdown(
            f"""
            <div class="summary-card">
                <div class="label">Budget fit</div>
                <div class="value">{traveler["budget"]}</div>
                <div class="sub">Hotel preference: {traveler["hotel_category"]}<br>Food preference: {traveler["food_preference"]}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with c4:
        interests = ", ".join(traveler.get("interests", [])) or "Flexible"
        st.markdown(
            f"""
            <div class="summary-card">
                <div class="label">Trip style</div>
                <div class="value">{traveler["travel_style"]}</div>
                <div class="sub">Pace: {traveler["pace"]}<br>Focus: {interests}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )


def render_card(title, subtitle, body, pills=None):
    st.markdown(f'<div class="recommendation-card"><h4>{title}</h4><div class="recommendation-meta">{subtitle}</div><div class="recommendation-body">{body}</div></div>', unsafe_allow_html=True)
    if pills:
        pill_row(pills)


def render_popover_details(button_label, lines):
    with st.popover(button_label):
        for line in lines:
            st.write(f"- {line}")


def render_overview_tab(report):
    final_report = report["final_report"]
    snapshot = final_report["destination_snapshot"]
    weather = report["weather_summary"]
    traveler = report["traveler_profile"]

    left, right = st.columns([1.45, 1])

    with left:
        st.markdown('<div class="section-title">Trip overview</div>', unsafe_allow_html=True)
        st.markdown(
            f"""
            <div class="info-banner">
                <strong>Why this destination works:</strong><br>
                {snapshot.get("summary", "No summary available.")}
                <div class="divider-space"></div>
                <span class="muted">{snapshot.get("traveler_fit", "")}</span>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.markdown("**Trip themes**")
        pill_row(snapshot.get("key_characteristics", []))

        st.markdown('<div class="section-title">Quick plan signals</div>', unsafe_allow_html=True)
        a, b, c = st.columns(3)
        a.metric("Trip duration", f'{traveler["days"]} days')
        b.metric("Today high / low", f'{weather["today_max_c"]}° / {weather["today_min_c"]}°')
        b.caption(weather["weather_description"])
        c.metric("Activity fit", weather["activity_suitability"])

    with right:
        st.markdown('<div class="section-title">Weather and planning</div>', unsafe_allow_html=True)
        weather_block = final_report["weather_climate"]
        render_card(
            "Today’s conditions",
            f'{weather["temperature_now_c"]}°C • {weather["weather_description"]} • Wind {weather["wind_speed_kmh"]} km/h',
            weather_block.get("summary", "No weather summary available."),
            pills=[weather["temperature_feel"], weather["wind_feel"], weather_block.get("comfort_level", "Moderate")]
        )
        if weather_block.get("planning_advice"):
            render_popover_details("View planning advice", weather_block.get("planning_advice"))

        tradeoffs = final_report.get("planning_tradeoffs", [])
        if tradeoffs:
            st.markdown('<div class="section-title">Planning trade-offs</div>', unsafe_allow_html=True)
            for item in tradeoffs:
                render_card(
                    item.get("topic", "Trade-off"),
                    "Decision lens",
                    f'{item.get("tradeoff", "")} {item.get("who_should_choose_this", "")}'
                )


def render_stay_tab(report):
    final_report = report["final_report"]
    areas = final_report.get("best_areas_to_stay", [])
    hotels = final_report.get("hotel_recommendations", [])

    st.markdown('<div class="section-title">Best areas to stay</div>', unsafe_allow_html=True)
    if not areas:
        st.info("No area recommendations available.")
    else:
        for area in areas:
            col1, col2 = st.columns([3.1, 1])
            with col1:
                render_card(
                    area.get("area_name", "Area"),
                    f'Budget fit: {area.get("budget_fit", "Unknown")} • Sentiment: {area.get("traveler_sentiment", "Unknown")}',
                    area.get("why_recommended", ""),
                    pills=area.get("best_for", [])
                )
            with col2:
                detail_lines = []
                for item in area.get("pros", []):
                    detail_lines.append(f"Pro: {item}")
                for item in area.get("cons", []):
                    detail_lines.append(f"Con: {item}")
                if area.get("connectivity_notes"):
                    detail_lines.append(f"Connectivity: {area.get('connectivity_notes')}")
                render_popover_details("View details", detail_lines or ["No extra details available."])

    st.markdown('<div class="section-title">Suggested hotels</div>', unsafe_allow_html=True)
    if not hotels:
        st.info("No hotel suggestions available.")
    else:
        cols = st.columns(2)
        for idx, hotel in enumerate(hotels):
            with cols[idx % 2]:
                render_card(
                    hotel.get("hotel_name", "Hotel"),
                    f'{hotel.get("area", "Unknown area")} • {hotel.get("pricing_note", "Pricing not available")}',
                    hotel.get("why_it_matches", ""),
                    pills=[hotel.get("hotel_category", ""), hotel.get("budget_fit", "")]
                )
                detail_lines = []
                for item in hotel.get("review_highlights", []):
                    detail_lines.append(f"Review highlight: {item}")
                for item in hotel.get("cautions", []):
                    detail_lines.append(f"Caution: {item}")
                if hotel.get("location_logic"):
                    detail_lines.append(f"Location logic: {hotel.get('location_logic')}")
                render_popover_details("Open hotel details", detail_lines or ["No extra hotel details available."])


def render_places_tab(report):
    final_report = report["final_report"]
    places = final_report.get("must_visit_places", [])
    interests = final_report.get("suggested_places_by_interest", [])

    st.markdown('<div class="section-title">Must-visit places</div>', unsafe_allow_html=True)
    if not places:
        st.info("No must-visit places available.")
    else:
        cols = st.columns(2)
        for idx, place in enumerate(places):
            with cols[idx % 2]:
                render_card(
                    place.get("name", "Place"),
                    f'{place.get("category", "Place")} • {place.get("time_needed", "Time not available")}',
                    place.get("why_visit", ""),
                    pills=place.get("best_for", [])
                )
                details = [
                    f"Best time to visit: {place.get('best_time_to_visit', 'Not specified')}",
                    f"Weather sensitivity: {place.get('weather_sensitivity', 'Moderate')}"
                ]
                render_popover_details("View place details", details)

    st.markdown('<div class="section-title">Matched to your interests</div>', unsafe_allow_html=True)
    if not interests:
        st.info("No personalized place suggestions available.")
    else:
        for item in interests:
            col1, col2 = st.columns([3.2, 1])
            with col1:
                render_card(
                    item.get("name", "Suggestion"),
                    f'Interest match: {item.get("matched_interest", "General")} • {item.get("indoor_outdoor", "Mixed")}',
                    item.get("why_suggested", "")
                )
            with col2:
                render_popover_details(
                    "Open details",
                    [f"Recommended time: {item.get('time_needed', 'Not specified')}"]
                )


def render_food_tab(report):
    final_report = report["final_report"]
    items = final_report.get("food_recommendations", [])

    st.markdown('<div class="section-title">Food recommendations</div>', unsafe_allow_html=True)
    st.markdown('<div class="mini-note">Compact recommendations on the main screen, with extra detail hidden behind popovers.</div>', unsafe_allow_html=True)

    if not items:
        st.info("No food suggestions available.")
    else:
        cols = st.columns(2)
        for idx, item in enumerate(items):
            with cols[idx % 2]:
                render_card(
                    item.get("place_name", "Restaurant"),
                    f'{item.get("cuisine", "Cuisine")} • {item.get("area", "Area not specified")}',
                    item.get("why_recommended", ""),
                    pills=[item.get("price_level", ""), item.get("vibe", "")]
                )
                details = []
                for sig in item.get("signature_items", []):
                    details.append(f"Try: {sig}")
                if item.get("notes"):
                    details.append(f"Note: {item.get('notes')}")
                render_popover_details("Open food details", details or ["No extra food details available."])


def render_transport_tab(report):
    final_report = report["final_report"]
    transport = final_report.get("local_transport", {})

    left, right = st.columns([1.15, 1])

    with left:
        st.markdown('<div class="section-title">Getting around</div>', unsafe_allow_html=True)
        render_card(
            "Transport overview",
            "How to move around the destination",
            transport.get("summary", "No transport summary available."),
            pills=transport.get("common_modes", [])
        )
        if transport.get("best_options_for_tourists"):
            st.markdown("**Best options for tourists**")
            pill_row(transport.get("best_options_for_tourists", []))

    with right:
        st.markdown('<div class="section-title">Practical transport details</div>', unsafe_allow_html=True)
        detail_lines = []
        for note in transport.get("cost_notes", []):
            detail_lines.append(f"Cost note: {note}")
        for tip in transport.get("practical_tips", []):
            detail_lines.append(f"Tip: {tip}")
        if transport.get("area_connectivity"):
            detail_lines.append(f"Connectivity: {transport.get('area_connectivity')}")
        if detail_lines:
            with st.expander("Open transport details"):
                for line in detail_lines:
                    st.write(f"- {line}")
        else:
            st.info("No extra transport details available.")


def render_safety_tab(report):
    final_report = report["final_report"]
    safety = final_report.get("safety_and_cautions", {})
    culture = final_report.get("culture_etiquette", {})

    left, right = st.columns(2)

    with left:
        st.markdown('<div class="section-title">Safety guidance</div>', unsafe_allow_html=True)
        render_card(
            "Visitor safety",
            "Practical travel awareness",
            safety.get("overall_note", "No safety note available."),
            pills=safety.get("safe_areas", [])
        )
        detail_lines = []
        for item in safety.get("caution_areas", []):
            detail_lines.append(f"Caution area: {item}")
        for item in safety.get("common_issues", []):
            detail_lines.append(f"Common issue: {item}")
        for item in safety.get("transport_cautions", []):
            detail_lines.append(f"Transport caution: {item}")
        for item in safety.get("food_hygiene_notes", []):
            detail_lines.append(f"Food hygiene: {item}")
        render_popover_details("Open safety details", detail_lines or ["No additional safety notes available."])

    with right:
        st.markdown('<div class="section-title">Culture and etiquette</div>', unsafe_allow_html=True)
        render_card(
            "Local etiquette",
            "Helpful behavior cues for visitors",
            culture.get("people_and_social_norms", "No culture note available.")
        )
        etiquette_lines = []
        if culture.get("dress_code"):
            etiquette_lines.append(f"Dress code: {culture.get('dress_code')}")
        if culture.get("dining_etiquette"):
            etiquette_lines.append(f"Dining etiquette: {culture.get('dining_etiquette')}")
        if culture.get("religious_site_etiquette"):
            etiquette_lines.append(f"Religious sites: {culture.get('religious_site_etiquette')}")
        for item in culture.get("dos", []):
            etiquette_lines.append(f"Do: {item}")
        for item in culture.get("donts", []):
            etiquette_lines.append(f"Don't: {item}")
        render_popover_details("Open etiquette details", etiquette_lines or ["No etiquette details available."])


def render_sources(report):
    research = report.get("research_summary", {})
    st.markdown('<div class="section-title">Research sources</div>', unsafe_allow_html=True)
    st.markdown('<div class="mini-note">These are hidden by default so the main screen stays client-friendly.</div>', unsafe_allow_html=True)

    with st.expander("Open web research sources"):
        top_web = research.get("top_web_sources", {})
        if not top_web:
            st.write("No web sources available.")
        for section, sources in top_web.items():
            st.markdown(f"**{section.replace('_', ' ').title()}**")
            if not sources:
                st.write("- No sources")
            for src in sources:
                title = src.get("title", "Untitled source")
                link = src.get("link", "")
                snippet = src.get("snippet", "")
                if link:
                    st.markdown(f"- [{title}]({link})")
                else:
                    st.write(f"- {title}")
                if snippet:
                    st.caption(snippet)

    with st.expander("Open YouTube research sources"):
        videos = research.get("top_youtube_sources", [])
        if not videos:
            st.write("No YouTube sources available.")
        for video in videos:
            title = video.get("title", "Untitled video")
            url = video.get("video_url", "")
            channel = video.get("channel", "Unknown channel")
            if url:
                st.markdown(f"- [{title}]({url})")
            else:
                st.write(f"- {title}")
            st.caption(f"Channel: {channel}")


def render_debug_panel():
    with st.sidebar:
        st.markdown("### App controls")
        st.session_state.debug_mode = st.toggle("Debug mode", value=st.session_state.debug_mode)
        if st.button("Clear report"):
            st.session_state.generated_report = None
            st.session_state.quality_warnings = []
            st.session_state.consistency_issues = []
            st.session_state.location_options = []
            st.session_state.pending_profile = None
            st.session_state.selected_location = None
            st.rerun()


def build_dashboard(report, quality_warnings):
    traveler = report["traveler_profile"]
    st.markdown(
        f"""
        <div class="app-hero">
            <h1>Travel Planner Dashboard</h1>
            <p>{traveler["origin"]} → {report["destination_context"]["city"]}, {report["destination_context"]["country"]} • {traveler["days"]} days • {traveler["travel_style"]} trip</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    render_summary_cards(report)

    if quality_warnings:
        with st.expander("Output quality notes"):
            for warning in quality_warnings:
                st.warning(warning)

    tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs(
        ["Overview", "Stay", "Places", "Food", "Transport", "Safety", "Sources"]
    )

    with tab1:
        render_overview_tab(report)
    with tab2:
        render_stay_tab(report)
    with tab3:
        render_places_tab(report)
    with tab4:
        render_food_tab(report)
    with tab5:
        render_transport_tab(report)
    with tab6:
        render_safety_tab(report)
    with tab7:
        render_sources(report)

    if st.session_state.debug_mode:
        with st.expander("Debug JSON"):
            st.json(report)


def collect_profile_form():
    st.markdown("### Trip inputs")
    with st.form("travel_form"):
        c1, c2, c3 = st.columns(3)
        with c1:
            origin = st.text_input("Origin city")
            destination_country = st.text_input("Destination country")
            destination_city_region = st.text_input("Destination city / region")
        with c2:
            days = st.number_input("Number of days", min_value=1, max_value=30, value=4)
            travelers = st.number_input("Number of travelers", min_value=1, max_value=10, value=2)
            budget = st.selectbox("Budget", ["Low", "Moderate", "High", "Luxury"])
        with c3:
            hotel_category = st.selectbox("Hotel preference", ["3-star", "4-star", "5-star"])
            food_preference = st.selectbox("Food preference", ["Veg", "Non-veg", "Both"])
            travel_style = st.selectbox("Travel style", ["Leisure", "Adventure", "Cultural", "Family", "Mixed"])
        pace = st.selectbox("Trip pace", ["Relaxed", "Moderate", "Packed"])
        interests = st.multiselect("Interests", ALLOWED_INTERESTS)

        submitted = st.form_submit_button("Generate travel dashboard", use_container_width=True)

    if not submitted:
        return

    errors = []
    origin = clean_text(origin)
    destination_country = clean_text(destination_country)
    destination_city_region = clean_text(destination_city_region)

    if not origin:
        errors.append("Origin city is required.")
    if not destination_country:
        errors.append("Destination country is required.")
    if not destination_city_region:
        errors.append("Destination city / region is required.")
    if not interests:
        errors.append("Please select at least one interest.")

    if errors:
        for error in errors:
            st.error(error)
        return

    parsed_profile = {
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

    try:
        with st.spinner("Finding destination matches..."):
            location_options = get_location_options(parsed_profile["destination_city_region"])

        if not location_options:
            st.warning("Could not find destination details. Try a more specific city or region.")
            return

        filtered_options = []
        user_country = parsed_profile["destination_country"].lower()
        for loc in location_options:
            loc_country = str(loc.get("country", "")).lower()
            if user_country in loc_country or loc_country in user_country:
                filtered_options.append(loc)

        if not filtered_options:
            filtered_options = location_options

        st.session_state.pending_profile = parsed_profile
        st.session_state.location_options = filtered_options
        st.session_state.generated_report = None
        st.session_state.selected_location = None
        st.rerun()

    except Exception as e:
        st.error("Something went wrong while processing the destination search.")
        st.code(str(e))


def render_location_picker_and_generate():
    if not st.session_state.pending_profile or not st.session_state.location_options:
        return

    st.markdown("### Confirm destination")
    options = st.session_state.location_options
    labels = [
        f"{loc.get('name', 'Unknown')}, {loc.get('country', 'Unknown Country')} ({loc.get('timezone', 'Unknown Timezone')})"
        for loc in options
    ]

    selected_label = st.selectbox("Select the correct destination", labels, key="destination_selector")
    selected_location = options[labels.index(selected_label)]

    c1, c2 = st.columns([1.2, 1])
    with c1:
        st.markdown(
            f"""
            <div class="info-banner">
                <strong>Selected location</strong><br>
                {selected_location.get("name")}, {selected_location.get("country")}<br>
                <span class="muted">Timezone: {selected_location.get("timezone")} • Lat: {selected_location.get("latitude")} • Lon: {selected_location.get("longitude")}</span>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with c2:
        if st.button("Build dashboard", use_container_width=True):
            try:
                with st.spinner("Gathering weather, live research, and personalized recommendations..."):
                    weather = get_weather_details(
                        selected_location.get("latitude"),
                        selected_location.get("longitude"),
                        selected_location.get("timezone")
                    )
                    weather_summary = build_weather_summary(weather)
                    live_research = build_live_research_context(st.session_state.pending_profile, selected_location)
                    combined_output, quality_warnings, consistency_issues = get_research_from_ollama(
                        st.session_state.pending_profile,
                        selected_location,
                        weather_summary,
                        live_research
                    )

                if consistency_issues:
                    st.session_state.generated_report = None
                    st.session_state.consistency_issues = consistency_issues
                    st.error("The generated report failed destination consistency checks.")
                else:
                    st.session_state.generated_report = combined_output
                    st.session_state.quality_warnings = quality_warnings
                    st.session_state.consistency_issues = []
                    st.session_state.selected_location = selected_location
                    st.success("Travel dashboard generated.")
                    st.rerun()

            except Exception as e:
                st.error("Something went wrong while generating the travel dashboard.")
                st.code(str(e))

    if st.session_state.consistency_issues:
        for issue in st.session_state.consistency_issues:
            st.warning(issue)


def main():
    init_state()
    inject_custom_css()
    render_debug_panel()

    st.markdown(
        """
        <div class="app-hero">
            <h1>✈️ Travel Planner Agent</h1>
            <p>Generate a polished, client-ready travel dashboard with destination insights, stay suggestions, places to visit, food, transport, and safety guidance.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    collect_profile_form()
    render_location_picker_and_generate()

    if st.session_state.generated_report:
        build_dashboard(st.session_state.generated_report, st.session_state.quality_warnings)
    else:
        st.markdown(
            """
            <div class="info-banner">
                <strong>How this view works</strong><br>
                Fill in the trip details, confirm the destination, and generate the dashboard. The final output is shown as a tabbed travel planner UI instead of raw JSON, while research sources remain hidden unless opened.
            </div>
            """,
            unsafe_allow_html=True,
        )


if __name__ == "__main__":
    main()