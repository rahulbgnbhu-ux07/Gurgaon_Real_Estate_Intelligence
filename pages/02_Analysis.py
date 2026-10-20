
import ast
import re
from pathlib import Path

import pandas as pd
import streamlit as st
import plotly.express as px
import matplotlib.pyplot as plt
import seaborn as sns
from wordcloud import WordCloud

# --------------------------------------------------
# PAGE CONFIGURATION
# --------------------------------------------------
st.set_page_config(
    page_title="Gurgaon Property Analysis",
    page_icon="🏙️",
    layout="wide"
)

st.title("Gurgaon Real Estate Analysis")
st.caption("Explore property prices, locations, amenities and BHK trends.")

# --------------------------------------------------
# LOAD DATA
# Keep the CSV files in the project root folder.
# --------------------------------------------------
BASE_DIR = Path(__file__).resolve().parent.parent

@st.cache_data
def load_data():
    properties = pd.read_csv(
        BASE_DIR / "gurgaon_properties_missing_value_imputation (1).csv"
    )
    properties_original = pd.read_csv(
        BASE_DIR / "gurgaon_properties.csv"
    )
    latlong = pd.read_csv(BASE_DIR / "latlong.csv")
    return properties, properties_original, latlong

try:
    df, df1, latlong = load_data()
except FileNotFoundError as e:
    st.error(f"Could not find a required CSV file: {e.filename}")
    st.info("Check that all three CSV files are uploaded to your GitHub repository.")
    st.stop()

# --------------------------------------------------
# BASIC DATA SUMMARY
# --------------------------------------------------
st.subheader("Dataset Overview")

c1, c2, c3 = st.columns(3)
c1.metric("Total properties", f"{len(df):,}")

if "sector" in df.columns:
    c2.metric("Unique sectors", f"{df['sector'].nunique():,}")

if "price" in df.columns:
    c3.metric("Average property price", f"{df['price'].mean():,.2f}")

with st.expander("Preview property data"):
    st.dataframe(df.head(20), use_container_width=True)

st.divider()

# --------------------------------------------------
# 1. GURGAON SECTOR MAP
# --------------------------------------------------
st.subheader("1. Gurgaon Property Location Map")

required_cols = {
    "sector", "price", "price_per_sqft", "built_up_area"
}

if required_cols.issubset(df.columns) and "coordinates" in latlong.columns:
    latlong = latlong.copy()

    # Extract latitude and longitude from coordinate strings.
    latlong["latitude"] = pd.to_numeric(
        latlong["coordinates"].astype(str)
        .str.split(",").str[0]
        .str.replace("°", "", regex=False)
        .str.strip(),
        errors="coerce"
    )

    latlong["longitude"] = pd.to_numeric(
        latlong["coordinates"].astype(str)
        .str.split(",").str[1]
        .str.replace("°", "", regex=False)
        .str.strip(),
        errors="coerce"
    )

    map_df = df.merge(latlong, on="sector", how="inner")

    group_df = (
        map_df.groupby("sector", as_index=False)
        .agg(
            price=("price", "mean"),
            price_per_sqft=("price_per_sqft", "mean"),
            built_up_area=("built_up_area", "mean"),
            latitude=("latitude", "mean"),
            longitude=("longitude", "mean")
        )
        .dropna(subset=["latitude", "longitude", "price_per_sqft"])
    )

    if not group_df.empty:
        fig_map = px.scatter_map(
            group_df,
            lat="latitude",
            lon="longitude",
            color="price_per_sqft",
            size="built_up_area",
            hover_name="sector",
            hover_data={
                "price": ":,.2f",
                "price_per_sqft": ":,.2f",
                "built_up_area": ":,.2f",
                "latitude": False,
                "longitude": False
            },
            color_continuous_scale=px.colors.cyclical.IceFire,
            zoom=10,
            map_style="carto-positron",
            title="Average Property Price per Sq Ft by Sector"
        )

        st.plotly_chart(fig_map, use_container_width=True)
    else:
        st.warning("No valid sector coordinates were found.")
else:
    st.warning("The map needs sector, price, price_per_sqft, built_up_area and coordinates columns.")

st.divider()

# --------------------------------------------------
# 2. WORD CLOUD OF PROPERTY FEATURES
# --------------------------------------------------
st.subheader("2. Most Common Property Features")

if "features" in df1.columns:
    feature_lists = []

    def parse_features(value):
        if pd.isna(value):
            return []
        try:
            parsed = ast.literal_eval(value) if isinstance(value, str) else value
            if isinstance(parsed, (list, tuple, set)):
                return [str(x) for x in parsed]
            return [str(parsed)]
        except (ValueError, SyntaxError):
            return [value] if isinstance(value, str) else []

    for item in df1["features"].dropna():
        feature_lists.extend(parse_features(item))

    feature_text = " ".join(feature_lists)

    if feature_text.strip():
        wordcloud = WordCloud(
            width=1000,
            height=600,
            background_color="white",
            stopwords={"s"},
            min_font_size=10
        ).generate(feature_text)

        fig_wc, ax = plt.subplots(figsize=(12, 6))
        ax.imshow(wordcloud, interpolation="bilinear")
        ax.axis("off")
        st.pyplot(fig_wc)
        plt.close(fig_wc)
    else:
        st.info("No usable property features were found.")
else:
    st.warning("The original dataset does not contain a 'features' column.")

st.divider()

# --------------------------------------------------
# 3. BUILT-UP AREA VS PRICE
# --------------------------------------------------
st.subheader("3. Built-up Area vs Property Price")

if {"built_up_area", "price", "bedRoom"}.issubset(df.columns):
    area_df = df[["built_up_area", "price", "bedRoom"]].copy()
    area_df["bedRoom"] = area_df["bedRoom"].astype(str)

    fig_area = px.scatter(
        area_df,
        x="built_up_area",
        y="price",
        color="bedRoom",
        title="Built-up Area vs Price",
        labels={
            "built_up_area": "Built-up Area",
            "price": "Price",
            "bedRoom": "Bedrooms"
        },
        hover_data=["bedRoom"]
    )
    st.plotly_chart(fig_area, use_container_width=True)
else:
    st.warning("Required columns for the area-versus-price chart are missing.")

st.divider()

# --------------------------------------------------
# 4. BEDROOM DISTRIBUTION
# --------------------------------------------------
st.subheader("4. Property Distribution by Number of Bedrooms")

if "bedRoom" in df.columns:
    bedroom_counts = (
        df["bedRoom"].dropna().astype(str)
        .value_counts()
        .rename_axis("Bedrooms")
        .reset_index(name="Properties")
    )

    fig_pie = px.pie(
        bedroom_counts,
        names="Bedrooms",
        values="Properties",
        title="Share of Properties by Bedroom Count",
        hole=0.35
    )
    st.plotly_chart(fig_pie, use_container_width=True)
else:
    st.warning("The dataset does not contain a 'bedRoom' column.")

st.divider()

# --------------------------------------------------
# 5. BHK PRICE RANGE
# --------------------------------------------------
st.subheader("5. Price Range by BHK")

if {"bedRoom", "price"}.issubset(df.columns):
    temp_df = df[
        (df["bedRoom"] <= 4) &
        df["bedRoom"].notna() &
        df["price"].notna()
    ].copy()

    if not temp_df.empty:
        fig_box = px.box(
            temp_df,
            x="bedRoom",
            y="price",
            points="outliers",
            title="Property Price Distribution for Up to 4 Bedrooms",
            labels={
                "bedRoom": "Number of Bedrooms",
                "price": "Price"
            }
        )
        st.plotly_chart(fig_box, use_container_width=True)
    else:
        st.info("No valid properties with four or fewer bedrooms were found.")
else:
    st.warning("Required columns for the BHK price chart are missing.")

st.divider()

# --------------------------------------------------
# 6. HOUSE VS FLAT PRICE DISTRIBUTION
# --------------------------------------------------
st.subheader("6. House vs Flat Price Distribution")

if {"property_type", "price"}.issubset(df.columns):
    type_df = df[
        df["property_type"].astype(str).str.lower().isin(["house", "flat"])
    ].copy()

    if not type_df.empty:
        fig_dist = px.histogram(
            type_df,
            x="price",
            color="property_type",
            histnorm="probability density",
            marginal="box",
            opacity=0.55,
            barmode="overlay",
            nbins=40,
            title="Price Distribution: Houses vs Flats",
            labels={
                "price": "Property Price",
                "property_type": "Property Type"
            }
        )
        st.plotly_chart(fig_dist, use_container_width=True)
    else:
        st.info("No rows labelled 'house' or 'flat' were found.")
else:
    st.warning("Required columns for the house-versus-flat comparison are missing.")

st.divider()
st.caption("Gurgaon Real Estate Intelligence | Data Analysis")
