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
    "determination_date_to": '2022-06-30',
    "results_per_page": 1000,
    "output_filename": 'development-applications.csv',
    "development_categories": ["Industrial", "Commercial", "Recreational", "Residential", "Other"],
    "base_filters": {
        "ApplicationType": "Development Application",
        "ApplicationStatus": ["Determined"]
    }
}

def main():
    """
    Main function to fetch data for multiple categories from the NSW ePlanning portal 
    and save it to a single CSV.
    """
    print("Starting data fetch from NSW ePlanning Portal...")
    all_applications = []

    # Using a requests.Session is more efficient as it reuses the same connection 
    # for all requests to the same server.
    with requests.Session() as session:
        # --- Step 1: Loop through each specified development category ---
        for category in CONFIG["development_categories"]:
            print(f"\n{'='*20}\nFetching category: {category}\n{'='*20}")
            
            # Combine the base filters with the current category and date range
            filter_payload = CONFIG['base_filters'].copy()
            filter_payload['DevelopmentCategory'] = [category] # Set the current category
            filter_payload['DeterminationDateFrom'] = CONFIG['determination_date_from']
            filter_payload['DeterminationDateTo'] = CONFIG['determination_date_to']
            
            headers = {
                'pageSize': str(CONFIG['results_per_page']),
                'pageNumber': '1',
                'filters': json.dumps({"filters": filter_payload})
            }

            try:
                # --- Step 2: Make the first request for the category to get total pages ---
                print("Fetching page 1 to determine total pages for this category...")
                response = session.get(CONFIG['api_url'], headers=headers)
                response.raise_for_status()
                data = response.json()

                total_pages = data.get('TotalPages', 0)
                total_records = data.get('TotalCount', 0)

                if total_records == 0:
                    print(f"No records found for '{category}'. Moving to next category.")
                    continue

                print(f"Found {total_records} records across {total_pages} pages for '{category}'.")
                
                # Add applications from the first page to our list
                all_applications.extend(data.get('Application', []))

                # --- Step 3: Loop through the remaining pages for the category ---
                if total_pages > 1:
                    for page_num in tqdm(range(2, total_pages + 1), desc=f"Fetching {category} Pages"):
                        headers['pageNumber'] = str(page_num)
                        response = session.get(CONFIG['api_url'], headers=headers)
                        response.raise_for_status()
                        page_data = response.json()
                        all_applications.extend(page_data.get('Application', []))
                        time.sleep(0.2) # Be polite to the API server
                
            except requests.exceptions.RequestException as e:
                print(f"\nAn error occurred while fetching '{category}': {e}")
                print("Skipping to the next category.")
                continue

    # --- Step 4: Process and save the combined data ---
    if not all_applications:
        print("\nNo data was collected across all categories. Exiting.")
        return

    print(f"\n\nAll categories fetched. Total applications collected: {len(all_applications)}")
    
    print("Processing final data and removing duplicates...")
    df = pd.DataFrame(all_applications)
    
    initial_count = len(df)
    # Remove duplicates based on the unique application number
    df.drop_duplicates(subset=['PlanningPortalApplicationNumber'], keep='first', inplace=True)
    final_count = len(df)

    if initial_count > final_count:
        print(f"Removed {initial_count - final_count} duplicate applications.")

    print(f"Saving {final_count} unique applications to '{CONFIG['output_filename']}'...")
    try:
        df.to_csv(CONFIG['output_filename'], index=False)
        print(f"Successfully exported all data.")
    except IOError as e:
        print(f"Error writing to CSV file: {e}")

    print('\nScript complete.')


# This ensures the main() function is called when the script is executed
if __name__ == "__main__":
    main()
