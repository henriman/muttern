"""This module includes everything to handle accessing barcode databases."""

import abc
from typing import Optional, Dict, Tuple, Generic, Union
import pathlib
import pickle
import requests
import product

class DatabaseHandler(abc.ABC, Generic[product.P]):
    """A default interface for handling access to an EAN database.

    To improve performance, results will be cached and saved to a file locally,
    as it is likely that the same products will be accessed repeatedly.

    The database handler is supposed to be accessed in a context manager
    with the `with` statement, to ensure that the cache is saved.
    """

    __slots__: Tuple[str, ...] = tuple()

    def __init__(self, cache_location: Optional[str] = None) -> None:
        """Initialize the database handler."""

        # Initalize an empty cache.
        self.products: Dict[str, Union[product.P, product.UnknownProduct]] = dict()

        # If a location for the local cache was provided, create a Path object from it.
        self.path: Optional[pathlib.Path] = None
        if cache_location is not None:
            self.path = pathlib.Path(cache_location)

    @abc.abstractmethod
    def _get(self, barcode: str) -> Union[product.P, product.UnknownProduct]:
        """Request the product associated with the given `barcode` from the database."""

        pass

    def get(self, barcode: str) -> Union[product.P, product.UnknownProduct]:
        """Return the product associated with the given `barcode`.

        Store the result in the cache for re-use.
        """

        # If the barcode is not in the cache, request the product from the database.
        if barcode not in self.products.keys():
            result = self._get(barcode)
            self.products[barcode] = result

        # Return the product associated with the barcode.
        return self.products[barcode]

    def __enter__(self) -> "DatabaseHandler":
        """Initialize the cache and enter into the context manager."""

        # If a location for the local cache was provided and it already exists,
        # deserialize the cache from it.
        if self.path is not None and self.path.is_file():
            with self.path.open(mode="rb") as local_database:
                self.products = pickle.load(local_database)

        # Return the `DatabaseHandler` itself to be used in the context manager.
        return self

    def __exit__(self, exc_type, exc_value, traceback) -> None:
        """If a path was given, save the cache to a file; exit the context manager."""

        if self.path is not None:
            with self.path.open(mode="wb") as local_database:
                pickle.dump(self.products, local_database)

class OFFDatabaseHandler(DatabaseHandler[product.OFFProduct]):
    """A class for handling access to the Open Food Facts database."""

    __slots__ = ("products", "path")

    @staticmethod
    def url(barcode: str) -> str:
        """Create the request URL from the given `barcode`."""

        return f"https://world.openfoodfacts.org/api/v0/product/{barcode}.json"

    def _get(self, barcode: str) -> Union[product.OFFProduct, product.UnknownProduct]:
        """Request the product associated with the given `barcode` from the database."""

        # Request the data associated with the given `barcode`.
        response = requests.get(url=self.url(barcode))
        data = response.json()

        # If the barcode was found in the database, return the corresponding product.
        return product.OFFProduct(barcode, data["product"]) if data["status"] == 1 else product.UnknownProduct(barcode)
