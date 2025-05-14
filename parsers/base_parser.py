class BaseParser:
    def __init__(self, raw_config):
        self.raw = raw_config

    def detect_model(self):
        return "Modelo não identificado"

    def parse_all(self):
        raise NotImplementedError("Implementar no parser do fabricante")
