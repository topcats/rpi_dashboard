# Auto Run Setup

## Data Getter
The Data getter is best setup to run on a schedule using cron tab
```bash
$> crontab -e
```
add the line below, to run the collection tool every 15 mintues
```bash
*/15 * * * * python /home/pi/dashdisplay/eClockDataGetter.py
```

## Dash Display
```bash
cd ~
cd .config/lxsession/LXDE-pi/
nano autostart
```
Add the line below BEFORE the @xscreensaver
```bash
@/usr/bin/python /home/pi/dashdisplay/eClock.py
```
