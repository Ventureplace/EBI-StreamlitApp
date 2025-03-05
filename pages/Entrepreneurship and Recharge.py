import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import plotly.express as px
from plotly import graph_objects as go


# Set up the Streamlit page configuration
st.set_page_config(page_title="Entrepreneurship and Recharge", page_icon="🔍", layout="wide")
st.title("🔍 Entrepreneurship and Recharge")

# Create connection to Google Sheets
conn = st.connection("gsheets_ebi2", type=GSheetsConnection)
df = conn.read()

# Clean column names by removing spaces and special characters
df.columns = df.columns.str.strip().str.replace(' ', '_')

# Top level metrics
col1, col2, col3 = st.columns(3)

with col1:
    st.metric(
        "Total Companies",
        len(df),
        delta=f"Since {df['Year_Founded'].min()}"
    )

with col2:
    total_raised = df['Total_Raised'].sum()
    st.metric(
        "Total Portfolio Funding",
        f"${total_raised:,.0f}M"
    )

with col3:
    total_employees = int(df['Employees'].sum())
    st.metric(
        "Total Employees",
        f"{total_employees:,}"
    )

# Create connection to Google Sheets
conn = st.connection("gsheets_berkeley", type=GSheetsConnection)
berkeley_df = conn.read()

# Extract years and values for the chart
years = list(range(2018, 2026))  # Keep existing year range

# Get EBI Squared and EBI Recharge data from berkeley_df
ebi_squared_row = berkeley_df[berkeley_df['Legend'] == 'EBI Squared'].iloc[0]
ebi_recharge_row = berkeley_df[berkeley_df['Legend'] == 'EBI Squared'].iloc[1]  # The EBI Recharge row

# Extract values for the selected years
ebi_squared_values = [float(str(ebi_squared_row[str(year)]).replace(',', '')) for year in years]
ebi_recharge_values = [float(str(ebi_recharge_row[str(year)]).replace(',', '') or 0) for year in years]

# Create stacked bar chart
fig = go.Figure()

# Add EBI Squared bars
fig.add_trace(
    go.Bar(
        x=years,
        y=ebi_squared_values,
        name='EBI²',
        text=[f"${x:,.0f}" for x in ebi_squared_values],
        textposition='auto',
        marker_color='#1f77b4'
    )
)

# Add EBI Recharge bars
fig.add_trace(
    go.Bar(
        x=years,
        y=ebi_recharge_values,
        name='EBI Recharge',
        text=[f"${x:,.0f}" for x in ebi_recharge_values],
        textposition='auto',
        marker_color='#2ca02c'
    )
)

fig.update_layout(
    title="Entrepreneurship and Recharge Annual Budget (2018-2025)",
    xaxis_title="Year",
    yaxis_title="Budget ($)",
    barmode='stack',
    height=500,
    showlegend=True,
    legend=dict(
        orientation="h",
        yanchor="bottom",
        y=1.02,
        xanchor="right",
        x=1
    )
)

# Display chart
st.plotly_chart(fig, use_container_width=True)

# Create two columns for main charts
left_column, right_column = st.columns(2)

with left_column:
    # Funding by Industry
    industry_funding = df.groupby('Primary_Industry_Code')['Total_Raised'].sum().sort_values(ascending=True)
    
    fig1 = px.bar(
        industry_funding,
        orientation='h',
        title="Total Funding by Industry",
        labels={'value': 'Total Raised ($M)', 'Primary_Industry_Code': 'Industry'}
    )
    fig1.update_layout(height=400)
    st.plotly_chart(fig1, use_container_width=True)
    st.caption("*Data sourced from PitchBook - values may not be fully accurate or up to date")

with right_column:
    # Employee distribution by industry
    industry_employees = df.groupby('Primary_Industry_Code')['Employees'].sum().sort_values(ascending=True)
    
    fig2 = px.bar(
        industry_employees,
        orientation='h',
        title="Total Employees by Industry",
        labels={'value': 'Number of Employees', 'Primary_Industry_Code': 'Industry'}
    )
    fig2.update_layout(height=400)
    st.plotly_chart(fig2, use_container_width=True)

# Create single column for additional chart
col1 = st.columns(1)[0]

with col1:
    # Funds raised by company (top 10)
    company_funding = df.nlargest(10, 'Total_Raised')[['Company', 'Total_Raised']]
    fig3 = px.bar(
        company_funding,
        x='Company',
        y='Total_Raised',
        title="Top 10 Companies by Funds Raised",
        labels={'Total_Raised': 'Total Raised ($M)', 'Company': 'Company Name'}
    )
    # Rotate x-axis labels for better readability
    fig3.update_layout(
        xaxis_tickangle=-45,
        height=400
    )
    st.plotly_chart(fig3, use_container_width=True)
    st.caption("*Data sourced from PitchBook - values may not be fully accurate or up to date")

# Company Details Section
st.markdown("---")
st.header("Company Details")

# Searchable company table
search = st.text_input("Search Companies", "")
if search:
    filtered_df = df[df['Company'].str.contains(search, case=False)]
else:
    filtered_df = df

# Show interactive table with key columns
st.dataframe(
    filtered_df[[
        'Company', 
        'Total_Raised',
        'Employees',
        'Primary_Industry_Code',
        'Last_Financing_Date',
        'Last_Financing_Size',
        'Website'
    ]],
    hide_index=True
)

# # Add filters in the sidebar
# st.sidebar.header("Filters")
# industry_filter = st.sidebar.multiselect(
#     "Filter by Industry",
#     options=sorted(df['Primary_Industry_Code'].unique())
# )

# year_filter = st.sidebar.slider(
#     "Filter by Founded Year",
#     min_value=int(df['Year_Founded'].min()),
#     max_value=int(df['Year_Founded'].max()),
#     value=(int(df['Year_Founded'].min()), int(df['Year_Founded'].max()))
# )

# # Apply filters if selected
# if industry_filter:
#     df = df[df['Primary_Industry_Code'].isin(industry_filter)]
# if year_filter:
#     df = df[df['Year_Founded'].between(year_filter[0], year_filter[1])]

# # Display the dataframe with column filters and sorting capabilities
# st.subheader("Raw Data")
# st.dataframe(
#     df,
#     use_container_width=True,
#     hide_index=True,
#     column_config={
#         col: st.column_config.NumberColumn(format="${:,.0f}") 
#         for col in df.select_dtypes(include=['float64', 'int64']).columns
#     }
# )


