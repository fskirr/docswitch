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
                    "nome": linha.split("interface ")[-1],
                    "descricao": "",
                    "modo": "",
                    "vlans_tagged": [],
                    "vlans_untagged": [],
                    "pvid": "",
                    "ip": ""
                }
            elif linha.startswith("description ") and atual:
                atual["descricao"] = linha.split("description ")[-1]
            elif linha.startswith("switchport mode") and atual:
                atual["modo"] = linha.split("switchport mode ")[-1]
            elif linha.startswith("switchport access vlan") and atual:
                atual["vlans_untagged"].append(linha.split()[-1])
                atual["pvid"] = linha.split()[-1]
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

    def parse_all(self):
        return {
            "fabricante": "Cisco",
            "modelo": self.detect_model(),
            "hostname": self._get_hostname(),
            "interfaces": self._get_interfaces(),
            "vlans": self._get_vlans(),
            "port_channels": self._get_port_channels()
        }
