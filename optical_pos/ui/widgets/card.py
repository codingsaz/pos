from PySide6.QtWidgets import QFrame, QVBoxLayout

class CardWidget(QFrame):
    """
    A reusable card widget that provides a styled container for content.
    It uses the #CardWidget object name to pick up styles from the QSS file.
    """
    def __init__(self):
        super().__init__()
        self.setObjectName("CardWidget")

        # The card itself is just a frame. The layout is managed by the
        # widget that uses the card. We provide a layout for convenience.
        self.card_layout = QVBoxLayout(self)

    def setLayout(self, layout):
        # This is a bit of a trick to allow setting a layout on the card
        # after the fact, by replacing the one we created.
        # A better way might be to have a content_widget inside the frame.
        # For now, this is simple.

        # Delete existing layout
        old_layout = self.layout()
        if old_layout is not None:
            # Reparent the widgets to avoid deleting them
            while old_layout.count():
                item = old_layout.takeAt(0)
                if item.widget():
                    item.widget().setParent(None)
            del old_layout

        super().setLayout(layout)
