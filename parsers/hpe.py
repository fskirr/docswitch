from .base_parser import BaseParser

class HpeParser(BaseParser):
    def parse_all(self):
        modelo = "Desconhecido"
        hostname = "Desconhecido"
        interfaces = []
        vlans = []
        port_vlan_map = {}

        for linha in self.raw.splitlines():
            linha = linha.strip()

            if linha.startswith("; J"):
                modelo = linha.replace(";", "").strip()

            elif linha.lower().startswith("hostname"):
                hostname = linha.split()[-1].strip()

            elif linha.lower().startswith("interface"):
                atual = {
                    "nome": linha.split()[-1],
                    "descricao": "",
                    "modo": "",
                    "vlans_tagged": [],
                    "vlans_untagged": [],
                    "pvid": "",
                    "ip": ""
                }

            elif linha.lower().startswith("name") and "vlan" not in linha.lower():
                atual["descricao"] = linha.split("name", 1)[-1].strip()

            elif "untagged vlan" in linha.lower():
                atual["modo"] = "access"
                atual["pvid"] = linha.split()[-1]
                atual["vlans_untagged"].append(linha.split()[-1])

            elif "tagged vlan" in linha.lower():
                atual["modo"] = "trunk"
                vlans_tag = linha.split("tagged vlan")[-1].strip()
                atual["vlans_tagged"] = [v.strip() for v in vlans_tag.split(",")]

            elif linha == "exit" and 'atual' in locals():
                interfaces.append(atual)
                del atual

            elif linha.lower().startswith("vlan ") and "name" in linha.lower():
                partes = linha.split("name")
                vlan_id = partes[0].replace("vlan", "").strip()
                nome = partes[1].strip()
                vlans.append({"id": vlan_id, "nome": nome})

        return {
            "fabricante": "HPE",
            "modelo": modelo,
            "hostname": hostname,
            "interfaces": interfaces,
            "vlans": vlans,
            "port_channels": []
        }
