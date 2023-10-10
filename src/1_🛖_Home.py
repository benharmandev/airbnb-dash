import altair as alt
import streamlit as st
import pandas as pd
from constants import BENS_COLORS as COLORS
from millify import millify
from sqlalchemy import func
from database.models import (
    ListingsCore,
    RoomTypes,
    ListingsLocation,
    Neighborhoods,
    Cities,
    Amenities,
    ListingsReviewsSummary,
)
from constants import CITIES
import utilities


# Configure the page -----------------------------------------------------------
st.set_page_config(
    page_title="Airbnb Dash | Home",
    page_icon=":hut:",
    layout="wide",
    initial_sidebar_state="auto",
    menu_items=None,
)


cities = CITIES
if "All Cities" not in cities:
    cities.insert(0, "All Cities")


# Configure the sidebar --------------------------------------------------------
# Add session state variable for city selection
st.session_state.selected_city = st.sidebar.selectbox(
    "Which city will we explore?", cities
)

st.sidebar.text("")
st.sidebar.text("")
st.sidebar.markdown("Developed by Ben Harman and powered by Streamlit.")
st.sidebar.markdown("Visit my [website](https://benharman.dev/) for more!")
st.sidebar.text("")
st.sidebar.markdown(
    f"[![LinkedIn](data:image/png;base64,{utilities.get_image_with_encoding('assets/linkedin.png')})](https://github.com/benharmandev) &nbsp;&nbsp;&nbsp; [![GitHub](data:image/png;base64,{utilities.get_image_with_encoding('assets/github.png')})](https://github.com/benharmandev)",
    unsafe_allow_html=True,
)


# Establish a connection to the SQLite database
conn = st.experimental_connection(
    "listings_db",
    type="sql",
    url="sqlite:///data/listings.sqlite",  # SQLite connection URL
)


# Generate metrics--------------------------------------------------------------
listings_count = conn.session.query(func.count(ListingsCore.listing_id)).scalar()
amenities_count = conn.session.query(func.count(Amenities.amenity_id)).scalar()
cities_count = conn.session.query(func.count(Cities.city_id)).scalar()
neighborhoods_count = conn.session.query(
    func.count(Neighborhoods.neighborhood_id)
).scalar()


# Generate listings count by city chart ----------------------------------------
# Define the listings count SQL query
listings_city_counts = pd.DataFrame(
    (
        conn.session.query(
            Cities.name.label("City"),
            func.count(ListingsCore.listing_id).label("Count"),
        )
        .join(ListingsLocation, ListingsLocation.listing_id == ListingsCore.listing_id)
        .join(
            Neighborhoods,
            Neighborhoods.neighborhood_id == ListingsLocation.neighborhood_id,
        )
        .join(Cities, Cities.city_id == Neighborhoods.city_id)
        .group_by(Cities.name)
    ).all()
)

listings_city_counts_chart = (
    alt.Chart(listings_city_counts, title="Listings by City")
    .mark_bar(
        opacity=0.7,
        color=COLORS["nature-green"],
    )
    .encode(
        x=alt.X("Count", sort="-x", axis=alt.Axis(title=None)),
        y=alt.Y("City", sort="-x", axis=alt.Axis(title=None)),
    )
)


# Generate page content --------------------------------------------------------
st.title("Airbnb Advisor")

text_col, padding, chart_col = st.columns((10, 2, 10))

with text_col:
    """
    Welcome to my **Airbnb Advisor** project. This app explores a huge set of Airbnb listings and aims to provide actionable insights for hosts. Whether you're new to hosting or a seasoned veteran, explore select cities and find ways to maximize your profitability, ratings, and visibility.

    ### 📘 Pages at a Glance

    - **📊 Charts & Metrics**: View relevant visuals covering several topics including review scores, amenities, and pricing.
    - **🗺️ Map**: Get a spatial overview of a specific city's listings arranged by neighborhood and their respective metrics.
    - **💻 SQL Exploration**: Dive into the SQL queries and database model that fuel this app's analytics.
    - **🤖 AI Chat**: Got specific questions? My AI assistant is here to answer specific questions about the data.
    - **📖 About**: Background on the data source, methodology, and the person behind this app.

    ### 📚 Data Source

    This app utilizes data from [Inside Airbnb](http://insideairbnb.com/), a project that focuses on the impact of Airbnb on residential communities. The data was last updated on March 6, 2023. Future updates to the app will be contingent upon new, comparable data releases.

    ### ⚠️ Disclaimer
    This app is an independent project and serves as an exploratory tool. While it aims to provide valuable insights, it is not a substitute for professional advice and nuanced understanding of individual listings.
    """

with chart_col:
    st.markdown("### 🗃️ Dataset Overview")

    metric1, metric2, metric3 = st.columns(3)
    metric1.metric("Unique Areas", cities_count)
    metric2.metric("Neighborhoods", neighborhoods_count)
    metric3.metric("Listings", millify(listings_count))

    st.markdown(
        "First review was on **May 3, 2009** and data was last updated on **March 28, 2023**. Listings with no reviews in Q1 2023 were deemed inactive and removed. Host and listing IDs were anonymized and listing geocoordinates removed for privacy."
    )

    st.altair_chart(listings_city_counts_chart, use_container_width=True)
