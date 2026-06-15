import streamlit as st

from agents.research_agent import (
    ALLOWED_INTERESTS,
    build_live_research_context,
    build_weather_summary,
    clean_text,
    get_location_options,
    get_research_from_ollama,
    get_weather_details,
)
from ui.dashboard import inject_custom_css, build_dashboard, render_debug_panel


st.set_page_config(page_title="Travel Planner Agent", page_icon="✈️", layout="wide")


COUNTRY_DESTINATION_SUGGESTIONS = {
    "India": [
        "Chennai",
        "Bangalore",
        "Delhi",
        "Kolkata",
        "Mumbai",
        "Pune",
        "Hyderabad",
        "Kerala",
    ],
    "Thailand": [
        "Phuket",
        "Krabi",
        "Pattaya",
        "Bangkok",
        "Chiang Mai",
        "Koh Samui",
        "Phi Phi Islands",
    ],
    "Indonesia": [
        "Bali",
        "Ubud",
        "Jakarta",
        "Yogyakarta",
        "Lombok",
        "Komodo Island",
    ],
    "Malaysia": [
        "Kuala Lumpur",
        "Langkawi",
        "Penang",
        "Malacca",
        "Cameron Highlands",
        "Kota Kinabalu",
    ],
    "Singapore": [
        "Marina Bay",
        "Sentosa",
        "Orchard Road",
        "Chinatown",
        "Little India",
    ],
    "Vietnam": [
        "Da Nang",
        "Hoi An",
        "Hanoi",
        "Ho Chi Minh City",
        "Ha Long Bay",
        "Nha Trang",
    ],
    "Japan": [
        "Tokyo",
        "Osaka",
        "Kyoto",
        "Nara",
        "Hokkaido",
        "Okinawa",
    ],
    "United States": [
        "New York",
        "Los Angeles",
        "San Francisco",
        "Las Vegas",
        "Miami",
        "Chicago",
        "Washington DC",
        "Orlando",
    ],
    "Australia": [
        "Sydney",
        "Melbourne",
        "Brisbane",
        "Gold Coast",
        "Perth",
        "Adelaide",
        "Cairns",
        "Tasmania",
    ],
    "New Zealand": [
        "Auckland",
        "Queenstown",
        "Christchurch",
        "Wellington",
        "Rotorua",
        "Milford Sound",
    ],
    "China": [
        "Beijing",
        "Shanghai",
        "Guangzhou",
        "Shenzhen",
        "Chengdu",
        "Xi'an",
        "Hangzhou",
    ],
    "South Korea": [
        "Seoul",
        "Busan",
        "Jeju",
        "Incheon",
        "Daegu",
        "Gyeongju",
    ],
    "Iceland": [
        "Reykjavik",
        "Golden Circle",
        "Blue Lagoon",
        "South Coast",
        "Akureyri",
        "Vik",
    ],
    "Maldives": [
        "Male",
        "Maafushi",
        "Hulhumale",
        "Ari Atoll",
        "Baa Atoll",
    ],
    "Mauritius": [
        "Grand Baie",
        "Flic en Flac",
        "Le Morne",
        "Port Louis",
        "Belle Mare",
    ],
    "UAE": [
        "Dubai",
        "Abu Dhabi",
        "Sharjah",
        "Ras Al Khaimah",
    ],
    "France": [
        "Paris",
        "Nice",
        "Lyon",
        "Marseille",
        "Bordeaux",
    ],
    "Italy": [
        "Rome",
        "Venice",
        "Florence",
        "Milan",
        "Amalfi Coast",
    ],
    "Switzerland": [
        "Zurich",
        "Lucerne",
        "Interlaken",
        "Geneva",
        "Zermatt",
    ],
}


AVAILABLE_COUNTRIES = list(COUNTRY_DESTINATION_SUGGESTIONS.keys())


def init_state():
    defaults = {
        "selected_location": None,
        "generated_report": None,
        "quality_warnings": [],
        "consistency_issues": [],
        "location_options": [],
        "pending_profile": None,
        "debug_mode": False,
        "selected_city_options": [],
        "selected_cities": [],
        "country_weather_mode": True,
        "destination_country": None,
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def get_suggested_destinations(country):
    if not country:
        return []
    return COUNTRY_DESTINATION_SUGGESTIONS.get(country, [])


def build_destination_search_query(custom_city_region, selected_cities, destination_country):
    custom_value = clean_text(custom_city_region)
    selected_cities = [clean_text(city) for city in selected_cities if clean_text(city)]

    if custom_value:
        return custom_value

    if selected_cities:
        return selected_cities[0]

    return clean_text(destination_country)


def render_selected_destinations_preview(selected_cities, custom_city_region, trip_days):
    chips = []

    for city in selected_cities:
        chips.append(f'<span class="pill">{city}</span>')

    custom_value = clean_text(custom_city_region)
    if custom_value:
        chips.append(f'<span class="pill">{custom_value}</span>')

    if chips:
        st.markdown("**Chosen destinations of interest**")
        st.markdown("".join(chips), unsafe_allow_html=True)

    if selected_cities or custom_value:
        joined_places = ", ".join(selected_cities + ([custom_value] if custom_value else []))
        st.markdown(
            f"""
            <div class="info-banner">
                <strong>Planner note</strong><br>
                The travel planner will use your {trip_days}-day trip, selected destinations, interests, and travel pace to recommend how the itinerary can be split across {joined_places}. You do not need to manually assign 1 day here and 2 days there — the planner will suggest that for you.
            </div>
            """,
            unsafe_allow_html=True,
        )


def collect_profile_form():
    st.markdown(
        """
        <div class="planner-hero">
            <h2>Design your next trip</h2>
            <p>Choose a country from the supported destinations, explore city ideas inside it, and let the planner recommend how to distribute your days across the best places.</p>
            <div class="planner-hero-badges">
                <span class="planner-badge">Country-based suggestions</span>
                <span class="planner-badge">Multi-city trip planning</span>
                <span class="planner-badge">Planner-led itinerary split</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        """
        <div class="quick-chip-row">
            <div class="quick-chip"><span class="label">Planner style</span><span class="value">Smart itinerary</span></div>
            <div class="quick-chip"><span class="label">Destination mode</span><span class="value">Country → cities</span></div>
            <div class="quick-chip"><span class="label">Weather mode</span><span class="value">Country overview</span></div>
            <div class="quick-chip"><span class="label">Output</span><span class="value">Day-wise dashboard</span></div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown('<div class="trip-shell">', unsafe_allow_html=True)
    st.markdown('<div class="section-kicker">Trip planner</div>', unsafe_allow_html=True)
    st.markdown("## Plan your travel inputs")
    st.markdown(
        '<div class="form-caption">Choose a supported country, tell the planner the places you are considering, and let it suggest how to split the itinerary for you.</div>',
        unsafe_allow_html=True,
    )

    st.markdown(
        """
        <div class="trip-card">
            <h4>Destination country</h4>
            <p>Select the country first. Once selected, the suggested cities and regions will appear automatically below.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    destination_country = st.selectbox(
        "Destination country",
        options=AVAILABLE_COUNTRIES,
        index=AVAILABLE_COUNTRIES.index(st.session_state.destination_country)
        if st.session_state.destination_country in AVAILABLE_COUNTRIES
        else None,
        placeholder="Select a country you want to explore",
        key="destination_country_selector",
    )

    st.session_state.destination_country = destination_country
    suggested_destinations = get_suggested_destinations(destination_country)

    with st.form("travel_form"):
        top1, top2 = st.columns(2)

        with top1:
            st.markdown(
                """
                <div class="trip-card">
                    <h4>Origin and destination ideas</h4>
                    <p>Tell the planner where the journey starts and which places inside the selected country you are considering.</p>
                </div>
                """,
                unsafe_allow_html=True,
            )
            origin = st.text_input("Origin city", placeholder="e.g. Chennai")

            selected_cities = st.multiselect(
                "Suggested cities / regions",
                options=suggested_destinations,
                default=[],
                placeholder="Select one or more destination ideas",
            )

            if destination_country and suggested_destinations:
                st.caption(f"Available suggestions for {destination_country}: {', '.join(suggested_destinations)}")
            elif destination_country and not suggested_destinations:
                st.caption(f"No preset city suggestions available yet for {destination_country}.")

            custom_city_region = st.text_input(
                "Custom city / region (optional)",
                placeholder="Add a city, island, town, or region not listed above",
            )

        with top2:
            st.markdown(
                """
                <div class="trip-card">
                    <h4>Trip basics</h4>
                    <p>Set the duration, number of travelers, and your overall budget so the planner can shape a practical trip.</p>
                </div>
                """,
                unsafe_allow_html=True,
            )
            col_a, col_b = st.columns(2)
            with col_a:
                days = st.number_input("Number of days", min_value=1, max_value=30, value=4)
                travelers = st.number_input("Number of travelers", min_value=1, max_value=10, value=2)
            with col_b:
                budget = st.selectbox(
                    "Budget",
                    [
                        "Below 50K",
                        "50K to 1L",
                        "1L to 2L",
                        "2L to 3L",
                        "3L to 4L",
                        "4L to 5L",
                        "Above 5L",
                    ],
                )
                budget_scope = st.selectbox("Budget applies to", ["Total trip", "Per person"])

        render_selected_destinations_preview(selected_cities, custom_city_region, days)

        pref1, pref2 = st.columns(2)

        with pref1:
            st.markdown(
                """
                <div class="trip-card">
                    <h4>Stay and food</h4>
                    <p>Choose your hotel comfort level and dining preference.</p>
                </div>
                """,
                unsafe_allow_html=True,
            )
            hotel_category = st.selectbox("Hotel preference", ["3-star", "4-star", "5-star"])
            food_preference = st.selectbox("Food preference", ["Veg", "Non-veg", "Both"])

        with pref2:
            st.markdown(
                """
                <div class="trip-card">
                    <h4>Travel vibe</h4>
                    <p>Define the kind of trip the planner should optimize for.</p>
                </div>
                """,
                unsafe_allow_html=True,
            )
            travel_style = st.selectbox("Travel style", ["Leisure", "Adventure", "Cultural", "Family", "Mixed"])
            pace = st.selectbox("Trip pace", ["Relaxed", "Moderate", "Packed"])

        st.markdown(
            """
            <div class="trip-card">
                <h4>Experiences you want</h4>
                <p>These interests help the planner decide what kinds of cities and attractions deserve more time in your itinerary.</p>
            </div>
            """,
            unsafe_allow_html=True,
        )
        interests = st.multiselect(
            "Interests",
            ALLOWED_INTERESTS,
            placeholder="Pick the experiences you want most",
        )

        submitted = st.form_submit_button("Generate polished travel dashboard", use_container_width=True)

    st.markdown("</div>", unsafe_allow_html=True)

    if not submitted:
        return

    errors = []
    origin = clean_text(origin)
    custom_city_region = clean_text(custom_city_region)

    if not origin:
        errors.append("Origin city is required.")
    if not destination_country:
        errors.append("Destination country is required.")
    if not interests:
        errors.append("Please select at least one interest.")
    if not selected_cities and not custom_city_region:
        errors.append("Please select at least one suggested destination or enter a custom city / region.")

    if errors:
        for error in errors:
            st.error(error)
        return

    anchor_destination_query = build_destination_search_query(
        custom_city_region=custom_city_region,
        selected_cities=selected_cities,
        destination_country=destination_country,
    )

    parsed_profile = {
        "origin": origin,
        "destination_country": destination_country,
        "destination_city_region": anchor_destination_query,
        "anchor_destination": anchor_destination_query,
        "selected_cities": selected_cities,
        "custom_city_region": custom_city_region,
        "days": int(days),
        "travelers": int(travelers),
        "budget": budget,
        "budget_scope": budget_scope,
        "hotel_category": hotel_category,
        "food_preference": food_preference,
        "travel_style": travel_style,
        "pace": pace,
        "interests": interests,
        "planner_mode": "multi_city_recommended_split",
        "weather_preference": "country_overview_then_city_planning",
    }

    try:
        with st.spinner("Finding destination matches..."):
            location_options = get_location_options(anchor_destination_query)

        if not location_options:
            st.warning("Could not find destination details for the primary anchor city. Try selecting a different first city or enter a more specific city / region.")
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
        st.session_state.selected_city_options = selected_cities
        st.session_state.selected_cities = selected_cities
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

    selected_label = st.selectbox("Select the primary anchor destination", labels, key="destination_selector")
    selected_location = options[labels.index(selected_label)]

    chosen_cities = st.session_state.pending_profile.get("selected_cities", [])
    custom_city_region = st.session_state.pending_profile.get("custom_city_region", "")
    anchor_destination = st.session_state.pending_profile.get("anchor_destination", "")

    c1, c2 = st.columns([1.25, 1])

    with c1:
        selected_places_html = "".join([f'<span class="pill">{city}</span>' for city in chosen_cities])
        if custom_city_region:
            selected_places_html += f'<span class="pill">{custom_city_region}</span>'

        st.markdown(
            f"""
            <div class="info-banner">
                <strong>Primary anchor destination</strong><br>
                {selected_location.get("name")}, {selected_location.get("country")}<br>
                <span class="muted">Timezone: {selected_location.get("timezone")} • Lat: {selected_location.get("latitude")} • Lon: {selected_location.get("longitude")}</span>
                <div class="divider-space"></div>
                <strong>Anchor used for lookup</strong><br>
                <span class="muted">{anchor_destination}</span>
                <div class="divider-space"></div>
                <strong>Trip planning mode</strong><br>
                The planner will use this location as the anchor and recommend how to distribute your trip across the selected destinations.
                <div class="divider-space"></div>
                {selected_places_html if selected_places_html else '<span class="muted">No secondary destinations selected.</span>'}
            </div>
            """,
            unsafe_allow_html=True,
        )

    with c2:
        st.markdown(
            """
            <div class="info-banner">
                <strong>Output style</strong><br>
                You do not need to manually assign one day here and one day there. The planner will recommend the itinerary split, along with overall country weather, best season, and city-specific attraction and stay guidance.
            </div>
            """,
            unsafe_allow_html=True,
        )

        if st.button("Build dashboard", use_container_width=True):
            try:
                with st.spinner("Gathering country weather, live research, and personalized itinerary recommendations..."):
                    weather = get_weather_details(
                        selected_location.get("latitude"),
                        selected_location.get("longitude"),
                        selected_location.get("timezone"),
                    )
                    weather_summary = build_weather_summary(weather)
                    live_research = build_live_research_context(
                        st.session_state.pending_profile,
                        selected_location,
                    )
                    combined_output, quality_warnings, consistency_issues = get_research_from_ollama(
                        st.session_state.pending_profile,
                        selected_location,
                        weather_summary,
                        live_research,
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
            <p>Generate a polished, client-ready travel dashboard with destination insights, planner-led itinerary ideas, stay suggestions, attractions, food, transport, and safety guidance.</p>
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
                Choose a supported country, select one or more destinations you are considering, and generate the dashboard. The planner will recommend how the trip can be split across the chosen places, while also showing overall weather guidance and city-level planning ideas.
            </div>
            """,
            unsafe_allow_html=True,
        )


if __name__ == "__main__":
    main()