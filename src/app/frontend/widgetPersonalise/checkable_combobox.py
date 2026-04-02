"""
CheckableComboBox — PySide6
Un menu déroulant avec cases à cocher pour la sélection multiple.
"""

from PySide6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QFrame, QScrollArea,
    QCheckBox, QSizePolicy, QMainWindow, QLineEdit
)
from PySide6.QtCore import Qt, Signal, QPoint
from PySide6.QtGui import QIcon, QCursor
import sys


class CheckableComboBox(QWidget):
    """
    Widget combinant une ComboBox et des CheckBox pour la sélection multiple.

    Signaux :
        selectionChanged(list) — émis à chaque changement, avec la liste des
                                  valeurs (data) sélectionnées.

    Utilisation rapide :
        combo = CheckableComboBox("Marques")
        combo.addItem("Yamaha",   data="yamaha")
        combo.addItem("Philips",  data="philips")
        combo.addItem("Sony",     data="sony")
        combo.selectionChanged.connect(lambda vals: print(vals))
    """

    selectionChanged = Signal(list)

    # ------------------------------------------------------------------ #
    #  Construction                                                        #
    # ------------------------------------------------------------------ #
    def __init__(self, placeholder: str = "Sélectionner…", parent=None):
        super().__init__(parent)
        self._placeholder = placeholder
        self._items: list[dict] = []   # {"label": str, "data": any, "checked": bool}
        self._popup: QFrame | None = None

        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # ── Bouton principal ────────────────────────────────────────────
        self._button = QPushButton(self._placeholder)
        self._button.setCheckable(False)
        self._button.setCursor(QCursor(Qt.PointingHandCursor))
        self._button.setStyleSheet(self._button_style())
        self._button.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self._button.setFixedHeight(38)
        self._button.clicked.connect(self._toggle_popup)

        layout.addWidget(self._button)

    # ------------------------------------------------------------------ #
    #  API publique                                                        #
    # ------------------------------------------------------------------ #
    def addItem(self, label: str, data=None, checked: bool = False):
        """Ajoute une option au menu."""
        self._items.append({"label": label, "data": data if data is not None else label, "checked": checked})
        self._update_button_text()

    def addItems(self, labels: list[str]):
        """Ajoute plusieurs options d'un coup (sans data personnalisée)."""
        for lbl in labels:
            self.addItem(lbl)

    def selectedData(self) -> list:
        """Retourne la liste des `data` des éléments cochés."""
        return [item["data"] for item in self._items if item["checked"]]

    def selectedLabels(self) -> list[str]:
        """Retourne la liste des labels des éléments cochés."""
        return [item["label"] for item in self._items if item["checked"]]

    def setChecked(self, data, checked: bool = True):
        """Coche ou décoche un élément par sa valeur `data`."""
        for item in self._items:
            if item["data"] == data:
                item["checked"] = checked
        self._update_button_text()

    def clearSelection(self):
        """Décoche tous les éléments."""
        for item in self._items:
            item["checked"] = False
        self._update_button_text()
        self.selectionChanged.emit([])

    def clear(self):
        """Supprime tous les éléments."""
        self._items.clear()
        self._update_button_text()
        self.selectionChanged.emit([])

    # ------------------------------------------------------------------ #
    #  Popup                                                               #
    # ------------------------------------------------------------------ #
    def _toggle_popup(self):
        if self._popup and self._popup.isVisible():
            self._popup.hide()
        else:
            self._show_popup()

    def _show_popup(self):
        # Crée (ou recrée) la popup
        if self._popup:
            self._popup.deleteLater()

        popup = QFrame(self.window(), Qt.Popup | Qt.FramelessWindowHint)
        popup.setStyleSheet(self._popup_style())
        popup.setMinimumWidth(self.width())

        outer = QVBoxLayout(popup)
        outer.setContentsMargins(6, 6, 6, 6)
        outer.setSpacing(2)

        # ── "Tout sélectionner" ─────────────────────────────────────────
        select_all = QCheckBox("Tout sélectionner")
        select_all.setStyleSheet(self._checkbox_style(bold=True))
        all_checked = all(i["checked"] for i in self._items) if self._items else False
        select_all.setChecked(all_checked)
        select_all.stateChanged.connect(lambda state: self._on_select_all(state, popup))
        outer.addWidget(select_all)

        # ── Barre de recherche ──────────────────────────────────────────
        search = QLineEdit()
        search.setPlaceholderText("Rechercher…")
        search.setClearButtonEnabled(True)
        search.setStyleSheet(self._search_style())
        outer.addWidget(search)

        # Séparateur
        sep = QFrame()
        sep.setFrameShape(QFrame.HLine)
        sep.setStyleSheet("color: #dde1e8;")
        outer.addWidget(sep)

        # ── Liste défilante ─────────────────────────────────────────────
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll.setStyleSheet("background: transparent;")

        container = QWidget()
        container.setStyleSheet("background: transparent;")
        vbox = QVBoxLayout(container)
        vbox.setContentsMargins(0, 0, 0, 0)
        vbox.setSpacing(1)

        self._checkboxes: list[tuple[QCheckBox, dict]] = []
        for item in self._items:
            cb = QCheckBox(item["label"])
            cb.setChecked(item["checked"])
            cb.setStyleSheet(self._checkbox_style())
            cb.stateChanged.connect(
                lambda state, it=item, sa=select_all: self._on_item_toggled(state, it, sa)
            )
            vbox.addWidget(cb)
            self._checkboxes.append((cb, item))

        # ── Filtre en temps réel ─────────────────────────────────────────
        def _filter(text: str):
            term = text.strip().lower()
            any_visible = False
            for cb, _ in self._checkboxes:
                visible = term == "" or term in cb.text().lower()
                cb.setVisible(visible)
                if visible:
                    any_visible = True
            # Mise à jour de "Tout sélectionner" selon les items visibles
            visible_items = [it for cb, it in self._checkboxes if cb.isVisible()]
            all_checked_visible = bool(visible_items) and all(it["checked"] for it in visible_items)
            select_all.blockSignals(True)
            select_all.setChecked(all_checked_visible)
            select_all.blockSignals(False)

        search.textChanged.connect(_filter)

        scroll.setWidget(container)
        outer.addWidget(scroll)

        # ── Étape 1 : coordonnées écran du bouton ───────────────────────
        btn_top_g    = self._button.mapToGlobal(QPoint(0, 0))
        btn_bottom_g = self._button.mapToGlobal(QPoint(0, self._button.height()))

        # Utilise le bas de la fenêtre parente comme limite
        window      = self.window()
        win_rect    = window.frameGeometry()
        win_bottom_g = win_rect.bottom()
        win_top_g    = win_rect.top()

        space_below = win_bottom_g - btn_bottom_g.y() - 6
        space_above = btn_top_g.y() - win_top_g       - 6
        open_above  = space_below < space_above

        # Hauteur initiale généreuse pour le premier rendu
        row_h        = 30
        ideal_scroll = min(len(self._items), 8) * row_h
        scroll.setFixedHeight(ideal_scroll)

        # ── Étape 2 : rendu hors-écran pour mesurer les dimensions réelles
        popup.setMinimumWidth(self.width())
        popup.move(-32000, -32000)
        popup.show()
        QApplication.processEvents()   # force le calcul du layout

        # Hauteur réelle de la partie fixe (header + marges + séparateur)
        real_fixed  = popup.height() - scroll.height()
        space_avail = (space_above if open_above else space_below)

        # ── Étape 3 : ajuste la scrollarea à l'espace réellement disponible
        max_scroll = max(space_avail - real_fixed, row_h)
        final_scroll_h = min(ideal_scroll, max_scroll)
        scroll.setFixedHeight(int(final_scroll_h))
        QApplication.processEvents()

        # ── Étape 4 : positionnement final ──────────────────────────────
        popup_h = popup.height()
        popup_w = popup.width()

        if open_above:
            pos = QPoint(btn_top_g.x(), btn_top_g.y() - popup_h)
        else:
            pos = QPoint(btn_bottom_g.x(), btn_bottom_g.y())

        # Recale si ça dépasse à droite de la fenêtre
        win_right = window.frameGeometry().right()
        if pos.x() + popup_w > win_right:
            pos.setX(win_right - popup_w - 4)

        popup.move(pos)
        popup.setFocus()
        self._popup = popup

    def _on_item_toggled(self, state, item: dict, select_all_cb: QCheckBox):
        item["checked"] = state == Qt.Checked.value if isinstance(state, int) else bool(state)
        # Met à jour "Tout sélectionner" sans déclencher sa cascade
        all_checked = all(i["checked"] for i in self._items)
        select_all_cb.blockSignals(True)
        select_all_cb.setChecked(all_checked)
        select_all_cb.blockSignals(False)
        self._update_button_text()
        self.selectionChanged.emit(self.selectedData())

    def _on_select_all(self, state, popup):
        checked = state == Qt.Checked.value if isinstance(state, int) else bool(state)
        # Ne coche/décoche que les items visibles (filtrés)
        for cb, item in self._checkboxes:
            if cb.isVisible():
                item["checked"] = checked
                cb.blockSignals(True)
                cb.setChecked(checked)
                cb.blockSignals(False)
        self._update_button_text()
        self.selectionChanged.emit(self.selectedData())

    # ------------------------------------------------------------------ #
    #  Texte du bouton                                                     #
    # ------------------------------------------------------------------ #
    def _update_button_text(self):
        selected = self.selectedLabels()
        if not selected:
            self._button.setText(self._placeholder)
        elif len(selected) == len(self._items):
            self._button.setText("Tous sélectionnés")
        elif len(selected) <= 2:
            self._button.setText(", ".join(selected))
        else:
            self._button.setText(f"{selected[0]}, {selected[1]} +{len(selected) - 2}")

    # ------------------------------------------------------------------ #
    #  Styles                                                              #
    # ------------------------------------------------------------------ #
    @staticmethod
    def _button_style() -> str:
        return """
            QPushButton {
                background-color: #ffffff;
                border: 1.5px solid #c8cdd8;
                border-radius: 8px;
                padding: 0 14px 0 12px;
                text-align: left;
                font-size: 13px;
                color: #3a3f52;
            }
            QPushButton:hover {
                border-color: #6c7ae0;
                background-color: #f7f8ff;
            }
            QPushButton:pressed {
                background-color: #eef0ff;
            }
        """

    @staticmethod
    def _popup_style() -> str:
        return """
            QFrame {
                background-color: #ffffff;
                border: 1.5px solid #dde1ee;
                border-radius: 10px;
                padding: 2px;
            }
            QScrollBar:vertical {
                width: 6px;
                background: transparent;
            }
            QScrollBar::handle:vertical {
                background: #c8cdd8;
                border-radius: 3px;
            }
        """

    @staticmethod
    def _search_style() -> str:
        return """
            QLineEdit {
                background-color: #f5f6fa;
                border: 1.5px solid #e0e3ee;
                border-radius: 6px;
                padding: 5px 10px;
                font-size: 12px;
                color: #3a3f52;
            }
            QLineEdit:focus {
                border-color: #6c7ae0;
                background-color: #ffffff;
            }
            QLineEdit::placeholder {
                color: #aab0c8;
            }
        """

    @staticmethod
    def _checkbox_style(bold: bool = False) -> str:
        weight = "600" if bold else "400"
        return f"""
            QCheckBox {{
                font-size: 13px;
                font-weight: {weight};
                color: #3a3f52;
                padding: 4px 6px;
                border-radius: 6px;
                spacing: 8px;
            }}
            QCheckBox:hover {{
                background-color: #f0f2ff;
            }}
            QCheckBox::indicator {{
                width: 16px;
                height: 16px;
                border-radius: 4px;
                border: 1.5px solid #c8cdd8;
                background: white;
            }}
            QCheckBox::indicator:checked {{
                background-color: #6c7ae0;
                border-color: #6c7ae0;
                image: url(data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMTIiIGhlaWdodD0iMTIiIHZpZXdCb3g9IjAgMCAxMiAxMiIgZmlsbD0ibm9uZSIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj48cGF0aCBkPSJNMiA2TDUgOUwxMCAzIiBzdHJva2U9IndoaXRlIiBzdHJva2Utd2lkdGg9IjEuOCIgc3Ryb2tlLWxpbmVjYXA9InJvdW5kIiBzdHJva2UtbGluZWpvaW49InJvdW5kIi8+PC9zdmc+);
            }}
            QCheckBox::indicator:hover {{
                border-color: #6c7ae0;
            }}
        """


# ====================================================================== #
#  Démo complète                                                          #
# ====================================================================== #
class DemoWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("CheckableComboBox — Démo")
        self.setMinimumWidth(420)

        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)
        layout.setContentsMargins(32, 32, 32, 32)
        layout.setSpacing(20)

        layout.addWidget(QLabel("<b>Filtres produits</b>", styleSheet="font-size:16px; color:#3a3f52;"))

        # ── Filtre Marques ──────────────────────────────────────────────
        layout.addWidget(QLabel("Marque", styleSheet="font-size:12px; color:#7a8099;"))
        self.combo_marques = CheckableComboBox("Toutes les marques")
        for brand in ["Yamaha", "Philips", "Sony", "Samsung", "Bose", "JBL", "Sennheiser"]:
            self.combo_marques.addItem(brand, data=brand.lower())
        self.combo_marques.selectionChanged.connect(self._on_change)
        layout.addWidget(self.combo_marques)

        # ── Filtre Catégories ───────────────────────────────────────────
        layout.addWidget(QLabel("Catégorie", styleSheet="font-size:12px; color:#7a8099;"))
        self.combo_cats = CheckableComboBox("Toutes les catégories")
        self.combo_cats.addItems(["Casques audio", "Enceintes", "Home cinéma", "Moniteurs studio", "Écouteurs"])
        layout.addWidget(self.combo_cats)

        # ── Résultat ────────────────────────────────────────────────────
        self._result_label = QLabel("Aucune marque sélectionnée.")
        self._result_label.setWordWrap(True)
        self._result_label.setStyleSheet(
            "background:#f5f6fa; border-radius:8px; padding:10px 14px; "
            "font-size:12px; color:#5a6080;"
        )
        layout.addWidget(self._result_label)
        layout.addStretch()

        self.setStyleSheet("QMainWindow { background: #f8f9fc; } QWidget { background: #f8f9fc; }")

    def _on_change(self, values: list):
        if values:
            self._result_label.setText(f"Marques sélectionnées : {', '.join(values)}")
        else:
            self._result_label.setText("Aucune marque sélectionnée.")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    win = DemoWindow()
    win.show()
    sys.exit(app.exec())
