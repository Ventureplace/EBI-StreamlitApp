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
numeric_columns = df.columns[1:]  # Skip the first column (categories)
for col in numeric_columns:
    df[col] = pd.to_numeric(df[col].astype(str).str.replace(',', ''), errors='coerce')

# Calculate totals up to 2024 for pie and bar charts
historical_years = ['2018', '2019', '2020', '2021', '2022', '2023', '2024']
df['Historical_Total'] = df[historical_years].sum(axis=1)

# Calculate forecast totals (2025-2029)
forecast_years = ['2025', '2026', '2027', '2028', '2029']
df['Forecast_Total'] = df[forecast_years].sum(axis=1)

# 1. Historical Pie Chart
st.subheader("EBI Lookback")
df_without_nsf = df[df[df.columns[0]] != 'NSF']  # Filter out NSF
fig_pie = px.pie(
    df_without_nsf,
    values='Historical_Total',
    names=df.columns[0],  # First column name
    title='EBI Lookback (2018-2024)'
)
fig_pie.update_traces(textinfo='percent+label')
st.plotly_chart(fig_pie, use_container_width=True)

# 2. Historical Bar Chart
historical_data = df[df[df.columns[0]] != 'NSF'].melt(  # Filter out NSF here
    id_vars=[df.columns[0]],
    value_vars=historical_years,
    var_name='Year',
    value_name='Funding'
)

fig_bar = px.bar(
    historical_data,
    x='Year',
    y='Funding',
    color=df.columns[0],  # Use the actual column name
    title='Historical Funding by Category (2018-2024)',
    labels={df.columns[0]: 'Category'}
)
fig_bar.update_layout(
    xaxis_title="Year",
    yaxis_title="Funding ($)",
    yaxis_tickformat='$,.0f'
)
st.plotly_chart(fig_bar, use_container_width=True)

# 3. Forecast Chart
forecast_data = df.melt(
    id_vars=[df.columns[0]],
    value_vars=forecast_years,
    var_name='Year',
    value_name='Funding'
)

fig_forecast = px.bar(
    forecast_data,
    x='Year',
    y='Funding',
    color=df.columns[0],  # Use the actual column name
    title='Funding Forecast (2025-2029)',
    labels={df.columns[0]: 'Category'}
)
fig_forecast.update_layout(
    xaxis_title="Year",
    yaxis_title="Funding ($)",
    yaxis_tickformat='$,.0f'
)
st.plotly_chart(fig_forecast, use_container_width=True)

# Add summary metrics
col1, col2 = st.columns(2)
with col1:
    total_historical = df['Historical_Total'].sum()
    st.metric("Total Historical Funding (2018-2024)", f"${total_historical:,.2f}")
with col2:
    total_forecast = df['Forecast_Total'].sum()
    st.metric("Total Forecast Funding (2025-2029)", f"${total_forecast:,.2f}")

# Display the DataFrame
st.subheader("Raw Data")
st.dataframe(
    df.style.format({
        col: "${:,.2f}" for col in df.columns if col != df.columns[0]  # Format all numeric columns as currency
    }),
    use_container_width=True
)