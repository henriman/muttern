"""Starting point for the application."""

import gui
import database
import barcode_scanner

if __name__ == "__main__":
    with database.OFFDatabaseHandler(cache_location=None) as dbh:
        with barcode_scanner.BarcodeScanner(dbh) as scanner:
            root = gui.MainGUI(scanner)
            root.mainloop()
