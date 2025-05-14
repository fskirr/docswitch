from .base_parser import BaseParser

class FortigateParser(BaseParser):
    def parse_all(self):
        hostname = "Desconhecido"
        interfaces = []
        vlans = []
        rotas = []

        atual = {}
        em_interface = False
        em_rota = False

        for linha in self.raw.splitlines():
            linha = linha.strip()

            if linha.startswith("set hostname"):
                hostname = linha.split("set hostname")[-1].strip()

            elif linha.startswith("edit") and "config system interface" in self.raw:
                em_interface = True
                if atual:
                    interfaces.append(atual)
                atual = {
                    "nome": linha.split("edit")[-1].strip('" '),
                    "descricao": "",
                    "modo": "",
                    "vlans_tagged": [],
                    "vlans_untagged": [],
                    "pvid": "",
                    "ip": ""
                }

            elif em_interface and linha.startswith("set alias") and atual:
                atual["descricao"] = linha.split("set alias")[-1].strip('" ')

            elif em_interface and linha.startswith("set ip") and atual:
                partes = linha.split()
                if len(partes) >= 3:
                    atual["ip"] = partes[2].strip()

            elif em_interface and linha.startswith("set vlanid") and atual:
                vlanid = linha.split()[-1]
                atual["pvid"] = vlanid
                atual["modo"] = "vlan"

            elif linha == "next" and em_interface and atual:
                interfaces.append(atual)
                atual = {}
                em_interface = False

            elif linha.startswith("config router static"):
                em_rota = True
                rota = {"destino": "", "gateway": ""}
            
            elif em_rota and linha.startswith("edit"):
                continue

            elif em_rota and linha.startswith("set dst"):
                rota["destino"] = linha.split("set dst")[-1].strip()

            elif em_rota and linha.startswith("set gateway"):
                rota["gateway"] = linha.split("set gateway")[-1].strip()

            elif em_rota and linha == "next":
                rotas.append(rota)
                rota = {}

            elif linha == "end":
                em_interface = False
                em_rota = False

        return {
            "fabricante": "Fortigate",
            "modelo": "Desconhecido",
            "hostname": hostname,
            "interfaces": interfaces,
            "vlans": vlans,
            "port_channels": [],
            "rotas": rotas
        }
