import database
import barcode_scanner
import gui

if __name__ == "__main__":
    with database.OFFDatabaseHandler(cache_location=None) as dbh:
        with barcode_scanner.BarcodeScanner(dbh) as scanner:
            root = gui.GUI(scanner)
            root.stream()
            root.mainloop()
