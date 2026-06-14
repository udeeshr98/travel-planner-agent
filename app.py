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


def init_state():
    defaults = {
        "selected_location": None,
        "generated_report": None,
        "quality_warnings": [],
        "consistency_issues": [],
        "location_options": [],
        "pending_profile": None,
        "debug_mode": False,
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


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

        with c3:
            hotel_category = st.selectbox("Hotel preference", ["3-star", "4-star", "5-star"])
            food_preference = st.selectbox("Food preference", ["Veg", "Non-veg", "Both"])
            travel_style = st.selectbox("Travel style", ["Leisure", "Adventure", "Cultural", "Family", "Mixed"])

        pace = st.selectbox("Trip pace", ["Relaxed", "Moderate", "Packed"])
        budget_scope = st.selectbox("Budget applies to", ["Total trip", "Per person"])
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
        "budget_scope": budget_scope,
        "hotel_category": hotel_category,
        "food_preference": food_preference,
        "travel_style": travel_style,
        "pace": pace,
        "interests": interests,
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