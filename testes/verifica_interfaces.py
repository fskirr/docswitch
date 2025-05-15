import os
import sys
import importlib
import inspect

# Adiciona o diretório base do projeto ao sys.path
sys.path.insert(0, "/opt/docswitch")

PARSERS_DIR = "/opt/docswitch/parsers"
OBRIGATORIOS = ["id", "description", "modo", "pvid", "vlans_tagged", "vlans_untagged", "ip"]

# Simulação leve de uma configuração que deve acionar a lógica de parsing
CONFIG_EXEMPLO = """
interface vlan 10
ip address 192.168.0.1 255.255.255.0
exit
interface Gi1/0/1
switchport mode access
switchport access vlan 10
exit
"""

def encontrar_classes_modulo(modulo):
    return [membro for nome, membro in inspect.getmembers(modulo, inspect.isclass)]

def verificar_parser(nome_arquivo):
    nome_modulo = nome_arquivo.replace(".py", "")
    if nome_modulo in ["__init__", "base_parser"]:
        return

    caminho_modulo = f"parsers.{nome_modulo}"
    try:
        modulo = importlib.import_module(caminho_modulo)
        classes = encontrar_classes_modulo(modulo)

        if not classes:
            print(f"[{nome_modulo}] ⚠️ Nenhuma classe encontrada no parser.")
            return

        for classe in classes:
            if not callable(getattr(classe, "parse_all", None)):
                print(f"[{nome_modulo}] ❌ Classe {classe.__name__} não implementa parse_all().")
                continue

            instancia = classe(CONFIG_EXEMPLO)
            resultado = instancia.parse_all()

            interfaces = resultado.get("interfaces", [])
            if not interfaces:
                print(f"[{nome_modulo}] ⚠️ Nenhuma interface retornada.")
                continue

            for idx, iface in enumerate(interfaces):
                faltando = [campo for campo in OBRIGATORIOS if campo not in iface]
                if faltando:
                    print(f"[{nome_modulo}] ❌ Interface {idx+1} faltando campos: {faltando}")
                else:
                    print(f"[{nome_modulo}] ✅ Interface {idx+1} OK")

    except Exception as e:
        print(f"[{nome_modulo}] ❌ Erro ao verificar: {e}")

def main():
    print("🔍 Verificando estrutura das interfaces em todos os parsers...\n")
    for arquivo in os.listdir(PARSERS_DIR):
        if arquivo.endswith(".py"):
            verificar_parser(arquivo)

if __name__ == "__main__":
    main()
