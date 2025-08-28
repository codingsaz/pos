from PySide6.QtWidgets import QWidget, QVBoxLayout, QGridLayout, QLabel
from optical_pos.ui.widgets.card import CardWidget
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

        # --- Main content layout ---
        content_layout = QGridLayout()
        self.main_layout.addLayout(content_layout)

        # Placeholder stats
        stats = {
            "Today's Sales": "$1,234.56",
            "Revenue (Month)": "$25,678.90",
            "New Customers": "12",
            "Pending Orders": "5",
        }

        positions = [(0, 0), (0, 1), (1, 0), (1, 1)]
        for (r, c), (key, value) in zip(positions, stats.items()):
            stat_card = self._create_stat_widget(key, value)
            content_layout.addWidget(stat_card, r, c)

        # --- Chart ---
        chart_card = self._create_sales_chart_card()
        content_layout.addWidget(chart_card, 0, 2, 2, 1) # Span 2 rows, 1 column

    def _create_stat_widget(self, title: str, value: str) -> CardWidget:
        """Helper to create a styled card for a single statistic."""
        card = CardWidget()
        layout = QVBoxLayout(card)

        title_label = QLabel(title)
        title_label.setStyleSheet("font-size: 14px;") # Style from QSS now

        value_label = QLabel(value)
        value_label.setStyleSheet("font-size: 28px; font-weight: bold;") # Style from QSS now

        layout.addWidget(title_label)
        layout.addWidget(value_label)

        return card

    def _create_sales_chart_card(self) -> CardWidget:
        """Creates a card containing a sample sales chart."""
        card = CardWidget()
        layout = QVBoxLayout(card)

        # Sample data
        data = {
            'Day': ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
            'Sales': [1200, 1500, 1300, 1800, 2100, 2500, 1900]
        }
        df = pd.DataFrame(data)

        # Create a matplotlib figure
        fig = Figure(figsize=(5, 3), dpi=100)
        fig.patch.set_alpha(0) # Make figure background transparent
        ax = fig.add_subplot(111)

        # Use seaborn to plot
        sns.barplot(x='Day', y='Sales', data=df, ax=ax, palette="viridis", hue='Day', legend=False)

        ax.set_title("Weekly Sales")
        ax.set_xlabel("Day of Week")
        ax.set_ylabel("Sales ($)")

        # Style matplotlib to match the dark/light theme better
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.tick_params(colors='#e0e0e0') # Assuming dark theme for now
        ax.yaxis.label.set_color('#e0e0e0')
        ax.xaxis.label.set_color('#e0e0e0')
        ax.title.set_color('#e0e0e0')

        fig.tight_layout()

        canvas = FigureCanvas(fig)
        layout.addWidget(canvas)
        return card
