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
from init_test import parsSmlFileData
import threading

try:
    # unhexlify for micropython
    import serial
except ImportError:
    logging.error("serial package not found")


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
    logging.info("Starting read data")
    with serial.Serial(
        serialProps.devicePath,
        serialProps.serialPort,
        xonxoff=serialProps.xonxoff,
        rtscts=serialProps.rtscts,
        bytesize=serialProps.bytesize,
        parity=serialProps.parity,
        stopbits=serialProps.stopbits,
    ) as serialDevice:
        while True:
            serialDevice.close()
            serialDevice.open()
            generateMetrics(serialDevice, writer, meterProperties)
            time.sleep(60)


def generateMetrics(serialDevice, writer: WriteData, meterProperties: MeterProperties):
    logging.info("Read data from serial port {}".format(serialProperties.devicePath))
    smlMsg = bytearray()
    startSequenc = bytes.fromhex(meterProperties.smlConfig.msgBlockStartBlock)
    endSequenc = bytes.fromhex(meterProperties.smlConfig.endEscapeSequenz)
    try:
        while True:
            smlMsg.extend(serialDevice.read())
            startIndex = smlMsg.find(startSequenc)
            if startIndex >= 0:
                smlMsg = bytearray(smlMsg[startIndex:])
                while True:
                    smlMsg.extend(serialDevice.read())
                    if smlMsg.find(endSequenc) >= 0:
                        smlMsg.extend(serialDevice.read(3))
                        logging.debug("Serial raw:\n{}".format(smlMsg.hex()))
                        threading.Thread(
                            target=convertDataToSmlEntries(
                                smlMsg, writer, meterProperties
                            )
                        )
                        smlMsg.clear()
                        time.sleep(10)
                        break
    except Exception as e:
        logging.error(e)
        serialDevice.close()
        time.sleep(60)
        serialDevice.open()
    except KeyboardInterrupt:
        serialDevice.close()
        sys.stdout.write("\program closed!\n")
        exit()


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
    logging.basicConfig(level=args.log)
    serialProperties = SerialProperties()

    if args.support:
        print(findSupportedMeter())
    elif args.test:
        logging.info("Run test")
        parsSmlFileData(args.file, meterConfiguration)
    elif args.mqtt:
        mqttWrite = MqttDataWriter(args.url, args.port, args.topic, args.qos)
        run(mqttWrite, meterConfiguration, serialProperties)
    else:
        writer = WriteData()
        valueResults = run(writer, meterConfiguration, serialProperties)
