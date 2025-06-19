from rich.console import Console, Group
from rich.table import Table
from rich.live import Live
from rich.panel import Panel
from rich.layout import Layout
from threading import Thread, Event
from typing import Callable, Dict
import time

from autograder.scripts.monitoring.TableBuilder import TableBuilder


# === Monitor Class for Live Table Updates ===
class Monitor:
    def __init__(self, refresh_interval: float = 1.0, auto_refresh: bool = False):
        self.console = Console()
        self.builders: Dict[str, TableBuilder] = {}
        self.refreshInterval = refresh_interval
        self.autoRefresh = auto_refresh
        self.stopEvent = Event()
        self.live = None
        self.thread = None

    def addTable(self, name: str, builder: TableBuilder):
        self.builders[name] = builder

    def updateTable(self, name: str, data: object):
        self.builders[name].updateTable(data)

    def renderAllTables(self):
        # layout = Layout()
        # layout.split_column(
        #     *[
        #         Layout(Panel(builder.buildTable(), title=name))
        #         for name, builder in self.builders.items()
        #     ]
        # )
        return Group(*[builder.buildTable() for name, builder in self.builders.items()])

    def start(self):
        if self.autoRefresh:
            self.thread = Thread(target=self.autoLoop, daemon=True)
            self.thread.start()
        else:
            self.live = Live(console=self.console, refresh_per_second=4, screen=True)
            self.live.start()

    def autoLoop(self):
        with Live(self.renderAllTables(), console=self.console, refresh_per_second=4, screen=True) as live:
            while not self.stopEvent.is_set():
                live.update(self.renderAllTables())
                time.sleep(self.refreshInterval)

    def stop(self):
        """
        Stop the monitor and live update thread.
        """
        self.stopEvent.set()
        if self.live:
            self.live.stop()

    def refresh(self):
        """
        Manually refresh the screen (only in manual refresh mode).
        """
        if self.live:
            self.live.update(self.renderAllTables())
