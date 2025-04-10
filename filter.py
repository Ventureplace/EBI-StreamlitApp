import pandas as pd

def filter_by_max_productivity(df, project_col='Project Name', productivity_col='Productivity and Deliverables'):
    """
    Filters the DataFrame to keep only the row with the most extensive productivity text for each project.
    """
    # Compute text length of productivity
    df['prod_len'] = df[productivity_col].fillna('').str.len()
    # Sort by project and text length descending
    sorted_df = df.sort_values(by=[project_col, 'prod_len'], ascending=[True, False])
    # Drop duplicates, keeping the first (longest productivity)
    filtered_df = sorted_df.drop_duplicates(subset=project_col, keep='first')
    # Remove helper column
    filtered_df = filtered_df.drop(columns=['prod_len'])
    return filtered_df

if __name__ == "__main__":
    # Example: load your data into df, e.g., from CSV
    df = pd.read_csv('/Users/iyangodwin/EBI-StreamlitApp/EBI Dashboard Data - Productivity Data.csv')
    filtered_df = filter_by_max_productivity(df)
    # Save or display the filtered result
    filtered_df.to_csv('filtered_projects.csv', index=False)
    print(filtered_df)
