"""This module includes classes to create and interact with products. """

# https://documenter.getpostman.com/view/8470508/SVtN3Wzy
# https://world.openfoodfacts.org/api/v0/product/4037400431598.json

import abc
import configparser
import database
from typing import Dict, Any, Tuple, Union, TypeVar

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
    def _get(self, key: str) -> str:
        """Return the information associated with the given key."""

        pass

class OFFProduct(Product):
    "A product from the Open Food Facts database."

    __slots__ = ("name", "data", "lc", "brands")

    def __init__(self, data: Dict[str, Any]):
        """Initialize the product."""

        super().__init__(data)

        # Gather all necessary information.
        self.lc = self.config["localities"]["language_code"]
        self.name = self._get("product_name")
        self.brands = self._get("brands")

        # TODO: add more information

    def _get(self, key: str) -> str:
        """Return the information associated with the given key."""

        return self.data[self._get_key_with_lc(key)]

    def _get_key_with_lc(self, key: str) -> str:
        """Get the key with the language code according to the config file.

        If there is no key entry with that language code,
        return another one, trying the default first.
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

P = TypeVar("P", bound=Product)
