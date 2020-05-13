from __future__ import print_function
from time import sleep
import re
import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request


# If modifying these scopes, delete the file token.json.
SCOPES = 'https://www.googleapis.com/auth/spreadsheets.readonly'


squadrons = {'VT 7':'0','VT 9':'1','HT 8':'2','HT 18':'3','HT 28':'4',
'VT 2':'5','VT 3':'6','VT 6':'7','VT 27':'8','VT 28':'9','VT 31':'10',
'VT 35':'11','VT 21':'12','VT 22':'13','VT 10':'14','TW 5 FITU':'15',
'TW 5 HITU':'16','VT 86':'17'}

carriers = {'T-Mobile':	'@tmomail.net','Verizon':'@vtext.com','AT&T':'@txt.att.net',
'Sprint':'@messaging.sprintpcs.com','Project Fi':'@msg.fi.google.com'}


# The ID and range of a sample spreadsheet.
SAMPLE_SPREADSHEET_ID = '12It7rRH2ZosFjqH7GW0aheqAHLeatP5ZeArSAvgArgg'
SAMPLE_RANGE_NAME = 'Form Responses 1!A:H'

def pull_sheet():
    """Shows basic usage of the Sheets API.
    Prints values from a sample spreadsheet.
    """
    creds = None
    # The file token.pickle stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server()
        # Save the credentials for the next run
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    service = build('sheets', 'v4', credentials=creds)

    # Call the Sheets API
    sheet = service.spreadsheets()
    result = sheet.values().get(spreadsheetId=SAMPLE_SPREADSHEET_ID,
                                range=SAMPLE_RANGE_NAME).execute()
    values = result.get('values', [])

    if not values:
        print('No data found.')
    else:
        return values

def format_user(r,blocked_list):
    one=''
    two=''
    three=''
    if r[6]=='T-Mobile':
        r[4] = 'Email'
    if r[1]=='ON':
        one=r[2]
        two=r[3]
        if r[4]=='Text message':
            if len(r[5])==10:
                try:three=r[5]+carriers[r[6]]
                except: return None
        elif r[4]=='Email':
            if len(r[7])>=8:
                three=r[7]
            else:
                return None
        if three.split('@')[0] in blocked_list:
          return None
        return {'search_term':two,'email':three,'squadron':one}

    return None

def get_blocked():
  import os
  import email
  p=re.compile(r'\D(\d{10})@')

  mail_dir = '/home/fidoh/Maildir/new/'
  keywords = ['stop','unsubscribe','undeliverable','undelivered','sprinkles']
  newly_blocked = set()
  body = ''

  for filename in os.listdir(mail_dir):
    with open(mail_dir+filename) as file:
      data = file.read()
    body = data
    #print (body)

    if any(word in body.lower() for word in keywords):
    #import pdb; pdb.set_trace()
      results=p.findall(body)
      for m in results:
        newly_blocked.add(m)
  try:
    with open('blocked_list.pickle','rb') as f:
      file_temp = pickle.load(f)
    if file_temp:
      blocked_list = file_temp
    else:
      blocked_list = []

  except: 
    print('no blocked list exists')
    blocked_list = []


  for n in newly_blocked:
    if n not in blocked_list:
      print("BLOCKING " + n)
      blocked_list.append(n)

  outfile = open('blocked_list.pickle','wb')
  pickle.dump(blocked_list,outfile)
  outfile.close()
  print(blocked_list)

  return blocked_list




def main():
    raw_users = pull_sheet()
    results = []
    blocked_list = get_blocked()
    #try: blocked_list = get_blocked()
    #except:  blocked_list = pickle.load('blocked_list.pickle')

    for r in raw_users:
        formatted = format_user(r,blocked_list)
        if formatted:
            results.append(formatted)

    print("********** " + str(len(results)) + " users updated*** " + str(len(blocked_list))+ " BLOCKED*********")

    return results


if __name__ == "__main__":
    results = main()

    for r in results[0:5]:
        print(r)
