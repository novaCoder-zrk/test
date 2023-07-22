import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


def sending(recipient, verify_code):
    sender = 'support@metaphantasy.com'
    subject = 'Verify Code'

    msg = MIMEMultipart()

    body = 'Your verify code is: '+verify_code +". The verify code will expire in five minutes."
    msg.attach(MIMEText(body, 'plain'))

    msg['From'] = 'Metaphantasy Support <' + sender + '>'
    msg['To'] = recipient
    msg['Subject'] = subject

    try:
        smtp_server = 'zhenxiao.mail.pairserver.com'
        smtp_port = 465
        server = smtplib.SMTP_SSL(smtp_server,smtp_port)
        smtp_password = 'chatbot230704'
        server.login(sender, smtp_password)
        server.sendmail(sender, recipient, msg.as_string())
        server.quit()
        print('Email sent successfully!')
        return True
    except Exception as e:
        print('Error sending email:', e)
        return False

