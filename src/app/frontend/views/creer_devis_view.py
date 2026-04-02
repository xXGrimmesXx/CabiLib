from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel
from app.frontend.widgetPersonalise.checkable_combobox import CheckableComboBox

class CreerDevisView(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("Page de création de devis (placeholder)"))
        self.checkable_combo = CheckableComboBox()
        self.checkable_combo.addItem("Option 1",1)
        self.checkable_combo.addItem("Option 2",2)
        self.checkable_combo.addItem("Option 3",3)
        self.checkable_combo.addItem("Option 4",4)
        self.checkable_combo.addItem("Option 5",5)
        self.checkable_combo.addItem("Option 6",6)
        self.checkable_combo.addItem("Option 7",7)
        self.checkable_combo.addItem("Option 8",8)
        self.checkable_combo.addItem("Option 9",9)
        self.checkable_combo.addItem("Option 10",10)
        self.checkable_combo.addItem("Option 110000000",11)
        self.checkable_combo.selectionChanged.connect(self.on_selection_changed)
        layout.addWidget(self.checkable_combo)
        self.setLayout(layout)
    def on_selection_changed(self, selected_ids):
        print("IDs sélectionnés :", selected_ids)

