import streamlit as st


# ---------------------------------------------------------------------------
# CSS
# ---------------------------------------------------------------------------

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

        .planner-hero {
            position: relative;
            overflow: hidden;
            border-radius: 24px;
            padding: 1.4rem 1.5rem;
            margin-bottom: 1rem;
            background: linear-gradient(135deg, #0f172a 0%, #1d4ed8 45%, #0ea5e9 100%);
            color: white;
            box-shadow: 0 18px 50px rgba(15, 23, 42, 0.18);
        }

        .planner-hero h2 {
            margin: 0 0 0.35rem 0;
            font-size: 2rem;
            line-height: 1.1;
        }

        .planner-hero p {
            margin: 0;
            color: rgba(255,255,255,0.88);
            font-size: 0.98rem;
            max-width: 760px;
        }

        .planner-hero-badges {
            margin-top: 0.9rem;
            display: flex;
            flex-wrap: wrap;
            gap: 0.5rem;
        }

        .planner-badge {
            display: inline-block;
            padding: 0.38rem 0.72rem;
            border-radius: 999px;
            background: rgba(255,255,255,0.14);
            border: 1px solid rgba(255,255,255,0.18);
            font-size: 0.8rem;
            font-weight: 700;
            backdrop-filter: blur(6px);
        }

        .trip-shell {
            background: linear-gradient(180deg, rgba(255,255,255,0.98), rgba(248,250,252,0.98));
            border: 1px solid rgba(148, 163, 184, 0.22);
            border-radius: 24px;
            padding: 1.2rem;
            box-shadow: 0 14px 36px rgba(15, 23, 42, 0.06);
            margin-bottom: 1rem;
        }

        .trip-card {
            background: white;
            border: 1px solid rgba(148, 163, 184, 0.18);
            border-radius: 20px;
            padding: 1rem 1rem 0.6rem 1rem;
            box-shadow: 0 8px 24px rgba(15, 23, 42, 0.04);
            margin-bottom: 1rem;
        }

        .trip-card h4 {
            margin: 0 0 0.2rem 0;
            color: #0f172a;
            font-size: 1rem;
            font-weight: 800;
        }

        .trip-card p {
            margin: 0 0 0.85rem 0;
            color: #64748b;
            font-size: 0.9rem;
        }

        .quick-chip-row {
            display: flex;
            flex-wrap: wrap;
            gap: 0.6rem;
            margin: 0.2rem 0 1rem 0;
        }

        .quick-chip {
            background: linear-gradient(180deg, #ffffff, #f8fafc);
            border: 1px solid rgba(148, 163, 184, 0.20);
            color: #0f172a;
            border-radius: 16px;
            padding: 0.7rem 0.9rem;
            min-width: 150px;
            box-shadow: 0 6px 18px rgba(15, 23, 42, 0.04);
        }

        .quick-chip .label {
            display: block;
            font-size: 0.74rem;
            color: #64748b;
            text-transform: uppercase;
            letter-spacing: 0.05em;
            font-weight: 700;
            margin-bottom: 0.15rem;
        }

        .quick-chip .value {
            font-size: 1rem;
            font-weight: 800;
            color: #0f172a;
        }

        .section-kicker {
            font-size: 0.82rem;
            text-transform: uppercase;
            letter-spacing: 0.06em;
            color: #2563eb;
            font-weight: 800;
            margin-bottom: 0.25rem;
        }

        .form-caption {
            color: #64748b;
            font-size: 0.92rem;
            margin-top: -0.2rem;
            margin-bottom: 0.8rem;
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

        .city-header {
            background: linear-gradient(135deg, #1e293b 0%, #1d4ed8 100%);
            color: white;
            border-radius: 16px;
            padding: 0.85rem 1.1rem;
            margin-bottom: 1rem;
            margin-top: 0.5rem;
        }

        .city-header h3 {
            margin: 0 0 0.2rem 0;
            font-size: 1.25rem;
            font-weight: 800;
        }

        .city-header p {
            margin: 0;
            font-size: 0.88rem;
            color: rgba(255,255,255,0.82);
        }

        .country-header {
            background: linear-gradient(135deg, #064e3b 0%, #065f46 100%);
            color: white;
            border-radius: 16px;
            padding: 0.85rem 1.1rem;
            margin-bottom: 1rem;
            margin-top: 0.5rem;
        }

        .country-header h3 {
            margin: 0 0 0.2rem 0;
            font-size: 1.15rem;
            font-weight: 800;
        }

        .country-header p {
            margin: 0;
            font-size: 0.88rem;
            color: rgba(255,255,255,0.82);
        }

        .intercity-route-card {
            border: 1px solid rgba(148, 163, 184, 0.25);
            border-radius: 14px;
            padding: 0.85rem 1rem;
            background: white;
            margin-bottom: 0.75rem;
            box-shadow: 0 4px 14px rgba(15, 23, 42, 0.04);
        }

        .intercity-route-card .route-title {
            font-weight: 800;
            color: #0f172a;
            font-size: 1rem;
            margin-bottom: 0.25rem;
        }

        .intercity-route-card .route-meta {
            color: #475569;
            font-size: 0.88rem;
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

        .stButton > button,
        div[data-testid="stForm"] button {
            border-radius: 14px;
            font-weight: 700;
            min-height: 3rem;
        }

        div[data-testid="stForm"] {
            border: none !important;
            background: transparent !important;
        }

        div[data-testid="stForm"] > form {
            border: none !important;
            background: transparent !important;
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


# ---------------------------------------------------------------------------
# Reusable UI helpers
# ---------------------------------------------------------------------------

def pill_row(items):
    if not items:
        st.write("—")
        return
    html = "".join([f'<span class="pill">{item}</span>' for item in items])
    st.markdown(html, unsafe_allow_html=True)


def render_card(title, subtitle, body, pills=None):
    st.markdown(
        f'<div class="recommendation-card"><h4>{title}</h4><div class="recommendation-meta">{subtitle}</div><div class="recommendation-body">{body}</div></div>',
        unsafe_allow_html=True,
    )
    if pills:
        pill_row(pills)


def render_popover_details(button_label, lines):
    with st.popover(button_label):
        for line in lines:
            st.write(f"- {line}")


def city_header(city, fit_summary=""):
    st.markdown(
        f"""
        <div class="city-header">
            <h3>{city}</h3>
            <p>{fit_summary if fit_summary else "City-specific recommendations below."}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def country_section_header(label, note=""):
    st.markdown(
        f"""
        <div class="country-header">
            <h3>{label}</h3>
            <p>{note}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


# ---------------------------------------------------------------------------
# Summary cards row
# ---------------------------------------------------------------------------

def render_summary_cards(report):
    destination = report["destination_context"]
    traveler = report["traveler_profile"]
    weather = report["weather_summary"]
    all_cities = destination.get("all_cities", [destination.get("anchor_city", "—")])
    cities_display = " + ".join(all_cities) if all_cities else destination.get("anchor_city", "—")

    c1, c2, c3, c4 = st.columns(4)

    with c1:
        st.markdown(
            f"""
            <div class="summary-card">
                <div class="label">Destinations</div>
                <div class="value">{cities_display}</div>
                <div class="sub">{destination.get("country", "")} • {traveler["days"]} days • {traveler["travelers"]} traveler(s)</div>
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
                <div class="sub">Hotel: {traveler["hotel_category"]}<br>Food: {traveler["food_preference"]}</div>
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


# ---------------------------------------------------------------------------
# Overview tab  (country context: climate + quick signals)
# ---------------------------------------------------------------------------

def render_overview_tab(report):
    final_report = report["final_report"]
    country_context = final_report.get("country_context", {})
    weather = report["weather_summary"]
    traveler = report["traveler_profile"]
    all_cities = report["destination_context"].get("all_cities", [])
    country = report["destination_context"].get("country", "")

    left, right = st.columns([1.45, 1])

    with left:
        st.markdown('<div class="section-title">Trip overview</div>', unsafe_allow_html=True)
        season = country_context.get("best_season_climate", {})
        st.markdown(
            f"""
            <div class="info-banner">
                <strong>Best season and climate for {country}:</strong><br>
                {season.get("summary", "No climate summary available.")}
                <div class="divider-space"></div>
                <span class="muted">Climate note: {season.get("climate_notes", "")}</span>
            </div>
            """,
            unsafe_allow_html=True,
        )

        best_months = season.get("best_months_to_visit", [])
        months_avoid = season.get("months_to_avoid", [])
        if best_months:
            st.markdown("**Best months to visit**")
            pill_row(best_months)
        if months_avoid:
            st.markdown("**Months to avoid**")
            pill_row(months_avoid)

        st.markdown('<div class="section-title">Quick plan signals</div>', unsafe_allow_html=True)
        a, b, c = st.columns(3)
        a.metric("Trip duration", f'{traveler["days"]} days')
        b.metric("Today high / low", f'{weather["today_max_c"]}° / {weather["today_min_c"]}°')
        b.caption(weather["weather_description"])
        c.metric("Activity fit", weather["activity_suitability"])

        st.markdown('<div class="section-title">Cities on this trip</div>', unsafe_allow_html=True)
        city_intel = final_report.get("city_intel", {})
        for city in all_cities:
            fit = city_intel.get(city, {}).get("city_fit_summary", "")
            st.markdown(
                f"""
                <div class="info-banner">
                    <strong>{city}</strong><br>
                    <span class="muted">{fit if fit else "City details available in the tabs below."}</span>
                </div>
                """,
                unsafe_allow_html=True,
            )

    with right:
        st.markdown('<div class="section-title">Visa and entry</div>', unsafe_allow_html=True)
        visa = country_context.get("visa_entry", {})
        render_card(
            f"Entry requirements for {country}",
            f'Visa on arrival: {visa.get("visa_on_arrival", "Check before travel")} • Duration: {visa.get("duration_allowed", "Varies")}',
            visa.get("summary", "No visa information available."),
        )
        if visa.get("key_requirements"):
            render_popover_details("View entry requirements", visa.get("key_requirements", []))

        st.markdown('<div class="section-title">Weather today</div>', unsafe_allow_html=True)
        render_card(
            "Current conditions",
            f'{weather["temperature_now_c"]}°C • {weather["weather_description"]} • Wind {weather["wind_speed_kmh"]} km/h',
            f'Feels {weather["temperature_feel"].lower()}. {weather["activity_suitability"]}.',
            pills=[weather["temperature_feel"], weather["wind_feel"]],
        )


# ---------------------------------------------------------------------------
# Stay tab  (city-wise areas + hotels)
# ---------------------------------------------------------------------------

def render_stay_tab(report):
    final_report = report["final_report"]
    city_intel = final_report.get("city_intel", {})
    all_cities = report["destination_context"].get("all_cities", [])

    if not all_cities:
        st.info("No city data available.")
        return

    for city in all_cities:
        city_data = city_intel.get(city, {})
        city_header(city, city_data.get("city_fit_summary", ""))

        areas = city_data.get("best_areas_to_stay", [])
        hotels = city_data.get("hotel_recommendations", [])

        st.markdown(f'<div class="section-title">Best areas to stay in {city}</div>', unsafe_allow_html=True)
        if not areas:
            st.info(f"No area recommendations available for {city}.")
        else:
            for area in areas:
                col1, col2 = st.columns([3.1, 1])
                with col1:
                    render_card(
                        area.get("area_name", "Area"),
                        f'Budget fit: {area.get("budget_fit", "Unknown")} • Sentiment: {area.get("traveler_sentiment", "Unknown")}',
                        area.get("why_recommended", ""),
                        pills=area.get("best_for", []),
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

        st.markdown(f'<div class="section-title">Suggested hotels in {city}</div>', unsafe_allow_html=True)
        if not hotels:
            st.info(f"No hotel suggestions available for {city}.")
        else:
            cols = st.columns(2)
            for idx, hotel in enumerate(hotels):
                with cols[idx % 2]:
                    render_card(
                        hotel.get("hotel_name", "Hotel"),
                        f'{hotel.get("area", "Unknown area")} • {hotel.get("pricing_note", "Pricing not available")}',
                        hotel.get("why_it_matches", ""),
                        pills=[hotel.get("hotel_category", ""), hotel.get("budget_fit", "")],
                    )
                    detail_lines = []
                    for item in hotel.get("review_highlights", []):
                        detail_lines.append(f"Review highlight: {item}")
                    for item in hotel.get("cautions", []):
                        detail_lines.append(f"Caution: {item}")
                    if hotel.get("location_logic"):
                        detail_lines.append(f"Location logic: {hotel.get('location_logic')}")
                    render_popover_details("Open hotel details", detail_lines or ["No extra hotel details available."])

        st.divider()


# ---------------------------------------------------------------------------
# Places tab  (city-wise must-visit + interest-matched)
# ---------------------------------------------------------------------------

def render_places_tab(report):
    final_report = report["final_report"]
    city_intel = final_report.get("city_intel", {})
    all_cities = report["destination_context"].get("all_cities", [])

    if not all_cities:
        st.info("No city data available.")
        return

    for city in all_cities:
        city_data = city_intel.get(city, {})
        city_header(city, city_data.get("city_fit_summary", ""))

        places = city_data.get("must_visit_places", [])
        interests = city_data.get("suggested_places_by_interest", [])

        st.markdown(f'<div class="section-title">Must-visit places in {city}</div>', unsafe_allow_html=True)
        if not places:
            st.info(f"No must-visit places available for {city}.")
        else:
            cols = st.columns(2)
            for idx, place in enumerate(places):
                with cols[idx % 2]:
                    render_card(
                        place.get("name", "Place"),
                        f'{place.get("category", "Place")} • {place.get("time_needed", "Time not available")}',
                        place.get("why_visit", ""),
                        pills=place.get("best_for", []),
                    )
                    details = [
                        f"Best time to visit: {place.get('best_time_to_visit', 'Not specified')}",
                        f"Weather sensitivity: {place.get('weather_sensitivity', 'Moderate')}",
                    ]
                    render_popover_details("View place details", details)

        st.markdown(f'<div class="section-title">Matched to your interests in {city}</div>', unsafe_allow_html=True)
        if not interests:
            st.info(f"No personalized suggestions available for {city}.")
        else:
            for item in interests:
                col1, col2 = st.columns([3.2, 1])
                with col1:
                    render_card(
                        item.get("name", "Suggestion"),
                        f'Interest match: {item.get("matched_interest", "General")} • {item.get("indoor_outdoor", "Mixed")}',
                        item.get("why_suggested", ""),
                    )
                with col2:
                    render_popover_details(
                        "Open details",
                        [f"Recommended time: {item.get('time_needed', 'Not specified')}"],
                    )

        st.divider()


# ---------------------------------------------------------------------------
# Food tab  (city-wise food recommendations)
# ---------------------------------------------------------------------------

def render_food_tab(report):
    final_report = report["final_report"]
    city_intel = final_report.get("city_intel", {})
    all_cities = report["destination_context"].get("all_cities", [])

    if not all_cities:
        st.info("No city data available.")
        return

    st.markdown(
        '<div class="mini-note">Food suggestions are city-specific and matched to your food preference. Tap a card for dish details.</div>',
        unsafe_allow_html=True,
    )

    for city in all_cities:
        city_data = city_intel.get(city, {})
        city_header(city, city_data.get("city_fit_summary", ""))

        items = city_data.get("food_recommendations", [])
        st.markdown(f'<div class="section-title">Food recommendations in {city}</div>', unsafe_allow_html=True)

        if not items:
            st.info(f"No food suggestions available for {city}.")
        else:
            cols = st.columns(2)
            for idx, item in enumerate(items):
                with cols[idx % 2]:
                    render_card(
                        item.get("place_name", "Restaurant"),
                        f'{item.get("cuisine", "Cuisine")} • {item.get("area", "Area not specified")}',
                        item.get("why_recommended", ""),
                        pills=[item.get("price_level", ""), item.get("vibe", "")],
                    )
                    details = []
                    for sig in item.get("signature_items", []):
                        details.append(f"Try: {sig}")
                    if item.get("notes"):
                        details.append(f"Note: {item.get('notes')}")
                    render_popover_details("Open food details", details or ["No extra food details available."])

        st.divider()


# ---------------------------------------------------------------------------
# Transport tab  (city-wise local transport + inter-city routes)
# ---------------------------------------------------------------------------

def render_transport_tab(report):
    final_report = report["final_report"]
    city_intel = final_report.get("city_intel", {})
    country_context = final_report.get("country_context", {})
    all_cities = report["destination_context"].get("all_cities", [])
    country = report["destination_context"].get("country", "")

    # Inter-city transport section
    intercity = country_context.get("intercity_transport", {})
    if intercity:
        country_section_header(
            f"Getting between cities in {country}",
            intercity.get("summary", ""),
        )

        routes = intercity.get("routes", [])
        if routes:
            st.markdown('<div class="section-title">Route options</div>', unsafe_allow_html=True)
            for route in routes:
                from_c = route.get("from_city", "")
                to_c = route.get("to_city", "")
                options = route.get("options", [])
                duration = route.get("estimated_duration", "")
                cost = route.get("cost_estimate", "")
                recommended = route.get("recommended_mode", "")
                st.markdown(
                    f"""
                    <div class="intercity-route-card">
                        <div class="route-title">{from_c} to {to_c}</div>
                        <div class="route-meta">Duration: {duration} &nbsp;|&nbsp; Cost: {cost} &nbsp;|&nbsp; Recommended: {recommended}</div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
                if options:
                    pill_row(options)
        if intercity.get("practical_tips"):
            render_popover_details("View intercity transport tips", intercity.get("practical_tips", []))

        st.divider()

    # City-level local transport
    st.markdown('<div class="section-title">Local transport by city</div>', unsafe_allow_html=True)
    for city in all_cities:
        city_data = city_intel.get(city, {})
        city_header(city, city_data.get("city_fit_summary", ""))
        transport = city_data.get("local_transport", {})

        left, right = st.columns([1.15, 1])

        with left:
            render_card(
                f"Getting around {city}",
                "Local transport options",
                transport.get("summary", f"No transport summary available for {city}."),
                pills=transport.get("common_modes", []),
            )
            if transport.get("best_options_for_tourists"):
                st.markdown("**Best options for tourists**")
                pill_row(transport.get("best_options_for_tourists", []))

        with right:
            detail_lines = []
            for note in transport.get("cost_notes", []):
                detail_lines.append(f"Cost note: {note}")
            for tip in transport.get("practical_tips", []):
                detail_lines.append(f"Tip: {tip}")
            if detail_lines:
                with st.expander(f"Open {city} transport details"):
                    for line in detail_lines:
                        st.write(f"- {line}")
            else:
                st.info(f"No extra transport details available for {city}.")

        st.divider()


# ---------------------------------------------------------------------------
# Safety tab  (country-level safety + etiquette)
# ---------------------------------------------------------------------------

def render_safety_tab(report):
    final_report = report["final_report"]
    country_context = final_report.get("country_context", {})
    country = report["destination_context"].get("country", "")

    safety = country_context.get("country_safety", {})
    culture = country_context.get("country_etiquette", {})

    left, right = st.columns(2)

    with left:
        country_section_header(f"Safety guidance for {country}", "Country-level travel safety awareness.")
        render_card(
            "Visitor safety",
            "Practical travel awareness",
            safety.get("overall_note", "No safety note available."),
            pills=safety.get("safe_areas", []),
        )
        detail_lines = []
        for item in safety.get("caution_areas", []):
            detail_lines.append(f"Caution area: {item}")
        for item in safety.get("common_issues", []):
            detail_lines.append(f"Common issue: {item}")
        if safety.get("emergency_numbers"):
            detail_lines.append(f"Emergency numbers: {safety.get('emergency_numbers')}")
        render_popover_details("Open safety details", detail_lines or ["No additional safety notes available."])

    with right:
        country_section_header(f"Culture and etiquette in {country}", "Helpful behavior cues for visitors.")
        render_card(
            "Local etiquette",
            "Social norms and customs",
            culture.get("people_and_social_norms", "No culture note available."),
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


# ---------------------------------------------------------------------------
# Sources tab
# ---------------------------------------------------------------------------

def render_sources(report):
    research = report.get("research_summary", {})
    final_report = report.get("final_report", {})
    city_intel = final_report.get("city_intel", {})
    country_research = final_report.get("country_context", {})
    all_cities = report["destination_context"].get("all_cities", [])

    st.markdown('<div class="section-title">Research sources</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="mini-note">Sources used to build the research context for this trip.</div>',
        unsafe_allow_html=True,
    )

    col1, col2, col3 = st.columns(3)
    col1.metric("Country web results", research.get("country_web_results", 0))
    col2.metric("City web results", research.get("city_web_results", 0))
    col3.metric("City YouTube results", research.get("city_youtube_results", 0))

    with st.expander("Open city research sources"):
        for city in all_cities:
            city_data = city_intel.get(city, {})
            city_web = city_data.get("web_research", {}) if isinstance(city_data, dict) else {}
            st.markdown(f"**{city}**")
            if not city_web:
                st.write("- No web sources logged for this city.")
            for section, sources in city_web.items():
                st.markdown(f"*{section.replace('_', ' ').title()}*")
                for src in sources[:2]:
                    title = src.get("title", "Untitled source")
                    link = src.get("link", "")
                    snippet = src.get("snippet", "")
                    if link:
                        st.markdown(f"  - [{title}]({link})")
                    else:
                        st.write(f"  - {title}")
                    if snippet:
                        st.caption(f"  {snippet}")

    with st.expander("Open city YouTube sources"):
        for city in all_cities:
            city_data = city_intel.get(city, {})
            videos = city_data.get("youtube_research", []) if isinstance(city_data, dict) else []
            st.markdown(f"**{city}**")
            if not videos:
                st.write("- No YouTube sources for this city.")
            for video in videos:
                title = video.get("title", "Untitled video")
                url = video.get("video_url", "")
                channel = video.get("channel", "Unknown channel")
                if url:
                    st.markdown(f"  - [{title}]({url})")
                else:
                    st.write(f"  - {title}")
                st.caption(f"  Channel: {channel}")


# ---------------------------------------------------------------------------
# Debug panel (sidebar)
# ---------------------------------------------------------------------------

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


# ---------------------------------------------------------------------------
# Main dashboard builder
# ---------------------------------------------------------------------------

def build_dashboard(report, quality_warnings):
    traveler = report["traveler_profile"]
    destination = report["destination_context"]
    all_cities = destination.get("all_cities", [destination.get("anchor_city", "")])
    cities_display = " + ".join(all_cities) if all_cities else destination.get("anchor_city", "")

    st.markdown(
        f"""
        <div class="app-hero">
            <h1>Travel Planner Dashboard</h1>
            <p>{traveler["origin"]} to {cities_display}, {destination.get("country", "")} • {traveler["days"]} days • {traveler["travel_style"]} trip</p>
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
