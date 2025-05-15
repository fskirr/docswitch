import re

class DellN1148PParser:
    def __init__(self, config_texto):
        self.config = config_texto.splitlines()
        self.resultado = {
            "fabricante": "Dell",
            "modelo": "N1148P-ON",
            "vlans": [],
            "interfaces": [],
            "ips": [],
            "port_channels": [],
            "rotas": [],
        }
        self._parse()

    def _parse(self):
        current_vlan = None
        current_interface = None
        ip_block = {}

        for line in self.config:
            line = line.strip()

            # VLAN com nome
            vlan_match = re.match(r'^vlan (\d+)', line)
            if vlan_match:
                current_vlan = {"id": vlan_match.group(1), "name": ""}
                continue

            if current_vlan and line.startswith("name "):
                current_vlan["name"] = line.split("name", 1)[1].strip().strip('"')
                self.resultado["vlans"].append(current_vlan)
                current_vlan = None
                continue

            # Interface física
            if line.startswith("interface ") and not "vlan" in line:
                current_interface = {
                    "id": line.split()[1],
                    "description": "",
                    "modo": "",
                    "pvid": "",
                    "vlans_tagged": [],
                    "vlans_untagged": [],
                    "ip": ""
                }
                continue

            if current_interface:
                if line.startswith("switchport mode"):
                    current_interface["modo"] = line.split()[-1]
                elif "switchport general allowed vlan add" in line:
                    vlans_raw = line.split("add", 1)[1].strip()
                    tagged = "tagged" in line
                    vlans = re.findall(r'\d+(?:-\d+)?', vlans_raw)
                    if tagged:
                        current_interface["vlans_tagged"].extend(vlans)
                    else:
                        current_interface["vlans_untagged"].extend(vlans)
                elif line == "exit":
                    self.resultado["interfaces"].append(current_interface)
                    current_interface = None
                continue

            # Interface VLAN com IP
            vlan_interface = re.match(r'^interface vlan (\d+)', line)
            if vlan_interface:
                ip_block = {"interface": f"vlan {vlan_interface.group(1)}"}
                continue

            if ip_block:
                if line.startswith("ip address"):
                    if "dhcp" in line:
                        ip_block["ip"] = "dhcp"
                        ip_block["type"] = "dhcp"
                    else:
                        ip_block["ip"] = line.split()[2]
                        ip_block["type"] = "static"
                elif line == "exit":
                    self.resultado["ips"].append(ip_block)
                    ip_block = {}

        # Atribuir IPs às interfaces VLANs
        for ip in self.resultado["ips"]:
            iface = {
                "id": ip["interface"],
                "description": "",
                "modo": "routed",
                "pvid": "",
                "vlans_tagged": [],
                "vlans_untagged": [],
                "ip": ip["ip"] if ip["type"] == "static" else "DHCP"
            }
            self.resultado["interfaces"].append(iface)

    def parse_all(self):
        return self.resultado
