# https://documenter.getpostman.com/view/8470508/SVtN3Wzy
# https://world.openfoodfacts.org/api/v0/product/4037400431598.json

import abc
import configparser
import database
from typing import Dict, Any

class Product(abc.ABC):

    __slots__ = ()

    config = configparser.ConfigParser()
    config.read("config.ini")

    def __init__(self, data: Dict[str, Any]):
        self.name = self._get_name(data)

    @abc.abstractmethod
    def _get_name(self, data: Dict[str, Any]) -> str:
        pass

class OFFProduct(Product):

    __slots__ = ("name",)

    def _get_name(self, data: Dict[str, Any]) -> str:
        lc = self.config["localities"]["language_code"]
        product_name_lc = f"product_name_{lc}"
        keys = [k for k in data.keys() if k.startswith("product_name") and bool(data[k])]
        if product_name_lc in keys:
            return data[product_name_lc]
        elif "product_name" in keys:
            return data["product_name"]
        else:
            return data[next(iter(keys))]
