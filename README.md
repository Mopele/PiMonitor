# PiMonitor
A Flask-Webside with Bokeh Plots to display the RaspberryPi's Perfromance! Written in python3

## How to install it
You should use it in a virtual enviroment. For that use `python3 venv venv` in the cloned directory. Then you have to install all the modules. For that you have to activate the virtualenviroment with `source venv/bin/activate`. This lets you use your own independent python3 runtime. Now you have to install all the modules with pip as followed:

```
pip3 install Flask==1.1.2
pip3 install regex==2020.6.7
pip3 install termcolor==1.1.0

pip3 install bokeh==1.4.0
pip3 install pandas
pip3 install psutil
```

## Confiugure ports
To configure on what port the PiMonitor webside will be reachable change the line 187 and there you can edit the port. The standart Port is 8080 and the IP is the localhost of the pi.

## Setup to start at bootup
Now we add the PiMonitor to the services to always start it when the Pi is booted. To do that we create a new Service with `sudo nano /lib/systemd/system/pimonitor.service`. In this file we write:
```
[Unit]
Description=Service to monitor the performance of Pi and look at logs. For more see: "https://github.com/Mopele/PiMonitor"
After=multi-user.target

[Service]
Type=simple
ExecStart=/home/pi/Documents/PiMonitor/venv/bin/python /home/pi/Documents/PiMonitor/Development/serv.py

[Install]
WantedBy=multi-user.target
```

When you want to display a specific log on the PiMonitor Server change the logpath in serv.py at line 40.

Finally we only need to give the file the necessary permissions and start the service:
```
sudo chmod 644 /lib/systemd/system/pimonitor.service
chmod +x /home/pi/Documents/PiMonitor/Development/serv.py

sudo systemctl daemon-reload
sudo systemctl enable pimonitor.service
sudo systemctl start pimonitor.service
```

To see what the service is doing and to start/stop it use:
```
sudo systemctl status pimonitor.service
sudo systemctl stop pimonitor.service

sudo journalctl -f -u pimonitor.service
```

## Frequent errors:
On the raspberry you can encounter an error qith numpy. The error is because of a failed extension of c and can be resoved with `sudo apt-get install libatlas-base-dev` installing the extension.
