import requests
from requests.auth import HTTPBasicAuth
from datetime import datetime, timedelta

# Jira credentials and base settings
base_url = "https://portonics.atlassian.net"
search_endpoint = "/rest/api/3/search"
project_key = "MYTMAPP"
headers = {
    'Authorization': 'Basic token',
    'Content-Type': 'application/json'
}

# Define date range
start_date = "2024-10-01"  # Start date of range
end_date = "2024-10-31"    # End date of range
date_format = "%Y-%m-%d"

# Convert start and end dates to datetime objects
current_date = datetime.strptime(start_date, date_format)
end_date = datetime.strptime(end_date, date_format)

# Iterate over each date in the range
while current_date <= end_date:
    # Format the current date in YYYY-MM-DD
    formatted_date = current_date.strftime(date_format)

    # JQL query to get tasks due by the current date that are not completed
    jql_query = f"project={project_key} AND due <= '{formatted_date}'"

    # Send the request to the Jira API
    response = requests.get(
        f"{base_url}{search_endpoint}",
        headers=headers,
        params={"jql": jql_query, "fields": "timetracking"}
    )

    # Process the response
    if response.status_code == 200:
        issues = response.json().get("issues", [])
        
        # Initialize counters for original and remaining estimates
        total_original_estimate = 0
        total_remaining_estimate = 0
        
        # Iterate through issues to sum original and remaining estimates
        for issue in issues:
            timetracking = issue['fields'].get('timetracking', {})
            original_estimate = timetracking.get('originalEstimateSeconds', 0)
            remaining_estimate = timetracking.get('remainingEstimateSeconds', 0)
            
            # Accumulate estimates (in seconds)
            total_original_estimate += original_estimate if original_estimate else 0
            total_remaining_estimate += remaining_estimate if remaining_estimate else 0

        # Convert seconds to hours for readability
        original_hours = total_original_estimate / 3600
        remaining_hours = total_remaining_estimate / 3600

        # Output results for the current date
        print(f"Date: {formatted_date}")
        print(f" - Total Original Estimate (hours): {original_hours}")
        print(f" - Total Remaining Estimate (hours): {remaining_hours}")
        print("-----")
    else:
        print(f"Failed to fetch issues for {formatted_date}: {response.status_code} - {response.text}")
    
    # Move to the next date
    current_date += timedelta(days=1)
