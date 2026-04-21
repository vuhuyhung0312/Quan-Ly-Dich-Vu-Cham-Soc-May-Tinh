"""ServiceTypeFormDialog — Popup Thêm / Chỉnh sửa loại dịch vụ."""
from __future__ import annotations
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout,
    QLabel, QLineEdit, QTextEdit, QPushButton, QFrame,
)
from config.settings import (
    BG_APP, BG_SURFACE, FG_PRIMARY, FG_MUTED, COLOR_BORDER,
    COLOR_TEAL, COLOR_DANGER, COLOR_DANGER_BG,
    FORM_INPUT_BG, FORM_INPUT_FG, FORM_INPUT_PLACEHOLDER,
)

_QSS = f"""
    QDialog {{ background: {BG_APP}; }}
    QFrame#card {{
        background: {BG_SURFACE};
        border: 1px solid {COLOR_BORDER};
        border-radius: 14px;
    }}
    QLabel {{ background: transparent; border: none; }}
    QLabel#dialogTitle {{ font-size: 17px; font-weight: 800; color: {FG_PRIMARY}; }}
    QLabel#fieldLabel  {{ font-size: 13px; font-weight: 600; color: {FG_PRIMARY}; }}
    QLabel#hintLabel   {{ font-size: 11px; color: {FG_MUTED}; }}
    QLabel#errorLabel {{
        font-size: 12px; color: {COLOR_DANGER};
        background: {COLOR_DANGER_BG};
        border: 1px solid #FECACA; border-radius: 8px;
        padding: 8px 12px;
    }}
    QLineEdit, QTextEdit {{
        background: {FORM_INPUT_BG}; color: {FORM_INPUT_FG};
        border: 1px solid {COLOR_BORDER};
        border-radius: 8px; padding: 8px 12px; font-size: 13px;
    }}
    QLineEdit:focus, QTextEdit:focus {{ border: 1.5px solid {COLOR_TEAL}; }}
    QLineEdit::placeholder {{ color: {FORM_INPUT_PLACEHOLDER}; }}
    QPushButton#cancelBtn {{
        background: white; color: {FG_MUTED};
        border: 1px solid {COLOR_BORDER}; border-radius: 8px;
        font-size: 13px; font-weight: 600;
    }}
    QPushButton#cancelBtn:hover {{ background: #F1F5F9; }}
    QPushButton#saveBtn {{
        background: {COLOR_TEAL}; color: white;
        border: none; border-radius: 8px;
        font-size: 13px; font-weight: 700;
    }}
    QPushButton#saveBtn:hover {{ background: #0D9488; }}
"""


class ServiceTypeFormDialog(QDialog):
    """
    Popup Thêm / Sửa Loại Dịch Vụ.
    edit_data = None → Thêm mới
    """
    def __init__(self, parent=None, edit_data: dict | None = None) -> None:
        super().__init__(parent)
        self._is_edit = edit_data is not None
        self._edit = edit_data or {}
        title = "✏️  Chỉnh sửa loại dịch vụ" if self._is_edit else "➕  Thêm loại dịch vụ mới"
        self.setWindowTitle(title)
        self.setModal(True)
        self.setFixedWidth(460)
        self.setStyleSheet(_QSS)
        self._build_ui()
        if self._is_edit:
            self._fill_data()

    def _build_ui(self) -> None:
        root = QVBoxLayout(self)
        root.setContentsMargins(20, 20, 20, 20)

        card = QFrame(); card.setObjectName("card")
        cl = QVBoxLayout(card)
        cl.setContentsMargins(28, 24, 28, 24)
        cl.setSpacing(16)

        title_row = QHBoxLayout()
        icon = QLabel("🛠"); icon.setStyleSheet("font-size: 22px;")
        lbl  = QLabel("Chỉnh sửa dịch vụ" if self._is_edit else "Dịch vụ mới")
        lbl.setObjectName("dialogTitle")
        title_row.addWidget(icon); title_row.addWidget(lbl, 1)
        cl.addLayout(title_row)

        sep = QFrame(); sep.setFixedHeight(1); sep.setStyleSheet(f"background: {COLOR_BORDER}; border: none;")
        cl.addWidget(sep)

        form = QFormLayout()
        form.setSpacing(14)
        form.setLabelAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        form.setFieldGrowthPolicy(QFormLayout.FieldGrowthPolicy.ExpandingFieldsGrow)

        def L(text): 
            l = QLabel(text); l.setObjectName("fieldLabel"); return l

        self._inp_name = QLineEdit()
        self._inp_name.setPlaceholderText("Ví dụ: Vệ sinh laptop")
        self._inp_name.setMaxLength(100)

        self._inp_price = QLineEdit()
        self._inp_price.setPlaceholderText("Ví dụ: 150000")
        self._inp_price.setMaxLength(15)

        self._inp_desc = QTextEdit()
        self._inp_desc.setPlaceholderText("Mô tả chi tiết hạng mục dịch vụ này...")
        self._inp_desc.setFixedHeight(80)

        form.addRow(L("Tên dịch vụ *"), self._inp_name)
        form.addRow(L("Giá cơ bản (VNĐ) *"), self._inp_price)
        form.addRow(L("Mô tả"), self._inp_desc)

        cl.addLayout(form)

        hint = QLabel("(*) Bắt buộc. Tên dịch vụ phải là duy nhất.")
        hint.setObjectName("hintLabel")
        cl.addWidget(hint)

        self._lbl_error = QLabel()
        self._lbl_error.setObjectName("errorLabel")
        self._lbl_error.setWordWrap(True)
        self._lbl_error.setVisible(False)
        cl.addWidget(self._lbl_error)

        sep2 = QFrame(); sep2.setFixedHeight(1); sep2.setStyleSheet(f"background: {COLOR_BORDER}; border: none;")
        cl.addWidget(sep2)

        btn_row = QHBoxLayout(); btn_row.addStretch()
        btn_cancel = QPushButton("Hủy bỏ"); btn_cancel.setObjectName("cancelBtn")
        btn_cancel.setFixedHeight(38); btn_cancel.setMinimumWidth(100)
        btn_cancel.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_cancel.clicked.connect(self.reject)

        self._btn_save = QPushButton("💾  Lưu lại" if self._is_edit else "✅  Khởi tạo")
        self._btn_save.setObjectName("saveBtn")
        self._btn_save.setFixedHeight(38); self._btn_save.setMinimumWidth(140)
        self._btn_save.setCursor(Qt.CursorShape.PointingHandCursor)
        self._btn_save.clicked.connect(self._on_save)

        btn_row.addWidget(btn_cancel); btn_row.addSpacing(8); btn_row.addWidget(self._btn_save)
        cl.addLayout(btn_row)
        root.addWidget(card)

    def _fill_data(self) -> None:
        self._inp_name.setText(self._edit.get("name", ""))
        self._inp_price.setText(str(self._edit.get("base_price", "")))
        self._inp_desc.setPlainText(self._edit.get("description", "") or "")

    def _on_save(self) -> None:
        self.clear_error()
        if not self._inp_name.text().strip():
            self.show_error("Vui lòng nhập tên dịch vụ.")
            self._inp_name.setFocus()
            return
        
        price_text = self._inp_price.text().strip().replace(",", "").replace(".", "")
        if not price_text:
            self.show_error("Vui lòng nhập giá tham khảo.")
            self._inp_price.setFocus()
            return

        try:
            p = int(price_text)
            if p < 0: raise ValueError
        except ValueError:
            self.show_error("Giá tham khảo phải là số nguyên lớn hơn hoặc bằng 0.")
            self._inp_price.selectAll()
            self._inp_price.setFocus()
            return

        self.accept()

    def show_error(self, msg: str) -> None:
        self._lbl_error.setText("⚠  " + msg); self._lbl_error.setVisible(True)

    def clear_error(self) -> None:
        self._lbl_error.setVisible(False)

    def get_name(self) -> str: return self._inp_name.text().strip()
    def get_base_price(self) -> int: 
        try:
            return int(self._inp_price.text().strip().replace(",", "").replace(".", ""))
        except ValueError:
            return 0
    def get_description(self) -> str: return self._inp_desc.toPlainText().strip()
