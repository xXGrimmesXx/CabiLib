import base64
import os
import mimetypes
from email.message import EmailMessage
from app.services.google_api_manager import get_gmailV1_service


def save_draft(service, user_id, message_body):
    if service is None:
        service = get_gmailV1_service()

    message = EmailMessage()
    message.set_content(message_body.get('body', ''))
    message['To'] = message_body.get('to', '')
    message['From'] = user_id
    message['Subject'] = message_body.get('subject', '')

    files = message_body.get('attachments')
    if files:
        for file_path in files:
            try:
                with open(file_path, 'rb') as f:
                    data = f.read()

                ctype, encoding = mimetypes.guess_type(file_path)
                if ctype is None:
                    maintype, subtype = 'application', 'octet-stream'
                else:
                    maintype, subtype = ctype.split('/', 1)

                filename = os.path.basename(file_path)
                message.add_attachment(data, maintype=maintype, subtype=subtype, filename=filename)
            except Exception as e:
                raise

    raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode()
    create_message = {
        'message': {
            'raw': raw_message
        }
    }
    draft = service.users().drafts().create(userId=user_id, body=create_message).execute()
    return draft

if __name__ == '__main__':
    service = get_gmailV1_service()

    user_id = 'me'
    message_body = {
        'to': 'm.louis.arnould@gmail.com',
        'subject': 'Test Draft Email',
        'body': 'This is a test draft email created using Gmail API.',
        'attachments': [r'C:\Users\mloui\Desktop\CabiLib\src\cabilib_logo.png', r'C:\Users\mloui\Desktop\CabiLib\src\trucs à faire.txt',r"C:\Users\mloui\Downloads\CV Louis Arnould Anglais.pdf"]  # Add file paths if needed
    }
    draft = save_draft(service,user_id, message_body)
    print(f"Draft created with ID: {draft['id']}")