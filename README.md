# emailimg-rpi
A simple tool turns a Raspberry Pi (RPi) into a security monitoring system, using email as a transport layer. The script has only been tested with an outlook.com account and a sina.com account.

# What are needed
- A Raspberry Pi (version 1-3) Model B (needs Internet connectivity)
- A camera module (this would work: https://www.raspberrypi.org/products/camera-module/)
- Python 2.7: smtplib, pyOpenSSL, ndg-httpsclient, pyasn1, PIL
- An email account (a free one can be obtained from live.com or sina.com)


## Email a JPEG image upon motion detection

Usage:

1. Install the camera module on the RPi, and enable camera module from `rspi-config` menu.

2. Obtain an email account that supports SMTP (e.g., from outlook.com or sina.com). 

3. Override the corresponding strings in `.config` with the respective values, for the SMTP server name & port, email username (address), and email password.

4. Create a ramdisk of size 80M bytes to store motion-detected image files.
   ```
   mkdir /mnt/ramdisk_motion
   mount -t tmpfs -o size=80M tmpfs /mnt/ramdisk_motion 
   ```

   To make the ramdisk persist over reboots, add the following lines to `/etc/fstab`:
   ```
    # ramdisk for camera capture
    tmpfs       /mnt/ramdisk_motion tmpfs   nodev,nosuid,noexec,nodiratime,size=80m   0 0
   ``` 

5. Run `emailimg-motion-run.sh`. 

6. (Optional) To turn off the LED red light in the camera module when taking pictures, edit the file `/boot/config.txt` to add / change the following line:
    ```
    disable_camera_led=1
    ```
## Email a JPEG image every 10 minutes (for time-lapse photography)

Usage:
1. Follow steps 1-3 as in the above section

2. Because we are going to write and delete a lot of files, in order to prevent the SD card worn out, create a ramdisk (of size 25M bytes) to store image files created during the process.
    ```
    mkdir /mnt/ramdisk_still
    mount -t tmpfs -o size=25m tmpfs /mnt/ramdisk_still
    ```
   To make the ramdisk persist over reboots, add the following lines to `/etc/fstab`:

    ```
    # ramdisk for camera capture (added 20160306)
    tmpfs       /mnt/ramdisk_still tmpfs   nodev,nosuid,noexec,nodiratime,size=25m   0 0
    ``` 
3. Create a cron job to take a still picture from the RPi camera module every 10 minute. Do `crontab -e` and add the following:

    ```
    # take still picture every 10 minutes, and email
    */10 * * * * /home/pi/bin/emailimg-rpi/email_raspistill.sh 2>&1
    ```
4. Do whatever you like with the emailed images. See the next section for time-lapse photography.

## How to make a time-lapse video from still images using Imagemagick and FFMPEG

1. Put all .jpg images to a directory, say `original`. Change to this directory.

2. Before converting to video, remove image meta info (to reduce the size of the final artifect):
   ```
   list=$(find `pwd` -name '*.jpg' | sort)
   mogrify -strip ${list}
   ```
3. (Optional) Turn images into grayscale, if a black-and-white video is preferred. Save grayscale images to a separate directory, say `grayscale`.
   ```
   for i in ${list}; do convert -type Grayscale "${i}" grayscale/"${i}"; done
   ```

4. (Optional) Normalize the histogram of the images (original or grayscale) using [histmatch](http://www.fmwconcepts.com/imagemagick/histmatch/index.php). Change into the directory of interest (`orignal` or `grayscale`), put the `histmatch` script there, and then do the following.
   ```
   for i in ${list}; do ./histmatch -c gray ref.jpg "${i}" normalized/"${i}"; done
   ```
   Here, `ref.jpg` is a reference image for histogram normalization. It is usually picked from `${list}.

5. Use Imagemagick to convert images of interest (in directories `original`, `grayscale`, `normalized`, respectively) to a MPEG video, adding 0.1 second delay between frames.
   ```
   (Change into appropriate directory)
   list=$(find `pwd` -name '*.jpg' | sort)
   convert -delay 10 ${list} video.mpeg
   ```
   Turn MPEG to MP4 using ffmpeg.
   ```
   ffmpeg -i video.mpeg video.mp4
   ```

   The final product is `video.mp4`. Enjoy!

## Some SMTP server settings

* outlook.com
  - Server: smtp-mail.outlook.com
  - Port: 587
  - Note: Outlook.com is quite annoying, in that it asks for human
    "verification" over and over again after a few emails are sent through
    smtplib. I would avoid outlook.com email for this application.

* sina.com
  - Server: smtp.sina.com
  - Port: 25

