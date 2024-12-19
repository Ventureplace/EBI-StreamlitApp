import streamlit as st

st.set_page_config(
    page_title="Hello",
    page_icon="👋",
)

st.write("# EBI Data Dashboard 👋")

st.sidebar.success("Select a page above.")

st.markdown(
    """
    📊 This dashboard displays data from the Energy Biosciences Institute (EBI) research projects.
    
    The app allows you to:
    - 📋 View raw project data in tabular format
    - 🔍 Filter and search projects by industry
    - 📝 See detailed project information including:
        - 👨‍🔬 Principal investigators
        - 👥 Research personnel
        - 📚 Publications and deliverables
    - 📈 Visualize project statistics through interactive charts
    
    **👈 Select a page from the sidebar** to explore the data!
"""
)