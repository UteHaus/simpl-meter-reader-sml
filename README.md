# simple meter read (SML)  ----- CURRENTLY IN PROGRESS ------


This tool help you to read SML based meters.


## features

[x] config SML search properties
[x] config OBIS value index
[x] run reader as service (linux)
[ ] CRC16 check
[ ] Test 


## run 

example howe to run
```sh
python read_meter_values.py --device /dev/ttyAMA0 --mqtt --url patu --topic meter/grid/meter1/
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
