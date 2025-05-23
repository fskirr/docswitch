from .base_parser import BaseParser

class HpeParser(BaseParser):
    def parse_all(self):
        modelo = "Desconhecido"
        hostname = "Desconhecido"
        interfaces = []
        vlans = []

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
            "port_channels": [],
            "rotas": self._get_rotas(),
            "stp": self._get_stp(),
            "igmp": self._get_igmp(),
            "dhcp_snooping": self._get_dhcp_snooping()
        }

    def _get_rotas(self):
        rotas = []
        for linha in self.raw.splitlines():
            if linha.lower().startswith("ip route"):
                partes = linha.split()
                if len(partes) >= 4:
                    destino = f"{partes[2]}/{self._mask_to_cidr(partes[3])}"
                    gateway = partes[4]
                    rotas.append({"destino": destino, "gateway": gateway})
        return rotas

    def _mask_to_cidr(self, mask):
        return sum([bin(int(o)).count("1") for o in mask.split(".")])

    def _get_stp(self):
        stp = {"status": "disabled", "mode": "", "priority": ""}
        for linha in self.raw.splitlines():
            linha = linha.strip().lower()
            if linha.startswith("spanning-tree"):
                stp["status"] = "enabled"
                if "mode" in linha:
                    stp["mode"] = linha.split()[-1]
                if "priority" in linha:
                    stp["priority"] = linha.split()[-1]
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
            if "dhcp-snooping" in linha.lower():
                if "disable" in linha.lower():
                    return {"status": "disabled"}
                return {"status": "enabled"}
        return {"status": "desconhecido"}
