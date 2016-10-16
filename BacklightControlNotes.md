# System Setup

## Get Correct Firmware
```bash
sudo apt-get install rpi-update 
sudo rpi-update
```

## Permissions Change
```bash
sudo nano /etc/udev/rules.d/backlight-permissions.rules
SUBSYSTEM=="backlight",RUN+="/bin/chmod 666 /sys/class/backlight/rpi_backlight/brightness /sys/class/backlight/rpi_backlight/bl_power"
```

## Disable auto poweroff
I also added a line to "/etc/lightdm/lightdm.conf" to turn off the automatic screen blanking, so the screen doesn't actually "blank" or "sleep" anymore, the button just manually turns the backlight on/off. Add the following under the "[SeatDefaults]" section in "/etc/lightdm/lightdm.conf".
```
[SeatDefaults]
xserver-command=X -s 0 -dpms
```

# Backlight Control
```bash
echo 0 > /sys/class/backlight/rpi_backlight/bl_power
echo 1 > /sys/class/backlight/rpi_backlight/bl_power
```
## Python Code
```python
backlight = open('/sys/class/backlight/rpi_backlight/bl_power', 'w')
backlight.write('1') # turn on
backlight.write('0') # turn off
```

# Brightness Control
Must be between 1 and 255
```bash
echo 80 > /sys/class/backlight/rpi_backlight/brightness
```
