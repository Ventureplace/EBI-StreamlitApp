import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import plotly.express as px

# Set up the Streamlit page configuration
st.set_page_config(page_title="Berkeley Centric", page_icon="🏛️", layout="wide")
st.title("🏛️ Berkeley Financial Overview")

# Create connection to Google Sheets
conn = st.connection("gsheets_berkeley", type=GSheetsConnection)
df = conn.read()

# Clean up the data - convert to numeric and handle NaN
numeric_columns = df.columns[2:]  # Skip the first two columns (Legend and Source)
for col in numeric_columns:
    df[col] = pd.to_numeric(df[col].astype(str).str.replace(',', ''), errors='coerce')

# Update category names
name_mapping = {
    'Research (Berkeley only)': 'Industrial Research Funds',
    'reports': 'Industrial Research Subawards',
    'Administration fee': 'EBI-Shell Administration fee'
}
df['Source'] = df['Source'].replace(name_mapping)

# Combine all Awarded Grants entries
awarded_mask = df['Legend'] == 'Awarded grants'
# Remove individual awarded grant rows
df = df[~awarded_mask]  

# Create a new row for the combined awarded grants with 3.5MM value
awarded_row = pd.DataFrame({
    'Legend': ['Awarded grants'],
    'Source': ['Awarded grants'],
    '2018': [0],
    '2019': [0],
    '2020': [0],
    '2021': [0],
    '2022': [0],
    '2023': [0],
    '2024': [3500000],  # Set 3.5MM for 2024
    '2025': [0],
    '2026': [0],
    '2027': [0],
    '2028': [0],
    '2029': [0]
})

# Concatenate the new awarded grants row
df = pd.concat([df, awarded_row], ignore_index=True)

# Remove rows where all numeric values are 0 or null
df = df[df[numeric_columns].sum(axis=1) != 0]

# Calculate totals up to 2024 for pie and bar charts
historical_years = ['2018', '2019', '2020', '2021', '2022', '2023', '2024']
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

# Define custom colors for each category
color_map = {
    'Industrial Research Funds': '#0052CC',  # Dark blue
    'EBI Squared': '#99C2FF',               # Light blue
    'Industrial Research Subawards': '#FF4444',  # Red
    'Awarded grants': '#FFCCCC',            # Light pink
    'EBI-Shell Administration fee': '#4DB6AC'  # Teal
}

# 1. Historical Pie Chart
st.subheader("EBI Lookback")
df_without_nsf = df[~df['Source'].str.contains('NSF', na=False)]
df_without_nsf = df_without_nsf[df_without_nsf['Historical_Total'] > 0]
df_without_nsf['Historical_Total_MM'] = df_without_nsf['Historical_Total'] / 1_000_000

fig_pie = px.pie(
    df_without_nsf,
    values='Historical_Total_MM',
    names='Source',
    title='EBI Lookback (2018-2024)',
    category_orders={'Source': category_order},
    color='Source',
    color_discrete_map=color_map
)
fig_pie.update_traces(
    texttemplate="%{value:.1f}MM",
    textinfo='label+value'
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
    title='Historical Funding by Category (2018-2024)',
    labels={'Source': 'Category'},
    category_orders={'Source': category_order},
    color_discrete_map=color_map
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
    labels={'Source': 'Category'},
    category_orders={'Source': category_order},
    color_discrete_map=color_map
)
fig_forecast.update_layout(
    xaxis_title="Year",
    yaxis_title="Funding ($)",
    yaxis_tickformat='$,.0f'
)
st.plotly_chart(fig_forecast, use_container_width=True)

# Display the DataFrame
st.subheader("Raw Data")
st.dataframe(
    df.style.format({
        col: "${:,.2f}" for col in df.columns if col not in ['Legend', 'Source']
    }),
    use_container_width=True
)

