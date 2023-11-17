#!/usr/bin/python3

from obis_keys import ObisEntryValueIndex
from enum import Enum
from sml_step_reader import SmlConfig
import logging
from typing import Union


class Meters(Enum):
    """
    Meter devices :
    """

    BZPlus3 = "BZPlus3"
    eBZ_DD3_DD3BZ06DTA_SMZ1="eBZ_DD3_DD3BZ06DTA-SMZ1"


class MeterProperties:
    additionObisValuesIndex: dict

    def __init__(self, defaultValueIndex: ObisEntryValueIndex, smlConfig: SmlConfig):
        self.defaultValueIndex = defaultValueIndex
        self.additionObisValuesIndex = dict()
        self.smlConfig = smlConfig

    def addAdditionalObisEntryValueIndex(
        self, obisKey: str, valuesIndex: ObisEntryValueIndex
    ):
        self.additionObisValuesIndex[obisKey] = valuesIndex

    def getObisValueIndexFor(self, obisKey: str = None):
        if obisKey is not None:
            valueIndexForObisKey = self.additionObisValuesIndex.get(obisKey)
            return (
                valueIndexForObisKey
                if valueIndexForObisKey is not None
                else self.defaultValueIndex
            )
        return self.defaultValueIndex


def findMeterConfiguration(meterKey: Union[Meters, str]):
    meter = Meters[meterKey] if isinstance(meterKey, str) else meterKey
    if Meters.BZPlus3.value == meter.value:
        return bZPlus3Configuration()
    
    if Meters.eBZ_DD3_DD3BZ06DTA_SMZ1.value== meter.value:
        return eBZDD3DD3BZ06DTASMZ1()
    
    logging.warning(
        "No supported meter for {}. Add new device on file meter_obis_value_index.py".format(
            meterKey
        )
    )
    return MeterProperties(
        ObisEntryValueIndex(-1, -1, -1, -1, -1, -1, -1, -1), SmlConfig()
    )


def findSupportedMeter():
    return list(Meters)


def eBZDD3DD3BZ06DTASMZ1():
    return MeterProperties( ObisEntryValueIndex(1,unitIndex=3 ,valueIndex=5),SmlConfig() )

def bZPlus3Configuration():
    gridFeedValueIndex = ObisEntryValueIndex(0, -1, -1, 2, 3, 4, -1, manualScaler=0.1)
    obisValueIndexBzPlus = MeterProperties(
        ObisEntryValueIndex(0, -1, -1, 2, 3, 4, -1),
        SmlConfig(startEscapeSequenz="1b1b1b1b"),
    )
    obisValueIndexBzPlus.addAdditionalObisEntryValueIndex(
        "0100020800", gridFeedValueIndex
    )
    obisValueIndexBzPlus.addAdditionalObisEntryValueIndex(
        "0100020801", gridFeedValueIndex
    )
    obisValueIndexBzPlus.addAdditionalObisEntryValueIndex(
        "0100020802", gridFeedValueIndex
    )
    obisValueIndexBzPlus.addAdditionalObisEntryValueIndex(
        "0100100700", ObisEntryValueIndex(0, -1, -1, 3, 4, 5, -1)
    )
    return obisValueIndexBzPlus
