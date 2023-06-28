import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication

# 设置发件人、收件人和邮件主题
sender = '540891528@qq.com'
recipient = 'zhangrongkai2000@163.com'
subject = 'Test Email'

# 创建一个多部分（multipart）电子邮件对象
msg = MIMEMultipart()

# 添加文本内容
body = 'This is a test email.'
msg.attach(MIMEText(body, 'plain'))

# 添加附件
# with open('attachment.pdf', 'rb') as f:
#     attachment = MIMEApplication(f.read(), _subtype='pdf')
#     attachment.add_header('Content-Disposition', 'attachment', filename='attachment.pdf')
#     msg.attach(attachment)

# 设置电子邮件头部信息
msg['From'] = sender
msg['To'] = recipient
msg['Subject'] = subject

# 连接到SMTP服务器并发送电子邮件
try:
    smtp_server = 'smtp.qq.com'  # 使用Gmail SMTP服务器
    smtp_port = 587  # SMTP服务器端口
    smtp_username = '540891528@qq.com'  # Gmail用户名
    smtp_password = 'cmzyhfwrdvahbbcj'  # Gmail密码

    server = smtplib.SMTP(smtp_server, smtp_port)
    print("server connnect")
    server.starttls()
    server.login(smtp_username, smtp_password)
    server.sendmail(sender, recipient, msg.as_string())
    server.quit()

    print('Email sent successfully!')
except Exception as e:
    print('Error sending email:', e)