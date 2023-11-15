#!/usr/bin/python3

from obis_keys import ObisEntryValueIndex
from enum import Enum
from sml_step_reader import SmlConfig
import logging


class Meters(Enum):
    """
    Meter devices :
    """

    BZPlus3 = "BZPlus3"


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


def findMeterConfiguration(meterKey: str):
    if Meters.BZPlus3.value == meterKey:
        obisValueIndexBzPlus = MeterProperties(
            ObisEntryValueIndex(0, -1, -1, 2, 3, 4, -1),
            SmlConfig(startEscapeSequenz="001b1b1b"),
        )
        obisValueIndexBzPlus.addAdditionalObisEntryValueIndex(
            "0100100700", ObisEntryValueIndex(0, -1, -1, 3, 4, 5, -1)
        )
        return obisValueIndexBzPlus

    logging.warning(
        "No supported meter for {}. And a new one on file meter_obis_value_index.py".format(
            meterKey
        )
    )
    return MeterProperties(
        ObisEntryValueIndex(-1, -1, -1, -1, -1, -1, -1, -1), SmlConfig()
    )


def findSupportedMeter():
    return list(Meters)
