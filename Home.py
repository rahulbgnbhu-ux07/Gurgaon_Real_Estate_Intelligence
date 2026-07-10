import streamlit as st

# ==========================================================
# PAGE CONFIG
# ==========================================================

st.set_page_config(
    page_title="Gurgaon Real Estate Intelligence",
    page_icon="🏡",
    layout="wide"
)

# ==========================================================
# SIDEBAR
# ==========================================================

with st.sidebar:

    st.title("🏡 Gurgaon Real Estate")

    st.markdown("---")

    st.subheader("🏠 Home")

    st.write("""
Welcome to the Gurgaon Real Estate Intelligence System.

This platform combines Machine Learning, Data Analytics, and a Content-Based Recommendation System to help users explore the Gurgaon housing market.

Navigate using the menu to predict prices, analyze market trends, and discover similar residential properties.
""")

    st.markdown("---")

    st.success("Machine Learning Portfolio Project")

    st.markdown("---")

    st.caption("Developed by Rahul Rai")

# ==========================================================
# TITLE
# ==========================================================

st.title("🏡 Gurgaon Real Estate Intelligence System")

st.markdown("""
### Machine Learning • Data Analytics • Recommendation System

An end-to-end data science application for predicting residential property prices, analysing housing market trends, and recommending similar apartments in Gurgaon.
""")

st.divider()

# ==========================================================
# PROJECT OVERVIEW
# ==========================================================

col1, col2, col3 = st.columns(3)

with col1:

    st.markdown("## 💰 Price Predictor")

    st.write("""
Predicts residential property prices using a trained Machine Learning Regression model.

**Features**

- Property Price Prediction
- Price Range Estimation
- Multiple Property Inputs
- ML Regression Pipeline
""")

with col2:

    st.markdown("## 📊 Analytics Dashboard")

    st.write("""
Interactive dashboard for analysing the Gurgaon real estate market.

**Features**

- Geographic Analysis
- Price Trends
- BHK Distribution
- Area vs Price
- Property Insights
""")

with col3:

    st.markdown("## 🏡 Recommendation System")

    st.write("""
Content-based recommendation engine for discovering similar apartments.

**Features**

- Nearby Apartments
- Similar Properties
- Location-Based Search
- Feature Similarity
""")

st.divider()

# ==========================================================
# TECHNOLOGY STACK
# ==========================================================

st.subheader("🛠 Technology Stack")

tech1, tech2, tech3, tech4 = st.columns(4)

with tech1:
    st.info("""
**Programming**

• Python

• Pandas

• NumPy
""")

with tech2:
    st.info("""
**Machine Learning**

• Scikit-Learn

• Regression Model

• Pipelines
""")

with tech3:
    st.info("""
**Visualization**

• Plotly

• Matplotlib

• Seaborn
""")

with tech4:
    st.info("""
**Framework**

• Streamlit

• Pickle

• WordCloud
""")

st.divider()

# ==========================================================
# PROJECT WORKFLOW
# ==========================================================

st.subheader("📌 Project Workflow")

st.markdown("""
1️⃣ **Data Collection**
- Web Scraping from 99acres

2️⃣ **Data Cleaning & Feature Engineering**
- Missing Value Treatment
- Outlier Handling
- Feature Creation

3️⃣ **Machine Learning**
- Property Price Prediction Model

4️⃣ **Interactive Analytics**
- Market Insights & Visualizations

5️⃣ **Recommendation Engine**
- Similar Property Recommendation using Cosine Similarity
""")

st.divider()

# ==========================================================
# FOOTER
# ==========================================================

st.success("🎯 Developed as a Machine Learning & Data Analytics Portfolio Project")

st.caption("© 2026 Rahul Rai | Gurgaon Real Estate Intelligence System")