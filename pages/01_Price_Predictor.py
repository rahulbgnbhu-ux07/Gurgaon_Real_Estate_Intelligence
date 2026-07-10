import streamlit as st
import pickle
import pandas as pd
import numpy as np
import os
import joblib

# ==========================================================
# PAGE CONFIG
# ==========================================================

st.set_page_config(
    page_title="Price Predictor",
    page_icon="💰",
    layout="wide"
)

# ==========================================================
# SIDEBAR
# ==========================================================

with st.sidebar:

    st.title("💰 Price Predictor")

    st.markdown("---")

    st.write("""
Estimate the market value of residential properties in Gurgaon using a Machine Learning Regression model trained on real housing data.

### Prediction Inputs

🏠 Property Type

📍 Sector

🛏 Bedrooms

🚿 Bathrooms

🌇 Balconies

📐 Built-up Area

🏗 Property Age

🛋 Furnishing

⭐ Luxury Category

🏢 Floor Category
""")

    st.markdown("---")

    st.success("Machine Learning Regression Model")

    st.markdown("---")

    st.caption("Developed by Rahul Rai")

# ==========================================================
# LOAD FILES
# ==========================================================

with open("datasets/df.pkl", "rb") as file:
    df = pickle.load(file)

pipeline = joblib.load("datasets/pipeline (2).pkl")

# ==========================================================
# PAGE TITLE
# ==========================================================

st.title("💰 Gurgaon Property Price Predictor")

st.markdown(
    "Predict the estimated market value of residential properties using a trained Machine Learning model."
)

st.divider()

# ==========================================================
# INPUT SECTION
# ==========================================================

st.subheader("📝 Property Information")

left, right = st.columns(2)

# ---------------- LEFT COLUMN ----------------

with left:

    property_type = st.selectbox(
        "Property Type",
        ['flat', 'house']
    )

    sector = st.selectbox(
        "Sector",
        sorted(df['sector'].unique().tolist())
    )

    bedrooms = float(
        st.selectbox(
            "Bedrooms",
            sorted(df['bedRoom'].unique().tolist())
        )
    )

    bathroom = float(
        st.selectbox(
            "Bathrooms",
            sorted(df['bathroom'].unique().tolist())
        )
    )

    balcony = st.selectbox(
        "Balconies",
        sorted(df['balcony'].unique().tolist())
    )

    built_up_area = st.number_input(
        "Built-up Area (Sq.ft)",
        min_value=100.0,
        value=1000.0,
        step=50.0
    )

# ---------------- RIGHT COLUMN ----------------

with right:

    property_age = st.selectbox(
        "Property Age",
        sorted(df['agePossession'].unique().tolist())
    )

    servant_room = float(
        st.selectbox(
            "Servant Room",
            [0.0, 1.0],
            format_func=lambda x: "Yes" if x == 1 else "No"
        )
    )

    store_room = float(
        st.selectbox(
            "Store Room",
            [0.0, 1.0],
            format_func=lambda x: "Yes" if x == 1 else "No"
        )
    )

    furnishing_type = st.selectbox(
        "Furnishing",
        sorted(df['furnishing_type'].unique().tolist())
    )

    luxury_category = st.selectbox(
        "Luxury Category",
        sorted(df['luxury_category'].unique().tolist())
    )

    floor_category = st.selectbox(
        "Floor Category",
        sorted(df['floor_category'].unique().tolist())
    )

st.divider()

predict = st.button(
    "🔮 Predict Property Price",
    use_container_width=True
)
# ==========================================================
# PREDICTION
# ==========================================================

if predict:

    input_data = [[
        property_type,
        sector,
        bedrooms,
        bathroom,
        balcony,
        property_age,
        built_up_area,
        servant_room,
        store_room,
        furnishing_type,
        luxury_category,
        floor_category
    ]]

    columns = [
        'property_type',
        'sector',
        'bedRoom',
        'bathroom',
        'balcony',
        'agePossession',
        'built_up_area',
        'servant room',
        'store room',
        'furnishing_type',
        'luxury_category',
        'floor_category'
    ]

    input_df = pd.DataFrame(input_data, columns=columns)

    # Predict Price
    predicted_price = np.expm1(
        pipeline.predict(input_df)
    )[0]

    lower_price = max(0, predicted_price - 0.22)
    upper_price = predicted_price + 0.22

    st.divider()

    st.subheader("📈 Prediction Result")

    st.success("Prediction completed successfully.")

    # ======================================================
    # METRICS
    # ======================================================

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric(
            label="💰 Estimated Price",
            value=f"₹ {predicted_price:.2f} Cr"
        )

    with col2:
        st.metric(
            label="📉 Minimum Expected",
            value=f"₹ {lower_price:.2f} Cr"
        )

    with col3:
        st.metric(
            label="📈 Maximum Expected",
            value=f"₹ {upper_price:.2f} Cr"
        )

    st.divider()

    # ======================================================
    # SUMMARY
    # ======================================================

    st.markdown("### 🏡 Property Summary")

    summary1, summary2 = st.columns(2)

    with summary1:

        st.write(f"**Property Type:** {property_type.title()}")
        st.write(f"**Sector:** {sector.title()}")
        st.write(f"**Bedrooms:** {int(bedrooms)}")
        st.write(f"**Bathrooms:** {int(bathroom)}")
        st.write(f"**Balconies:** {balcony}")
        st.write(f"**Built-up Area:** {built_up_area:.0f} Sq.ft")

    with summary2:

        st.write(f"**Property Age:** {property_age}")
        st.write(f"**Furnishing:** {furnishing_type}")
        st.write(f"**Luxury Category:** {luxury_category}")
        st.write(f"**Floor Category:** {floor_category}")
        st.write(f"**Servant Room:** {'Yes' if servant_room else 'No'}")
        st.write(f"**Store Room:** {'Yes' if store_room else 'No'}")

    st.divider()

    st.info(
        f"""
### Estimated Market Value

Based on the entered property specifications and the trained Machine Learning model, the estimated market value of this property is **₹ {predicted_price:.2f} Crore**.

The expected price range is between **₹ {lower_price:.2f} Cr** and **₹ {upper_price:.2f} Cr**.

*This prediction is intended as an estimate and actual market prices may vary depending on current market conditions, negotiations, and other property-specific factors.*
"""
    )