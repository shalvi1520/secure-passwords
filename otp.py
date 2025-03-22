import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
def send_otp(email, otp):
    sender_email = "khareshalvi77@gmail.com"  
    sender_password = "crtvwihdgzzoroyg"  
    receiver_email = email

    subject = "Your OTP Code"
    body = f"Your OTP code is {otp}"

    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = receiver_email
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain'))

    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(sender_email, sender_password)
            server.sendmail(sender_email, receiver_email, msg.as_string())
    except Exception as e:
        print(f"Error sending email: {e}")
