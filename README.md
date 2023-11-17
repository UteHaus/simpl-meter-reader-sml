# simple meter read (SML)  ----- CURRENTLY IN PROGRESS ------


This tool help you to read SML based meters.


## features

- [x] config SML search properties
- [x] config OBIS value index
- [x] run reader as service (linux)
- [ ] CRC16 check
- [x] Test 

## run 

example with console output
```sh
python read_meter_values.py --device /dev/ttyAMA0 --meter BZPlus3
```
example with mqtt 
```sh
python read_meter_values.py --device /dev/ttyAMA0 --mqtt --url 172.0.0.1 --topic meter/grid/meter1/ --meter BZPlus3
```


## setup
### service

```sh
sudo nano /etc/systemd/system/grid-meter1.servic
```
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
