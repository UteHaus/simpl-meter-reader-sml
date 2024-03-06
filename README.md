# simple meter read (SML)  

This tool help you to read SML based meters.

## features

- [x] config SML search properties
- [x] config OBIS value index
- [x] run reader as service (linux)
- [ ] CRC16 check
- [x] Test 

## run 
Find your serial port like `S0` or `ttyAMA0` and use it instead fo my example port `ttyAMA0`.


### packages

This tool use for serial reading the [pyserial](https://pyserial.readthedocs.io/en/latest/index.html) package.
```
python -m pip install pyserial
```
For mqtt 
```
pip install paho-mqtt
```
### execution samples

example with console output
```sh
python read_meter_values.py --device /dev/ttyAMA0 --meter BZPlus3
```
example with mqtt 
```sh
python read_meter_values.py --device /dev/ttyAMA0 --mqtt --url 172.0.0.1 --topic meter/grid/meter1/ --meter BZPlus3
```
Your service name has a differ port name as my `ttyAMA0`.

## setup grid meter
### Sagemcom Smarty BZ-Plu
Unter den Einstellungen muss das dSS-Protokollstandard auf `dSS-r` gesetzt werden. Dazu muss SML Einstellung auf dSS-r eingestellt werden.

## system

To read the serial data without system breaks, it is better to stop the service `serial-getty@[your serial port].service`:
```sh
systemctl stop serial-getty@ttyAMA0.service
```


### service
Copy the service to the `system`. (Optional) change the device name.
```sh
sudo cp grid-meter1.servic nano /etc/systemd/system/
```
Start the service.
```sh
systemctl start grid-meter1.service
```

## test
Run a test with hex data file
```sh
read_meter_values.py --test --meter BZPlus3 --file sml_files/bz-pus-10.hex -l DEBUG 
```


## existing meter configurations
- Sagemcom Smarty BZ-Plu
- eBZ DD3 DD3BZ06DTA SMZ1
