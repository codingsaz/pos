import pandas as pd
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QTableView,
    QPushButton,
    QLabel,
    QComboBox,
    QDateEdit,
    QHeaderView,
)
from PySide6.QtCore import QAbstractTableModel, Qt, QModelIndex, QDate
from typing import List, Any
from optical_pos.services import report_service
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import seaborn as sns

class PandasTableModel(QAbstractTableModel):
    """A table model that displays a pandas DataFrame."""
    def __init__(self, data: pd.DataFrame):
        super().__init__()
        self._data = data

    def rowCount(self, parent: QModelIndex = QModelIndex()) -> int:
        return self._data.shape[0]

    def columnCount(self, parent: QModelIndex = QModelIndex()) -> int:
        return self._data.shape[1]

    def data(self, index: QModelIndex, role: int = Qt.DisplayRole) -> Any:
        if role == Qt.DisplayRole:
            return str(self._data.iloc[index.row(), index.column()])
        return None

    def headerData(self, section: int, orientation: Qt.Orientation, role: int = Qt.DisplayRole) -> Any:
        if role == Qt.DisplayRole and orientation == Qt.Horizontal:
            return str(self._data.columns[section])
        return None

class ReportsScreen(QWidget):
    def __init__(self):
        super().__init__()
        self.main_layout = QVBoxLayout(self)
        self.current_df = None

        title_label = QLabel("Reports")
        title_label.setStyleSheet("font-size: 24px; font-weight: bold;")
        self.main_layout.addWidget(title_label)

        # --- Controls ---
        controls_layout = QHBoxLayout()
        self.report_combo = QComboBox()
        self.report_combo.addItems(["Sales by Period", "Top Products", "Profit & Loss"])
        self.start_date_edit = QDateEdit(QDate.currentDate().addMonths(-1))
        self.end_date_edit = QDateEdit(QDate.currentDate())
        self.generate_button = QPushButton("Generate Report")
        self.generate_button.clicked.connect(self.generate_report)

        controls_layout.addWidget(QLabel("Report Type:"))
        controls_layout.addWidget(self.report_combo)
        controls_layout.addWidget(QLabel("Start Date:"))
        controls_layout.addWidget(self.start_date_edit)
        controls_layout.addWidget(QLabel("End Date:"))
        controls_layout.addWidget(self.end_date_edit)
        controls_layout.addWidget(self.generate_button)
        controls_layout.addStretch()
        self.main_layout.addLayout(controls_layout)

        # --- Report Display Area ---
        display_layout = QHBoxLayout()
        self.table_view = QTableView()
        self.table_view.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

        self.chart_canvas = FigureCanvas(Figure(figsize=(5, 4)))

        display_layout.addWidget(self.table_view, 2) # 2/3 space
        display_layout.addWidget(self.chart_canvas, 1) # 1/3 space
        self.main_layout.addLayout(display_layout)

    def generate_report(self):
        report_type = self.report_combo.currentText()
        start_date = self.start_date_edit.date().toPython()
        end_date = self.end_date_edit.date().toPython()

        if report_type == "Sales by Period":
            self.current_df = report_service.get_sales_report(start_date, end_date)
            self.display_sales_chart()
        elif report_type == "Top Products":
            self.current_df = report_service.get_top_products_report()
            self.display_top_products_chart()
        elif report_type == "Profit & Loss":
            self.current_df = report_service.get_profit_loss_report(start_date, end_date)
            self.display_pl_chart()

        # Display data in table
        table_model = PandasTableModel(self.current_df)
        self.table_view.setModel(table_model)

    def display_sales_chart(self):
        fig = self.chart_canvas.figure
        fig.clear()
        ax = fig.add_subplot(111)

        if not self.current_df.empty:
            # Aggregate sales by date for plotting
            daily_sales = self.current_df.groupby('date')['total'].sum().reset_index()
            sns.lineplot(x='date', y='total', data=daily_sales, ax=ax)
            ax.set_title("Sales Over Time")
            ax.tick_params(axis='x', rotation=45)
        else:
            ax.text(0.5, 0.5, "No data to display", ha='center', va='center')

        fig.tight_layout()
        self.chart_canvas.draw()

    def display_top_products_chart(self):
        fig = self.chart_canvas.figure
        fig.clear()
        ax = fig.add_subplot(111)

        if not self.current_df.empty:
            sns.barplot(x='total_quantity', y='name', data=self.current_df, ax=ax, orient='h')
            ax.set_title("Top Selling Products")
        else:
            ax.text(0.5, 0.5, "No data to display", ha='center', va='center')

        fig.tight_layout()
        self.chart_canvas.draw()

    def display_pl_chart(self):
        fig = self.chart_canvas.figure
        fig.clear()
        ax = fig.add_subplot(111)

        if not self.current_df.empty:
            sns.barplot(x='Metric', y='Amount', data=self.current_df, ax=ax)
            ax.set_title("Profit & Loss Summary")
        else:
            ax.text(0.5, 0.5, "No data to display", ha='center', va='center')

        fig.tight_layout()
        self.chart_canvas.draw()
