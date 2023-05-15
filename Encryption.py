#Encryption
#Amanda Lamphere
#This is the module that performs the main encryption
#for the application. This is started by the sender of
#the image and runs until the encrypted image is emailed.

import pandas as pd
import numpy as np
from datetime import datetime
import cv2 as cv
from PIL import Image
import win32com
from Exponentiation import *
from CreateKeyS import *
import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders

#Take in emails and handle gmail variable
sender = input('Enter your email: \n')

gmail = False
if sender[-10:] == '@gmail.com':
    gmail = True

receiver = input("Enter receipient's email: \n")

#Take in filepath
imgToImport = input("Enter filepath for desired image to be encrypted: \n")

#Creation of Start Time
startTime = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
startTime = datetime.strptime(startTime, '%Y-%m-%d %H:%M:%S')

#Calculate the starting prime in the out.CSV
hours = startTime.hour
minutes = startTime.minute
seconds = startTime.second
startPrime = pow((hours+minutes), seconds, 100)

#Import list of primes
outCSV = str(os.getcwd()) + "/out.csv"
df = pd.read_csv(outCSV)

#Choose prime
prime = df['Primes'][startPrime]
primitiveRoot = df['Primitive Roots'][startPrime]

#Import Image to Encrypt
img = Image.open(imgToImport)
rows = img.height
columns = img.width

#Create starting point s
getKey = CreateKeyS(startTime, startPrime, outCSV, sender, receiver)
s = getKey.getS()

#Get one-time pad
x = Exponentiation(s, prime, primitiveRoot, rows, columns)
newElements = x.oneTimePad()

#Encrypt and save image
i = 0
imgArr = np.array(img)
for row in range(rows):
    for column in range(columns):
        red = imgArr[row][column][0]
        green = imgArr[row][column][1]
        blue = imgArr[row][column][2]
        imgArr[row][column] = [(red + newElements[i]) % 256, (green + newElements[i+1]) % 256, (blue + newElements[i+2]) % 256]
        i = i + 3

#Save image to desired filepath
img = Image.fromarray(imgArr)
img.save(str(imgToImport[0:-5]) + "encrypted.png")
subject = "Encrypted Image"
body = "Check this out!"
recipients = [receiver]

#Handles Gmail
if gmail:
    #Must be created app password
    password = input('Enter app password for gmail: \n')
    msg = MIMEMultipart()
    msg['Subject'] = subject
    msg['From'] = sender
    msg['To'] = ', '.join(recipients)

    #Open file to send
    attachment = open(imgToImport, "rb")
    
    p = MIMEBase('application', 'octet-stream')
    p.set_payload((attachment).read())
    encoders.encode_base64(p)
    
    #Add attachment
    msg.attach(p)

    #Send email to receiver
    smtp_server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
    smtp_server.login(sender, password)
    smtp_server.sendmail(sender, recipients, msg.as_string())
    smtp_server.quit()

#Handles Outlook
else:
    ol=win32com.client.Dispatch("outlook.application")
    olmailitem=0x0 #size of the new email
    newmail=ol.CreateItem(olmailitem)
    newmail.Subject= subject
    newmail.To=receiver
    newmail.Body= body
    newmail.Attachments.Add(str(imgToImport[0:-5]) + "encrypted.png")
    newmail.Send()

print("Encrypted Image Sent")

#How long to application took
print(datetime.now() - startTime)