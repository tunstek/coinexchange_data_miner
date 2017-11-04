import smtplib
from email.MIMEMultipart import MIMEMultipart
from email.MIMEText import MIMEText

from send_email_config import *
# This file contains the credentials for your email client
# eg:
#   mail_server_username = *SERVER USERNAME*
#   mail_server_password = *SERVER PASSWORD*
#   sender = *DISPLAYED SENDER*
#   receiver = *DISPLAYED RECEIVER*

# Check to ensure they are defined
try:
    mail_server_username
    mail_server_password
    sender
    receiver
except:
    print "Err: Please define email credentials in send_email_config.py - see example for details"
    exit()



def send_alert(subject, body):


    msg = MIMEMultipart()
    msg['From'] = sender
    msg['To'] = receiver
    msg['Subject'] = subject
    message = body
    msg.attach(MIMEText(message))

    mailserver = smtplib.SMTP('smtp1r.cp.blacknight.com',587)
    # identify ourselves to smtp gmail client
    mailserver.ehlo()
    # secure our email with tls encryption
    mailserver.starttls()
    # re-identify ourselves as an encrypted connection
    mailserver.ehlo()
    mailserver.login(mail_server_username, mail_server_password)

    mailserver.sendmail(sender,receiver,msg.as_string())

    mailserver.quit()
