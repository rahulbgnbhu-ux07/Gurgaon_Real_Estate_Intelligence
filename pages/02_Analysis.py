from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st
import ast
import matplotlib.pyplot as plt
from wordcloud import WordCloud


st.set_page_config(
    page_title="Gurgaon Market Analysis",
    page_icon="📊",
    layout="wide",
)

DATA_PATH = Path(__file__).resolve().parents[1] / "datasets" / "data_viz1.csv"
REQUIRED_COLUMNS = {
    "property_type",
    "sector",
    "price",
    "price_per_sqft",
    "bedRoom",
    "built_up_area",
    "latitude",
    "longitude",
}


@st.cache_data
def load_data(path: Path) -> pd.DataFrame:
    data = pd.read_csv(path)
    missing_columns = REQUIRED_COLUMNS.difference(data.columns)
    if missing_columns:
        raise ValueError(f"Analysis data is missing columns: {', '.join(sorted(missing_columns))}")
    return data.dropna(subset=["sector", "price", "price_per_sqft", "bedRoom", "built_up_area"])


st.title("Gurgaon Real Estate Analysis")
st.caption("Explore listing prices, property sizes, bedroom mix, and sector-level market patterns.")

if not DATA_PATH.exists():
    st.error(f"Analysis dataset not found: {DATA_PATH}")
    st.stop()

try:
    listings = load_data(DATA_PATH)
except (OSError, ValueError, pd.errors.ParserError) as error:
    st.error(f"Unable to load the analysis dataset: {error}")
    st.stop()

with st.sidebar:
    st.header("Filters")
    property_types = ["All"] + sorted(listings["property_type"].dropna().unique().tolist())
    selected_type = st.selectbox("Property type", property_types)

    sectors = ["All"] + sorted(listings["sector"].dropna().unique().tolist())
    selected_sector = st.selectbox("Sector", sectors)

    bedroom_min = int(listings["bedRoom"].min())
    bedroom_max = int(listings["bedRoom"].max())
    selected_bedrooms = st.slider(
        "Bedrooms",
        min_value=bedroom_min,
        max_value=bedroom_max,
        value=(bedroom_min, bedroom_max),
    )

filtered = listings
if selected_type != "All":
    filtered = filtered[filtered["property_type"] == selected_type]
if selected_sector != "All":
    filtered = filtered[filtered["sector"] == selected_sector]
filtered = filtered[filtered["bedRoom"].between(*selected_bedrooms)]

if filtered.empty:
    st.warning("No listings match the selected filters. Adjust the filters to see market data.")
    st.stop()

metric_columns = st.columns(4)
metric_columns[0].metric("Listings", f"{len(filtered):,}")
metric_columns[1].metric("Median price", f"₹{filtered['price'].median():.2f} Cr")
metric_columns[2].metric("Median price / sq.ft", f"₹{filtered['price_per_sqft'].median():,.0f}")
metric_columns[3].metric("Median built-up area", f"{filtered['built_up_area'].median():,.0f} sq.ft")

market_tab, location_tab, features_tab, listings_tab = st.tabs(
    ["Market overview", "Location insights", "Property features", "Listings"]
)

with market_tab:
    area_chart, bedroom_chart = st.columns(2)
    with area_chart:
        price_by_area = px.scatter(
            filtered,
            x="built_up_area",
            y="price",
            color="bedRoom",
            hover_data=["sector", "property_type", "price_per_sqft"],
            labels={
                "built_up_area": "Built-up area (sq.ft)",
                "price": "Price (Cr)",
                "bedRoom": "Bedrooms",
            },
            title="Price vs. built-up area",
            color_continuous_scale="Tealgrn",
        )
        price_by_area.update_layout(margin=dict(l=10, r=10, t=55, b=10))
        st.plotly_chart(price_by_area, use_container_width=True)

    with bedroom_chart:
        price_by_bedroom = px.box(
            filtered,
            x="bedRoom",
            y="price",
            color="bedRoom",
            points="outliers",
            labels={"bedRoom": "Bedrooms", "price": "Price (Cr)"},
            title="Price range by bedroom count",
            color_discrete_sequence=px.colors.qualitative.Set2,
        )
        price_by_bedroom.update_layout(showlegend=False, margin=dict(l=10, r=10, t=55, b=10))
        st.plotly_chart(price_by_bedroom, use_container_width=True)

    type_counts = filtered["property_type"].value_counts().rename_axis("Property type").reset_index(name="Listings")
    type_chart = px.bar(
        type_counts,
        x="Property type",
        y="Listings",
        color="Property type",
        title="Listings by property type",
        color_discrete_sequence=px.colors.qualitative.Set2,
    )
    type_chart.update_layout(showlegend=False, margin=dict(l=10, r=10, t=55, b=10))
    st.plotly_chart(type_chart, use_container_width=True)

with location_tab:
    sector_summary = (
        filtered.groupby("sector", as_index=False)
        .agg(
            latitude=("latitude", "mean"),
            longitude=("longitude", "mean"),
            median_price=("price", "median"),
            median_price_per_sqft=("price_per_sqft", "median"),
            listings=("price", "size"),
        )
    )
    mapped_sectors = sector_summary.dropna(subset=["latitude", "longitude"])

    if mapped_sectors.empty:
        st.info("Location coordinates are not available for the selected listings.")
    else:
        location_map = px.scatter_map(
            mapped_sectors,
            lat="latitude",
            lon="longitude",
            color="median_price_per_sqft",
            size="listings",
            hover_name="sector",
            hover_data={
                "median_price": ":.2f",
                "median_price_per_sqft": ":,.0f",
                "listings": True,
                "latitude": False,
                "longitude": False,
            },
            map_style="open-street-map",
            zoom=9,
            color_continuous_scale="Viridis",
            labels={
                "median_price_per_sqft": "Median ₹ / sq.ft",
                "median_price": "Median price (Cr)",
                "listings": "Listings",
            },
        )
        location_map.update_layout(height=560, margin=dict(l=0, r=0, t=10, b=0))
        st.plotly_chart(location_map, use_container_width=True)

    st.subheader("Sector summary")
    st.dataframe(
        sector_summary.sort_values("median_price_per_sqft", ascending=False),
        hide_index=True,
        use_container_width=True,
        column_config={
            "median_price": st.column_config.NumberColumn("Median price (Cr)", format="%.2f"),
            "median_price_per_sqft": st.column_config.NumberColumn("Median ₹ / sq.ft", format="%,.0f"),
            "listings": st.column_config.NumberColumn("Listings", format="%d"),
            "latitude": None,
            "longitude": None,
        },
    )


with features_tab:
    st.subheader("Most Common Property Features")
    st.caption("Explore frequently mentioned amenities and property features.")

    # Load the original dataset containing the features column.
    FEATURES_PATH = (
        Path(__file__).resolve().parents[1]
        / "gurgaon_properties.csv"
    )

    if not FEATURES_PATH.exists():
        st.warning(
            "The word cloud dataset was not found. "
            "Please add gurgaon_properties.csv to the project root."
        )
    else:
        try:
            features_df = pd.read_csv(FEATURES_PATH)

            if "features" not in features_df.columns:
                st.warning(
                    "The dataset does not contain a 'features' column."
                )
            else:
                all_features = []

                for item in features_df["features"].dropna():
                    try:
                        parsed = (
                            ast.literal_eval(item)
                            if isinstance(item, str)
                            else item
                        )

                        if isinstance(parsed, (list, tuple, set)):
                            all_features.extend(
                                str(feature) for feature in parsed
                            )
                        elif isinstance(parsed, str):
                            all_features.append(parsed)

                    except (ValueError, SyntaxError):
                        # Skip feature entries that cannot be parsed.
                        continue

                feature_text = " ".join(all_features)

                if feature_text.strip():
                    wordcloud = WordCloud(
                        width=1200,
                        height=600,
                        background_color="white",
                        min_font_size=10,
                        collocations=False,
                    ).generate(feature_text)

                    fig_wc, ax = plt.subplots(figsize=(14, 7))
                    ax.imshow(wordcloud, interpolation="bilinear")
                    ax.axis("off")
                    fig_wc.tight_layout(pad=0)

                    st.pyplot(fig_wc)
                    plt.close(fig_wc)
                else:
                    st.info(
                        "No usable property features were found "
                        "to generate the word cloud."
                    )

        except (OSError, pd.errors.ParserError) as error:
            st.error(f"Unable to load property features: {error}")

with listings_tab:
    st.dataframe(
        filtered.sort_values("price", ascending=False),
        hide_index=True,
        use_container_width=True,
        column_config={
            "price": st.column_config.NumberColumn("Price (Cr)", format="₹%.2f"),
            "price_per_sqft": st.column_config.NumberColumn("Price / sq.ft", format="₹%,.0f"),
            "built_up_area": st.column_config.NumberColumn("Built-up area (sq.ft)", format="%,.0f"),
        },
    )
