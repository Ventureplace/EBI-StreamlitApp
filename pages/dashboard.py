import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from streamlit_gsheets import GSheetsConnection

st.set_page_config(page_title="Research Dashboard", page_icon="📊", layout="wide")
st.title("Research Projects and Funding Dashboard")

@st.cache_data(ttl=600)
def load_data():
    conn_dashboard = st.connection("gsheets_dashboard", type=GSheetsConnection)
    conn_funding = st.connection("gsheets_funding", type=GSheetsConnection)
    return conn_dashboard.read(), conn_funding.read()

# This function removes duplicate projects and consolidates Principle Investigator names
def consolidate_data(df):
    # Remove duplicate rows based on "Project Name"
    df = df.drop_duplicates(subset=["Project Name"], keep="first")
    
    # First, fill NaN values with a placeholder or remove rows with NaN PIs
    df = df.dropna(subset=['Principle Investigator'])  # Remove rows where PI is NaN
    
    # Use simple approximate matching to unify PI names
    import difflib
    name_map = {}
    for pi_name in df['Principle Investigator'].unique():
        best_match = difflib.get_close_matches(pi_name, list(name_map.keys()), n=1, cutoff=0.8)
        if best_match:
            name_map[pi_name] = best_match[0]
        else:
            name_map[pi_name] = pi_name
            
    df['Principle Investigator'] = df['Principle Investigator'].apply(lambda x: name_map[x])
    return df

projects_df, funding_df = load_data()
projects_df = consolidate_data(projects_df)



# Advanced search functionality
def search_dataframe(df, search_term):
    """
    Search across multiple columns and return matching rows with highlighted search results
    """
    if not search_term:
        return df, None
    
    # Define columns to search in
    search_columns = [
        "Discipline", "Program", "Project Name", "Principle Investigator",
        "Personnel", "Institution", "Productivity and Deliverables", "Sponsor"
    ]
    
    # Create a mask for each column
    masks = []
    for col in search_columns:
        if col in df.columns:  # Check if column exists
            masks.append(df[col].astype(str).str.contains(search_term, case=False, na=False))
    
    # Combine all masks with OR operation
    final_mask = pd.concat(masks, axis=1).any(axis=1)
    return df[final_mask], final_mask

# Create search interface
st.write("### Search Projects and PIs")
col1, col2 = st.columns([3, 1])
with col1:
    search_term = st.text_input("Search across all fields", "")
with col2:
    search_type = st.selectbox(
        "Filter by",
        ["All", "PI", "Institution", "Program", "Discipline"]
    )

if search_term:
    filtered_df, mask = search_dataframe(projects_df, search_term)
    
    if not filtered_df.empty:
        st.write(f"Found {len(filtered_df)} matching results")
        
        # If searching specifically for a PI
        if search_type == "PI":
            pi_projects = filtered_df.groupby("Principle Investigator")
            
            for pi, projects in pi_projects:
                with st.expander(f"📊 {pi} ({len(projects)} projects)"):
                    # PI Summary
                    st.write("#### Summary")
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("Total Projects", len(projects))
                    with col2:
                        st.metric("Institutions", projects['Institution'].nunique())
                    with col3:
                        st.metric("Programs", projects['Program'].nunique())
                    
                    # Project Details
                    st.write("#### Projects")
                    for _, project in projects.iterrows():
                        with st.container():
                            st.markdown(f"""
                            **Project:** {project['Project Name']}  
                            **Program:** {project['Program']}  
                            **Institution:** {project['Institution']}  
                            **Deliverables:** {project['Productivity and Deliverables']}
                            ---
                            """)
        else:
            # Display regular search results
            st.dataframe(
                filtered_df,
                use_container_width=True,
                height=400
            )
    else:
        st.warning("No matching results found")

st.write("### Dataset Overview")
st.write(f"Number of rows: {projects_df.shape[0]}")
st.write(f"Number of columns: {projects_df.shape[1]}")
st.write("\n### Column Names:")
st.write(projects_df.columns.tolist())

# Create metrics
col1, col2, col3 = st.columns([1, 1, 1], gap="medium")

with col1:
    total_projects = len(projects_df)
    st.metric("Total Projects", total_projects)

with col2:
    total_pis = projects_df['Principle Investigator'].nunique()
    st.metric("Total PIs", total_pis)

with col3:
    total_programs = projects_df['Program'].nunique()
    st.metric("Total Programs", total_programs)

# Create visualizations
col5, col6 = st.columns(2)

with col5:
    # Projects by Program
    program_counts = projects_df['Program'].value_counts().reset_index()
    fig1 = px.bar(program_counts, 
                  x='Program', 
                  y='count',
                  title='Projects by Program')
    st.plotly_chart(fig1, use_container_width=True)

with col6:
    # Projects by Program
    program_counts = projects_df['Program'].value_counts().reset_index()
    fig2 = px.pie(program_counts, 
                  values='count', 
                  names='Program',
                  title='Distribution by Program')
    st.plotly_chart(fig2, use_container_width=True)


# Load data from both sheets
conn_funding = st.connection("gsheets_funding", type=GSheetsConnection)
conn_admin = st.connection("gsheets_admin", type=GSheetsConnection)

funding_df = conn_funding.read()
admin_df = conn_admin.read()

# Extract values
berkeley_research_earnings = 48_858_138.26  # Total Berkeley research earnings
berkeley_admin_earnings = 1_907_444.95 + 35_846_686.11     # Total Berkeley admin earnings

# Create pie chart data
ebi_distribution = pd.DataFrame({
    'Category': ["Berkeley's Earnings Admin", "Berkeley's Earnings Research"],
    'Amount': [berkeley_admin_earnings, berkeley_research_earnings]
})

# Display total amounts
st.header("Total EBI Contribution to Campus")
col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Berkeley Research Funds", f"${berkeley_research_earnings:,.2f}")
with col2:
    st.metric("Non-Research Funds", f"${berkeley_admin_earnings:,.2f}") 
with col3:
    total_funds = berkeley_research_earnings + berkeley_admin_earnings
    st.metric("Total Funds", f"${total_funds:,.2f}")


def load_finance_data():
    # Load data from Google Sheets
    conn_funding = st.connection("gsheets_funding", type=GSheetsConnection)
    df = conn_funding.read()
    
    # Remove rows after the actual data (notes, totals, etc.)
    df = df[df['Type'].notna()]  # Keep only rows with a valid Type
    
    # Fill NaN values with 0
    df = df.fillna(0)
    
    # Convert string numbers to float for numeric columns
    for col in df.columns:
        if col not in ['Gift', 'Type', 'PI']:
            try:
                df[col] = df[col].astype(str).str.replace(',', '').astype(float)
            except ValueError:
                print(f"Warning: Could not convert column {col}")
                df[col] = 0
    
    return df

def create_funding_type_chart(df):
    # Calculate total actual funding by type per year
    research_total = []
    subaward_total = []
    years = range(2008, 2024)
    
    for year in years:
        research_mask = df['Type'] == 'Research'
        subaward_mask = df['Type'] == 'Sub-award'
        
        research_total.append(df[research_mask][f'{year} Actual'].sum())
        subaward_total.append(df[subaward_mask][f'{year} Actual'].sum())
    
    fig = go.Figure()
    fig.add_trace(go.Bar(x=list(years), y=research_total, name='Research'))
    fig.add_trace(go.Bar(x=list(years), y=subaward_total, name='Sub-award'))
    
    fig.update_layout(
        title='Research vs Sub-award Funding by Year',
        barmode='stack',
        xaxis_title='Year',
        yaxis_title='Funding Amount ($)'
    )
    
    return fig

def create_top_pi_chart(df):
    # Calculate total funding per PI
    pi_totals = []
    for _, row in df.iterrows():
        total = sum(row[f'{year} Actual'] for year in range(2008, 2024))
        pi_totals.append({'PI': row['PI'], 'Total': total})
    
    pi_df = pd.DataFrame(pi_totals)
    top_10 = pi_df.nlargest(10, 'Total')
    
    fig = px.bar(top_10, 
                 x='PI', 
                 y='Total',
                 title='Top 10 Funded Principal Investigators')
    
    return fig

def analyze_program_funding(finance_df, productivity_df):
    productivity_df['Last_Name'] = productivity_df['Principle Investigator'].str.split().str[-1]
    
    merged_df = pd.merge(
        finance_df,
        productivity_df[['Last_Name', 'Program', 'Discipline']],
        left_on='PI',
        right_on='Last_Name',
        how='inner'
    )
    
    # Calculate total funding by discipline
    discipline_funding = []
    # Get yearly funding by discipline
    discipline_yearly_funding = {}
    
    for discipline in merged_df['Discipline'].unique():
        discipline_data = merged_df[merged_df['Discipline'] == discipline]
        total_funding = 0
        yearly_totals = {}
        
        for year in range(2008, 2024):
            actual_col = f'{year} Actual'
            if actual_col in discipline_data.columns:
                year_total = discipline_data[actual_col].sum()
                total_funding += year_total
                yearly_totals[year] = year_total
        
        discipline_funding.append({
            'Discipline': discipline,
            'Total_Funding': total_funding,
            'Number_of_PIs': len(discipline_data['PI'].unique())
        })
        discipline_yearly_funding[discipline] = yearly_totals
    
    return pd.DataFrame(discipline_funding), merged_df, discipline_yearly_funding

def analyze_institution_funding(finance_df, productivity_df):
    # Merge finance and productivity data
    productivity_df['Last_Name'] = productivity_df['Principle Investigator'].str.split().str[-1]
    
    merged_df = pd.merge(
        finance_df,
        productivity_df[['Last_Name', 'Institution', 'Sponsor']],
        left_on='PI',
        right_on='Last_Name',
        how='inner'
    )
    
    # Calculate total funding per institution for BP period (2008-2015)
    bp_funding = {}
    for institution in merged_df['Institution'].unique():
        inst_data = merged_df[merged_df['Institution'] == institution]
        total = 0
        for year in range(2008, 2016):
            actual_col = f'{year} Actual'
            if actual_col in inst_data.columns:
                total += inst_data[actual_col].sum()
        bp_funding[institution] = total

    # Calculate total funding per institution for Shell period (2016-2024)
    shell_funding = {}
    for institution in merged_df['Institution'].unique():
        inst_data = merged_df[merged_df['Institution'] == institution]
        total = 0
        for year in range(2016, 2024):
            actual_col = f'{year} Actual'
            if actual_col in inst_data.columns:
                total += inst_data[actual_col].sum()
        shell_funding[institution] = total

    return bp_funding, shell_funding

# Create visualizations
st.header("Program Funding Analysis")

# Load and prepare data
finance_df = load_finance_data()
conn_dashboard = st.connection("gsheets_dashboard", type=GSheetsConnection)
productivity_df = conn_dashboard.read()

# Get program funding data and merged dataframe
program_funding_df, merged_df, yearly_funding = analyze_program_funding(finance_df, productivity_df)
program_funding_df = program_funding_df.sort_values('Total_Funding', ascending=False)

# Original total funding bar chart
fig_program = px.bar(program_funding_df,
                     x='Discipline',
                     y='Total_Funding',
                     text='Number_of_PIs',
                     title='Total Funding by Program')

fig_program.update_layout(
    xaxis_title="Program",
    yaxis_title="Total Funding ($)",
    yaxis_tickformat='$,.0f'
)

fig_program.update_traces(
    texttemplate='%{text} PIs',
    textposition='outside'
)
st.plotly_chart(fig_program, use_container_width=True)

# Create time series data
time_series_data = []
for discipline, yearly_data in yearly_funding.items():
    for year, amount in yearly_data.items():
        time_series_data.append({
            'Discipline': discipline,
            'Year': year,
            'Funding': amount
        })

time_series_df = pd.DataFrame(time_series_data)

# Create time series chart
fig_time_series = px.line(time_series_df, 
                         x='Year', 
                         y='Funding', 
                         color='Discipline',
                         title='Funding by Program Over Time')

fig_time_series.update_layout(
    xaxis_title="Year",
    yaxis_title="Funding ($)",
    yaxis_tickformat='$,.0f'
)

st.plotly_chart(fig_time_series, use_container_width=True)

bp_dist, shell_dist = analyze_institution_funding(finance_df, productivity_df)


# Calculate combined funding
combined_funding = {}
for institution in set(bp_dist.keys()) | set(shell_dist.keys()):
    combined_funding[institution] = bp_dist.get(institution, 0) + shell_dist.get(institution, 0)

# Create combined funding visualization below the two columns
st.markdown("---")  # Add a visual separator
st.subheader("Total Combined Funding Distribution (2008-2024)")
# Filter out institutions with zero funding
filtered_funding = {k: v for k, v in combined_funding.items() if v > 0}

fig_combined = px.pie(
    values=list(filtered_funding.values()),
    names=list(filtered_funding.keys()),
    title='Combined Funding Distribution by Institution (2008-2024)'
)
fig_combined.update_traces(textinfo='percent+label')
st.plotly_chart(fig_combined, use_container_width=True)


# Create institution funding visualizations
st.header("Institution Funding Distribution")
col1, col2 = st.columns(2)

with col1:
    # Filter out null/zero values for BP
    bp_filtered = {k: v for k, v in bp_dist.items() if v and v > 0}
    fig_bp = px.pie(
        values=list(bp_filtered.values()),
        names=list(bp_filtered.keys()),
        title='BP Funding Distribution by Institution (2008-2015)'
    )
    fig_bp.update_traces(textinfo='percent+label')
    st.plotly_chart(fig_bp, use_container_width=True)

with col2:
    # Filter out null/zero values for Shell  
    shell_filtered = {k: v for k, v in shell_dist.items() if v and v > 0}
    fig_shell = px.pie(
        values=list(shell_filtered.values()),
        names=list(shell_filtered.keys()),
        title='Shell Funding Distribution by Institution (2016-2024)'
    )
    fig_shell.update_traces(textinfo='percent+label')
    st.plotly_chart(fig_shell, use_container_width=True)







# Now show the program details
st.subheader("Program Details")
for program in merged_df['Program'].unique():
    program_data = merged_df[merged_df['Program'] == program]
    total_funding = sum(
        program_data[f'{year} Actual'].sum() 
        for year in range(2008, 2024) 
        if f'{year} Actual' in program_data.columns
    )
    
    with st.expander(f"{program} (${total_funding:,.2f})"):
        # Get PIs and their funding for this program
        program_pis = merged_df[merged_df['Program'] == program]
        pi_funding = []
        
        for pi in program_pis['PI'].unique():
            pi_data = program_pis[program_pis['PI'] == pi]
            total = 0
            for year in range(2008, 2024):
                actual_col = f'{year} Actual'
                if actual_col in pi_data.columns:
                    total += float(pi_data[actual_col].iloc[0]) if pd.notna(pi_data[actual_col].iloc[0]) else 0
            
            pi_funding.append({
                'PI': pi,
                'Type': pi_data['Type'].iloc[0],
                'Total_Funding': total,
                'Discipline': pi_data['Discipline'].iloc[0]
            })
        
        if pi_funding:
            pi_df = pd.DataFrame(pi_funding)
            pi_df = pi_df.sort_values('Total_Funding', ascending=False)
            
            # Display program metrics
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Total Funding", f"${total_funding:,.2f}")
            with col2:
                st.metric("Number of PIs", len(pi_df))
            with col3:
                avg_funding = total_funding / len(pi_df)
                st.metric("Average per PI", f"${avg_funding:,.2f}")
            
            # Create 3 columns for charts
            col1, col2, col3 = st.columns(3)
            
            with col1:
                # Program funding chart
                program_funding = pi_df.groupby('Type')['Total_Funding'].sum()
                fig1 = px.pie(
                    values=program_funding.values,
                    names=program_funding.index,
                    title='Funding Distribution by Type'
                )
                fig1.update_traces(textinfo='percent+label')
                st.plotly_chart(fig1, use_container_width=True, key=f"{program}_funding_dist")

            with col2:
                # Institution funding chart
                institution_totals = {}
                for _, row in pi_df.iterrows():
                    # Get institution from productivity_df using PI's last name
                    pi_inst = productivity_df[productivity_df['Last_Name'] == row['PI']]['Institution'].iloc[0] \
                        if not productivity_df[productivity_df['Last_Name'] == row['PI']].empty else 'Unknown'
                    
                    # Add funding to institution total
                    institution_totals[pi_inst] = institution_totals.get(pi_inst, 0) + row['Total_Funding']
                
                fig2 = px.pie(
                    values=list(institution_totals.values()),
                    names=list(institution_totals.keys()),
                    title='Funding by Institution'
                )
                fig2.update_traces(textinfo='percent+label')
                st.plotly_chart(fig2, use_container_width=True, key=f"{program}_inst_dist")

            with col3:
                # Deliverables chart (existing code)
                program_deliverables = productivity_df[productivity_df['Program'] == program]['Productivity and Deliverables'].dropna()
                
                # Initialize counters
                deliverable_counts = {
                    'Publications': 0,
                    'Presentations': 0,
                    'Reports': 0,
                    'Other': 0
                }

                # Process each deliverable entry
                for entry in program_deliverables:
                    entry = str(entry).lower()
                    # Count publications
                    if any(keyword in entry for keyword in ['publication', 'paper', 'journal', 'article']):
                        # Try to extract number if format is like "5 publications"
                        import re
                        nums = re.findall(r'(\d+)\s*(?:publication|paper|article)', entry)
                        deliverable_counts['Publications'] += sum([int(n) for n in nums]) if nums else 1
                    
                    # Count presentations
                    if any(keyword in entry for keyword in ['presentation', 'conference', 'workshop']):
                        nums = re.findall(r'(\d+)\s*(?:presentation|conference|workshop)', entry)
                        deliverable_counts['Presentations'] += sum([int(n) for n in nums]) if nums else 1
                    
                    # Count reports
                    if 'report' in entry:
                        nums = re.findall(r'(\d+)\s*report', entry)
                        deliverable_counts['Reports'] += sum([int(n) for n in nums]) if nums else 1
                    
                    # Count other deliverables
                    if any(keyword in entry for keyword in ['dataset', 'software', 'tool', 'patent']):
                        deliverable_counts['Other'] += 1

                # Create deliverables chart
                fig_deliverables = px.bar(
                    x=list(deliverable_counts.keys()),
                    y=list(deliverable_counts.values()),
                    title='Program Deliverables',
                    labels={'x': 'Type', 'y': 'Count'}
                )
                fig_deliverables.update_traces(texttemplate='%{y}', textposition='outside')
                st.plotly_chart(fig_deliverables, use_container_width=True, key=f"{program}_deliverables")

            # Show PI breakdown
            st.dataframe(
                pi_df.style.format({
                    'Total_Funding': '${:,.2f}'
                }),
                use_container_width=True
            )
        else:
            st.write("No PI data available for this program")




