#CreateKeyS
#Amanda Lamphere
#This class creates the starting point 's' between
#0 and the prime to start the one-time pad at for the sender.
#This must be the same 's' calculated for the receiver as well.
#The class also sends the initial email to start the key
#exchange that creates the same 's' and waits for the 
#receiving email to come back.

import pandas as pd
import sys
import random
import time
from Exponentiation import *
import win32com.client
import smtplib
import email
import imaplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders

class CreateKeyS():

    #Initializes the variables
    def __init__(self, startTime, startPrime, filepath, sender, receiver):
        self.startTime = startTime
        self.startPrime = startPrime
        self.filepath = filepath
        self.sender = sender
        self.receiver = receiver
        
    def getS(self):

        #Import list of primes
        df = pd.read_csv(self.filepath)

        #Choose prime
        prime = df['Primes'][self.startPrime]
        primitiveRoot = df['Primitive Roots'][self.startPrime]

        #Calculate public key (primitive root)^a
        a = random.randint(pow(10,4), pow(10,5))
        phi = pow((int)(primitiveRoot), a)

        #Extends amout of digits allowed in a string
        sys.set_int_max_str_digits(0)

        #Set up basis for email
        subject = "I'd Like to Share an Image"
        body = "{phi}".format(phi=phi) + "\n" + str(self.startTime)
        recipients = [self.receiver]

        #Set gmail boolean variable
        gmail = False
        if self.sender[-10:] == '@gmail.com':
            gmail = True

        #Handles gmail
        if gmail:

            #Send first email
            password = input('Enter app password for gmail: \n')
            msg = MIMEText(body)
            msg['Subject'] = subject
            msg['From'] = self.sender
            msg['To'] = ', '.join(recipients)

            smtp_server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
            smtp_server.login(self.sender, password)
            smtp_server.sendmail(self.sender, recipients, msg.as_string())
            smtp_server.quit()

            #Run until return message is found
            loop = True
            while(loop):
                print("Message Not Found")
                time.sleep(30)
                server = 'imap.gmail.com'
                mail = imaplib.IMAP4_SSL(server)
                mail.login(self.sender, password)
                mail.select('inbox')
                status, data = mail.search(None, 'ALL')
                mail_ids = []
                for block in data:
                    mail_ids += block.split()

                    #Search through emails
                    for i in mail_ids:
                        status, data = mail.fetch(i, '(RFC822)')

                        for response_part in data:
                            if isinstance(response_part, tuple):
                                #Get message
                                message = email.message_from_bytes(response_part[1])

                                #Get sender and subject
                                mail_from = email.utils.parseaddr(message['from'])
                                mail_subject = message['subject']

                                if mail_from[1] == self.receiver and mail_subject == "Let's Share":

                                    #Plain text vs. multipart
                                    if message.is_multipart():
                                        mail_content = ''
                                        for part in message.get_payload():
                                            #Extract plain text
                                            if part.get_content_type() == 'text/plain':
                                                mail_content += part.get_payload()
                                    else:
                                        mail_content = message.get_payload()
                                    list = mail_content.split('\n', 1)
                                    print("Found Message")

                                    sys.set_int_max_str_digits(0)
                                    string = list[0]

                                    #Store (primitive root)^b
                                    B = int(str(string[0:-3]))
                                    loop = False
        #Handles Outlook
        else:
            ol=win32com.client.Dispatch("outlook.application")
            olmailitem=0x0 #size of the new email
            newmail=ol.CreateItem(olmailitem)
            newmail.Subject= subject
            newmail.To=self.receiver
            newmail.Body= body
            newmail.Send()

            #Open outlook
            outlook = win32com.client.Dispatch("Outlook.Application").GetNamespace("MAPI")

            inbox = outlook.GetDefaultFolder(6) #Inbox
            messages = inbox.Items
            message = None

            #Run until return message is found
            while(message is None):
                for msg in messages:
                    if msg.subject == "Let's Share":
                        print("Found Message")
                        message = msg
                if message is None:
                    print("Message Not Found")
                time.sleep(10)

            #Get body and sender
            body_content = message.body
            sender = message.SenderEmailAddress

            list = body_content.split('\n', 1)

            sys.set_int_max_str_digits(0)
            #Store (primitive root)^b
            B = int(list[0])

        #Calculate s and return it: (primitive root)^(ab)
        s = pow(B, a, int(prime))

        return s