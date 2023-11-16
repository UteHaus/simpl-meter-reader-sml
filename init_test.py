from meter_obis_value_index import Meters
from sml_block_maper import mapSmlBlocksObisEntry
from obis_keys import ObisEntryValueIndex
from sml_step_reader import encodeSml
from meter_obis_value_index import findMeterConfiguration, MeterProperties
from write_data import WriteData
from typing import Union


def parsSmlFileData(filePath: str, meterProperties: MeterProperties):
    writer = WriteData()
    dataAsHex = open(filePath, "r").read()
    dataAsBytes = bytes.fromhex(dataAsHex)

    # pars hex data to slm entries
    smlBlocks = encodeSml(dataAsBytes, meterProperties.smlConfig)
    smlEntries = mapSmlBlocksObisEntry(smlBlocks, meterProperties)
    writer.writeData(smlEntries)
