from PySide6.QtWidgets import QWidget, QVBoxLayout, QGridLayout, QLabel
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import seaborn as sns
import pandas as pd

class DashboardScreen(QWidget):
    def __init__(self):
        super().__init__()
        self.main_layout = QVBoxLayout(self)

        # --- Title ---
        title_label = QLabel("Dashboard")
        title_label.setStyleSheet("font-size: 24px; font-weight: bold;")
        self.main_layout.addWidget(title_label)

        # --- Stats Grid ---
        stats_layout = QGridLayout()
        self.main_layout.addLayout(stats_layout)

        # Placeholder stats
        stats = {
            "Today's Sales": "$1,234.56",
            "Revenue (Month)": "$25,678.90",
            "New Customers": "12",
            "Pending Orders": "5",
        }

        positions = [(i, j) for i in range(2) for j in range(2)]
        for (i, j), (key, value) in zip(positions, stats.items()):
            stat_widget = self._create_stat_widget(key, value)
            stats_layout.addWidget(stat_widget, i, j)

        # --- Chart ---
        chart_canvas = self._create_sales_chart()
        self.main_layout.addWidget(chart_canvas)

    def _create_stat_widget(self, title: str, value: str) -> QWidget:
        """Helper to create a styled widget for a single statistic."""
        widget = QWidget()
        layout = QVBoxLayout(widget)

        title_label = QLabel(title)
        title_label.setStyleSheet("font-size: 14px; color: #888;")

        value_label = QLabel(value)
        value_label.setStyleSheet("font-size: 20px; font-weight: bold;")

        layout.addWidget(title_label)
        layout.addWidget(value_label)

        widget.setStyleSheet("background-color: #fff; border-radius: 5px; padding: 10px;")
        return widget

    def _create_sales_chart(self) -> FigureCanvas:
        """Creates a sample sales chart using matplotlib and seaborn."""
        # Sample data
        data = {
            'Day': ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
            'Sales': [1200, 1500, 1300, 1800, 2100, 2500, 1900]
        }
        df = pd.DataFrame(data)

        # Create a matplotlib figure
        fig = Figure(figsize=(5, 3), dpi=100)
        ax = fig.add_subplot(111)

        # Use seaborn to plot
        sns.barplot(x='Day', y='Sales', data=df, ax=ax, palette="viridis")

        ax.set_title("Weekly Sales")
        ax.set_xlabel("Day of Week")
        ax.set_ylabel("Sales ($)")
        fig.tight_layout()

        # Create the canvas widget to display the figure
        canvas = FigureCanvas(fig)
        return canvas
