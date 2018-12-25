from __future__ import print_function
from googleapiclient.discovery import build
from httplib2 import Http
from oauth2client import file, client, tools
import ConfigParser
import base64
from apiclient import errors
import email

# dependencies needed for send messages
from email.mime.audio import MIMEAudio
from email.mime.base import MIMEBase
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import mimetypes
import os



# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly','https://www.googleapis.com/auth/gmail.send']

# Load the config file information 
config = ConfigParser.ConfigParser()
config.read('config.ini')
config.sections()
UserId = config.get('Default','UserId')
SendTo = config.get('Default','SendTo')
Query = config.get('Default','Query')
Title = config.get('Default','Title')
MaxEmailCount = int(config.get('Default','MaxEmailCount'))

def main():
    """Shows basic usage of the Gmail API.
    Lists the user's Gmail labels.
    """

    # Initialize the gmail api, enable ouath for credential storage.
    # Note: The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    store = file.Storage('token.json')
    creds = store.get()
    if not creds or creds.invalid:
        flow = client.flow_from_clientsecrets('credentials.json', SCOPES)
        creds = tools.run_flow(flow, store)
    service = build('gmail', 'v1', http=creds.authorize(Http()))

    # Retrive all the needed Emails
    # While there's still next page, retrive the results and save it in list
    messagesList = []
    # Call the Gmail API
    results = getMessagesByQuery(service,UserId,Query,pageToken=None)
    labels = results.get('labels', [])
    nextPageToken =results.get('nextPageToken', '') 
    messagesList.extend(results.get('messages',[]))
    while True:
        if nextPageToken:
            results = getMessagesByQuery(service,UserId,Query,nextPageToken)
            nextPageToken = results.get('nextPageToken', '')
            tempMessages = results.get('messages',[])
            messagesList.extend(results.get('messages',[]))
        else:
            break 
    
    # Organize them then send it to a target account
    count = 0
    for message in messagesList:
        # results = service.users().messages().get(id=message.get('id',''),userId =UserId).execute()
        tempMessage = GetMimeMessage(service,UserId,message.get('id',''))
        results = CreateMessage(UserId,SendTo,Title,tempMessage)
        results = SendMessage(service,UserId,results)
        count +=1
        if count >=MaxEmailCount:
            break

def getMessagesByQuery(service, user_id,query,pageToken):
    try:
        if pageToken!=None:
            messages = service.users().messages().list(userId=UserId,q=query,pageToken=pageToken).execute()
            return messages
        else:
            messages = service.users().messages().list(userId=UserId,q=query).execute()
            return messages
    except errors.HttpError, error:
        print (error)
# helper function to return the message 
def GetMimeMessage(service, user_id, msg_id):
    """Get a Message and use it to create a MIME Message.

    Args:
        service: Authorized Gmail API service instance.
        user_id: User's email address. The special value "me"
        can be used to indicate the authenticated user.
        msg_id: The ID of the Message required.

    Returns:
        A MIME Message, consisting of data from Message.
    """
    try:
        message = service.users().messages().get(userId=user_id, id=msg_id,
                                                format='raw').execute()
        msg_str = base64.urlsafe_b64decode(message['raw'].encode('ASCII'))
        mime_msg = email.message_from_string(msg_str)
        return mime_msg
    except errors.HttpError, error:
        print (error)
def SendMessage(service, user_id, message):
    """Send an email message.

    Args:
        service: Authorized Gmail API service instance.
        user_id: User's email address. The special value "me"
        can be used to indicate the authenticated user.
        message: Message to be sent.

    Returns:
        Sent Message.
    """
    try:
        message = (service.users().messages().send(userId=user_id, body=message)
                .execute())
        return message
    except errors.HttpError, error:
        print(error)


def CreateMessage(sender, to, subject, tempMessage):
    """Create a message for an email.

    Args:
        sender: Email address of the sender.
        to: Email address of the receiver.
        subject: The subject of the email message.
        message_text: The text of the email message.

    Returns:
        An object containing a base64url encoded email object.
    """

    tempMessage['from'] = sender

    """
    Delete the subject item, as well as the To Item in the email object
    Because otherwise both the old parameters and new parameters will be conflicted with the old ones.

    """
    tempMessage.__delitem__("Subject")
    tempMessage.__delitem__("To")
    # tempMessage.__getitem__("To")
    tempMessage['to'] = to
    tempMessage['Subject'] = subject

    return {'raw': base64.urlsafe_b64encode(tempMessage.as_string())}


def CreateMessageWithAttachment(sender, to, subject, message_text, file_dir,
                                filename):
    """Create a message for an email.

    Args:
        sender: Email address of the sender.
        to: Email address of the receiver.
        subject: The subject of the email message.
        message_text: The text of the email message.
        file_dir: The directory containing the file to be attached.
        filename: The name of the file to be attached.

    Returns:
        An object containing a base64url encoded email object.
    """
    message = MIMEMultipart()
    message['to'] = to
    message['from'] = sender
    message['subject'] = subject

    msg = MIMEText(message_text)
    message.attach(msg)

    path = os.path.join(file_dir, filename)
    content_type, encoding = mimetypes.guess_type(path)

    if content_type is None or encoding is not None:
        content_type = 'application/octet-stream'
    main_type, sub_type = content_type.split('/', 1)
    if main_type == 'text':
        fp = open(path, 'rb')
        msg = MIMEText(fp.read(), _subtype=sub_type)
        fp.close()
    elif main_type == 'image':
        fp = open(path, 'rb')
        msg = MIMEImage(fp.read(), _subtype=sub_type)
        fp.close()
    elif main_type == 'audio':
        fp = open(path, 'rb')
        msg = MIMEAudio(fp.read(), _subtype=sub_type)
        fp.close()
    else:
        fp = open(path, 'rb')
        msg = MIMEBase(main_type, sub_type)
        msg.set_payload(fp.read())
        fp.close()

    msg.add_header('Content-Disposition', 'attachment', filename=filename)
    message.attach(msg)

    return {'raw': base64.urlsafe_b64encode(message.as_string())}

if __name__ == '__main__':
    main()  