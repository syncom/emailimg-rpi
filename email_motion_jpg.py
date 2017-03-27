#!/usr/bin/env python

"""Email motion-detected JPEG image.
This module captures and emails a motion-detected JPEG image from a Raspberry
Pi with a camera module. The image capture part is credited to the excellent
post https://www.raspberrypi.org/forums/viewtopic.php?t=45235, by brainflakes.
Read brainflakes' original post for the algorithm. I have removed the force
capture part for this script.

The design of this software is very similar to that of
https://github.com/syncom/twitimg-rpi. The only difference is that this tool
uses email instead of twitter as the transport layer, which is useful in
countries where twitter access is blocked.
"""

import StringIO
import subprocess
import os
import sys
import time
import argparse
from datetime import datetime
from PIL import Image
import smtplib
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart

# Tested for @outlook.com email
smtp_server = ''
smtp_port = ''
username = ''
password = ''
config_file = os.path.dirname(os.path.realpath(__file__)) + '/.config'

def send_email_with_image(img_filepath, subject):
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

def get_mtime_str(file):
    ''' Obtain file modification time string.
    Return str
    '''
    try:
        mtime = os.path.getmtime(file)
    except OSError:
        return ''
    is_dst = time.daylight and time.localtime().tm_isdst > 0
    # UTC offset in seconds
    offset = - (time.altzone if is_dst else time.timezone)
    time_str = time.ctime(mtime) + ' UTC' + str(offset/3600)
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


# Motion detection and imaging part
#
# Motion detection settings:
# - threshold: how much a pixel has to change by to be marked as "changed"
# - sensitivity: how many changed pixels before capturing an image
threshold = 10
sensitivity = 729
test_width = 100
test_height = 75

# File settings
save_width = 1280
save_height = 960
reserve_diskspace = 40 * 1024 * 1024 # Keep 40 mb free on disk

# Capture a small bitmap test image, for motion detection
def captureTestImage():
    command = "raspistill -w %s -h %s -t 1000 -e bmp -o -" % (test_width,
              test_height)
    output = None
    image_data = StringIO.StringIO()
    try:
        output = subprocess.check_output(command, shell=True)
    except subprocess.CalledProcessError:
        print "Command exited with non-zero code. No output."
        return None, None

    if output:
        image_data.write(output)
        image_data.seek(0)
        im = Image.open(image_data)
        buffer = im.load()

    image_data.close()
    return im, buffer

# Save a full size image to disk
def saveImage(width, height, dirname, diskSpaceToReserve):
    keepDiskSpaceFree(dirname, diskSpaceToReserve)
    time = datetime.now()
    filename = "motion-%04d%02d%02d-%02d%02d%02d.jpg" % (time.year, time.month, time.day, time.hour, time.minute, time.second)
    command = "raspistill -w %s -h %s -t 10 -e jpg -q 15 -o %s/%s" % (width, height, dirname.rstrip('/'), filename)
    try:
        subprocess.call(command, shell=True)
    except subprocess.CalledProcessError:
        print "Command exited with non-zero code. No file captured."
        return None

    print "Captured %s/%s" % (dirname.rstrip('/'), filename)
    return dirname.rstrip('/') + '/' + filename

# Keep free space above given level
def keepDiskSpaceFree(dirname, bytesToReserve):
    if (getFreeSpace(dirname) < bytesToReserve):
        for filename in sorted(os.listdir(dirname)):
            if filename.startswith("motion") and filename.endswith(".jpg"):
                os.remove(dirname.rstrip('/') +"/" + filename)
                print "Deleted %s/%s to avoid filling disk" % ( dirname.rstrip('/'), filename )
                if (getFreeSpace(dirname) > bytesToReserve):
                    return
    return

# Get available disk space
def getFreeSpace(dir):
    st = os.statvfs(dir)
    du = st.f_bavail * st.f_frsize
    return du
 
# Where work happens
def do_email_motion(dirname):
    				          
    # Get first image
    captured1 = False
    while (not captured1):
        image1, buffer1 = captureTestImage()
        if image1:
            captured1 = True

    while (True):

        # Get comparison image
        captured2 = False
        while (not captured2):
            image2, buffer2 = captureTestImage()
            if image2:
                captured2 = True

        # Count changed pixels
        changedPixels = 0
        for x in xrange(0, test_width):
            for y in xrange(0, test_height):
                # Just check green channel as it's the highest quality channel
                pixdiff = abs(buffer1[x,y][1] - buffer2[x,y][1])
                if pixdiff > threshold:
                    changedPixels += 1

        # Save an image if pixels changed
        if changedPixels > sensitivity:
            fpath = saveImage(save_width, save_height, dirname, reserve_diskspace)
            # Tweet saved image
            if fpath:
                try:
                    do_email(fpath)
                except Exception, e:
                    print "Email might not have been sent. Encountered exception, as follows: "
                    print e
                    time.sleep(300) # Wait 5 minutes
       
        # Swap comparison buffers
        image1 = image2
        buffer1 = buffer2

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("dir_path")
    args = parser.parse_args()
    do_email_motion(args.dir_path)
