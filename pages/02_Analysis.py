import streamlit as st
import pandas as pd
import plotly.express as px
import pickle
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import seaborn as sns

# ==========================================================
# PAGE CONFIG
# ==========================================================

st.set_page_config(
    page_title="Analysis Dashboard",
    page_icon="📊",
    layout="wide"
)

# ==========================================================
# SIDEBAR
# ==========================================================

with st.sidebar:

    st.title("📊 Analytics Dashboard")

    st.markdown("---")

    st.write("""
Explore the Gurgaon real estate market through interactive visualizations and market insights.

### Dashboard Includes

📍 Geographic Analysis

📈 Price Trends

🏘 Sector Analysis

🏠 BHK Distribution

💰 Price Distribution

🏷 Property Features

Each visualization is designed to help understand market behaviour and property trends.
""")

    st.markdown("---")

    st.success("Powered by Plotly")

    st.markdown("---")

    st.caption("Developed by Rahul Rai")

# ==========================================================
# LOAD DATA
# ==========================================================

new_df = pd.read_csv("datasets/data_viz1.csv")

feature_text = pickle.load(open("datasets/feature_text.pkl", "rb"))

numeric_cols = [
    "price",
    "price_per_sqft",
    "built_up_area",
    "latitude",
    "longitude"
]

for col in numeric_cols:
    new_df[col] = pd.to_numeric(new_df[col], errors="coerce")

new_df = new_df.dropna(subset=["latitude", "longitude"])

# ==========================================================
# KPI VALUES
# ==========================================================

total_properties = len(new_df)

total_sectors = new_df["sector"].nunique()

avg_price = round(new_df["price"].mean(), 2)

avg_price_sqft = round(new_df["price_per_sqft"].mean())

# ==========================================================
# DASHBOARD HEADER
# ==========================================================

st.title("📊 Gurgaon Real Estate Analytics Dashboard")

st.write(
    "Explore the Gurgaon housing market using interactive visualizations and business insights."
)

st.divider()

# ==========================================================
# KPI CARDS
# ==========================================================

col1, col2, col3, col4 = st.columns(4)

col1.metric(
    "🏠 Total Properties",
    f"{len(new_df):,}"
)

col2.metric(
    "📍 Sectors",
    new_df["sector"].nunique()
)

col3.metric(
    "💰 Avg Price",
    f"₹ {round(new_df['price'].mean(),2)} Cr"
)

col4.metric(
    "📈 Avg Price/Sq.ft",
    f"₹ {int(new_df['price_per_sqft'].mean()):,}"
)

st.divider()

# ==========================================================
# GEOGRAPHIC ANALYSIS
# ==========================================================

st.markdown("## 📍 Geographic Analysis")

st.caption(
    "Bubble size represents built-up area while colour represents price per sq.ft."
)

sector_list = sorted(new_df["sector"].dropna().unique())

selected_sector = st.selectbox(
    "Select Sector",
    ["All Sectors"] + sector_list
)

if selected_sector == "All Sectors":
    map_df = new_df.copy()
else:
    map_df = new_df[new_df["sector"] == selected_sector]

fig = px.scatter_mapbox(
    map_df,
    lat="latitude",
    lon="longitude",
    color="price_per_sqft",
    size="built_up_area",
    hover_name="society",
    hover_data=[
        "sector",
        "price",
        "bedRoom"
    ],
    zoom=10,
    height=650,
    color_continuous_scale=px.colors.cyclical.IceFire
)

fig.update_layout(
    mapbox_style="open-street-map",
    margin=dict(l=0, r=0, t=0, b=0)
)

with st.container(border=True):
    st.plotly_chart(fig, use_container_width=True)

st.info(
    "This map displays the geographical distribution of properties across Gurgaon. Larger markers indicate larger built-up areas, while colour intensity reflects the price per square foot."
)

st.divider()

# ==========================================================
# MARKET OVERVIEW
# ==========================================================

st.markdown("## 📈 Market Overview")

left, right = st.columns(2)

# ==========================================================
# AREA VS PRICE
# ==========================================================

with left:

    st.subheader("📐 Built-up Area vs Property Price")

    property_type = st.selectbox(
        "Select Property Type",
        ["flat", "house"]
    )

    fig1 = px.scatter(
        new_df[new_df["property_type"] == property_type],
        x="built_up_area",
        y="price",
        color="bedRoom",
        hover_name="society",
        hover_data=[
            "sector",
            "price_per_sqft"
        ]
    )

    st.plotly_chart(
        fig1,
        use_container_width=True
    )

    st.info(
        "This chart shows how built-up area influences property prices. Larger properties generally command higher prices."
    )

# ==========================================================
# WORD CLOUD
# ==========================================================

with right:

    st.subheader("🏷 Property Feature Word Cloud")

    wordcloud = WordCloud(
        width=800,
        height=800,
        background_color="white",
        stopwords=set(["s"]),
        min_font_size=10
    ).generate(feature_text)

    fig_wc, ax = plt.subplots(figsize=(8, 8))

    ax.imshow(wordcloud, interpolation="bilinear")

    ax.axis("off")

    st.pyplot(fig_wc)

    st.info(
        "Frequently occurring amenities and property features extracted from residential listings."
    )

st.divider()

# ==========================================================
# PROPERTY INSIGHTS
# ==========================================================

st.markdown("## 🏠 Property Insights")

left, right = st.columns(2)

# ==========================================================
# BHK DISTRIBUTION
# ==========================================================

with left:

    st.subheader("🏠 BHK Distribution")

    sector_options = sorted(new_df["sector"].dropna().unique().tolist())
    sector_options.insert(0, "Overall")

    selected_sector_pie = st.selectbox(
        "Select Sector",
        sector_options,
        key="pie_sector"
    )

    if selected_sector_pie == "Overall":
        pie_df = new_df.copy()
    else:
        pie_df = new_df[new_df["sector"] == selected_sector_pie]

    bhk_count = pie_df["bedRoom"].value_counts().reset_index()
    bhk_count.columns = ["BHK", "Count"]

    fig2 = px.pie(
        bhk_count,
        names="BHK",
        values="Count",
        hole=0.45,
        color_discrete_sequence=px.colors.qualitative.Set3
    )

    st.plotly_chart(fig2, use_container_width=True)

    st.info(
        "This chart shows the proportion of different BHK configurations available in the selected sector."
    )

# ==========================================================
# BHK PRICE COMPARISON
# ==========================================================

with right:

    st.subheader("💰 BHK-wise Price Comparison")

    selected_sector_box = st.selectbox(
        "Select Sector",
        sector_options,
        key="box_sector"
    )

    if selected_sector_box == "Overall":

        box_df = new_df[
            new_df["bedRoom"] <= 4
        ]

    else:

        box_df = new_df[
            (new_df["sector"] == selected_sector_box) &
            (new_df["bedRoom"] <= 4)
        ]

    fig3 = px.box(
        box_df,
        x="bedRoom",
        y="price",
        color="bedRoom",
        points="outliers"
    )

    st.plotly_chart(fig3, use_container_width=True)

    st.info(
        "Compare the variation in property prices across different BHK categories."
    )

st.divider()

# ==========================================================
# PRICE DISTRIBUTION
# ==========================================================

st.markdown("## 💰 Price Distribution")

st.caption(
    "Compare the overall price distribution of houses and flats."
)

fig4, ax = plt.subplots(figsize=(10,5))

sns.histplot(
    data=new_df[new_df["property_type"]=="house"],
    x="price",
    kde=True,
    stat="density",
    label="House",
    alpha=0.5,
    ax=ax
)

sns.histplot(
    data=new_df[new_df["property_type"]=="flat"],
    x="price",
    kde=True,
    stat="density",
    label="Flat",
    alpha=0.5,
    ax=ax
)

ax.set_xlabel("Price (Cr)")
ax.set_ylabel("Density")
ax.legend()

with st.container(border=True):
    st.pyplot(fig4)

st.info(
    "Independent houses generally show a wider price range than flats due to larger plot sizes and premium locations."
)

st.divider()

# ==========================================================
# KEY MARKET INSIGHTS
# ==========================================================

st.markdown("## 📌 Key Market Insights")

highest_sector = (
    new_df.groupby("sector")["price"]
    .mean()
    .idxmax()
)

highest_price = (
    new_df.groupby("sector")["price"]
    .mean()
    .max()
)

lowest_sector = (
    new_df.groupby("sector")["price"]
    .mean()
    .idxmin()
)

most_common_bhk = (
    int(new_df["bedRoom"].mode()[0])
)

avg_area = int(new_df["built_up_area"].mean())

col1, col2 = st.columns(2)

with col1:

    st.success(f"""
🏆 **Highest Average Price**

**{highest_sector}**

₹ {highest_price:.2f} Cr
""")

    st.success(f"""
🏠 **Most Common Configuration**

**{most_common_bhk} BHK**
""")

with col2:

    st.info(f"""
📍 **Lowest Average Price**

**{lowest_sector}**
""")

    st.info(f"""
📐 **Average Built-up Area**

**{avg_area:,} sq.ft**
""")

st.divider()

st.markdown(
"""
<div style='text-align:center;color:gray'>
📊 Gurgaon Real Estate Analytics Dashboard
<br>
Built using Python • Streamlit • Plotly • Pandas
</div>
""",
unsafe_allow_html=True
)