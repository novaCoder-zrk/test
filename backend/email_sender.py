import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
import pandas as pd
from verify_code_handler import get_verify_code


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


def send_verify_code(username):
    df = pd.read_excel('account.xlsx')
    mask = df["account"] == username

    user_data = df.loc[mask]
    user_email = user_data['email'].values[0]
    print(user_email)
    code = get_verify_code(username)
    return sending(user_email, code) #返回邮件发送状态

#
# def try_sending():
#     recipient = 'zhangrongkai2000@163.com'
#     code = "AAA"
#     sending(recipient, code)
#
#
# try_sending()