"""This file includes everything to handle accessing the database."""

from typing import Optional, Dict
import pathlib
import pickle

# https://docs.python.org/3/reference/datamodel.html
# https://docs.python.org/3/library/pickle.html
# https://docs.python.org/3/library/typing.html

class DatabaseHandler:
    """An default interface for handling access to an EAN database.

    To improve performance, results will be cached and saved to a file locally,
    as it is likely that the same products will be accessed repeatedly.

    The database handler is supposed to be accessed in a context manager
    with the `with` statement, to ensure that the cache is saved.
    """

    def __init__(self, local_location: Optional[str] = None) -> None:
        """Initialize the database handler."""

        # If a location for the local database was provided, create a Path object from it.
        self.path: Optional[pathlib.Path] = None
        if local_location is not None:
            self.path = pathlib.Path(local_location)

    def __enter__(self) -> "DatabaseHandler":
        """Initialize the cache and enter into the context manager."""

        # If a location for the local database was provided and it already exists,
        # deserialize the cache from it.
        self.cache: Dict[str, str] = dict()
        if self.path is not None and self.path.is_file():
            with self.path.open(mode="rb") as local_database:
                self.cache = pickle.load(local_database)

        # Return the `DatabaseHandler` itself to be used in the context manager.
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        """Serialize and save the cache to a file and exit the context manager."""

        with self.path.open(mode="wb") as local_database:
            pickle.dump(self.cache, local_database)
