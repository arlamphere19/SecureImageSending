#Decryption
#Amanda Lamphere
#This file is used to decrypt an image. It is begun
#when an email (Subject: I'd Like to Share an Image) 
#from a sender has been received to begin the process.

import pandas as pd
import numpy as np
from PIL import Image
import Exponentiation
from CreateKeyR import *
import time
import os
import smtplib
import email
import imaplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders

#Import list of primes
outCSV = str(os.getcwd()) + "/out.csv"
df = pd.read_csv(outCSV)

#Get Info from Email
receiver = input('Enter your email: \n')
sender = input("Enter sender's email: \n")
getKey = CreateKeyR(outCSV, sender, receiver)
list = getKey.getR()
s = list[0]

#Boolean to see if gmail
gmailR = False
if receiver[-10:] == '@gmail.com':
    gmailR = True

#Handles Gmail
if gmailR:
    password = input('Enter app password for gmail: \n')
    loop = True
    while(loop):
        print("Message Not Found")
        time.sleep(30)
        server = 'imap.gmail.com'
        mailBox = imaplib.IMAP4_SSL(server)

        # Login
        mailBox.login(receiver, password)

        boxList = mailBox.list()

        mailBox.select()
        searchQuery = 'Encrypted Image'

        result, data = mailBox.uid('search', None, searchQuery)
        ids = data[0]
        # list of uids
        id_list = ids.split()

        i = len(id_list)
        for x in range(i):
            latest_email_uid = id_list[x]

            #Get the email body
            result, email_data = mailBox.uid('fetch', latest_email_uid, '(RFC822)')

            raw_email = email_data[0][1]

            #Convert byte literal
            raw_email_string = raw_email.decode('utf-8')
            email_message = email.message_from_string(raw_email_string)

            #Downloading Attachments
            for part in email_message.walk():
                #This part of the code is not correct or complete
                if part.get_content_maintype() == 'multipart':
                    continue
                if part.get('Content-Disposition') is None:
                    continue
                fileName = part.get_filename()

                imgName = input("Enter nmae to save file under: \n")
                imgToImport = input("Enter path to save file to: \n")

                if bool(fileName):
                    filePath = os.path.join(imgToImport, imgName)
                    if not os.path.isfile(filePath) :
                        fp = open(filePath, 'wb')
                        fp.write(part.get_payload(decode=True))
                        fp.close()
    print("Found Message")
    loop = False

#Handles Outlook
else:
    outlook = win32com.client.Dispatch("Outlook.Application").GetNamespace("MAPI")

    inbox = outlook.GetDefaultFolder(6) #Inbox

    messages = inbox.Items
    message = None

    #Run while waiting to receive message with image
    while(message is None):
        for msg in messages:
            if msg.subject == "Encrypted Image":
                print("Found Message")
                message = msg
        if message is None:
            print("Message Not Found")
        time.sleep(10)

    #Get attachment
    attachments = message.Attachments
    attachment = attachments[0]

    #Allow user to save under name and filepath
    imgName = input("Enter name to save file under: \n")
    imgToImport = input("Enter path to save file to: \n")
    imgPath = imgToImport + "/" + imgName + ".png"
    attachment.SaveAsFile(imgPath)

newimg = Image.open(imgPath)

rows = newimg.height
columns = newimg.width

#Choose prime
startPrime = list[1]
prime = df['Primes'][startPrime]
primitiveRoot = df['Primitive Roots'][startPrime]

#Get one-time pad
x = Exponentiation(s, prime, primitiveRoot, rows, columns)
newElements = x.oneTimePad()

#Decrypt image and send
newimgArr = np.array(newimg)
j = 0
for row in range(rows):
    for column in range(columns):
        red = newimgArr[row][column][0]
        green = newimgArr[row][column][1]
        blue = newimgArr[row][column][2]
        newimgArr[row][column] = [(red - newElements[j]) % 256, (green - newElements[j+1]) % 256, (blue - newElements[j+2]) % 256]
        j = j + 3

newimg = Image.fromarray(newimgArr)

#Save image to filepath with *name*decrypted.jpeg
newimg.save(imgToImport + "/" + imgName + "decrypted.jpeg")
print("Image Saved to Filepath")
