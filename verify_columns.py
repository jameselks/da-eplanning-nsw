import pandas as pd

try:
    df = pd.read_csv('da.csv')
    print("Columns in da.csv:")
    for col in df.columns:
        print(f"- {col}")

    previously_dropped_columns = [
        'LodgementDate','AccompaniedByVPAFlag',
        'DevelopmentSubjectToSICFlag', 'EPIVariationProposedFlag',
        'SubdivisionProposedFlag', 'AssessmentExhibitionEndDate',
        'AssessmentExhibitionStartDate','VariationToDevelopmentStandardsApprovedFlag'
    ]

    missing_columns = []
    present_columns = []

    for col in previously_dropped_columns:
        if col in df.columns:
            present_columns.append(col)
        else:
            missing_columns.append(col)

    if present_columns:
        print("\nThe following previously dropped columns ARE NOW PRESENT:")
        for col in present_columns:
            print(f"- {col}")

    if missing_columns:
        print("\nWARNING: The following previously dropped columns ARE STILL MISSING:")
        for col in missing_columns:
            print(f"- {col}")
    else:
        print("\nAll previously dropped columns are now present in da.csv.")

except FileNotFoundError:
    print("Error: da.csv not found. Make sure ExtractDA.py ran successfully.")
except Exception as e:
    print(f"An error occurred: {e}")
