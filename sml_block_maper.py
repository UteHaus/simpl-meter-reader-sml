from sml_step_reader import SmlBlock
from sml_units import SmlUnits
from obis_keys import OBIS_NAMES
from meter_obis_value_index import MeterProperties
import logging


class SmlEntry:
    def sensorValue(self, baseValue: int, scaler: float):
        if baseValue != "string" and baseValue is not None:
            return float(baseValue) if scaler <= 0 else float(baseValue) * float(scaler)
        else:
            return baseValue

    def __init__(
        self,
        obis: str,
        status: str,
        valTime: int,
        unit: int,
        scaler: float,
        baseValue,
        valueSignature,
    ):
        self.obis = obis
        self.obisName = OBIS_NAMES.get(self.obis)
        self.status = status
        self.time = valTime
        self.unit = "" if unit is None else (SmlUnits[unit] if 0 < unit < 73 else "")
        self.scaler = scaler if isinstance(scaler, (int, float)) else -1
        self.value = self.sensorValue(baseValue, self.scaler)
        self.signature = valueSignature

    def __str__(self):
        str = "{} ({})  ".format(self.obis, self.obisName)
        str += "{}".format(self.value)

        return str


def findValueForObisIndex(smlBlock: SmlBlock, obisValueIndex: int):
    if (obisValueIndex) >= 0:
        if len(smlBlock.values) >= obisValueIndex:
            return smlBlock.values[obisValueIndex]
        else:
            logging.warning(
                "No value found on index {}. The sml block: {}".format(
                    obisValueIndex, smlBlock.reprJSON()
                )
            )
    return None


def convertSmlBlockToObisEntry(
    smlBlock: SmlBlock, obisKey: str, meterProperties: MeterProperties
):
    obisValueIndex = meterProperties.getObisValueIndexFor(obisKey)
    return SmlEntry(
        obis=obisKey,
        status=findValueForObisIndex(smlBlock, obisValueIndex.statusIndex),
        baseValue=findValueForObisIndex(smlBlock, obisValueIndex.valueIndex),
        scaler=findValueForObisIndex(smlBlock, obisValueIndex.scalerIndex),
        unit=findValueForObisIndex(smlBlock, obisValueIndex.unitIndex),
        valTime=findValueForObisIndex(smlBlock, obisValueIndex.statusIndex),
        valueSignature=findValueForObisIndex(smlBlock, obisValueIndex.valueSignature),
    )


def findSmlBlockObisEntry(smlBlock: SmlBlock):
    for smlBlockValue in smlBlock.values:
        obisName = OBIS_NAMES.get(smlBlockValue)
        if obisName is not None:
            return smlBlockValue

    return None


def mapSmlBlocksObisEntry(smlBlocks: list[SmlBlock], meterProperties: MeterProperties):
    obisEntries = []
    for smlBlock in smlBlocks:
        entries = mapSmlBlockObisEntry(smlBlock, meterProperties)
        obisEntries.extend(entries)
    return obisEntries


def mapSmlBlockObisEntry(smlBlock: SmlBlock, meterProperties: MeterProperties):
    obisEntries = []
    obisKey = findSmlBlockObisEntry(smlBlock)
    if obisKey is not None:
        newObisEntry = convertSmlBlockToObisEntry(smlBlock, obisKey, meterProperties)
        obisEntries.append(newObisEntry)

    if len(smlBlock.childList) > 0:
        for childBlock in smlBlock.childList:
            childObisEntries = mapSmlBlockObisEntry(childBlock, meterProperties)
            obisEntries.extend(childObisEntries)
    return obisEntries
