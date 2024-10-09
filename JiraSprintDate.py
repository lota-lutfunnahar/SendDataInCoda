import requests

# Jira API request to get sprint details (start and end dates)
sprint_url = 'https://portonics.atlassian.net/rest/agile/1.0/sprint/748'
headers = {
    'Authorization': 'Basic <Jira Token>',
    'Content-Type': 'application/json'
}

response = requests.get(sprint_url, headers=headers)

# Parse the sprint response
sprint_data = response.json()
print(sprint_data)

# Extract sprint details
sprint_name = sprint_data['name']
start_date = sprint_data.get('startDate', 'N/A')
end_date = sprint_data.get('endDate', 'N/A')

print(f"Sprint Name: {sprint_name}")
print(f"Sprint Start Date: {start_date}")
print(f"Sprint End Date: {end_date}")


print(start_date)
