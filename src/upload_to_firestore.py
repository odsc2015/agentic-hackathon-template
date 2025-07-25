# src/upload_to_firestore.py

import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
import json
import os

# --- Configuration ---
# Path to your Firebase service account key file
# IMPORTANT: This file should be in your .gitignore!
SERVICE_ACCOUNT_KEY_PATH = 'src/firebase-service-account.json'

# Directory where your generated JSON data files are located
DATA_DIR = 'src/data'

# The base path for your collections in Firestore.
# The __app_id variable is provided by the Canvas environment.
# For local testing, you can use a default like 'default-app-id'.
APP_ID = os.getenv('__app_id', 'default-app-id')

# Define the collections and their corresponding JSON files
COLLECTIONS_TO_UPLOAD = {
    'individuals': 'individuals.json',
    'properties': 'properties.json', # This includes shelters, hostels, food banks
    'skills': 'skills.json',
    'microcourses': 'microcourses.json'
}

# --- Initialize Firebase Admin SDK ---
def initialize_firebase():
    """Initializes the Firebase Admin SDK."""
    try:
        cred = credentials.Certificate(SERVICE_ACCOUNT_KEY_PATH)
        firebase_admin.initialize_app(cred)
        print("Firebase Admin SDK initialized successfully.")
    except Exception as e:
        print(f"Error initializing Firebase Admin SDK: {e}")
        print("Please ensure 'firebase-service-account.json' is in 'src/' and is valid.")
        exit()

# --- Upload Data Function ---
def upload_data_to_firestore():
    """Uploads data from JSON files to Firestore collections."""
    db = firestore.client()

    for collection_name, json_file in COLLECTIONS_TO_UPLOAD.items():
        file_path = os.path.join(DATA_DIR, json_file)
        if not os.path.exists(file_path):
            print(f"Warning: JSON file not found for '{collection_name}': {file_path}. Skipping.")
            continue

        print(f"\nUploading data for collection: '{collection_name}' from {file_path}")
        
        try:
            with open(file_path, 'r') as f:
                data = json.load(f)
        except json.JSONDecodeError as e:
            print(f"Error decoding JSON from {file_path}: {e}. Skipping.")
            continue

        if not isinstance(data, list):
            print(f"Error: Expected a list of objects in {file_path}, but got {type(data)}. Skipping.")
            continue

        # Construct the full collection path including the app_id
        # For public data, use /artifacts/{appId}/public/data/{your_collection_name}
        # For private data, use /artifacts/{appId}/users/{userId}/{your_collection_name}
        # For this upload script, we'll use a public-like path for simplicity,
        # but in your actual app, you'll use the user-specific path for private data.
        full_collection_path = f"artifacts/{APP_ID}/public/data/{collection_name}"
        collection_ref = db.collection(full_collection_path)

        for item in data:
            try:
                # Firestore automatically generates document IDs if you don't provide one.
                # If your JSON items have unique IDs (e.g., 'individual_id', 'property_id'),
                # you can use them as document IDs, but it's often simpler to let Firestore generate.
                # For this script, we'll let Firestore generate the IDs.
                doc_ref = collection_ref.document() # Let Firestore generate a unique ID
                doc_ref.set(item)
                # print(f"  Uploaded document with ID: {doc_ref.id}") # Uncomment for verbose output
            except Exception as e:
                print(f"  Error uploading document to '{collection_name}': {item}. Error: {e}")
        print(f"Finished uploading data for collection '{collection_name}'.")

# --- Main Execution ---
if __name__ == "__main__":
    initialize_firebase()
    upload_data_to_firestore()
    print("\nData upload process completed.")

