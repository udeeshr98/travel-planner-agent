import streamlit as st


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
            pills=[weather["temperature_feel"], weather["wind_feel"], weather_block.get("comfort_level", "Moderate")],
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
                    f'{item.get("tradeoff", "")} {item.get("who_should_choose_this", "")}',
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
                    pills=place.get("best_for", []),
                )
                details = [
                    f"Best time to visit: {place.get('best_time_to_visit', 'Not specified')}",
                    f"Weather sensitivity: {place.get('weather_sensitivity', 'Moderate')}",
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
                    item.get("why_suggested", ""),
                )
            with col2:
                render_popover_details(
                    "Open details",
                    [f"Recommended time: {item.get('time_needed', 'Not specified')}"],
                )


def render_food_tab(report):
    final_report = report["final_report"]
    items = final_report.get("food_recommendations", [])

    st.markdown('<div class="section-title">Food recommendations</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="mini-note">Compact recommendations on the main screen, with extra detail hidden behind popovers.</div>',
        unsafe_allow_html=True,
    )

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
                    pills=[item.get("price_level", ""), item.get("vibe", "")],
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
            pills=transport.get("common_modes", []),
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
            pills=safety.get("safe_areas", []),
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


def render_sources(report):
    research = report.get("research_summary", {})
    st.markdown('<div class="section-title">Research sources</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="mini-note">These are hidden by default so the main screen stays client-friendly.</div>',
        unsafe_allow_html=True,
    )

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