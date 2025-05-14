from .base_parser import BaseParser

class ArubaParser(BaseParser):
    def parse_all(self):
        modelo = "Desconhecido"
        hostname = "Desconhecido"
        interfaces = []
        vlans = []
        atual = {}

        for linha in self.raw.splitlines():
            linha = linha.strip()

            if linha.startswith("; J"):
                modelo = linha.replace(";", "").strip()

            elif linha.lower().startswith("hostname"):
                hostname = linha.split("hostname", 1)[1].strip().strip('"')

            elif linha.lower().startswith("interface"):
                if atual:
                    interfaces.append(atual)
                nome = linha.split()[-1]
                atual = {
                    "nome": nome,
                    "descricao": "",
                    "modo": "",
                    "vlans_tagged": [],
                    "vlans_untagged": [],
                    "pvid": "",
                    "ip": ""
                }

            elif linha.lower().startswith("name ") and "vlan" not in linha.lower():
                atual["descricao"] = linha.split("name", 1)[-1].strip().strip('"')

            elif "untagged vlan" in linha.lower() and atual:
                vlan = linha.split()[-1]
                atual["modo"] = "access"
                atual["vlans_untagged"].append(vlan)
                atual["pvid"] = vlan

            elif "tagged vlan" in linha.lower() and atual:
                vlans_tag = linha.split("tagged vlan")[-1].strip()
                atual["modo"] = "trunk"
                atual["vlans_tagged"] = [v.strip() for v in vlans_tag.split(",")]

            elif linha == "exit" and atual:
                interfaces.append(atual)
                atual = {}

            elif linha.lower().startswith("vlan "):
                partes = linha.split()
                if len(partes) >= 2:
                    vlan_id = partes[1]
                    nome = ""
                    if "name" in linha:
                        nome = linha.split("name", 1)[-1].strip().strip('"')
                    vlans.append({"id": vlan_id, "nome": nome})

        if atual:
            interfaces.append(atual)

        return {
            "fabricante": "Aruba",
            "modelo": modelo,
            "hostname": hostname,
            "interfaces": interfaces,
            "vlans": vlans,
            "port_channels": []  # não aplicável neste modelo
        }
