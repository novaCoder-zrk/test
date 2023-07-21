import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
import pandas as pd

def sending(recipient, verify_code):
    # 设置发件人、收件人和邮件主题
    sender = 'support@metaphantasy.com'
    subject = 'Verify Code'

    # 创建一个多部分（multipart）电子邮件对象
    msg = MIMEMultipart()

    # 添加文本内容
    body = 'Your verify code is: '+verify_code +". The verify code will expire in five minutes."
    msg.attach(MIMEText(body, 'plain'))

    # 设置电子邮件头部信息
    msg['From'] = 'Metaphantasy Support <' + sender + '>'
    msg['To'] = recipient
    msg['Subject'] = subject

    # 连接到SMTP服务器并发送电子邮件
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
        # 邮件发送不成功
        print('Error sending email:', e)
        return False

