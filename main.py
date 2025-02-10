import os
import streamlit as st
from datetime import datetime, timezone, timedelta
from google.cloud import asset_v1

def search_resources(org_id, query):
    """Searches all resources within a given scope based on the provided query.

    Args:
        org_id: The organization ID.
        query: The query string.
    """

    # Initialize the Asset client
    client = asset_v1.AssetServiceClient()

    # Build the request
    scope = f"organizations/{org_id}"
    request = asset_v1.SearchAllResourcesRequest(
        scope=scope,
        asset_types=["cloudresourcemanager.googleapis.com/Project"],  # Specifying asset type
        query=query,
    )

    # Initialize an empty list to store the results
    results = []

    # Iterate through the search results and append relevant information to the list
    for response in client.search_all_resources(request=request):
        result = {
            "name": response.name,
            "asset_type": response.asset_type,
            "project": response.project,
            "display_name": response.display_name,
            "description": response.description,
            "state": response.state,  # Accessing enum value name string
            "create_time": response.create_time.astimezone(timezone(timedelta(hours=9))).strftime('%Y-%m-%d %H:%M:%S %Z'),
            "update_time": response.update_time.astimezone(timezone(timedelta(hours=9))).strftime('%Y-%m-%d %H:%M:%S %Z') if response.update_time else None, # Convert update_time to KST if it exists

        }
        if response.additional_attributes and "projectId" in response.additional_attributes:
            result["project_id"] = response.additional_attributes["projectId"]
        

        results.append(result)
    return results


# Streamlit app
st.title("Google Cloud Asset Inventory Search")

# Sidebar with input fields
with st.sidebar:
    org_id = st.text_input("Organization ID", "1234567890") # Your organization ID (e.g., 1234567890...)
    query = st.text_input("Query", "displayName:My*Project*")
    refresh_button = st.button("Refresh")


# Display the table and refresh time
if refresh_button:
    refresh_time = datetime.now(timezone(timedelta(hours=9))).strftime('%Y-%m-%d %H:%M:%S %Z')
    data = search_resources(org_id, query)
    st.table(data)
    st.write(f"Last refreshed at: {refresh_time}")


# TODO: Add Project Last Access Time.