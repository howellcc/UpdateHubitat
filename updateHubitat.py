import requests, json, smtplib, configparser
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# REQUIREMENTS:
# pip install requests

def UpgradeHub():
    config = ReadConfig()

    hubUsername = config["HUB"]["hubUsername"]
    hubPassword = config["HUB"]["hubPassword"]
    hubAddress = config["HUB"]["hubAddress"]
    
    emailServerSettings = {
        "useEmailNotifications": config["EMAIL"]["useEmailNotifications"],
        "serverAddress": config["EMAIL"]["serverAddress"],
        "serverPort": config["EMAIL"]["serverPort"],
        "senderEmail": config["EMAIL"]["senderEmail"],
        "useTLS":ToBool(config["EMAIL"]["useTLS"]),
        "useAuthentication":ToBool(config["EMAIL"]["useAuthentication"]),
        "senderPassword":config["EMAIL"]["senderPassword"],
        "recipientEmail": config["EMAIL"]["recipientEmail"]
    }

    baseurl = f"http://{hubAddress}"
    loginUrl = f"{baseurl}/login"
    checkUpdateUrl = f"{baseurl}/hub/cloud/checkForUpdate"
    updateHubUrl = f"{baseurl}/hub/cloud/updatePlatform"

    #build login data
    loginData = {
        "username" : hubUsername,
        "password" : hubPassword
    }

    #create session
    s = requests.session()

    #attempt login
    loginResponse = s.post(loginUrl,data=loginData)

    if loginResponse.status_code == 200:
        #check For Update
        updateCheckResponse = s.get(checkUpdateUrl)

        if updateCheckResponse.status_code == 200:
            updateCheckData = json.loads(updateCheckResponse.text)

            # updateCheckData example return
            # {
            # 'version': '2.3.5.146', 
            # 'upgrade': True, 
            # 'releaseNotesUrl': 'https://community.hubitat.com/t/release-2-3-5-available/113395/99', 
            # 'status': 'UPDATE_AVAILABLE'
            # }

            if updateCheckData["status"] == "UPDATE_AVAILABLE":
                #send email notification about update.
                upgradeMessage = f"Hubitat Hub at {hubAddress} is about to be updated to\n"
                upgradeMessage += f"version: {updateCheckData['version']}\n"
                upgradeMessage += f"release notes: {updateCheckData['releaseNotesUrl']}"
                
                SendEmail(emailServerSettings, "Hubitat Hub Upgrade", upgradeMessage)

                #Tell up to perform update
                s.get(updateHubUrl)
            else:
                SendEmail(emailServerSettings, "Hubitat Hub Upgrade - Not available", "No hub updates are available at this time.")

        else:
            SendEmail(emailServerSettings, "Hubitat Hub Upgrade Failed", "Update check failed")
    else:
        SendEmail(emailServerSettings, "Hubitat Hub Upgrade Failed", "Hubitat login failed")



def SendEmail(emailSettings, subject, message):
    if(emailSettings["useEmailNotifications"]):
        # Create a multipart message
        email_message = MIMEMultipart()
        email_message['From'] = emailSettings["senderEmail"]
        email_message['To'] = emailSettings["recipientEmail"]
        email_message['Subject'] = subject

        # Add the message body
        email_message.attach(MIMEText(message, 'plain'))

        # Create a secure SSL/TLS connection to the SMTP server
        smtp_conn = smtplib.SMTP(emailSettings["serverAddress"], emailSettings["serverPort"])
        
        if(emailSettings["useTLS"]):
            smtp_conn.starttls()

        try:
            if(emailSettings["useAuthentication"]):
                # Log in to the SMTP server
                smtp_conn.login(emailSettings["senderEmail"], emailSettings["senderPassword"])

            # Send the email
            smtp_conn.sendmail(emailSettings["senderEmail"], emailSettings["recipientEmail"], email_message.as_string())

            #print("Email sent successfully!")
        except smtplib.SMTPAuthenticationError:
            print("Failed to authenticate. Please check your email credentials.")
        except smtplib.SMTPException as e:
            print(f"An error occurred while sending the email: {str(e)}")

        # Close the SMTP connection
        smtp_conn.quit()
    else:
        return

def ReadConfig():
    config = configparser.ConfigParser()
    config.read('updateHubitat.conf')
    return config

def ToBool(stringBool):
    if(stringBool.lower() in ['true','t']):
        return True
    else:
        return False

UpgradeHub()
