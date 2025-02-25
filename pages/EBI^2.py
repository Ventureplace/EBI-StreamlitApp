import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import plotly.express as px
from plotly import graph_objects as go


# Set up the Streamlit page configuration
st.set_page_config(page_title="EBI^2", page_icon="🔍", layout="wide")
st.title("🔍 EBI^2")

# Create connection to Google Sheets
conn = st.connection("gsheets_ebi2", type=GSheetsConnection)
df = conn.read()



# Clean column names by removing spaces and special characters
df.columns = df.columns.str.strip().str.replace(' ', '_')

# Top level metrics
col1, col2, col3, col4 = st.columns(4)

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
    total_employees = df['Employees'].sum()
    st.metric(
        "Total Employees",
        f"{total_employees:,}"
    )

with col4:
    active_investors = df['Active_Investors'].nunique()
    st.metric(
        "Active Investors",
        active_investors
    )

    years = list(range(2018, 2026))
ebi_squared_values = [34373, 127839, 50507, 66815, 162304, 118231, 140268, 140268]

# Create bar chart
fig = go.Figure()
fig.add_trace(
    go.Bar(
        x=years,
        y=ebi_squared_values,
        text=[f"${x:,}" for x in ebi_squared_values],
        textposition='auto',
        marker_color='#1f77b4'  # Professional blue color
    )
)

fig.update_layout(
    title="EBI² Annual Budget (2018-2025)",
    xaxis_title="Year",
    yaxis_title="Budget ($)",
    showlegend=False,
    height=500  # Make chart taller for better visibility
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

with right_column:
    # Companies by founding year
    yearly_companies = df['Year_Founded'].value_counts().sort_index()
    
    fig2 = px.line(
        yearly_companies,
        title="Companies Founded by Year",
        labels={'value': 'Number of Companies', 'index': 'Year'}
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

# Add filters in the sidebar
st.sidebar.header("Filters")
industry_filter = st.sidebar.multiselect(
    "Filter by Industry",
    options=sorted(df['Primary_Industry_Code'].unique())
)

year_filter = st.sidebar.slider(
    "Filter by Founded Year",
    min_value=int(df['Year_Founded'].min()),
    max_value=int(df['Year_Founded'].max()),
    value=(int(df['Year_Founded'].min()), int(df['Year_Founded'].max()))
)

# Apply filters if selected
if industry_filter:
    df = df[df['Primary_Industry_Code'].isin(industry_filter)]
if year_filter:
    df = df[df['Year_Founded'].between(year_filter[0], year_filter[1])]

