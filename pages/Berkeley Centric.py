import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import plotly.express as px
from plotly import graph_objects as go

# Set up the Streamlit page configuration
st.set_page_config(page_title="Berkeley Centric", page_icon="🏛️", layout="wide")
st.title("🏛️ Berkeley Financial Overview")

# Add toggle for historical data (place this after st.title and before the charts)
show_full_history = st.toggle(
    "Show Full History (2008-2024)",
    help="Toggle between full historical view (2008-2024) and recent history (2018-2024)"
)

# Add time series filter
col1, col2 = st.columns(2)
with col1:
    min_year = 2008 if show_full_history else 2018
    max_year = 2024
    time_series_year_range = st.slider(
        "Select Year Range",
        min_value=min_year,
        max_value=max_year,
        value=(min_year, max_year),
        step=1,
        help="Filter data by year range"
    )

# Update year ranges based on toggle and slider
historical_years = [str(year) for year in range(time_series_year_range[0], time_series_year_range[1] + 1)]

# Create connection to Google Sheets
conn = st.connection("gsheets_berkeley", type=GSheetsConnection)
df = conn.read()

# Clean up the data - convert to numeric and handle NaN
numeric_columns = df.columns[2:]  # Skip the first two columns (Legend and Source)
for col in numeric_columns:
    df[col] = pd.to_numeric(df[col].astype(str).str.replace(',', ''), errors='coerce')

# Update category names and add historical data for Industrial Research Funds
name_mapping = {
    'Research (Berkeley only)': 'Industrial Research Funds',
    'reports': 'Industrial Research Subawards',
    'Administration fee': 'EBI-Shell Administration fee'
}
df['Source'] = df['Source'].replace(name_mapping)

# Add historical data for Industrial Research Funds (2008-2017)
historical_data = {
    '2008': 20584189,
    '2009': 25096496,
    '2010': 26605738,
    '2011': 23479193,
    '2012': 24834119,
    '2013': 23661767,
    '2014': 22907166,
    '2015': 15701583,
    '2016': 3307551,
    '2017': 2521255
}

# Add historical data to Industrial Research Funds rows
for year, value in historical_data.items():
    df.loc[df['Source'] == 'Industrial Research Funds', year] = value

# Combine all Awarded Grants entries
awarded_mask = df['Legend'] == 'Awarded grants'
awarded_total = df[awarded_mask].sum(numeric_only=True)
df = df[~awarded_mask]  # Remove individual awarded grant rows

# Create a new row for the combined awarded grants with the correct total
awarded_row = pd.DataFrame({
    'Legend': ['Awarded grants'],
    'Source': ['Awarded grants'],
    '2018': [0],
    '2019': [0],
    '2020': [0],
    '2021': [0],
    '2022': [0],
    '2023': [0],
    '2024': [3522000],  # Updated to exactly 3.522MM
    '2025': [0],
    '2026': [0],
    '2027': [0],
    '2028': [0],
    '2029': [0]
})

df = pd.concat([df, awarded_row], ignore_index=True)

# Remove rows where all numeric values are 0 or null
df = df[df[numeric_columns].sum(axis=1) != 0]

# Calculate totals up to 2024 for pie and bar charts
df['Historical_Total'] = df[historical_years].sum(axis=1)

# Calculate forecast totals (2025-2029)
forecast_years = ['2025', '2026', '2027', '2028', '2029']
df['Forecast_Total'] = df[forecast_years].sum(axis=1)

# Define custom category order only
category_order = [
    'Industrial Research Funds',
    'EBI Squared',
    'Industrial Research Subawards',
    'Awarded grants',
    'EBI-Shell Administration fee'
]

# 1. Historical Pie Chart
st.subheader("EBI Lookback")
# Prepare data for pie chart
pie_data = df[~df['Source'].str.contains('NSF', na=False)].copy()
totals = pie_data[historical_years].sum(axis=1)
pie_data = pie_data[totals > 0].copy()
pie_data['Total'] = totals[totals > 0] / 1_000_000

# Create pie chart without custom colors
fig_pie = go.Figure(data=[go.Pie(
    labels=pie_data['Source'],
    values=pie_data['Total'],
    textinfo='label+value',
    texttemplate='%{label}<br>%{value:.1f}MM'
)])

fig_pie.update_layout(
    title=f'EBI Lookback ({time_series_year_range[0]}-{time_series_year_range[1]})',
    showlegend=True
)

st.plotly_chart(fig_pie, use_container_width=True)

# 2. Historical Bar Chart
historical_data = df[~df['Source'].str.contains('NSF', na=False)].melt(
    id_vars=['Legend', 'Source'],
    value_vars=historical_years,
    var_name='Year',
    value_name='Funding'
)

fig_bar = px.bar(
    historical_data,
    x='Year',
    y='Funding',
    color='Source',
    title=f'Historical Funding by Category ({time_series_year_range[0]}-{time_series_year_range[1]})',
    labels={'Source': 'Category'}
)
fig_bar.update_layout(
    xaxis_title="Year",
    yaxis_title="Funding ($)",
    yaxis_tickformat='$,.0f'
)
st.plotly_chart(fig_bar, use_container_width=True)

# 3. Forecast Chart
forecast_data = df.melt(
    id_vars=['Legend', 'Source'],
    value_vars=forecast_years,
    var_name='Year',
    value_name='Funding'
)

fig_forecast = px.bar(
    forecast_data,
    x='Year',
    y='Funding',
    color='Source',
    title='Funding Forecast (2025-2029)',
    labels={'Source': 'Category'}
)
fig_forecast.update_layout(
    xaxis_title="Year",
    yaxis_title="Funding ($)",
    yaxis_tickformat='$,.0f'
)
st.plotly_chart(fig_forecast, use_container_width=True)

# # Display the DataFrame
# st.subheader("Raw Data")
# st.dataframe(
#     df.style.format({
#         col: "${:,.2f}" for col in df.columns if col not in ['Legend', 'Source']
#     }),
#     use_container_width=True
# )

