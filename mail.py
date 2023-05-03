import smtplib
import ssl
from dotenv import load_dotenv
from os import environ as env
from threading import Thread as T
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from datetime import datetime
from traceback import format_exc


load_dotenv()

def send(reciever, subject, content, sender_name=env['MAIL_SENDER']):
	def _send(reciever, subject, content, sender_name):
		smtp_server = env['MAIL_SERVER']
		port = int(env['MAIL_PORT'])
		sender_email = env['MAIL_SENDER']
		reciever_email = reciever
		msg = MIMEMultipart('alternative')
		msg['Subject'] = "[Twilight] " + subject
		msg['From'] = sender_name
		msg['To'] = reciever
		msg.attach(MIMEText(content, 'html'))
		password = env['MAIL_PASSWORD']
		ctx = ssl.SSLContext(ssl.PROTOCOL_TLS)
		server = smtplib.SMTP(smtp_server, port)
		server.set_debuglevel(1)
		try:
			server.ehlo()
			server.starttls(context=ctx)
			server.ehlo()
			server.login(sender_email, password)
			server.sendmail(sender_email, reciever_email, msg.as_string())
		except Exception as e:
			err = format_exc()
			ee = err.replace('\n', '<br>\n')
			with open('log.txt', 'a') as log:
				logstr = f"""<code>
    				Exception occured at <i>{datetime.utcnow().strftime('%m/%d/%y %H:%M:%S')}</i>:<br> \
    				{type(e).__name__}: {e}<br>
    				{ee}
				</code>
				<br>
				<br>
				<br>"""
				log.write(logstr)
		finally:
			server.quit()
	T(target=_send, args=(reciever, subject, content, sender_name)).start()
