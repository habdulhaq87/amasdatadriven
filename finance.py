import sys
import pandas as pd
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QTableView, QApplication,
    QMessageBox, QPushButton, QHBoxLayout, QCheckBox, QTabWidget, QComboBox, QLineEdit, QDateEdit
)
from PyQt5.QtCore import Qt, QDate, QAbstractTableModel, QVariant
from db_handler import DatabaseManager  # Use your actual import

class PandasModel(QAbstractTableModel):
    def __init__(self, df=pd.DataFrame()):
        super().__init__()
        self._df = df.copy()
        self._headers = list(self._df.columns)

    def setDataFrame(self, df):
        self.beginResetModel()
        self._df = df.copy()
        self._headers = list(self._df.columns)
        self.endResetModel()

    def rowCount(self, parent=None):
        return len(self._df)

    def columnCount(self, parent=None):
        return len(self._df.columns)

    def data(self, index, role=Qt.DisplayRole):
        if not index.isValid():
            return QVariant()
        value = self._df.iloc[index.row(), index.column()]
        if role == Qt.DisplayRole:
            if isinstance(value, float):
                # Format Total Price
                if self._headers[index.column()] == "Total Price":
                    return f"{value:,.2f}"
                else:
                    return f"{value:,.2f}" if abs(value) > 1000 else str(value)
            return str(value)
        return QVariant()

    def headerData(self, section, orientation, role=Qt.DisplayRole):
        if role == Qt.DisplayRole:
            if orientation == Qt.Horizontal:
                return self._headers[section]
            else:
                return section + 1
        return QVariant()

    def flags(self, index):
        return Qt.ItemIsEnabled | Qt.ItemIsSelectable

class InventoryTab(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Inventory Overview")
        self.db = DatabaseManager()
        self.inventory_df = pd.DataFrame()
        self.supplier_df = pd.DataFrame()
        self.setLayout(QVBoxLayout())

        self.tabs = QTabWidget()
        self.layout().addWidget(self.tabs)

        # Main inventory tab
        self.main_widget = QWidget()
        self.main_layout = QVBoxLayout(self.main_widget)
        self._build_main_tab()
        self.tabs.addTab(self.main_widget, "All Inventory")

        # By supplier tab
        self.supplier_widget = QWidget()
        self.supplier_layout = QVBoxLayout(self.supplier_widget)
        self._build_supplier_tab()
        self.tabs.addTab(self.supplier_widget, "By Supplier")

        self.load_inventory()

    # -------- Main Inventory Tab --------

    def _build_main_tab(self):
        main_layout = self.main_layout

        self.total_label = QLabel("")
        self.total_label.setStyleSheet("font-size:1.4rem;font-weight:700;color:#2563eb;margin-bottom:12px;")
        main_layout.addWidget(self.total_label)

        btn_box = QHBoxLayout()
        self.all_date_filter_checkbox = QCheckBox("Enable date filter")
        self.all_date_filter_checkbox.setChecked(True)
        self.all_date_filter_checkbox.stateChanged.connect(self.update_table)
        btn_box.addWidget(self.all_date_filter_checkbox)

        btn_box.addWidget(QLabel("From:"))
        self.all_from_date = QDateEdit()
        self.all_from_date.setDisplayFormat("yyyy-MM-dd")
        self.all_from_date.setCalendarPopup(True)
        one_month_ago = QDate.currentDate().addMonths(-1)
        self.all_from_date.setDate(one_month_ago)
        self.all_from_date.setSpecialValueText("")
        btn_box.addWidget(self.all_from_date)
        btn_box.addWidget(QLabel("To:"))
        self.all_to_date = QDateEdit()
        self.all_to_date.setDisplayFormat("yyyy-MM-dd")
        self.all_to_date.setCalendarPopup(True)
        self.all_to_date.setDate(QDate.currentDate())
        self.all_to_date.setSpecialValueText("")
        btn_box.addWidget(self.all_to_date)

        self.sort_checkbox = QCheckBox("Sort by value: highest first")
        self.sort_checkbox.stateChanged.connect(self.update_table)
        btn_box.addWidget(self.sort_checkbox)

        self.refresh_btn = QPushButton("Refresh")
        self.refresh_btn.clicked.connect(self.load_inventory)
        btn_box.addWidget(self.refresh_btn)
        btn_box.addStretch()
        main_layout.addLayout(btn_box)

        # QTableView + PandasModel for main table
        self.table = QTableView()
        self.table.setSortingEnabled(False)
        self.model = PandasModel(pd.DataFrame())
        self.table.setModel(self.model)
        self.table.horizontalHeader().setStretchLastSection(True)
        main_layout.addWidget(self.table)

        self.all_from_date.dateChanged.connect(self.update_table)
        self.all_to_date.dateChanged.connect(self.update_table)

    # -------- By Supplier Tab --------

    def _build_supplier_tab(self):
        supplier_layout = self.supplier_layout

        sup_box = QHBoxLayout()
        sup_box.addWidget(QLabel("Supplier:"))
        self.supplier_combo = QComboBox()
        self.supplier_combo.currentIndexChanged.connect(self.update_supplier_table)
        sup_box.addWidget(self.supplier_combo)
        sup_box.addWidget(QLabel("or Type:"))
        self.supplier_search = QLineEdit()
        self.supplier_search.setPlaceholderText("Type supplier name...")
        sup_box.addWidget(self.supplier_search)

        self.supplier_date_filter_checkbox = QCheckBox("Enable date filter")
        self.supplier_date_filter_checkbox.setChecked(True)
        self.supplier_date_filter_checkbox.stateChanged.connect(self.update_supplier_table)
        sup_box.addWidget(self.supplier_date_filter_checkbox)

        sup_box.addWidget(QLabel("From:"))
        self.from_date = QDateEdit()
        self.from_date.setDisplayFormat("yyyy-MM-dd")
        self.from_date.setCalendarPopup(True)
        one_month_ago = QDate.currentDate().addMonths(-1)
        self.from_date.setDate(one_month_ago)
        self.from_date.setSpecialValueText("")
        sup_box.addWidget(self.from_date)
        sup_box.addWidget(QLabel("To:"))
        self.to_date = QDateEdit()
        self.to_date.setDisplayFormat("yyyy-MM-dd")
        self.to_date.setCalendarPopup(True)
        self.to_date.setDate(QDate.currentDate())
        self.to_date.setSpecialValueText("")
        sup_box.addWidget(self.to_date)
        sup_box.addStretch()
        supplier_layout.addLayout(sup_box)

        self.supplier_total_label = QLabel("")
        self.supplier_total_label.setStyleSheet("font-size:1.2rem;font-weight:700;color:#059669;margin-bottom:10px;")
        supplier_layout.addWidget(self.supplier_total_label)

        # QTableView + PandasModel for supplier table
        self.supplier_table = QTableView()
        self.supplier_model = PandasModel(pd.DataFrame())
        self.supplier_table.setModel(self.supplier_model)
        self.supplier_table.horizontalHeader().setStretchLastSection(True)
        supplier_layout.addWidget(self.supplier_table)

        self.supplier_search.textChanged.connect(self._on_supplier_search_changed)
        self.from_date.dateChanged.connect(self.update_supplier_table)
        self.to_date.dateChanged.connect(self.update_supplier_table)

    # -------- Inventory Data --------

    def load_inventory(self):
        try:
            sql = """
                SELECT inv.batchid, inv.itemid, inv.quantity, inv.expirationdate, inv.storagelocation,
                       inv.datereceived, inv.lastupdated, inv.cost_per_unit, inv.poid, inv.costid,
                       s.suppliername AS supplier
                FROM inventory inv
                LEFT JOIN itemsupplier its ON inv.itemid = its.itemid
                LEFT JOIN supplier s ON its.supplierid = s.supplierid
                ORDER BY inv.batchid
            """
            df = self.db.fetch_data(sql)
        except Exception as e:
            QMessageBox.critical(self, "DB error", str(e))
            self.inventory_df = pd.DataFrame()
            self.supplier_df = pd.DataFrame()
            self.update_table()
            self.update_supplier_table()
            return

        if df.empty:
            self.inventory_df = pd.DataFrame()
            self.supplier_df = pd.DataFrame()
            self.update_table()
            self.update_supplier_table()
            return

        df["Total Price"] = df["quantity"] * df["cost_per_unit"]

        for dcol in ["datereceived", "expirationdate", "lastupdated"]:
            if dcol in df.columns:
                df[dcol] = pd.to_datetime(df[dcol], errors="coerce").dt.date

        self.inventory_df = df

        supplier_df = pd.DataFrame(df["supplier"].dropna().unique(), columns=["supplier"])
        supplier_df = supplier_df.sort_values("supplier").reset_index(drop=True)
        self.supplier_df = supplier_df

        self._update_supplier_combo_and_table()
        self.update_table()
        self.update_supplier_table()

    # -------- Table Updates --------

    def update_table(self):
        df = self.inventory_df.copy()
        if df.empty:
            self.model.setDataFrame(pd.DataFrame([["No inventory found."]], columns=["Info"]))
            self.total_label.setText("Total Inventory Value: 0")
            return

        # Date filter
        if self.all_date_filter_checkbox.isChecked():
            from_dt = self.all_from_date.date()
            to_dt = self.all_to_date.date()
            use_from = from_dt.isValid()
            use_to = to_dt.isValid()
            if use_from and use_to:
                df = df[(df["datereceived"] >= from_dt.toPyDate()) & (df["datereceived"] <= to_dt.toPyDate())]
            elif use_from:
                df = df[df["datereceived"] >= from_dt.toPyDate()]
            elif use_to:
                df = df[df["datereceived"] <= to_dt.toPyDate()]

        if self.sort_checkbox.isChecked():
            df = df.sort_values("Total Price", ascending=False)
        else:
            df = df.sort_values("batchid")

        cols = list(df.columns)
        if "supplier" in cols:
            cols.remove("supplier")
            cols.insert(2, "supplier")

        df = df[cols]
        self.model.setDataFrame(df)
        self.table.resizeColumnsToContents()
        total_sum = df["Total Price"].sum() if "Total Price" in df.columns else 0
        self.total_label.setText(
            f"💰 Total Inventory Value: <span style='color:#059669'>{total_sum:,.2f}</span>"
        )

    def update_supplier_table(self):
        supplier = self.supplier_combo.currentData()
        df = self.inventory_df.copy()

        if self.supplier_date_filter_checkbox.isChecked():
            from_dt = self.from_date.date()
            to_dt = self.to_date.date()
            use_from = from_dt.isValid()
            use_to = to_dt.isValid()
            if use_from and use_to:
                df = df[(df["datereceived"] >= from_dt.toPyDate()) & (df["datereceived"] <= to_dt.toPyDate())]
            elif use_from:
                df = df[df["datereceived"] >= from_dt.toPyDate()]
            elif use_to:
                df = df[df["datereceived"] <= to_dt.toPyDate()]

        if supplier:
            df = df[df["supplier"] == supplier]

        if df.empty:
            info_text = "Select a supplier to view details." if not supplier else "No inventory for this supplier/dates."
            self.supplier_model.setDataFrame(pd.DataFrame([[info_text]], columns=["Info"]))
            self.supplier_total_label.setText("")
            return

        cols = list(df.columns)
        if "supplier" in cols:
            cols.remove("supplier")
            cols.insert(2, "supplier")

        df = df[cols]
        self.supplier_model.setDataFrame(df)
        self.supplier_table.resizeColumnsToContents()
        total_sum = df["Total Price"].sum() if "Total Price" in df.columns else 0
        self.supplier_total_label.setText(
            f"Supplier Inventory Value: <span style='color:#059669'>{total_sum:,.2f}</span>"
        )

    def _on_supplier_search_changed(self, text):
        text = text.strip().lower()
        if text:
            matches = self.supplier_df[self.supplier_df["supplier"].str.lower().str.contains(text)]
        else:
            matches = self.supplier_df
        self._update_supplier_combo_and_table(matches)

    def _update_supplier_combo_and_table(self, matches_df=None):
        if matches_df is None:
            matches_df = self.supplier_df

        self.supplier_combo.blockSignals(True)
        self.supplier_combo.clear()
        self.supplier_combo.addItem("Select supplier...", None)
        for sup in matches_df["supplier"]:
            self.supplier_combo.addItem(sup, sup)
        self.supplier_combo.blockSignals(False)

        if len(matches_df) > 0:
            self.supplier_combo.setCurrentIndex(1)
        else:
            self.supplier_combo.setCurrentIndex(0)
        self.update_supplier_table()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    w = InventoryTab()
    w.resize(1300, 650)
    w.show()
    sys.exit(app.exec_())
