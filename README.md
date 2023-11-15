# simple meter read (SML)

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

