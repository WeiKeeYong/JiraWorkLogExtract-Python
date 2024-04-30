import csv
import sys
from datetime import datetime
from jira import JIRA

# Define your JIRA credentials
JIRA_URL = 'https://your_org.atlassian.net/'
JIRA_USERNAME = 'username@something.com'

def read_api_key_from_file(file_path, start_with):
    try:
        with open(file_path, 'r') as file:
            for line in file:
                # Find the keypair
                if line.startswith(start_with):
                    # Extract the  key
                    api_key = line.strip().split(':')[1].strip()
                    return api_key
        # If no API key line is found matching the specified pattern
        raise ValueError(f"key not found starting with '{start_with}' in file '{file_path}'") 

    except FileNotFoundError:
        print(f"Error: File '{file_path}' not found.")
        sys.exit(1)  # Exit
    except ValueError as e:
        print(str(e))
        sys.exit(1)  # Exit with error code 1 if key not found

# Read JIRA API token from key.txt

JIRA_API_TOKEN = read_api_key_from_file('key.txt','JiraKey:')

# Initialize the JIRA client
options = {
    'server': JIRA_URL,
    'verify': True
}
jira = JIRA(options, basic_auth=(JIRA_USERNAME, JIRA_API_TOKEN))

# Define your JQL query, Can alway exectue from Jira Adv search and put the exact string 

#jql = 'fixVersion = TI_PRD-Y24R01 and issuetype in (bug, Story) and issuekey not in (opc-997, opc-996, opc-995, opc-995)'
jql = 'issuekey = opc-1114 or parentEpic = opc-1114'

# Reduce the payload only get the minimal fields required, Jira will still send some extra fields.
fields = 'key, timeestimate, timespent, worklog'


# Prepare CSV file to write to
timestamp = datetime.now().strftime('%d%m%Y_%H%M')  # Format: ddmmyyyy_hhmm
csv_file = f'work_logs_{timestamp}.csv'
csv_columns = ['Issue Key', 'Time Spent (Hours)', 'Logged By']

# Retrieve all issues (handle pagination)
issues = []
start_at = 0
max_results = 50

while True:
    results = jira.search_issues(jql, startAt=start_at, maxResults=max_results, fields=fields)
    if not results:
        break
    issues.extend(results)
    start_at += len(results)

# Write to CSV file
with open(csv_file, mode='w', newline='') as file:
    writer = csv.DictWriter(file, fieldnames=csv_columns)
    
    # Write total number of issues being processed as the first line
    writer.writerow({'Issue Key': f'Total JIRA Issues Processed: {len(issues)}'})

    # Write header row
    writer.writeheader()

    # Iterate through all retrieved issues
    for issue in issues:
        issue_key = issue.key

        # Get work logs for the current issue
        work_logs = jira.worklogs(issue_key)

        # Iterate through the work logs
        for work_log in work_logs:
            time_spent_hours = work_log.timeSpentSeconds / 3600  # Convert seconds to hours
            logged_by = work_log.author.displayName

            # Write the work log to the CSV file
            writer.writerow({'Issue Key': issue_key, 'Time Spent (Hours)': time_spent_hours, 'Logged By': logged_by})

print(f'Work logs extracted successfully and saved to {csv_file}.')
