import smtplib, ssl, sys
import getpass
import argparse
import email.message

def Email_sender(sender,list_of_receivers,password,message,subject,number_of_messages):
    port = 465
    if check(sender,list_of_receivers) == 1:
        print('Sending Mail')
        for i in range(number_of_messages):
            for receiver in list_of_receivers:
                try:
                    with smtplib.SMTP_SSL("smtp.gmail.com", port, context = ssl.create_default_context()) as server:

                        msg = email.message.Message()
                        msg['Subject'] = subject
                        msg['From'] = sender
                        msg['To'] = receiver
                        msg.add_header('Content-Type','text/html')
                        msg.set_payload(message)
                        server.login(sender,password)
                        server.sendmail(msg['From'], [msg['To']], msg.as_string())
                        server.quit()
                        print('Email sent.')
                except:
                    print("Login error...")
                    return -1
                    exit(0)
    else:
        print("Incorrect email ID.")
        print("This program only supports the gmail smtp service.")
        print("Exiting")
        return -2

def check(sender,list_of_receivers):
    if '@gmail.com' in sender:
        pass
    else:
        return 0
    for i in list_of_receivers:
        if '@gmail.com' in i:
            pass
        else:
            return 0
    return 1