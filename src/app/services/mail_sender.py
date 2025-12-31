from base64 import urlsafe_b64encode
from os import path
from mimetypes import guess_type
from email.message import EmailMessage
import traceback
from app.services.google_api_manager import get_gmailV1_service


def save_draft(message_body):
    """Saves a draft email in the user's Gmail account.
    Args:
        message_body: A dictionary containing 'to', 'subject', 'body', and optional 'attachments' (list of file paths).
    Returns:
        The created draft email.
    """
    
    service = get_gmailV1_service()

    message = EmailMessage()
    # Utiliser HTML comme corps du message
    message.set_content(message_body.get('body', ''), subtype='html')
    message['To'] = message_body.get('to', '')
    message['From'] = 'me'
    message['Subject'] = message_body.get('subject', '')

    files = message_body.get('attachments')
    if files:
        for file_path in files:
            try:
                with open(file_path, 'rb') as f:
                    data = f.read()

                ctype, encoding = guess_type(file_path)
                if ctype is None:
                    maintype, subtype = 'application', 'octet-stream'
                else:
                    maintype, subtype = ctype.split('/', 1)

                filename = path.basename(file_path)
                message.add_attachment(data, maintype=maintype, subtype=subtype, filename=filename)
            except Exception as e:
                print(f"Erreur lors de l'ajout de la pièce jointe {file_path}:")
                traceback.print_exc()
                raise

    raw_message = urlsafe_b64encode(message.as_bytes()).decode()
    create_message = {
        'message': {
            'raw': raw_message
        }
    }
    draft = service.users().drafts().create(userId='me', body=create_message).execute()
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