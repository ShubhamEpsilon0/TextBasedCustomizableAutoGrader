from rich.table import Table

class DictTableBuilder:
    def __init__(self, title: str, columns: list):
        self.title = title
        self.columns = columns
        self.data = {}

    def buildTable(self) -> Table:        
        table = Table(title=self.title)
        for col in self.columns:
            table.add_column(col)

        for key, value in self.data.items():
            table.add_row(str(key), str(value))
        return table
    
    def updateTable(self, data: dict):
        try:
            self.data = dict(data)
        except Exception as e:
            raise ValueError(f"Invalid data provided: {e}. It must be a dictionary.")