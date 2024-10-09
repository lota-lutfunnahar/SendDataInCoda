import requests
from datetime import datetime, timedelta

# Jira API request details
jira_url = 'https://portonics.atlassian.net/rest/agile/1.0/sprint/748/issue?fields=summary,status,customfield_10016,timeoriginalestimate,timeestimate,timetracking'
headers = {
    'Authorization': 'Basic <Jira Token>',
    'Content-Type': 'application/json'
}

# 1. Fetch Sprint Details (including Sprint Name)
def get_sprint_details(sprint_id):
    sprint_url = f'https://portonics.atlassian.net/rest/agile/1.0/sprint/{sprint_id}'
    response = requests.get(sprint_url, headers=headers)
    sprint_info = response.json()

    sprint_name = sprint_info.get('name')
    start_date = sprint_info.get('startDate')
    end_date = sprint_info.get('endDate')
    print(f"Sprint Name: {sprint_name}, Sprint Start Date: {start_date}, Sprint End Date: {end_date}")
    
    return sprint_name, start_date, end_date

# 2. Fetch Issues in Sprint (including Original Estimate)
def get_issues_in_sprint(sprint_id):
    issues_url = f'https://portonics.atlassian.net/rest/agile/1.0/sprint/{sprint_id}/issue?fields=summary,status,customfield_10016,timeoriginalestimate,timeestimate,timetracking'
    response = requests.get(issues_url, headers=headers)
    issues = response.json()

    sprint_issues = []
    for issue in issues['issues']:
        issue_info = {
            'id': issue['id'],
            'summary': issue['fields']['summary'],
            'status': issue['fields']['status']['name'],
            'original_estimate': issue['fields'].get('timeoriginalestimate', 0) / 3600,  # Convert to hours
            'remaining_estimate': issue['fields'].get('timeestimate', 0)
        }
        sprint_issues.append(issue_info)
        print(f"Issue: {issue_info['summary']},  Original Estimate: {issue_info['original_estimate']} hours, Remaining Estimate: {issue_info['remaining_estimate']} seconds")
    
    return sprint_issues

# 3. Fetch Issue Changelog to Track Remaining Time (same as before)
def get_issue_changelog(issue_id):
    changelog_url = f'https://portonics.atlassian.net/rest/api/3/issue/{issue_id}/changelog'
    response = requests.get(changelog_url, headers=headers)
    changelog = response.json()

    remaining_time_changes = []

    # Track remaining estimate changes
    for history in changelog['values']:
        for item in history['items']:
            if item['field'] == 'timeestimate':
                created = history['created']  # Date of change
                from_estimate = item['from']  # Previous estimate in seconds
                to_estimate = item['to']  # New estimate in seconds
                remaining_time_changes.append({
                    'date': created,
                    'from_estimate': from_estimate,
                    'to_estimate': to_estimate
                })
                print(f"Date: {created}, From Estimate: {from_estimate} sec, To Estimate: {to_estimate} sec")

    return remaining_time_changes

# 4. Calculate Daily Remaining Work (same as before)
def calculate_daily_remaining_work(sprint_issues, sprint_start_date, sprint_end_date):
    daily_remaining_work = {}
    date_format = "%Y-%m-%dT%H:%M:%S.%f%z"

    sprint_start = datetime.strptime(sprint_start_date, date_format).date()
    sprint_end = datetime.strptime(sprint_end_date, date_format).date()

    current_date = sprint_start
    while current_date <= sprint_end:
        total_remaining_work = 0

        for issue in sprint_issues:
            changelog = get_issue_changelog(issue['id'])
            remaining_estimate = issue['remaining_estimate']  # Initial remaining estimate
            
            # Check if there was a change in remaining time for the current date
            for change in changelog:
                change_date = datetime.strptime(change['date'], date_format).date()
                if change_date == current_date:
                    remaining_estimate = int(change['to_estimate']) if change['to_estimate'] else remaining_estimate

            total_remaining_work += remaining_estimate
        
        daily_remaining_work[current_date] = total_remaining_work / 3600  # Convert from seconds to hours
        current_date = current_date + timedelta(days=1)

    return daily_remaining_work

# 5. Send Burndown Data to Coda (including Sprint Name and Original Estimate)
def send_burndown_to_coda(daily_remaining_work, sprint_issues, sprint_name):
    coda_url = 'https://coda.io/apis/v1/docs/WSKws0ybrj/tables/grid-GZSlYP-1ES/rows'
    headers = {
        'Authorization': 'Bearer 207f4a8a-657c-4ed2-82e1-36c035ea8de3',
        'Content-Type': 'application/json'
    }
    
    for date, remaining_hours in daily_remaining_work.items():
        for issue in sprint_issues:
            data = {
                "rows": [
                    {
                        "cells": [
                            {"column": "Date", "value": date.strftime('%Y-%m-%d')},
                            {"column": "Original Estimate (Hours)", "value": issue['original_estimate']},
                            {"column": "Remaining Work (Hours)", "value": remaining_hours},
                            {"column": "Sprint Name", "value": sprint_name}
                        ]
                    }
                ]
            }

            response = requests.post(coda_url, headers=headers, json=data)

            # Check if the response is successful
            if response.status_code == 202:
                print(f"Remaining work for {date} inserted successfully into Coda!")
            else:
                print(f"Failed to insert data for {date}. Error: {response.text}")

# Main function to get the data and send to Coda
def main():
    sprint_id = 748

    # Step 1: Fetch Sprint Details (including Sprint Name)
    sprint_name, sprint_start_date, sprint_end_date = get_sprint_details(sprint_id)

    # Step 2: Fetch Issues in Sprint
    sprint_issues = get_issues_in_sprint(sprint_id)

    # Step 3: Calculate Remaining Work by Day
    daily_remaining_work = calculate_daily_remaining_work(sprint_issues, sprint_start_date, sprint_end_date)
    
    # Step 4: Send the Burndown Data to Coda (including Sprint Name and Original Estimate)
    send_burndown_to_coda(daily_remaining_work, sprint_issues, sprint_name)

if __name__ == '__main__':
    main()
