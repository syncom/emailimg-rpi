# emailimg-rpi
A simple tool turns a Raspberry Pi (RPi) into a security monitoring system, using email as a transport layer. The script has only been tested with an outlook.com account.

# What are needed
- A Raspberry Pi (version 1-3) Model B (needs Internet connectivity)
- A camera module (this would work: https://www.raspberrypi.org/products/camera-module/)
- Python 2.7: smtplib, pyOpenSSL, ndg-httpsclient, pyasn1, PIL
- An email account (a free one can be obtained from live.com)


## Tweet a JPEG image upon motion detection

Usage:

1. Install the camera module on the RPi, and enable camera module from `rspi-config` menu.

2. Obtain an email account that supports SMTP (e.g., from outlook.com). 

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
