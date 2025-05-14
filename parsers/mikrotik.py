from .base_parser import BaseParser

class MikrotikParser(BaseParser):
    def parse_all(self):
        hostname = "Desconhecido"
        interfaces = []
        vlans = []
        rotas = []

        interfaces_dict = {}

        for linha in self.raw.splitlines():
            linha = linha.strip()

            if linha.startswith("/system identity"):
                if "name=" in linha:
                    hostname = linha.split("name=")[-1].strip()

            elif linha.startswith("/interface") and "add" in linha:
                if "name=" in linha:
                    nome = self._extrair(linha, "name")
                    desc = self._extrair(linha, "comment")
                    interfaces_dict[nome] = {
                        "nome": nome,
                        "descricao": desc or "",
                        "modo": "",
                        "vlans_tagged": [],
                        "vlans_untagged": [],
                        "pvid": "",
                        "ip": ""
                    }

            elif linha.startswith("/interface vlan add"):
                nome = self._extrair(linha, "name")
                vlan_id = self._extrair(linha, "vlan-id")
                if nome:
                    vlans.append({"id": vlan_id or "?", "nome": nome})

            elif linha.startswith("/ip address add"):
                ip = self._extrair(linha, "address")
                iface = self._extrair(linha, "interface")
                if iface and iface in interfaces_dict:
                    interfaces_dict[iface]["ip"] = ip

            elif linha.startswith("/ip route add"):
                dst = self._extrair(linha, "dst-address")
                gw = self._extrair(linha, "gateway")
                if dst and gw:
                    rotas.append({"destino": dst, "gateway": gw})

        interfaces = list(interfaces_dict.values())

        return {
            "fabricante": "Mikrotik",
            "modelo": "Desconhecido",
            "hostname": hostname,
            "interfaces": interfaces,
            "vlans": vlans,
            "port_channels": [],
            "rotas": rotas
        }

    def _extrair(self, linha, chave):
        for parte in linha.split():
            if parte.startswith(f"{chave}="):
                return parte.split("=", 1)[-1].strip()
        return ""
