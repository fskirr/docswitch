# DocSwitch

Sistema web para análise e documentação automática de configurações (`running-config`) de equipamentos de rede.

---

## ✨ Funcionalidades

- Upload de arquivos `.txt` extraídos diretamente de switches/firewalls
- Suporte a múltiplos fabricantes:
  - Cisco
  - HPE
  - Dell
  - Aruba
  - Fortigate
  - Mikrotik
- Detecção automática de:
  - Modelo
  - Hostname
  - Interfaces, modos, VLANs, IPs
  - Port-channels
  - Rotas
- Exportação em:
  - HTML
  - PDF
- Histórico persistente com SQLite
- Interface web leve com TailwindCSS

---

## 📁 Estrutura de diretórios

```
/opt/docswitch/
├── app.py                  # Aplicação principal Flask
├── requirements.txt        # Dependências do projeto
├── venv/                   # Ambiente virtual Python
├── uploads/                # Arquivos de configuração enviados
├── templates/              # HTMLs Jinja2 (resultado, histórico)
├── parsers/                # Parsers por fabricante
├── utils/
│   ├── parser_factory.py   # Seleciona o parser com base no fabricante
│   └── db.py               # Salvamento e leitura no SQLite
├── db.sqlite3              # Banco de dados local (histórico)
└── .gitignore              # Exclusões do versionamento
```

---

## ⚙️ Execução como serviço (systemd)

### Arquivo de serviço:

```ini
/etc/systemd/system/docswitch.service
```

### Comandos:

```bash
sudo systemctl start docswitch
sudo systemctl stop docswitch
sudo systemctl restart docswitch
sudo systemctl status docswitch
```

---

## 🚀 Como subir o ambiente

```bash
# Clonar repositório
git clone git@github.com:fskirr/docswitch.git
cd docswitch

# Criar ambiente virtual
python3 -m venv venv
source venv/bin/activate

# Instalar dependências
pip install -r requirements.txt

# Iniciar manualmente (para testes)
python app.py
```

---

## 🌐 Rotas disponíveis

| Rota         | Descrição                        |
|--------------|----------------------------------|
| `/`          | Tela inicial (upload)           |
| `/analisar`  | Processamento e exibição         |
| `/historico` | Lista de análises realizadas     |
| `/exportar/html` | Exporta resultado em HTML    |
| `/exportar/pdf`  | Exporta resultado em PDF     |

---

## 📋 Exemplo de uso

1. Acesse `http://<IP ou domínio da VM>`
2. Envie um arquivo `.txt` com a running-config
3. Escolha o fabricante
4. Visualize a análise e exporte o resultado

---

## 🔒 Requisitos

- Python 3.11+
- Debian 12
- Pacotes do sistema:
  ```bash
  sudo apt install libpango-1.0-0 libpangocairo-1.0-0 libcairo2 libffi-dev libjpeg-dev libxml2 libxslt1-dev
  ```

---

## 🧠 Observações

- O parser espera **configs brutas** salvas direto do terminal do equipamento (sem formatação extra).
- Ideal para uso por equipes de redes, documentação e auditoria técnica.

---

## 📌 Autor

Desenvolvido por [fskirr](https://github.com/fskirr)
