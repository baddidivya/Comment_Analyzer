

import smtplib
import mimetypes
from email.mime.multipart import MIMEMultipart
from email.message import Message
from email.mime.text import MIMEText
from email.mime.image import MIMEImage


def mailsend(emailto):


  emailfrom = "commentanalyzer12@gmail.com"
  fileToSend = ["Full Comments.csv", "Positive Comments.csv", "Negative Comments.csv"]
  ImagesToSend = ["word_cloud_plot.png","pie_chart_plot.png"]
  username = "commentanalyzer12@gmail.com"
  password = "xtkcyiszhomxzekh"


  msg = MIMEMultipart()
  msg["From"] = emailfrom
  msg["To"] = emailto
  msg["Subject"] = "Comments Analysis is ready  -From COMMENT ANALYZER"



  subtype = 'vnd.ms-excel'
  for f in fileToSend:
    fp = open(f, encoding = 'utf8')
    attachment = MIMEText(fp.read(), _subtype = subtype)
    fp.close()
    attachment.add_header("Content-Disposition", "attachment", filename=f)
    msg.attach(attachment)
  for f in ImagesToSend:
    with open(f, 'rb') as fp:
        attachment = MIMEImage(fp.read())
        attachment.add_header("Content-Disposition", "attachment", filename=f)
        msg.attach(attachment)


  server = smtplib.SMTP("smtp.gmail.com:587")
  server.starttls()
  server.login(username,password)
  server.sendmail(emailfrom, emailto, msg.as_string())
  server.quit()
