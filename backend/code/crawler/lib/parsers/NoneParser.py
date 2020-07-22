from .BaseParser import BaseParser

class NoneParser(BaseParser):
    def parse(self, data, timing):
        return timing
