"""
Create team from group

https://learn.microsoft.com/en-us/graph/api/team-put-teams?view=graph-rest-1.0
"""

from office365.graph_client import GraphClient
from tests import create_unique_name
from tests.graph_case import acquire_token_by_username_password


def print_failure(retry_number, ex):
    print(f"{retry_number}: Team creation still in progress, waiting...")


client = GraphClient(acquire_token_by_username_password)
group_name = create_unique_name("Flight")
group = client.groups.create_m365_group(group_name)
team = group.add_team().execute_query_retry(max_retry=10, failure_callback=print_failure)
print("Team has been created:  {0}".format(team.web_url))

# clean up resources
print("Deleting a group...")
group.delete_object(True).execute_query()
