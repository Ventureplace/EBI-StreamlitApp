import streamlit as st
import pandas as pd
import plotly.express as px
from streamlit_gsheets import GSheetsConnection
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail

# Set up the Streamlit page configuration with a wide layout and IP Dashboard title/icon
st.set_page_config(page_title="IP Dashboard", page_icon="📄",layout="wide")
st.title("📄 IP Dashboard")
st.write(
    """
    This app displays Intellectual Property data from a Google Sheet, organized by industry,
    and provides visualizations of IP types and document counts.
    """
)

# Create connection to Google Sheets using the gsheets_ip connection defined in secrets.toml
conn = st.connection("gsheets_ip", type=GSheetsConnection)
# Read the data from the connected Google Sheet into a pandas DataFrame
df = conn.read()

# Convert the Application Year column to string type for consistent display
df['Application_YR'] = df['Application_YR'].astype(str)

# Display all column names in the DataFrame for debugging/reference
st.write(df.columns.tolist())

# Show the DataFrame in a Streamlit table widget
# Specify column order to display most relevant columns first
# Use full container width for better visibility
st.dataframe(df,
column_order = ['Application_YR','PI','Company','Country', 'Institution','Discipline', 'Program' , 'Patent Title'],
use_container_width=True )








# Show some metrics and charts about the data
# Display header for IP metrics section
st.header("Successful IP Metrics")

# Create 4 equal columns for metrics
col1, col2, col3, col4 = st.columns(4)

# Display total number of unique inventions
with col1:
    st.metric(label="Total IPs📝", value=df['Patent Title'].nunique())

# Display number of Shell inventions by filtering Company column
with col2:
    st.metric(label="Total Shell IPs🐚", value=df[df['Sponsor'] == 'Shell']['Patent Title'].nunique())

# Display number of BP inventions by filtering Company column  
with col3:
    st.metric(label="Total BP IPs☀️", value=df[df['Sponsor'] == 'BP']['Patent Title'].nunique())

# Display total number of unique Principal Investigators
with col4:
    st.metric(label="Total PI's 👨‍🔬", value=df['PI'].nunique())



# Create 4 columns with large gaps
col5 , col6, col7, col8 = st.columns(4,gap ='large')

# Create 2 columns of equal width (0.5 each) for first row
col5, col6, = st.columns([0.5, 0.5])

# Create 2 columns of equal width (0.5 each) for second row 
col7, col8, = st.columns([0.5, 0.5])

with col5:
    # Count number of patents per discipline
    discipline_counts = df.groupby('Discipline')['Patent Title'].nunique().reset_index()
    discipline_counts = discipline_counts.sort_values('Patent Title', ascending=False)

    # Create histogram showing patent distribution across disciplines
    fig = px.bar(discipline_counts,
                x='Discipline',
                y='Patent Title',
                title='Distribution of Patents by Discipline',
                labels={'Discipline': 'Research Discipline',
                       'Patent Title': 'Number of Patents'},
                color='Discipline',  # Color bars by discipline
                height=500)

    # Update layout for better readability
    fig.update_layout(
        xaxis_tickangle=-45,  # Angle discipline names for better fit
        showlegend=False,  # No need for legend since discipline is on x-axis
        margin=dict(b=100),  # Add bottom margin for rotated labels
        yaxis_title="Number of Patents"
    )

    st.plotly_chart(fig, use_container_width=True)

    # Create bar chart showing total patent counts by company (needed for col6)
    company_counts = df.groupby('Sponsor')['Patent Title'].nunique().reset_index()



with col6:
    fig = px.bar(company_counts,
                x='Sponsor',
                y='Patent Title',
                title='Total Patents by Sponsor',
                labels={'Patent Title': 'Number of Patents',
                        'Sponsor': 'Sponsor'},
                color='Sponsor',  # Color bars by company 
                height=500)

    # Update layout for better readability
    fig.update_layout(
        showlegend=False,  # No need for legend since company is on x-axis
        margin=dict(b=50),
        yaxis_title="Number of Patents"
    )

    st.plotly_chart(fig, use_container_width=True)
    
with col7:
    # Count number of IPs per PI
    pi_counts = df.groupby('PI')['Patent Title'].nunique().reset_index()
    pi_counts = pi_counts.sort_values('Patent Title', ascending=False)

    fig = px.bar(pi_counts,
                x='PI',
                y='Patent Title', 
                title='Number of IPs by Principal Investigator',
                labels={'PI': 'Principal Investigator',
                        'Patent Title': 'Number of IPs'},
                height=500)

    fig.update_layout(
        xaxis_tickangle=-45,  # Angle PI names for better fit
        showlegend=False,
        margin=dict(b=100),  # Add bottom margin for rotated labels
        yaxis_title="Number of IPs"
    )

    st.plotly_chart(fig, use_container_width=True)


with col8:
    # Count number of patents per institution and calculate percentages
    institution_counts = df.groupby('Institution')['Patent Title'].nunique().reset_index()
    institution_counts['Percentage'] = (institution_counts['Patent Title'] / institution_counts['Patent Title'].sum()) * 100

    # Create pie chart showing distribution of patents across institutions
    fig = px.pie(institution_counts,
                values='Patent Title',
                names='Institution',
                title='Distribution of Patents by Institution (%)',
                height=500)

    # Update layout for better readability
    fig.update_layout(
        showlegend=True,
        legend_title='Institution',
        margin=dict(b=50)
    )

    # Add percentage labels to pie slices
    fig.update_traces(textposition='inside', textinfo='percent+label')

    st.plotly_chart(fig, use_container_width=True)



# Add custom chart section
st.header("Custom Charts")
st.write("Create custom charts by selecting variables to compare")

# Create columns for variable and chart type selection
col_select1, col_select2, col_select3 = st.columns(3)

with col_select1:
    # First variable selector
    x_var = st.selectbox(
        "Select X-axis variable",
        options=['PI', 'Institution', 'Filing Type', 'Lead Inv Dept', 'Lead Sponsor'],
        help="Choose the variable for the X-axis"
    )

with col_select2:
    # Second variable selector for y-axis metric
    y_metric = st.selectbox(
        "Select analysis metric",
        options=['Count', 'Percentage'],
        help="Choose how to measure the data"
    )

with col_select3:
    # Chart type selector
    chart_type = st.selectbox(
        "Select chart type",
        options=['Bar Chart', 'Pie Chart', 'Line Chart', 'Scatter Plot'],
        help="Choose the type of chart to display"
    )

# Generate dynamic chart based on selections
custom_counts = df.groupby(x_var)['Patent Title'].nunique().reset_index()

if y_metric == 'Percentage':
    custom_counts['Value'] = (custom_counts['Patent Title'] / custom_counts['Patent Title'].sum()) * 100
    y_axis_title = "Percentage (%)"
else:
    custom_counts['Value'] = custom_counts['Patent Title']
    y_axis_title = "Count"

# Create dynamic chart based on selected type
if chart_type == 'Bar Chart':
    fig = px.bar(custom_counts,
                x=x_var,
                y='Value',
                title=f'{y_metric} of IPs by {x_var}',
                labels={x_var: x_var, 'Value': y_axis_title},
                height=500)
    
    fig.update_layout(
        xaxis_tickangle=-45,
        showlegend=False,
        margin=dict(b=100),
        yaxis_title=y_axis_title
    )

elif chart_type == 'Pie Chart':
    fig = px.pie(custom_counts,
                values='Value',
                names=x_var,
                title=f'Distribution of IPs by {x_var} ({y_metric})',
                height=500)
    
    fig.update_layout(
        showlegend=True,
        legend_title=x_var,
        margin=dict(b=50)
    )
    
    fig.update_traces(textposition='inside', textinfo='percent+label')

elif chart_type == 'Line Chart':
    fig = px.line(custom_counts,
                x=x_var,
                y='Value',
                title=f'{y_metric} of IPs by {x_var}',
                labels={x_var: x_var, 'Value': y_axis_title},
                height=500)
    
    fig.update_layout(
        xaxis_tickangle=-45,
        showlegend=False,
        margin=dict(b=100),
        yaxis_title=y_axis_title
    )

else:  # Scatter Plot
    fig = px.scatter(custom_counts,
                    x=x_var,
                    y='Value',
                    title=f'{y_metric} of IPs by {x_var}',
                    labels={x_var: x_var, 'Value': y_axis_title},
                    height=500)
    
    fig.update_layout(
        xaxis_tickangle=-45,
        showlegend=False,
        margin=dict(b=100),
        yaxis_title=y_axis_title
    )

st.plotly_chart(fig, use_container_width=True)

# # Form to submit new IP
# st.header("Submit New Case")
# with st.form("ip_form"):
#     case_no = st.text_input("Case Number")
#     case_title = st.text_input("Case Title")
#     lead_inv = st.text_input("Lead Inventor")
#     mktg_stat = st.selectbox("Marketing Status", df['Mktg Stat'].unique())
#     pros_stat = st.selectbox("Prosecution Status", df['Pros Stat'].unique())
#     filing_type = st.selectbox("Filing Type", df['Filing Type'].unique())
#     us_app_no = st.text_input("US Application Number")
#     us_app_dt = st.date_input("US Application Date")
#     lead_sponsor = st.text_input("Lead Sponsor")
#     lead_inv_dept = st.selectbox("Lead Inventor Department", df['Lead Inv Dept'].unique())
#     submitted = st.form_submit_button("Submit")

# if submitted:
#     # Modify email content for new schema
#     message = Mail(
#         from_email='iyanjgodwin@gmail.com',
#         to_emails='iyanjgodwin@gmail.com',
#         subject='New Case Submission',
#         plain_text_content=f"""
#         New Case Submission:
#         Case Number: {case_no}
#         Case Title: {case_title}
#         Lead Inventor: {lead_inv}
#         Marketing Status: {mktg_stat}
#         Prosecution Status: {pros_stat}
#         Filing Type: {filing_type}
#         US Application Number: {us_app_no}
#         US Application Date: {us_app_dt}
#         Lead Sponsor: {lead_sponsor}
#         Lead Inventor Department: {lead_inv_dept}
#         """
#     )

#     try:
#         sg = SendGridAPIClient(st.secrets["sendgrid"]["api_key"])
#         response = sg.send(message)
#         st.success("Case submitted and email sent for approval.")
#     except Exception as e:
#         st.error(f"Error sending email: {e}")

# Note: The actual writing to a database after approval is not implemented here.


##bp and shell pie chart

#quick qc