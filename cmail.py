import smtplib
from smtplib import SMTP
from email.message import EmailMessage

def sendmail(to,subject,body):
    server=smtplib.SMTP_SSL('smtp.gmail.com',465)
    server.login('siri.kamma7@gmail.com','dphx hecq ymwl idzh')
    msg=EmailMessage()
    msg['From']='siri.kamma7@gmail.com'
    msg['Subject']=subject
    msg['To']='20n01a0224@scce.ac.in'
    msg.set_content(body)
    server.send_message(msg)
    server.quit()
    