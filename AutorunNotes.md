# Raspberry PI Dash Display - Auto Run Setup

## Data Getters

The Data getter is best setup to run on a schedule using cron tab

```bash
$> crontab -e
```

add the lines below;
the collection tool will run every 15 minutes
and then a daily collection tool once a day at 4am

```bash
*/15 * * * * python3 /home/pi/dashdisplay/eClockDataGetter.py
0 4 * * 1 python3 /home/pi/dashdisplay/eDailyDataGetter.py
```

## RPI Display - Auto Run Service Setup

The Display can be setup to run automatically

```bash
sudo cp edisplay.service /lib/systemd/system/
sudo chmod 644 /lib/systemd/system/edisplay.service
chmod +x /home/pi/dashdisplay/eDisplay.py
sudo systemctl daemon-reload
sudo systemctl enable edisplay.service
sudo systemctl start edisplay.service
```
