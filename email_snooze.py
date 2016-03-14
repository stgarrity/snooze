# with credit to Google's Gmail API quickstart for Python: https://developers.google.com/gmail/api/quickstart/python

from __future__ import print_function
import httplib2
import os
import sys

from apiclient import discovery
import oauth2client
from oauth2client import client
from oauth2client import tools

# If modifying these scopes, delete your previously saved credentials
# at ~/.credentials/[username].json
SCOPES = 'https://www.googleapis.com/auth/gmail.modify'
CLIENT_SECRET_FILE = 'client_secret.json'
APPLICATION_NAME = 'Mailbox tribute label snoozer'

LABEL_MAP = {'tonight': '.Snooze/1 - This Evening',
             'tomorrow': '.Snooze/2 - Tomorrow',
             'weekend': '.Snooze/3 - This Weekend',
             'nextweek': '.Snooze/4 - Next Week'}

try:
    import argparse
    parser = argparse.ArgumentParser(parents=[tools.argparser])
    parser.add_argument('schedule', choices=LABEL_MAP.keys() + ["none"])
    flags = parser.parse_args()
except ImportError:
    flags = None


def get_credentials(username):
    """Gets valid user credentials from storage.

    If nothing has been stored, or if the stored credentials are invalid,
    the OAuth2 flow is completed to obtain the new credentials.

    Returns:
    Credentials, the obtained credential.
    """
    home_dir = os.path.expanduser('~')
    credential_dir = os.path.join(home_dir, '.credentials')
    if not os.path.exists(credential_dir):
        os.makedirs(credential_dir)
    credential_path = os.path.join(credential_dir,
                                   '%s.json' % username)

    store = oauth2client.file.Storage(credential_path)
    credentials = store.get()
    if not credentials or credentials.invalid:
        flow = client.flow_from_clientsecrets(CLIENT_SECRET_FILE, SCOPES)
        flow.user_agent = APPLICATION_NAME
        if flags:
            credentials = tools.run_flow(flow, store, flags)
        else: # Needed only for compatibility with Python 2.6
            credentials = tools.run(flow, store)
        print('Storing credentials to ' + credential_path)
    return credentials

def create_label(service, label_name):
    service.users().labels().create(userId='me',
                                  body={'name': label_name}).execute()

def create_labels(service):
    create_label(service, '.Snooze')  # need to create the top-level label first

    for label_name in LABEL_MAP.values():
        create_label(service, label_name)


def find_label_id(labels, label_name):
    for label in labels:
        if label['name'] == label_name:
            return label['id']
    return None


def run_snooze(service):
    results = service.users().labels().list(userId='me').execute()
    labels = results.get('labels', [])

    search_label_name = LABEL_MAP.get(flags.schedule)
    if not search_label_name:
        print("invalid argument")
        sys.exit(2)  # FIXME should this validation be here?

    inbox_label = find_label_id(labels, "INBOX")
    search_label = find_label_id(labels, search_label_name)

    # make sure the labels exist
    if not inbox_label:
        raise Exception("failed to find inbox...that's not good'")
    if not search_label:
        create_labels(service)
        labels = service.users().labels().list(userId='me').execute().get('labels', [])  # FIXME factoring?
        search_label = find_label_id(labels, search_label_name)
        if not search_label:
            raise Exception("failed to create labels")

    # FIXME: doesn't support pagination
    results = service.users().threads().list(userId="me", labelIds=search_label).execute()
    threads = results.get('threads', [])

    for thread in threads:
        service.users().threads().modify(userId="me",
                                         id=thread['id'],
                                         body={'addLabelIds': [inbox_label],
                                               'removeLabelIds': [search_label]}).execute()


def snooze_for_user(username):
    credentials = get_credentials(username)
    http = credentials.authorize(httplib2.Http())
    service = discovery.build('gmail', 'v1', http=http)

    if flags.schedule != "none":
        run_snooze(service)


if __name__ == '__main__':
    users = ['work@example.com', 'personal@example.com']

    for user in users:
        # FIXME error handling to alert me?
        snooze_for_user(user)
