"""
Create group and team.

https://learn.microsoft.com/en-us/graph/teams-create-group-and-team
"""

from office365.graph_client import GraphClient
from tests import create_unique_name
from tests.graph_case import acquire_token_by_username_password


def print_failure(retry_number, ex):
    """
    Print progress status
    """
    print(f"{retry_number}: Team creation still in progress, waiting...")


client = GraphClient(acquire_token_by_username_password)
group_name = create_unique_name("Flight")
group = client.groups.create_with_team(group_name).execute_query_retry(
    max_retry=10, failure_callback=print_failure
)
print("Team has been created:  {0}".format(group.team.web_url))

# clean up resources
group.delete_object(True).execute_query()
