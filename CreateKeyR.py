#CreateKeyR
#Amanda Lamphere
#This class creates the starting point 's' between
#0 and the prime to start the one-time pad at for the receiver.
#This must be the same 's' calculated for the sender as well.
#The class also sends the initial return email to continue the key
#exchange that creates the same 's'.

import pandas as pd
from datetime import datetime
from Exponentiation import *
import sys
import win32com.client
import random
import time
import smtplib
import email
import imaplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders

class CreateKeyR():

    #Initialize the variables
    def __init__(self, filepath, sender, receiver) -> None:
        self.filepath = filepath
        self.sender = sender
        self.receiver = receiver

    #Create starting point s
    def getR(self):

        #Set gmail boolean variable
        gmailR = False
        if self.receiver[-10:] == '@gmail.com':
            gmailR = True

        #Handles gmail
        if gmailR:
            password = input('Enter app password for gmail: \n')

            #Run until first message is found
            loop = True
            while(loop):
                print("Message Not Found")
                time.sleep(30)
                server = 'imap.gmail.com'
                mail = imaplib.IMAP4_SSL(server)
                mail.login(self.receiver, password)
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
                                #Get context
                                message = email.message_from_bytes(response_part[1])

                                #Extract sender and subject
                                mail_from = email.utils.parseaddr(message['from'])
                                mail_subject = message['subject']

                                if mail_from[1] == self.sender and mail_subject == "I'd Like to Share an Image":

                                    # plain text vs. multipart
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

                                    #Store the variable (primitive root)^a
                                    A = int(str(string[0:-3]))
                                    loop = False

        #Handles Outlook
        else:
            outlook = win32com.client.Dispatch("Outlook.Application").GetNamespace("MAPI")
            
            #Check Inbox
            inbox = outlook.GetDefaultFolder(6)

            messages = inbox.Items
            message = None

            #Run until message is found
            while(message is None):
                for msg in messages:
                    if msg.subject == "I'd Like to Share an Image":
                        print("Found Message")
                        message = msg
                if message is None:
                    print("Message Not Found")
                time.sleep(10)

            #Save message and sender information
            body_content = message.body
            sender = message.SenderEmailAddress

            list = body_content.split('\n', 1)
            sys.set_int_max_str_digits(0)

            #Store the variable (primitive root)^a
            A = int(list[0])

        #Calculate same start time and prime as sender
        escapes = ''.join([chr(char) for char in range(1, 32)])
        translator = str.maketrans('', '', escapes)
        t = list[1].translate(translator)
        t = t.strip()

        dateFormat = '%Y-%m-%d %H:%M:%S'

        #Calculating the prime
        startTime = datetime.strptime(t[-19:], dateFormat)
        hours = startTime.hour
        minutes = startTime.minute
        seconds = startTime.second
        startPrime = pow((hours+minutes), seconds, 100)

        #Import list of primes
        df = pd.read_csv(self.filepath)

        #Choose prime
        prime = df['Primes'][startPrime]
        primitiveRoot = df['Primitive Roots'][startPrime]

        #Calculate (primitive root)^b
        b = random.randint(pow(10,4), pow(10,5))
        phi = pow((int)(primitiveRoot), b)

        subject = "Let's Share"
        body = "{phi}".format(phi=phi) + "\n" + str(startTime)

        #Handles gmail
        if gmailR:
            #Send return email
            password = input('Enter app password for gmail: \n')
            msg = MIMEText(body)
            msg['Subject'] = subject
            msg['From'] = self.receiver
            msg['To'] = self.sender

            smtp_server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
            smtp_server.login(self.receiver, password)
            smtp_server.sendmail(self.receiver, self.sender, msg.as_string())
            smtp_server.quit()

        #Handles Outlook
        else:
            #Send email
            ol=win32com.client.Dispatch("outlook.application")
            olmailitem=0x0 #size of the new email
            newmail=ol.CreateItem(olmailitem)
            newmail.Subject= subject
            newmail.To=sender
            newmail.Body= body
            newmail.Send()
        print("Return Email Sent")

        #Calculate and return the starting point s: (primitive root)^(ab)
        s = pow(A, b, int(prime))
        return [s, startPrime]