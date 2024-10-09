import requests

# Jira API request details
jira_url = 'https://portonics.atlassian.net/rest/agile/1.0/sprint/748/issue?fields=summary,status,customfield_10016,duedate,timeoriginalestimate,timeestimate'
headers = {
    'Authorization': 'Basic <Jira API token>',
    'Content-Type': 'application/json'
}

response = requests.get(jira_url, headers=headers)

sprint_url = 'https://portonics.atlassian.net/rest/agile/1.0/sprint/748'
headers = {
    'Authorization': 'Basic <Jira API token>',
    'Content-Type': 'application/json'
}

responseData = requests.get(sprint_url, headers=headers)

sprint_info = responseData.json()

start_date = sprint_info.get('startDate', 'N/A')
end_date = sprint_info.get('endDate', 'N/A')
sprint_name = sprint_info['name']

print(f"Sprint Start Date: {start_date}")
print(f"Sprint End Date: {end_date}")

# Parse the sprint response
sprint_data = response.json()

sprint_timeline = f"Start: {start_date}, End: {end_date}"

# Parse Jira response
issues = response.json()

for issue in issues['issues']:
    # Extract the required fields
    issue_name = issue['fields']['summary']
    status = issue['fields']['status']['name']
    due_date = issue['fields'].get('duedate', 'N/A')  # Due date (if exists)
    
    # Original estimate in seconds (convert to hours if needed)
    original_estimate_seconds = issue['fields'].get('timeoriginalestimate', 0)
    original_estimate_hours = original_estimate_seconds / 3600 if original_estimate_seconds else 'N/A'
    remaining_time_seconds = issue['fields'].get('timeestimate', 0)
    print(remaining_time_seconds)
    remaining_time_hours = remaining_time_seconds / 3600 if remaining_time_seconds else 0
    print(remaining_time_hours)
    
    

    # Coda API details
    # Coda API details
    coda_url = 'https://coda.io/apis/v1/docs/WSKws0ybrj/tables/grid-u4PzGJJWNO/rows'
    headers = {
        'Authorization': 'Bearer <Coda API token>',
        'Content-Type': 'application/json'
    }
    # Prepare the data to insert into Coda
    data = {
        "rows": [
            {
                "cells": [
                    {"column": "Issue Name", "value": issue_name},
                    # {"column": "Story Points", "value": story_points},
                    {"column": "Status", "value": status},
                    {"column": "Due Date", "value": due_date},
                    {"column": "Original Estimate (Hours)", "value": original_estimate_hours},
                    {"column": "Remaining Time (Hours)", "value": remaining_time_hours},
                    {"column": "Sprint Timeline", "value": sprint_timeline},
                    {"column": "sprint Name", "value": sprint_name}
                ]
            }
        ]
    }

    # Post the data to Coda
    response = requests.post(coda_url, headers=headers, json=data)

    # Check if the response is successful
    if response.status_code == 202:
        print(f"Issue '{issue_name}' inserted successfully into Coda!")
    else:
        print(f"Failed to insert issue '{issue_name}'. Error: {response.text}")
