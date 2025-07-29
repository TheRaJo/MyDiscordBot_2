import sys
import ssl 
from imapclient import IMAPClient 
import email
from email.header import decode_header
import asyncio 

try:
    from mailauth import mailauth
except ImportError:
    print("[HIBA] Nem található a 'mailauth.py' fájl.")
    print("Kérlek, hozd létre a 'mailauth.py' nevű fájlt ugyanabban a mappában, ahol a bot fut,")
    print("és illeszd bele az e-mail hitelesítési adatait.")
    sys.exit(1)

async def check_for_new_emails():
    """
    Ellenőrzi az új e-maileket az IMAP szerveren az IMAPClient használatával.
    """
    try:
        
        context = ssl.create_default_context()
        # context.check_hostname = False
        # context.verify_mode = ssl.CERT_NONE

        with IMAPClient('imap.gmail.com', port=993, ssl=True, ssl_context=context) as client:
            client.login(mailauth.emailusername, mailauth.emailpassword)
            client.select_folder(mailauth.emailbox)

            messages = client.search(['UNSEEN'])

            new_email_subjects = []
            if messages:
                response = client.fetch(messages, ['RFC822'])

                for msg_id, data in response.items():
                    msg = email.message_from_bytes(data[b'RFC822'])
                    subject, encoding = decode_header(msg['Subject'])[0]
                    if isinstance(subject, bytes):
                        subject = subject.decode(encoding if encoding else 'utf-8')
                    new_email_subjects.append(subject)
                    client.set_flags([msg_id], ['\\Seen'])

            client.logout()
            return new_email_subjects
    except Exception as e:
        print(f"[HIBA] Hiba történt az e-mailek ellenőrzése során: {e}")
        return []
