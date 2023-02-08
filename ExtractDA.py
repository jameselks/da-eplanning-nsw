import pandas as pd
import numpy as np
import requests

#Some basic parameters
api_url = "https://api.apps1.nsw.gov.au/eplanning/data/v0/OnlineDA"
DeterminationDateFrom = '2022-01-01'
DeterminationDateTo = '2022-12-31'
ResultsToReturn = '10'

#Set the API headers
headers = {
    'pageSize': ResultsToReturn,
    'pageNumber': '1',
    'filters': '{ "filters": { "ApplicationType": "Development Application", "DevelopmentCategory": ["Commercial"], "ApplicationStatus": ["Determined"], "DeterminationDateFrom":"' + DeterminationDateFrom + '", "DeterminationDateTo": "' + DeterminationDateTo + '" } }'
}

#Call API and get the data
try:
    response = requests.get(api_url, headers=headers)
    response.raise_for_status()
    data = response.json()

    #Write the API JSON response to a file. Might want to work with that locally later.
    with open("response_data.json", "w")    as file:
        file.write(response.text)
        print("Response data saved to response_data.json")

except requests.exceptions.HTTPError as error:
    print("HTTP error occurred:", error)
except requests.exceptions.RequestException as error:
    print("Request exception occurred:", error)

#Create dataframe with normalised data in it
flat=pd.json_normalize(data, record_path=['Application'])

#Drop a bunch of columns
flat = flat.drop(['LodgementDate','AccompaniedByVPAFlag', 'DevelopmentSubjectToSICFlag', 'EPIVariationProposedFlag', 'SubdivisionProposedFlag', 'AssessmentExhibitionEndDate', 'AssessmentExhibitionStartDate','VariationToDevelopmentStandardsApprovedFlag'], axis=1)

#Function that unpacks a dictionary that's within a field
def unpackDict (y):
    out = ''
    for x in y:
        for w in x.values():
            w = w.strip()
            out = out + w + ";"
    return out

#Unpack dictionary of Development Types
flat['DevelopmentType'] = flat['DevelopmentType'].apply(unpackDict)

#Create columns for each Development Type
mask=flat['DevelopmentType'].str.get_dummies(sep=';').replace('?',np.nan)
for col in mask.columns:
    mask[col].fillna(col, inplace=True)
final = flat.join(mask.replace(0,np.nan))
flat = final

#Export results to CSV
flat.to_csv('da-2021-22-v.csv')

#Done!
print('Script complete')