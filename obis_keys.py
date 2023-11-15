#!/usr/bin/python3

# https://www.promotic.eu/en/pmdoc/Subsystems/Comm/PmDrivers/IEC62056_OBIS.htm

OBIS_NAMES = {
    "0100000009": "Geräteeinzelidentifikation",
    "0100010800": "Zählerstand Total",
    "0100010801": "Zählerstand Tarif 1",
    "0100010802": "Zählerstand Tarif 2",
    "0100011100": "Total-Zählerstand",
    "0100020800": "Wirkenergie Total",
    "0100020801": "Wirkenergie Tarif 1",
    "0100020802": "Wirkenergie Tarif 2",
    "0100100700": "aktuelle Wirkleistung",
    "0100170700": "Momentanblindleistung L1",
    "01001f0700": "Strom L1",
    "0100200700": "Spannung L1",
    "0100240700": "Wirkleistung L1",
    "01002b0700": "Momentanblindleistung L2",
    "0100330700": "Strom L2",
    "0100340700": "Spannung L2",
    "0100380700": "Wirkleistung L2",
    "01003f0700": "Momentanblindleistung L3",
    "0100470700": "Strom L3",
    "0100480700": "Spannung L3",
    "01004c0700": "Wirkleistung L3",
    "0100510701": "Phasenabweichung Spannungen L1/L2",
    "0100510702": "Phasenabweichung Spannungen L1/L3",
    "0100510704": "Phasenabweichung Strom/Spannung L1",
    "010051070f": "Phasenabweichung Strom/Spannung L2",
    "010051071a": "Phasenabweichung Strom/Spannung L3",
    "010060320002": "Aktuelle Chiptemperatur",
    "010060320003": "Minimale Chiptemperatur",
    "010060320004": "Maximale Chiptemperatur",
    "010060320005": "Gemittelte Chiptemperatur",
    "010060320303": "Spannungsminimum",
    "010060320304": "Spannungsmaximum",
    "01000e0700": "Netz Frequenz",
    "8181c78203": "Hersteller-Identifikation",
    "8181c78205": "Öentlicher Schlüssel",
}


class ObisEntryValueIndex:
    def __init__(
        self,
        obisIndex: int,
        statusIndex: int,
        timeIndex: int,
        unitIndex: int,
        scalerIndex: int,
        valueIndex: int,
        valueSignature: int,
        obisKey: str = None,
    ):
        self.obisIndex = obisIndex
        self.statusIndex = statusIndex
        self.timeIndex = timeIndex
        self.unitIndex = unitIndex
        self.scalerIndex = scalerIndex
        self.valueIndex = valueIndex
        self.valueSignature = valueSignature
