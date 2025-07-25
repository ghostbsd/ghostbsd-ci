#!/usr/bin/env python

import os
import requests

# GitHub GraphQL endpoint
api_url = "https://api.github.com/graphql"

# Get token from environment
token = os.getenv("GITHUB_TOKEN")
if not token:
    print("Set GITHUB_TOKEN environment variable")
    exit(1)

# Headers
headers = {
    "Authorization": f"Bearer {token}",
    "Content-Type": "application/json",
    "GraphQL-Features": "issue_types"
}

# Simple GraphQL query without nested nodes
query = """
query($cursor: String) {
  organization(login: "ghostbsd") {
    projectV2(number: 4) {
      items(first: 100, after: $cursor) {
        pageInfo {
          hasNextPage
          endCursor
        }
        nodes {
          content {
            ... on Issue {
              number
              title
              url
              issueType {
                id
                name
              }
              assignees(first: 10) {
                nodes {
                  login
                  name
                }
              }
              labels(first: 10) {
                nodes {
                  name
                }
              }
              repository {
                nameWithOwner
              }
            }
            ... on PullRequest {
              number
              title
              url
              assignees(first: 10) {
                nodes {
                  login
                  name
                }
              }
              labels(first: 10) {
                nodes {
                  name
                }
              }
              repository {
                nameWithOwner
              }
            }
          }
          fieldValues(first: 10) {
            nodes {
              ... on ProjectV2ItemFieldSingleSelectValue {
                name
                field {
                  ... on ProjectV2FieldCommon {
                    name
                  }
                }
              }
              ... on ProjectV2ItemFieldIterationValue {
                title
                field {
                  ... on ProjectV2FieldCommon {
                    name
                  }
                }
              }
            }
          }
        }
      }
    }
  }
}
"""

# Fetch all pages
all_items = []
cursor = None

while True:
    variables = {"cursor": cursor}
    response = requests.post(api_url, json={"query": query, "variables": variables}, headers=headers)
    data = response.json()

    if "errors" in data:
        print("Errors:", data["errors"])
        break

    items_data = data["data"]["organization"]["projectV2"]["items"]
    items = items_data["nodes"]
    all_items.extend(items)

    # Check if there are more pages
    if not items_data["pageInfo"]["hasNextPage"]:
        break

    cursor = items_data["pageInfo"]["endCursor"]

print(f"Found {len(all_items)} total items")

def get_field_value(project_item, field_name):
    """Get project field value by name"""
    for node in project_item["fieldValues"]["nodes"]:
        if node.get("field", {}).get("name") == field_name:
            return node.get("name") or node.get("title") or node.get("text")
    return None

def get_issue_type(project_item):
    """Get issue type from either issueType or project fields"""
    if project_item.get("content", {}).get("issueType"):
        return project_item["content"]["issueType"]["name"]
    return get_field_value(project_item, "Issue Type")

def build_item_line(project_item):
    """Build HTML line for changelog item"""
    content = project_item["content"]
    url = content["url"]
    repository = content["repository"]["nameWithOwner"]
    number = content["number"]
    title = content["title"]
    return f'<a href="{url}">{repository}#{number}</a> {title}'

def categorize_item(type_name):
    """Determine which changelog section an item belongs to"""
    if type_name in ['Bug']:
        return 'Bug'
    elif type_name in ['Security']:
        return 'Security'
    elif type_name in ['Enhancement', 'Feature', 'Task']:
        return 'Feature'
    elif type_name in ['Epic']:
        return 'Epic'
    else:
        return 'Feature'  # Default

release = '25.02-R14.3p0'

Epic = '<h3>Epics</h3>\n<ul>\n'
Feature = '<h3>Enhancement, Improvements and New Features</h3>\n<ul>\n'
Bug = '<h3>Bug Fixes</h3>\n<ul>\n'
Security = '<h3>Security Fixes</h3>\n<ul>\n'

# Process all items
for item in all_items:
    # Skip items without content
    if not item.get("content"):
        continue
    
    # Check if item is for target release
    release_field = get_field_value(item, "Release")
    if release_field != release:
        continue
    
    # Build the changelog line
    line = build_item_line(item)
    
    # Get issue type and determine item type (Issue/PR)
    issue_type = get_issue_type(item)
    item_type = "Issue" if "issueType" in item["content"] else "PR"
    
    # Categorize and add to appropriate section
    category = categorize_item(issue_type)
    
    if category == 'Bug':
        Bug += f'<li>\n{item_type}: {line}\n</li>\n'
    elif category == 'Security':
        Security += f'<li>\n{item_type}: {line}\n</li>\n'
    elif category == 'Epic':
        Epic += f'<li>\n{item_type}: {line}\n</li>\n'
    else:  # Feature
        Feature += f'<li>\n{item_type}: {line}\n</li>\n'

Epic += '</ul>\n'
Feature += '</ul>\n'
Bug += '</ul>\n'
Security += '</ul>\n'
with open('change-log.html', 'w') as file:
    file.writelines('<h2>25.02-R14.3p0 Changelog</h2>\n')
    file.writelines(Epic)
    file.writelines(Feature)
    file.writelines(Bug)
    file.writelines(Security)