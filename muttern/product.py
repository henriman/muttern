# https://documenter.getpostman.com/view/8470508/SVtN3Wzy
# https://world.openfoodfacts.org/api/v0/product/4037400431598.json

import configparser
import database
from typing import Dict, Any

class OFFProduct:
    config = configparser.ConfigParser()
    config.read("config.ini")

    def __init__(self, data: Dict[str, Any]):
        self.name = self._get_name(data)

    def _get_name(self, data: Dict[str, Any]) -> str:
        return data["product_name"]
