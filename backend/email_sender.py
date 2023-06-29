import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication


class EmailSender:
    # 设置发件人、收件人和邮件主题
    def sending(self, recipient='zhangrongkai2000@163.com', verify_code=''):
        sender = '540891528@qq.com'
        subject = 'Test Email'

        # 创建一个多部分（multipart）电子邮件对象
        msg = MIMEMultipart()

        # 添加文本内容
        body = 'Your verify code is: '+verify_code
        msg.attach(MIMEText(body, 'plain'))

        # 设置电子邮件头部信息
        msg['From'] = sender
        msg['To'] = recipient
        msg['Subject'] = subject

        # 连接到SMTP服务器并发送电子邮件
        try:
            smtp_server = 'smtp.qq.com'
            smtp_port = 587
            server = smtplib.SMTP(smtp_server, smtp_port)
            smtp_password = 'fclioblajhyqztzb'  # Gmail密码g
            print("server connnect")
            server.starttls()
            server.login(sender, smtp_password)
            server.sendmail(sender, recipient, msg.as_string())
            server.quit()

            print('Email sent successfully!')
        except Exception as e:
            print('Error sending email:', e)