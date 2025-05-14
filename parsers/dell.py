from .base_parser import BaseParser

class DellParser(BaseParser):
    def parse_all(self):
        modelo = "Desconhecido"
        hostname = "Desconhecido"
        interfaces = []
        vlans = []

        atual = {}

        for linha in self.raw.splitlines():
            linha = linha.strip()

            if linha.lower().startswith("hostname "):
                hostname = linha.split("hostname", 1)[1].strip()

            elif linha.startswith("! System Description"):
                modelo = linha.split(":")[-1].strip()

            elif linha.startswith("interface vlan"):
                vlan_id = linha.replace("interface vlan", "").strip()
                nome = ""
                atual_vlan = {"id": vlan_id, "nome": ""}

            elif linha.lower().startswith("description") and 'atual_vlan' in locals():
                atual_vlan["nome"] = linha.split("description", 1)[-1].strip()

            elif linha == "!" and 'atual_vlan' in locals():
                vlans.append(atual_vlan)
                del atual_vlan

            elif linha.startswith("interface"):
                if atual:
                    interfaces.append(atual)
                nome_iface = linha.split("interface", 1)[-1].strip()
                atual = {
                    "nome": nome_iface,
                    "descricao": "",
                    "modo": "",
                    "vlans_tagged": [],
                    "vlans_untagged": [],
                    "pvid": "",
                    "ip": ""
                }

            elif "description" in linha.lower() and atual:
                atual["descricao"] = linha.split("description", 1)[-1].strip()

            elif "switchport access vlan" in linha and atual:
                vlan = linha.split()[-1]
                atual["pvid"] = vlan
                atual["vlans_untagged"].append(vlan)
                atual["modo"] = "access"

            elif "switchport mode" in linha and atual:
                atual["modo"] = linha.split("switchport mode", 1)[-1].strip()

            elif "switchport general allowed vlan add" in linha and atual:
                vlans_tag = linha.split("add", 1)[-1].strip()
                atual["vlans_tagged"].extend(v.strip() for v in vlans_tag.split(","))

            elif "switchport trunk allowed vlan add" in linha and atual:
                vlans_tag = linha.split("add", 1)[-1].strip()
                atual["vlans_tagged"].extend(v.strip() for v in vlans_tag.split(","))

            elif linha == "exit" and atual:
                interfaces.append(atual)
                atual = {}

        if atual:
            interfaces.append(atual)

        return {
            "fabricante": "Dell",
            "modelo": modelo,
            "hostname": hostname,
            "interfaces": interfaces,
            "vlans": vlans,
            "port_channels": []  # suporte futuro
        }
