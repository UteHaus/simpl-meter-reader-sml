#!/usr/bin/python3

import argparse
import sys
import time
import logging
from typing import List
from write_data import WriteData, MqttDataWriter
from sml_block_maper import mapSmlBlocksObisEntry
from obis_keys import ObisEntryValueIndex
from sml_step_reader import encodeSml
from meter_obis_value_index import (
    findSupportedMeter,
    findMeterConfiguration,
    MeterProperties,
)
from testing.init_test import parsSmlFileData
import threading

try:
    import serial
except ImportError:
    logging.error("serial package not found")

logger = logging.getLogger('general_logger')

class SerialProperties:
    def __init__(
        self,
        devicePath="/dev/ttyAMA0",
        serialPort=9600,
        xonxoff=0,
        rtscts=0,
        bytesize=8,
        parity="N",
        stopbits=1,
    ):
        super().__init__()
        self.devicePath = devicePath
        self.serialPort = serialPort
        self.xonxoff = xonxoff
        self.rtscts = rtscts
        self.bytesize = bytesize
        self.parity = parity
        self.stopbits = stopbits


def run(
    writer: WriteData,
    meterProperties: MeterProperties,
    serialProps: SerialProperties,
):
    logger.info("Starting read data")
    while True:
        with newInstanceOfSerial(serialProps)  as serialDevice:
            try:
                serialDevice.close() #when the port is already open, close the port 
                generateMetrics(serialDevice, writer, meterProperties)
            except serial.SerialException as e:
                logger.error(e)
            except Exception as e:
                logger.error(e)
            except KeyboardInterrupt:
                serialDevice.close()
                sys.stdout.write("\program closed!\n")
                exit()
            finally:
                serialDevice.close()
        time.sleep(60)

        

def newInstanceOfSerial(serialProps: SerialProperties):
    return serial.Serial(
        serialProps.devicePath,
        serialProps.serialPort,
        xonxoff=serialProps.xonxoff,
        rtscts=serialProps.rtscts,
        bytesize=serialProps.bytesize,
        parity=serialProps.parity,
        stopbits=serialProps.stopbits,
    ) 


def generateMetrics(serialDevice, writer: WriteData, meterProperties: MeterProperties):
    logger.info("Read data from serial port {}".format(serialProperties.devicePath))
    smlMsg = bytearray()
    startSequenc = bytes.fromhex(meterProperties.smlConfig.msgBlockStartBlock)
    endSequenc = bytes.fromhex(meterProperties.smlConfig.endEscapeSequenz)
    startIndex=0
    # open and close the serial connection to prevent serial connection breaks and consistently data sets.
    serialDevice.open()
    
    # find start sequenc
    while True:
        smlMsg.extend(serialDevice.read())
        startIndex = smlMsg.find(startSequenc)
    
        if startIndex >= 0:
            break
        
    # buffer bytes and map bytes to SML data set
    smlMsg = bytearray(smlMsg[startIndex:])
    while True:
        smlMsg.extend(serialDevice.read())
        if smlMsg.find(endSequenc) >= 0:
            smlMsg.extend(serialDevice.read(3))
            logger.debug("Serial raw:\n{}".format(smlMsg.hex()))
            threading.Thread(
                target=convertDataToSmlEntries(
                    smlMsg, writer, meterProperties
                )
            )
            smlMsg.clear()
            break
        
    time.sleep(20)    
    serialDevice.close()
            

def convertDataToSmlEntries(
    data: bytes, writer: WriteData, meterProperties: MeterProperties
):
    smlBlocks = encodeSml(data, meterProperties.smlConfig)
    smlEntries = mapSmlBlocksObisEntry(smlBlocks, meterProperties)
    writer.writeData(smlEntries)


def initialArgumentParser():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--log",
        "-l",
        default="ERROR",
        help="Set log level. Level: CRITICAL, FATAL, ERROR, WARNING, WARNING, INFO, DEBUG, NOTSET ",
    )
    parser.add_argument(
        "--device",
        help="The name of the device which is monitored",
        default="/dev/ttyAMA0",
    )
    parser.add_argument("--meter", help="The supported meter device. You can use the ")
    parser.add_argument(
        "--support", help="List of supported meters", action="store_true"
    )
    mqttParser = parser.add_argument_group("mqtt")
    mqttParser.add_argument(
        "--port", help="The port where to expose the exporter", default=1883
    )
    mqttParser.add_argument(
        "--topic", help="The mqtt topic prefix", default="meter/test"
    )
    mqttParser.add_argument("--qos", help="The mqtt qos", default=0)
    mqttParser.add_argument("--url", help="The url", default="http://localhost")
    mqttParser.add_argument(
        "--mqtt",
        action="store_true",
    )

    parser.add_argument("-rr", help="repetition rate in 1 minute", default=1)
    testGroup = parser.add_argument_group("test", description="Run test for sml data.")
    testGroup.add_argument("--test", "-t", action="store_true")
    testGroup.add_argument("--file", "-f", help="File path to the hex data file.")

    return parser


if __name__ == "__main__":
    parser = initialArgumentParser()
    args = parser.parse_args()

    meterConfiguration = findMeterConfiguration(args.meter)
    logger.setLevel(args.log)
    serialProperties = SerialProperties(devicePath=args.device)

    if args.support:
        print(findSupportedMeter())
    elif args.test:
        logger.info("Run test")
        parsSmlFileData(args.file, meterConfiguration)
    elif args.mqtt:
        mqttWrite = MqttDataWriter(args.url, args.port, args.topic, args.qos)
        run(mqttWrite, meterConfiguration, serialProperties)
    else:
        writer = WriteData()
        valueResults = run(writer, meterConfiguration, serialProperties)
