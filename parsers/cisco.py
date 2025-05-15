from .base_parser import BaseParser

class CiscoParser(BaseParser):
    def detect_model(self):
        for linha in self.raw.splitlines():
            if "Model number" in linha or "Model:" in linha:
                return linha.split(":")[-1].strip()
        return "Modelo Cisco não detectado"

    def _get_hostname(self):
        for linha in self.raw.splitlines():
            if linha.startswith("hostname "):
                return linha.split("hostname ")[-1].strip()
        return "Desconhecido"

    def _get_interfaces(self):
        interfaces = []
        atual = {}
        for linha in self.raw.splitlines():
            linha = linha.strip()
            if linha.startswith("interface "):
                if atual:
                    interfaces.append(atual)
                atual = {
                    "id": linha.split("interface ")[-1],
                    "description": "",
                    "modo": "",
                    "pvid": "",
                    "vlans_tagged": [],
                    "vlans_untagged": [],
                    "ip": ""
                }
            elif linha.startswith("description ") and atual:
                atual["description"] = linha.split("description ")[-1]
            elif linha.startswith("switchport mode") and atual:
                atual["modo"] = linha.split("switchport mode ")[-1]
            elif linha.startswith("switchport access vlan") and atual:
                vlan = linha.split()[-1]
                atual["vlans_untagged"].append(vlan)
                atual["pvid"] = vlan
            elif linha.startswith("switchport trunk native vlan") and atual:
                atual["pvid"] = linha.split()[-1]
            elif linha.startswith("switchport trunk allowed vlan") and atual:
                vlans = linha.split()[-1].split(",")
                atual["vlans_tagged"].extend(vlans)
            elif linha.startswith("ip address") and atual:
                partes = linha.split()
                if len(partes) >= 3:
                    atual["ip"] = partes[2]
        if atual:
            interfaces.append(atual)
        return interfaces

    def _get_vlans(self):
        vlans = []
        atual = {}
        for linha in self.raw.splitlines():
            linha = linha.strip()
            if linha.startswith("vlan "):
                if atual:
                    vlans.append(atual)
                atual = {"id": linha.split("vlan ")[-1], "nome": ""}
            elif linha.startswith("name ") and atual:
                atual["nome"] = linha.split("name ")[-1]
        if atual:
            vlans.append(atual)
        return vlans

    def _get_port_channels(self):
        port_channels = []
        grupos = {}
        for linha in self.raw.splitlines():
            linha = linha.strip()
            if linha.startswith("interface "):
                iface = linha.split("interface ")[-1]
            elif "channel-group" in linha:
                partes = linha.split()
                try:
                    id_grupo = partes[1]
                    grupos.setdefault(id_grupo, []).append(iface)
                except:
                    continue
        for id_grupo, membros in grupos.items():
            port_channels.append({
                "id": id_grupo,
                "interfaces_membro": membros
            })
        return port_channels

    def _get_rotas(self):
        rotas = []
        for linha in self.raw.splitlines():
            linha = linha.strip()
            if linha.startswith("ip route "):
                partes = linha.split()
                if len(partes) >= 5:
                    destino = f"{partes[2]}/{self._mask_to_cidr(partes[3])}"
                    gateway = partes[4]
                    rotas.append({"destino": destino, "gateway": gateway})
                elif len(partes) >= 4:
                    destino = partes[2]
                    gateway = partes[3]
                    rotas.append({"destino": destino, "gateway": gateway})
        return rotas

    def _mask_to_cidr(self, mask):
        return sum([bin(int(oct)).count("1") for oct in mask.split(".")])

    def _get_stp(self):
        stp = {"status": "desconhecido", "mode": "", "priority": ""}
        for linha in self.raw.splitlines():
            linha = linha.strip()
            if linha.startswith("spanning-tree mode"):
                stp["status"] = "enabled"
                stp["mode"] = linha.split()[-1]
            elif "spanning-tree vlan" in linha and "priority" in linha:
                stp["priority"] = linha.split()[-1]
        return stp

    def _get_igmp(self):
        for linha in self.raw.splitlines():
            if "ip igmp snooping" in linha.lower():
                if "disable" in linha.lower() or "no ip igmp" in linha.lower():
                    return {"status": "disabled"}
                return {"status": "enabled"}
        return {"status": "desconhecido"}

    def _get_dhcp_snooping(self):
        for linha in self.raw.splitlines():
            if "ip dhcp snooping" in linha.lower():
                if "no ip dhcp snooping" in linha.lower():
                    return {"status": "disabled"}
                return {"status": "enabled"}
        return {"status": "desconhecido"}

    def parse_all(self):
        return {
            "fabricante": "Cisco",
            "modelo": self.detect_model(),
            "hostname": self._get_hostname(),
            "interfaces": self._get_interfaces(),
            "vlans": self._get_vlans(),
            "port_channels": self._get_port_channels(),
            "rotas": self._get_rotas(),
            "stp": self._get_stp(),
            "igmp": self._get_igmp(),
            "dhcp_snooping": self._get_dhcp_snooping()
        }
