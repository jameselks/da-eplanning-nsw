import pandas as pd
import requests
import time
import json
from tqdm import tqdm  # For a user-friendly progress bar

# --- Configuration ---
# All settings are grouped here for easy modification.
CONFIG = {
    "api_url": "https://api.apps1.nsw.gov.au/eplanning/data/v0/OnlineDA",
    "determination_date_from": '2022-01-01',
    "determination_date_to": '2022-12-31',
    "results_per_page": 100,  # The API is capped at 100 per page
    "output_filename": 'development-applications.csv',
    "filters": {
        "ApplicationType": "Development Application",
        "DevelopmentCategory": ["Commercial"],
        "ApplicationStatus": ["Determined"]
    }
}

def main():
    """
    Main function to fetch data from the NSW ePlanning portal and save it to a CSV.
    """
    print("Starting data fetch from NSW ePlanning Portal...")
    all_applications = []

    # Combine the base filters with the date range for the request
    filter_payload = CONFIG['filters'].copy()
    filter_payload['DeterminationDateFrom'] = CONFIG['determination_date_from']
    filter_payload['DeterminationDateTo'] = CONFIG['determination_date_to']
    
    # Define the headers for the API request
    headers = {
        'pageSize': str(CONFIG['results_per_page']),
        'pageNumber': '1',
        'filters': json.dumps({"filters": filter_payload})
    }

    # Using a requests.Session is more efficient as it reuses the same connection for all requests to the same server.
    with requests.Session() as session:
        try:
            # --- Step 1: Make the first request to get total pages ---
            print("Fetching page 1 to determine total pages...")
            response = session.get(CONFIG['api_url'], headers=headers)
            response.raise_for_status()  # Check for HTTP errors (like 404 or 500)
            data = response.json()

            total_pages = data.get('TotalPages', 0)
            total_records = data.get('TotalCount', 0)

            if total_records == 0:
                print("No records found for the specified criteria. Exiting.")
                return

            print(f"Found {total_records} total records across {total_pages} pages.")
            
            # Add applications from the first page to our list
            all_applications.extend(data.get('Application', []))

            # --- Step 2: Loop through the remaining pages ---
            if total_pages > 1:
                # The tqdm wrapper creates a nice progress bar for the loop
                for page_num in tqdm(range(2, total_pages + 1), desc="Fetching Pages"):
                    headers['pageNumber'] = str(page_num)
                    
                    # Fetch the next page of data
                    response = session.get(CONFIG['api_url'], headers=headers)
                    response.raise_for_status()
                    page_data = response.json()
                    
                    # Add the new applications to our master list
                    all_applications.extend(page_data.get('Application', []))

                    # A small delay to be polite to the API server
                    time.sleep(0.2)
            
            print(f"\nAll pages fetched. Total applications collected: {len(all_applications)}")

        except requests.exceptions.RequestException as e:
            print(f"\nAn error occurred during the request: {e}")
            print("Aborting script.")
            return

    # --- Step 3: Save the collected data to a CSV file ---
    if not all_applications:
        print("No data was collected to save.")
        return

    print(f"Saving data to '{CONFIG['output_filename']}'...")
    df = pd.DataFrame(all_applications)
    
    try:
        df.to_csv(CONFIG['output_filename'], index=False)
        print(f"Successfully exported all data.")
    except IOError as e:
        print(f"Error writing to CSV file: {e}")

    print('\nScript complete.')


# This ensures the main() function is called when the script is executed
if __name__ == "__main__":
    main()
