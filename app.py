import streamlit as st

st.title("Travel Planner - Input & Preference Agent")

st.write("Fill in your travel preferences below.")

origin = st.text_input("Origin city")
destination = st.text_input("Destination")
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

if st.button("Create Travel Profile"):
    st.subheader("Structured Travel Profile")
    st.json({
        "origin": origin,
        "destination": destination,
        "days": days,
        "travelers": travelers,
        "budget": budget,
        "hotel_category": hotel_category,
        "food_preference": food_preference,
        "travel_style": travel_style,
        "pace": pace,
        "interests": interests
    })