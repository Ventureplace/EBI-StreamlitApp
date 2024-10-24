import streamlit as st
import gspread
import pandas as pd
from oauth2client.service_account import ServiceAccountCredentials
import plotly.express as px

# Set up Streamlit page
st.set_page_config(
    page_title="Dashboard",
    page_icon="📊",
)

# Access Google Sheet
gc = gspread.service_account()  # No credentials needed for public sheets
sheet = gc.open_by_url('https://docs.google.com/spreadsheets/d/13L0yBtHGAtAYOEegd2pf8bMtR3y2PnN3M0OWOC5de68/edit?usp=sharing')
worksheet = sheet.sheet1
data = worksheet.get_all_records()

# Convert to DataFrame
df = pd.DataFrame(data)

# Group by Industry
industries = df['Industry'].unique()

# Display data as cards
for industry in industries:
    st.header(industry)
    industry_data = df[df['Industry'] == industry]
    for _, row in industry_data.iterrows():
        st.subheader(row['Project Name'])
        st.write(f"Principal Investigator: {row['Principal Investigator']}")
        st.write(f"Year: {row['Year']}")
        st.write(f"Affiliation: {row['Affiliation']}")
        st.write(f"Funding: {row['Funding']}")
        # Add more fields as needed

# Add charts using Plotly
st.header("Funding by Industry")
funding_chart = px.bar(df, x='Industry', y='Funding', color='Industry', title="Funding by Industry")
st.plotly_chart(funding_chart, use_container_width=True)

st.header("Projects Over Time")
time_chart = px.line(df, x='Year', y='Project Name', color='Industry', title="Projects Over Time", markers=True)
st.plotly_chart(time_chart, use_container_width=True)
