"""This module includes classes to create and interact with products. """

# https://documenter.getpostman.com/view/8470508/SVtN3Wzy
# https://world.openfoodfacts.org/api/v0/product/4037400431598.json

import abc
import configparser
from typing import Any, Dict, Tuple, TypeVar, Union

import database


class Product(abc.ABC):
    "A default interface for working with a product."

    __slots__: Tuple[str, ...] = tuple()

    # Parse the config file.
    config = configparser.ConfigParser()
    config.read("config.ini")

    def __init__(self, barcode: str, data: Dict[str, Any]):
        """Initialize the product."""

        self.barcode = barcode
        self.data = data

    @abc.abstractmethod
    def _get(self, key: str) -> str:
        """Return the information associated with the given key."""

        pass


class OFFProduct(Product):
    "A product from the Open Food Facts database."

    __slots__ = ("barcode", "data", "lc", "name", "generic_name", "quantity",
                 "packaging_text", "packaging", "brands", "categories",
                 "labels", "manufacturing_places", "emb_codes", "link",
                 "last_edit", "purchase_places", "stores", "countries",
                 "ingredients_text", "ingredients", "allergens", "allergens",
                 "allergens_from_ingredients", "traces",
                 "traces_from_ingredients", "origins", "serving_size",
                 "nutriments")

    # Key suffixes to ignore.
    suffixes = ("hierarchy", "lc", "old", "tags", "analysis_tags",
                "from_or_that_may_be_from_palm_oil_n", "from_palm_oil_n",
                "from_palm_oil_tags", "n", "n_tags", "original_tags")

    def __init__(self, barcode: str, data: Dict[str, Any]):
        """Initialize the product."""

        super().__init__(barcode, data)

        self.lc = self.config["localities"]["language_code"]

        # Gather product information.
        self.name = self._get("product_name")
        self.generic_name = self._get("generic_name")
        self.quantity = self._get("quantity")
        self.packaging_text = self._get("packaging_text")
        self.packaging = self._get("packaging")
        self.brands = self._get("brands")
        self.categories = self._get("categories")
        self.labels = self._get("labels")
        self.manufacturing_places = self._get("manufacturing_places")
        self.emb_codes = self._get("emb_codes")
        self.link = self._get("link")
        self.last_edit = self._get("last_edit_dates_tags")[0]
        self.purchase_places = self._get("purchase_places")
        self.stores = self._get("stores")
        self.countries = self._get("countries")
        self.ingredients_text = self._get("ingredients_text")
        self.ingredients = self._get("ingredients")
        self.allergens = self._get("allergens")
        self.allergens_from_ingredients = self._get(
            "allergens_from_ingredients")
        self.traces = self._get("traces")
        self.traces_from_ingredients = self._get("traces_from_ingredients")
        self.origins = self._get("origins")
        self.serving_size = self._get("serving_size")
        self.nutriments = self._get("nutriments")
        # emissions?

    def _get(self, key: str) -> str:
        """Return the information associated with the given key."""

        # Solution with walrus operator; Python 3.8+
        # return self.data[(k := self._get_key_with_lc(key))] if k is not None else None
        key = self._get_key_with_lc(key)
        return self.data[key] if key is not None else None

    def _get_key_with_lc(self, key: str) -> str:
        """Get the key with the language code according to the config file.

        If there is no key entry with that language code,
        return another one, trying the default first.
        """

        # Filter to-be-ignored suffixes if they are part of `key`.
        suffixes = list(
            filter(lambda s: s not in key.split("_"), self.suffixes))

        # Find all keys with the `key`; if the key is not in the data, return `None`.
        keys = [
            k for k in self.data.keys() if k.startswith(key) and not any(
                k.endswith(f"_{suffix}") for suffix in suffixes)
        ]
        if not keys:
            return None

        # Concatenate the key with the language code.
        key_lc = f"{key}_{self.lc}"

        # Return the best fitting key.
        # Order by the relevance (key with most appropriate language code).
        keys.sort(key=lambda k: 2 if k == key_lc else 1 if k == key else 0)
        # However, keys with non-empty data entries should be preferred.
        keys.sort(key=lambda k: bool(self.data[k]))
        return keys[-1]


class UnknownProduct(Product):
    "A product which could not be found in a database."

    __slots__ = ("barcode", "data")

    def __init__(self, barcode: str):
        """Initialize the product with the only information we have: the barcode."""

        super().__init__(barcode, dict())

    def _get(self, key: str) -> str:
        return str()


P = TypeVar("P", bound=Product)
