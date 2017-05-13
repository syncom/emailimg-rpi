#!/usr/bin/env python

"""Email an image to a prescribed address
This module emails an image file to a pre-configured address
"""

import os
import time
import argparse
import smtplib
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart

# Tested for @outlook.com and @sina.com emails
config_file = os.path.dirname(os.path.realpath(__file__)) + '/.config'

def send_email_with_image(img_filepath, subject):
    """
    This function loads email configuration from a file, and sends the
    captured image to (and from) this email address as an attachment.
    """
    [smtp_server, smtp_port, username, password] = get_config_info()
    from_address = username
    to_address = username
    image_data = open(img_filepath, 'rb').read()
    msg = MIMEMultipart()
    msg['Subject'] = subject
    msg['From'] = from_address
    msg['To'] = to_address
    text = MIMEText(subject)
    msg.attach(text)
    image = MIMEImage(image_data, name=os.path.basename(img_filepath))
    msg.attach(image)

    s = smtplib.SMTP(smtp_server, smtp_port)
    s.ehlo()
    s.starttls()
    s.ehlo()
    s.login(username, password)
    s.sendmail(from_address, to_address, msg.as_string())
    s.quit()

def get_config_info():
    ''' Obtain SMTP server info from file .config
    Returns list
    '''
    f = open(config_file, 'rb')
    c = f.read()
    t = c.splitlines()
    return t[0:4]

def get_mtime_str(fil):
    ''' Obtain file modification time string.
    Return str
    '''
    try:
        mtime = os.path.getmtime(fil)
    except OSError:
        return ''
    is_dst = time.daylight and time.localtime().tm_isdst > 0
    # UTC offset in seconds
    offset = - (time.altzone if is_dst else time.timezone)
    time_str = time.ctime(mtime) + ' UTC ' + str(offset/3600)
    return time_str

def do_email(img_filepath):
    '''Email, image modification time as subject and image as attachment
    '''
    subject = get_mtime_str(img_filepath)
    if not subject:
        print "Something has gone wrong. No email was sent."
    else:
        send_email_with_image(img_filepath, subject)
        print "Emailed image taken at " + subject

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("filepath")
    args = parser.parse_args()
    do_email(args.filepath)


