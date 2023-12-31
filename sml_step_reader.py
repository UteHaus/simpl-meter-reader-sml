#!/usr/bin/python3
import logging
import json
import struct

try:
    # hexlify for micropython
    from ubinascii import hexlify
except ImportError:
    # default to python standard
    from binascii import hexlify

logger = logging.getLogger('general_logger')


class SmlConfig:
    def __init__(
        self,
        startEscapeSequenz: str = "1b1b1b1b",
        endEscapeSequenz: str = "1b1b1b1b1a",
        smlVersion: str = "01010101",
    ):
        super().__init__()
        self.startEscapeSequenz = startEscapeSequenz
        self.endEscapeSequenz = endEscapeSequenz
        self.smlVersion = smlVersion
        self.msgBlockStartBlock = startEscapeSequenz + smlVersion


class SmlBlock:
    def __init__(self):
        super().__init__()
        self.childList = []
        self.values = []
        self.checkSum = None

    def reprJSON(self):
        valuesJson = "[]"
        childListJson = "[]"

        if len(self.values) > 0:
            valuesJson = json.dumps(self.values)

        if len(self.childList) > 0:
            childListAsStringArray = []
            for item in self.childList:
                childListAsStringArray.append(item.reprJSON())
            childListJson = ",".join(childListAsStringArray)

        return (
            '{"checkSum":'
            + json.dumps(self.checkSum)
            + ',"values":'
            + valuesJson
            + ', "childList":['
            + childListJson
            + "]}"
        )


def parsBytesToNumber(data: bytes, sequencHex: str):
    if sequencHex.startswith("5"):
        if len(data) == 1:
            return struct.unpack(">b", data)[0]
        elif len(data) == 2:
            return struct.unpack(">h", data)[0]
        elif len(data) == 4:
            return struct.unpack(">i", data)[0]
        elif len(data) == 8:
            return struct.unpack(">q", data)[0]
    else:
        if len(data) == 1:
            return struct.unpack(">B", data)[0]
        elif len(data) == 2:
            return struct.unpack(">H", data)[0]
        elif len(data) == 4:
            return struct.unpack(">I", data)[0]
        elif len(data) == 8:
            return struct.unpack(">Q", data)[0]
    return 0


def parsValueToString(value: bytes):
    try:
        return hexlify(value).decode("ascii")
    except Exception as e:
        logger.exception(e)
        return value.hex()


def parsSmlBlock(data: bytes, smlBlock: SmlBlock, sequenzCount=-1):
    while len(data) > 0 and sequenzCount != 0:
        sequenzCount = sequenzCount - 1
        sequencHex: str = data[0:1].hex()
        if sequencHex == "00":
            data = data[1:]
        elif sequencHex.startswith("0") and sequencHex != "00":
            dataLenght = int.from_bytes(bytes.fromhex(sequencHex), "big") - 1
            if dataLenght > 0:
                dataValue = data[1:dataLenght]
                smlBlock.values.append(parsValueToString(dataValue))
            else:
                smlBlock.values.append(None)
            data = data[(dataLenght + 1) :]
        elif sequencHex.startswith("5") or sequencHex.startswith("6"):
            valueLength= int.from_bytes(bytes.fromhex( ("0"+sequencHex[1])))
            dataValue = parsBytesToNumber(data[1:valueLength], sequencHex)
            data = data[valueLength:]
            smlBlock.values.append(dataValue)
        elif sequencHex == "42":
            value = bool.from_bytes(data[1, 2])
            smlBlock.values.append(value)
            data = data[2:]
        elif sequencHex.strip()[0:1] == "7":
            listLenght = int(sequencHex.strip()[1:])
            data = data[1:]
            newBlock = SmlBlock()
            restData, newBlock = parsSmlBlock(data, newBlock, listLenght)
            data = restData
            smlBlock.childList.append(newBlock)
        else:
            data = data[1:]
    return data, smlBlock


def findMessageWithEscapeSequenc(data: bytes, smlConfig: SmlConfig):
    msgBlocks = []
    startMsgBlockIndex = 0
    endEscapeSequenzBytes = bytes.fromhex(smlConfig.endEscapeSequenz)
    msgBlockStartBlockBytes = bytes.fromhex(smlConfig.msgBlockStartBlock)
    while data.find(msgBlockStartBlockBytes) >= 0:
        startMsgBlockIndex = data.find(msgBlockStartBlockBytes, startMsgBlockIndex)
        logger.debug("Message block start index: {}".format(startMsgBlockIndex))
        if startMsgBlockIndex >= 0:
            firstBlockValueIndex = startMsgBlockIndex + len(msgBlockStartBlockBytes)
            endEscapeSequenzIndex = data.find(
                endEscapeSequenzBytes, firstBlockValueIndex
            )
            logger.debug("Message block end index: {}".format(endEscapeSequenzIndex))
            if endEscapeSequenzIndex - firstBlockValueIndex > 0:
                newMsgBlock = data[firstBlockValueIndex:endEscapeSequenzIndex]
                logger.debug("Message block found: {}".format(newMsgBlock.hex()))
                startMsgBlockIndex = 0
                data = data[(endEscapeSequenzIndex + len(endEscapeSequenzBytes) + 4) :]
                # todo check msg block check sum last 1a xx YY ZZ
                msgBlocks.append(newMsgBlock)
            else:
                return msgBlocks
        elif startMsgBlockIndex < 0:
            return msgBlocks
        else:
            data = data[(len(msgBlockStartBlockBytes) + startMsgBlockIndex) :]
    return msgBlocks


def trimSmlBlock(smlBlock: SmlBlock):
    if len(smlBlock.values) == 0 and len(smlBlock.childList) == 1:
        return smlBlock.childList[0]
    return smlBlock


def encodeSml(data: bytes, smlConfig: SmlConfig):
    logger.debug("encode sml data (bytes)")
    msgBlocks = findMessageWithEscapeSequenc(data, smlConfig)
    if len(msgBlocks) == 0:
        logger.warning("Non message block found in the data.")

    smlBlock = SmlBlock()
    findSmlBlock = []
    for msgBlock in msgBlocks:
        try:
            data, changedBlock = parsSmlBlock(msgBlock, smlBlock)
            newSmlBlock = trimSmlBlock(changedBlock)
            findSmlBlock.append(newSmlBlock)
            logger.debug("Find sml block: \n{}".format(newSmlBlock.reprJSON()))
        except Exception as e:
            logging.error(e)

    return findSmlBlock
