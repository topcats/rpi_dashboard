# eClockDataGetterTC - Re Authentication

## 1) Rename `o365_token-php.json`

- backup the token file
- remove the existing file

## 2) Run `GetAuthenticationURL()`

``` bash
pi@rpi-2hp:~/dashdisplay $ php -f alternate/eClockDataGetterTC.php
```

## 3) Authenticate Via Browser

``` bash
Authentication URL:

https://##############################

No Authentication!
```

1. Open Web browser
2. Open Developer Tools
3. Paste URL
4. *Authenticate if needed*
5. Save Querystring Response

## 4) Clear down `o365_token-php.json`

- Remove `"token"`
- Replace `"auth"`

``` json
    "auth": {
        "code": "",
        "state": "12345",
        "session_state": ""
    }
```

## 5) Run `DoAuthenticationToken()`

``` bash
pi@rpi-2hp:~/dashdisplay $ php -f alternate/eClockDataGetterTC.php
```
