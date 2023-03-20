#!/usr/bin/env python

import json
import re
import requests

issues_completed_url = 'https://github.com/orgs/ghostbsd/projects/4/views/17'

raw_page = requests.get(issues_completed_url).text

search = '<script type="application/json" id="memex-items-data">'

issues_text = re.search(rf'(.*?{search}.*?)\n', raw_page).group(1)

issues = json.loads(issues_text.replace(search, '').replace('</script>', ''))

# print(issues[0])
issues_completed = []
PullRequest = []
for issue in issues:
    if issue['memexProjectColumnValues'][0]['value']['state'] in ['closed', 'merged']:
        issues_completed.append(issue)
        print(issue["memexProjectColumnValues"][0]["value"]["title"]["raw"])
        print(issue["memexProjectColumnValues"][0]["value"]["number"])
        print(issue["content"]["url"])
        print(issue["contentType"])
