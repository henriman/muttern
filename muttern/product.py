"""This module includes classes to create and interact with products. """

# https://documenter.getpostman.com/view/8470508/SVtN3Wzy
# https://world.openfoodfacts.org/api/v0/product/4037400431598.json

import abc
import configparser
import database
from typing import Dict, Any, Tuple, Union

class Product(abc.ABC):
    "A default interface for working with a product."

    __slots__: Tuple[str, ...] = tuple()

    # Parse the config file.
    config = configparser.ConfigParser()
    config.read("config.ini")

    def __init__(self, data: Dict[str, Any]):
        """Initialize the product."""

        self.data = data

    @abc.abstractmethod
    def _get_name(self) -> str:
        """Parse the (brand) name of the product from the data."""

        pass

class OFFProduct(Product):
    "A product from the Open Food Facts database."

    __slots__ = ("name", "data", "lc")

    def __init__(self, data: Dict[str, Any]):
        """Initialize the product."""

        super().__init__(data)

        self.lc = self.config["localities"]["language_code"]
        self.name = self._get_name()

    def _get_key_with_lc(self, key: str) -> str:
        """Get the key with the language code according to the config file.

        If there is no key entry with that language code,
        return the another one, trying the default first.
        """

        # Find all keys with the `key`.
        keys = [k for k in self.data.keys() if k.startswith(key) and bool(self.data[k])]
        # Concatenate the key with the language code.
        key_lc = f"{key}_{self.lc}"

        # Return the best fitting key.
        if key_lc in keys:
            return key_lc
        elif key in keys:
            return key
        else:
            return next(iter(keys))

    def _get_name(self) -> str:
        """Parse the (brand) name of the product from the data."""

        return self.data[self._get_key_with_lc("product_name")]
