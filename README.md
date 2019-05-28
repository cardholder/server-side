# Django Backend 
[![Build Status](https://travis-ci.org/cardholder/server-side.svg?branch=master)](https://travis-ci.org/cardholder/server-side) 


## Daphne

Auf dem Server ist ein Daphne Service. Dieser Service kann mit 
```bash
$ sudo systemctl stop/restart/start daphne
```
gestoppt, neugestartet oder gestartet werden.

## Redis
Auf dem Server läuft eine Docker instanz von einem Redis Server. Dieser muss gestartet werden damit Django den Channel Layer besitzt. 
Der Redis Server wird mit folgendem Befehl gestartet.
```bash
$ sudo docker run -p 6379:6379 -d redis:2.8
```
