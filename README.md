# rpi_dashboard
**Raspberry PI Dashboard**

A Dashboard for raspberry pi Module 3 with the Raspberry 7" Touch Screen

## Features
* Time
* Date
* Reads Number of local Media Files on MiniDLNA (Music/Video)
* Gets local Weather from OpenWeather
* Checks to see if Owner is home (Pings mobile phone)

## Data Storage
* Saves data to JSON files so does not flood online services, called `data_*.txt`
* Saves images to `icon_*.png`
* Saves a backup of current data/images which are used incase of data update failure
* Config file eClock.cfg, this is created using setup.py

## setup
* Register with [OpenWeatherMap](http://www.openweathermap.org/)
* run `setup.py` to create config file
* read [Backlight Setup manual](BacklightControlNotes.md)
* read [Auto run manual](AutorunNotes.md)
