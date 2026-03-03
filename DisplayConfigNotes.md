# eClock Dashboard Display - Config Notes

`display.json` is used for all configuration details.

## Screen Schedule

Can have as many Schedules as needed.  
The system will start at the top and pick the first schedule that fits.  
Therefore it is possible to have overlapping schedules to prevent multiples.  

- **Day:** uses php Day of weeks, (Sunday=0, Monday=1, ..., Saturday=6)
- **Start & Stop:** 24 hour clock, no seconds
- **Brightness:**
  - `1 - 255`, sets the brightness and the screen on
  - `0` will turn off the screen.
- **Style:** On screen display style
  - `0` (Default) : Plain, clock and date only; suitable for low light
  - `1` : Clock, date, weather; suitable for low light
  - `2` : Full system, lcars

```json
"schedule": {
    "list":[
        {
            "day": [
                1,
                2,
                3,
                4,
                5
            ],
            "start": "09:00",
            "stop": "20:00",
            "brightness": 250,
            "style":2
        }
    ]
}
```

### Schedule Override

It is possible to override the schedule, indefinately or for a time length.

If override is set and the `end` value is not nothing, the override will activate.  
If `end` is `- 1`, override will run indefinately.  
Else the override will run until the end date and time.

- **Brightness:**
  - `1 - 255`, sets the brightness and the screen on
  - `0` will turn off the screen.
- **Style:** On screen display style
  - `0` (Default) : Plain, clock and date only; suitable for low light
  - `1` : Clock, date, weather; suitable for low light
  - `2` : Full system, lcars
- **end** Set the override finish date/time
  - `null` : turns off override
  - `- 1` : override on indefinately
  - `1771095809`: datetime.timestamp stop point
- **endtext** a useful text representation of the end value

```json
"schedule": {
    "override": {
        "brightness": 250,
        "style": 1,
        "end": null,
        "endtext": "off"
    }
}
```

## ZWave

Configuration details for ZWave control, can be disabled.

```json
"zwave": {
    "enabled": true,
    "url": "http://localhost:8083/ZAutomation/api/v1/",
    "username": "admin",
    "password": ""
}
```

> **NB:** The Password is encoded to the machine.

## Weather

Select which town (ID) is wanted

```json
{
    "weather": 2650311
}
```
