"""
Grant or revoke API permissions

https://learn.microsoft.com/en-us/graph/permissions-grant-via-msgraph?tabs=http&pivots=grant-application-permissions
"""

from office365.graph_client import GraphClient
from tests import (
    test_admin_principal_name,
    test_client_id,
    test_tenant,
)

client = GraphClient.with_token_interactive(
    test_tenant, test_client_id, test_admin_principal_name
)

# Step 1: Get the appRoles of the resource service principal
resource = (
    client.service_principals.get_by_name("Microsoft Graph")
    .get()
    .select(["id", "displayName", "appId", "appRoles"])
    .execute_query()
)


# select specific appRole
app_role = resource.app_roles["Place.Read.All"]

# Step 2: Grant an app role to a client app
app = client.applications.get_by_app_id(test_client_id)
resource.grant(app, app_role).execute_query()


# Step 3. Print app role assignments
result = resource.app_role_assigned_to.get_all().execute_query()
for app_role_assignment in result:
    print(app_role_assignment)
