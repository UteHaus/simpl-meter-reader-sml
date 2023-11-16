#!/usr/bin/python3

import argparse
import sys
import threading
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
        timeout=4
    ) as serialDevice:
        serialDevice.close()
        serialDevice.open()
        while True:
            generateMetrics(serialDevice, writer, meterProperties)
            time.sleep(60)


def generateMetrics(serialDevice, writer: WriteData, meterProperties: MeterProperties):
    logging.info("Read data from serial port {}".format(serialProperties.devicePath))
    try:
        raw = serialDevice.read_until(bytes.fromhex("00000000000000"), 1000)
        logging.debug("Serial raw:\n{}".format(raw.hex()))
        convertDataToSmlEntries(raw, writer, meterProperties)
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


def runTest(dataWriter: WriteData, meterProperties: MeterProperties):
    b2 = bytes.fromhex(
        "0000006200620200620062007265000002017101632f35001b1b1b1b1a00c16c1b1b1b1b010101017605000000006200620072650000010176010105000000000b0a0153414720014333e37262016503e666490163cecc007605000000016200620072650000070177010b0a0153414720014333e3070100620affff7262016503e6664979770701006032010101010101045341470177070100600100ff010101010b0a0153414720014333e30177070100010800ff65001c01047262016503e66649621e52ff69000000000303d7c20177070100010801ff017262016503e66649621e52ff6900000000016d636f0177070100010802ff017262016503e66649621e52ff6900000000019674530177070100020800ff017262016503e66649621e52ff69000000000b8bca870177070100020801ff017262016503e66649621e52ff6900000000096d78c70177070100020802ff017262016503e66649621e52ff6900000000021e51c00177070100100700ff0101621b520059000000000000012801010163c9a20076050062007265000002017101632f35001b1b1b1b1a0060f10000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000"
    )
    b3 = bytes.fromhex(
        "78fe00788000781b1b1b010101017605000000006200620200620062007265000002017101632f35001b1b1b1b"
    )
    b4 = bytes.fromhex(
        "1B1B1B1B010101017605F12CAD07620062007263010176010102310B0A01445A47000282225E7262016505E748D7620263955C007605F22CAD07620062007263070177010B0A01445A47000282225E070100620AFFFF7262016505E748D77577070100603201010172620162006200520004445A470177070100600100FF017262016200620052000B0A01445A47000282225E0177070100010800FF641C01047262016200621E52FF65033C93890177070100020800FF017262016200621E52FF650FA49A9E0177070100100700FF017262016200621B52FE538B28010101636B99007605F32CAD076200620072630201710163D90C00001B1B1B1B1A01C3E1"
    )
    b5 = bytes.fromhex("")
    logging.info("\nRun Test!\n")
    convertDataToSmlEntries(b3, dataWriter, meterProperties)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
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
    parser.add_argument("--debug", action="store_true")
    parser.add_argument("-rr", help="repetition rate in 1 minute", default=1)
    testGroup = parser.add_argument_group("test")
    testGroup.add_argument("--test", action="store_true")
    args = parser.parse_args()

    obisValueIndex = findMeterConfiguration(args.meter)
    serialProperties = SerialProperties()
    if args.debug:
        logging.basicConfig(level=logging.DEBUG)

    if args.support:
        print(findSupportedMeter())
    elif args.test:
        writer = WriteData()
        runTest(writer, obisValueIndex)
    elif args.mqtt:
        mqttWrite = MqttDataWriter(args.url, args.port, args.topic, args.qos)
        run(mqttWrite, obisValueIndex, serialProperties)
    else:
        writer = WriteData()
        valueResults = run(writer, obisValueIndex, serialProperties)
