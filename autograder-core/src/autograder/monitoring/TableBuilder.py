from rich.table import Table


class TableBuilder:
    def __init__(self, title: str, columns: list):
        pass
    def buildTable(self) -> Table:
        """
        Return a new rich.Table object based on the current data.
        """
        pass
    def updateTable(self, data: object):
        """
        Update the internal data structure with new data.
        This method should be implemented in subclasses.
        """
        pass
