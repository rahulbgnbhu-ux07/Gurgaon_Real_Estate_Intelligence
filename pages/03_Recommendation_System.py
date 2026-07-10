import streamlit as st
import pandas as pd
import pickle

# ---------------- PAGE CONFIG ----------------

st.set_page_config(
    page_title="Recommendation System",
    page_icon="🏡",
    layout="wide"
)

# ---------------- SIDEBAR ----------------

with st.sidebar:

    st.title("🏡 Recommendation System")

    st.markdown("---")

    st.write("""
Discover similar residential properties based on your preferred location.

### Recommendation Factors

📍 Nearby Location

🏢 Property Features

⭐ Amenities

🛣 Location Advantages

🏠 Similar Property Characteristics

Select a location and search radius to receive personalized property recommendations.
""")

    st.markdown("---")

    st.success("Content-Based Recommendation Engine")

    st.markdown("---")

    st.caption("Developed by Rahul Rai")

# ---------------- LOAD FILES ----------------

location_df = pickle.load(open("datasets/location_distance.pkl", "rb"))

cosine_sim1 = pickle.load(open("datasets/cosine_sim1.pkl", "rb"))
cosine_sim2 = pickle.load(open("datasets/cosine_sim2.pkl", "rb"))
cosine_sim3 = pickle.load(open("datasets/cosine_sim3.pkl", "rb"))

df = pickle.load(open("datasets/recommendation_df.pkl", "rb"))

# ---------------- FINAL SIMILARITY MATRIX ----------------

cosine_sim = 30 * cosine_sim1 + 20 * cosine_sim2 + 8 * cosine_sim3

# ---------------- RECOMMENDATION FUNCTION ----------------


def recommend_properties(property_name, top_n=5):

    idx = df.index[df["PropertyName"] == property_name].tolist()[0]

    sim_scores = list(enumerate(cosine_sim[idx]))

    sim_scores = sorted(
        sim_scores,
        key=lambda x: x[1],
        reverse=True
    )

    sim_scores = sim_scores[1:top_n + 1]

    property_indices = [i[0] for i in sim_scores]

    scores = [i[1] for i in sim_scores]

    max_score = max(scores)

    match_percentage = [
        round((score / max_score) * 100)
        for score in scores
    ]

    recommendations = pd.DataFrame({

        "Apartment":
            df["PropertyName"].iloc[property_indices].values,

        "Match (%)":
            match_percentage

    })

    return recommendations


# ---------------- USER INTERFACE ----------------

st.title("🏡 Property Recommendation System")

st.write(
    "Find apartments similar to your preferred property using our Content-Based Recommendation Engine."
)

st.divider()

selected_location = st.selectbox(
    "📍 Select Location",
    sorted(location_df.columns.tolist())
)

radius = st.number_input(
    "📏 Radius (Km)",
    min_value=1.0,
    max_value=50.0,
    value=10.0
)

st.divider()

if st.button(
        "🔍 Find Similar Apartments",
        use_container_width=True):

    result = location_df[
        location_df[selected_location] <= radius * 1000
        ][selected_location].sort_values()

    apartment_list = result.index.tolist()

    if len(apartment_list) == 0:

        st.warning("No apartments found within the selected radius.")

    else:

        selected_apartment = st.selectbox(
            "🏠 Select Apartment",
            apartment_list
        )

        st.success(
            f"📍 Selected apartment is **{round(result[selected_apartment] / 1000, 2)} Km** from **{selected_location}**."
        )

        recommendations = recommend_properties(selected_apartment)

        st.divider()

        st.subheader("🏡 Recommended Apartments")

        col1, col2, col3 = st.columns(3)

        col1.metric(
            "Recommendations",
            len(recommendations)
        )

        col2.metric(
            "Search Radius",
            f"{radius} Km"
        )

        col3.metric(
            "Best Match",
            f"{recommendations['Match (%)'].max()}%"
        )

        st.divider()

        for _, row in recommendations.iterrows():

            with st.container(border=True):

                c1, c2 = st.columns([5, 1])

                with c1:

                    st.markdown(
                        f"### 🏠 {row['Apartment']}"
                    )

                    st.write(
                        "This property is recommended because it has similar location, nearby amenities, property characteristics and neighbourhood features."
                    )

                with c2:

                    st.metric(
                        "Match",
                        f"{row['Match (%)']}%"
                    )

                st.progress(row["Match (%)"] / 100)

        st.divider()

        st.info(
            """
**What does Match (%) mean?**

Match (%) represents how closely each apartment matches your selected apartment based on:

• 📍 Location

• 🏢 Property Features

• ⭐ Amenities

• 🛣 Nearby Facilities

• 🏠 Similar Property Characteristics

A higher Match (%) indicates a stronger recommendation.
"""
        )