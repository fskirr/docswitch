from parsers.cisco import CiscoParser
from parsers.aruba import ArubaParser
from parsers.hpe import HpeParser
from parsers.dell import DellParser
from parsers.dell_x1050 import DellX1050Parser
from parsers.dell_n1148p import DellN1148PParser
from parsers.fortigate import FortigateParser
from parsers.mikrotik import MikrotikParser

def get_parser(fabricante, config_texto):
    fabricante = fabricante.lower()

    if fabricante == "cisco":
        return CiscoParser(config_texto)
    elif fabricante == "aruba":
        return ArubaParser(config_texto)
    elif fabricante == "hpe":
        return HpeParser(config_texto)
    elif fabricante == "dell":
        return DellParser(config_texto)
    elif fabricante == "dell x1050":
        return DellX1050Parser(config_texto)
    elif fabricante == "dell n1148p":
        return DellN1148PParser(config_texto)
    elif fabricante == "fortigate":
        return FortigateParser(config_texto)
    elif fabricante == "mikrotik":
        return MikrotikParser(config_texto)
    else:
        raise ValueError(f"Fabricante '{fabricante}' não suportado.")
