import os
import json
import requests
import msal
import datetime

from dotenv import (
    load_dotenv,
    dotenv_values
)

ENV_FILE = f".env"
print(f"Loading environment configuration from: {ENV_FILE}")
load_dotenv(ENV_FILE)

# Azure AD Credentials
CLIENT_ID = os.getenv("CLIENT_ID").strip()
CLIENT_SECRET = os.getenv("CLIENT_SECRET").strip()
TENANT_ID = os.getenv("TENANT_ID").strip()

AUTHORITY = f"https://login.microsoftonline.com/{TENANT_ID}"
SCOPES = ["https://graph.microsoft.com/.default"]

# Get Access Token
def get_access_token():
    app = msal.ConfidentialClientApplication(
        CLIENT_ID, authority=AUTHORITY, client_credential=CLIENT_SECRET
    )
    token_response = app.acquire_token_for_client(SCOPES)

    if "access_token" in token_response:
        return token_response["access_token"]
    else:
        raise Exception("Failed to obtain access token:", token_response)

# Fetch Contacts for a Specific User
def get_user_contacts(user_id):
    token = get_access_token()
    headers = {"Authorization": f"Bearer {token}"}
    url = f"https://graph.microsoft.com/v1.0/users/{user_id}/contacts"

    contacts = []
    
    while url:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            data = response.json()
            contacts.extend(data.get("value", []))
            url = data.get("@odata.nextLink")  # Handle pagination
        else:
            print("Error:", response.json())
            break

    return contacts

# Save Results to JSON File with Timestamp
def save_contacts_to_json(user_id, contacts):
    timestamp = datetime.datetime.now().strftime("%Y%m%d")
    filename = f"output/{user_id.replace('@', '_').replace('.', '_')}_contacts_{timestamp}.json"
    
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(contacts, f, indent=4)
    
    print(f"Contacts saved to {filename}")

# Run Script
if __name__ == "__main__":
    user_id = "ted@nntin.com"  # Replace with the target user's email or Object ID
    contacts = get_user_contacts(user_id)
    save_contacts_to_json(user_id, contacts)