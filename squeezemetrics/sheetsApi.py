import os
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from oauth2client.service_account import ServiceAccountCredentials
from google.oauth2 import service_account

SCOPES = ["https://www.googleapis.com/auth/drive","https://www.googleapis.com/auth/spreadsheets"]

# Source: https://developers.google.com/sheets/api/quickstart/python
def get_or_create_credentials(scopes):
	return ServiceAccountCredentials.from_json_keyfile_name('credentials.json', scopes)


def append_row_to_gsheet(list_of_vals, gsheet):
	spreadsheet_id = '1wrDGscPisgbTnwK1TMKVE83n_k_vCr3i5m4Mi4NaZEY'  # this is part of the url of google
	rows = [list_of_vals]
	# -----------

	credentials = get_or_create_credentials(scopes=SCOPES)  # or use GoogleCredentials.get_application_default()
	service = build('sheets', 'v4', credentials=credentials)
	service.spreadsheets().values().append(
		spreadsheetId=spreadsheet_id,
		range="{}!A:Z".format(gsheet),
		body={
		    "majorDimension": "ROWS",
		    "values": rows
		},
		valueInputOption="USER_ENTERED"
	).execute()



