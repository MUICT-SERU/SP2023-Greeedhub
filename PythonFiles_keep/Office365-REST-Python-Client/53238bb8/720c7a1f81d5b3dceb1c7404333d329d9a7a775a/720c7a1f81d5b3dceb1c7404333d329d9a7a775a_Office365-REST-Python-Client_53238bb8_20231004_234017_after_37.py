"""
Demonstrates how to retrieve a flat list of all TermSet objects
"""
from office365.graph_client import GraphClient
from tests import test_team_site_url
from tests.graph_case import acquire_token_by_client_credentials

client = GraphClient(acquire_token_by_client_credentials)
term_sets = (
    client.sites.get_by_url(test_team_site_url)
    .term_store.get_all_term_sets()
    .execute_query()
)
names = [ts.localized_names[0].name for ts in term_sets]
print(names)
