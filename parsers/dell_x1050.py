from .base_parser import BaseParser

class DellX1050Parser(BaseParser):
    def parse_all(self):
        modelo = "Dell X1050"
        hostname = "Desconhecido"
        interfaces = []
        vlans = []
        rotas = []
        gateway = ""

        for linha in self.raw.splitlines():
            linha = linha.strip()

            if linha.lower().startswith("hostname"):
                hostname = linha.split("hostname", 1)[-1].strip()

            elif linha.startswith("ip default-gateway"):
                gateway = linha.split()[-1]

            elif linha.lower().startswith("ip route"):
                partes = linha.split()
                if len(partes) >= 5:
                    rotas.append({
                        "destino": partes[2],
                        "gateway": partes[4]
                    })

            elif linha.startswith("interface vlan"):
                vlan_id = linha.split("interface vlan")[-1].strip()
                atual = {"id": vlan_id, "nome": ""}
            elif linha.startswith("name") and 'atual' in locals():
                atual["nome"] = linha.split("name", 1)[-1].strip()
            elif "ip address" in linha and 'atual' in locals():
                partes = linha.split()
                if len(partes) >= 3:
                    atual["ip"] = partes[2]
            elif linha == "!" and 'atual' in locals():
                vlans.append(atual)
                del atual

            elif linha.startswith("interface gigabitethernet"):
                iface_nome = linha.split("interface")[-1].strip()
                iface = {
                    "nome": iface_nome,
                    "descricao": "",
                    "modo": "",
                    "vlans_tagged": [],
                    "vlans_untagged": [],
                    "pvid": "",
                    "ip": ""
                }

            elif "switchport mode" in linha and 'iface' in locals():
                iface["modo"] = linha.split()[-1]

            elif "allowed vlan add" in linha and 'iface' in locals():
                if "tagged" in linha:
                    vlans_tag = linha.split("add")[-1].replace("tagged", "").strip()
                    for vlan in vlans_tag.replace("-", ",").split(","):
                        iface["vlans_tagged"].append(vlan.strip())
                elif "untagged" in linha:
                    untag = linha.split("add")[-1].replace("untagged", "").strip()
                    iface["vlans_untagged"].append(untag)
                    iface["pvid"] = untag

            elif linha == "!" and 'iface' in locals():
                interfaces.append(iface)
                del iface

        return {
            "fabricante": "Dell",
            "modelo": modelo,
            "hostname": hostname,
            "interfaces": interfaces,
            "vlans": vlans,
            "port_channels": [],
            "rotas": rotas,
            "gateway": gateway,
            "stp": self._get_stp(),
            "igmp": self._get_igmp(),
            "dhcp_snooping": self._get_dhcp_snooping()
        }

    def _get_stp(self):
        stp = {"status": "disabled", "mode": "", "priority": ""}
        for linha in self.raw.splitlines():
            linha = linha.strip().lower()
            if linha.startswith("spanning-tree"):
                stp["status"] = "enabled"
                if "mode" in linha:
                    stp["mode"] = linha.split()[-1]
        return stp

    def _get_igmp(self):
        for linha in self.raw.splitlines():
            if "igmp" in linha.lower():
                if "disable" in linha.lower():
                    return {"status": "disabled"}
                return {"status": "enabled"}
        return {"status": "desconhecido"}

    def _get_dhcp_snooping(self):
        for linha in self.raw.splitlines():
            if "dhcp snooping" in linha.lower():
                if "disable" in linha.lower():
                    return {"status": "disabled"}
                return {"status": "enabled"}
        return {"status": "desconhecido"}
