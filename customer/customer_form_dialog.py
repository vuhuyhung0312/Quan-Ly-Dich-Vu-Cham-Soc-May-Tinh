"""CustomerFormDialog — Popup Thêm / Chỉnh sửa khách hàng."""
from __future__ import annotations
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout,
    QLabel, QLineEdit, QTextEdit, QPushButton, QFrame,
)
from config.settings import (
    BG_APP, BG_SURFACE, FG_PRIMARY, FG_MUTED, COLOR_BORDER,
    COLOR_TEAL, COLOR_TEAL_PALE, COLOR_DANGER, COLOR_DANGER_BG,
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
    QPushButton#saveBtn:disabled {{ background: #A7F3D0; }}
"""


class CustomerFormDialog(QDialog):
    """
    Mode: edit_data=None → Thêm mới
          edit_data={...}  → Chỉnh sửa
    """

    def __init__(
        self,
        parent=None,
        edit_data: dict | None = None,
    ) -> None:
        super().__init__(parent)
        self._is_edit = edit_data is not None
        self._edit    = edit_data or {}
        title = "✏️  Chỉnh sửa khách hàng" if self._is_edit else "➕  Thêm khách hàng mới"
        self.setWindowTitle(title)
        self.setModal(True)
        self.setFixedWidth(540)
        self.setStyleSheet(_QSS)
        self._build_ui()
        if self._is_edit:
            self._fill_data()

    # ── Build ────────────────────────────────────────────────────────────────

    def _build_ui(self) -> None:
        root = QVBoxLayout(self)
        root.setContentsMargins(20, 20, 20, 20)

        card = QFrame(); card.setObjectName("card")
        cl = QVBoxLayout(card)
        cl.setContentsMargins(28, 24, 28, 24)
        cl.setSpacing(16)

        # Title
        title_row = QHBoxLayout()
        icon = QLabel("👥"); icon.setStyleSheet("font-size: 22px;")
        lbl  = QLabel("Chỉnh sửa khách hàng" if self._is_edit else "Khách hàng mới")
        lbl.setObjectName("dialogTitle")
        title_row.addWidget(icon); title_row.addWidget(lbl, 1)
        cl.addLayout(title_row)
        cl.addWidget(_sep())

        # Form
        form = QFormLayout()
        form.setSpacing(14)
        form.setLabelAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        form.setFieldGrowthPolicy(QFormLayout.FieldGrowthPolicy.ExpandingFieldsGrow)

        def L(text): 
            l = QLabel(text); l.setObjectName("fieldLabel"); return l

        self._inp_name    = QLineEdit(); self._inp_name.setPlaceholderText("vd: Nguyễn Thị Hoa"); self._inp_name.setMaxLength(100)
        self._inp_phone   = QLineEdit(); self._inp_phone.setPlaceholderText("vd: 0901234567")    ; self._inp_phone.setMaxLength(15)
        self._inp_email   = QLineEdit(); self._inp_email.setPlaceholderText("vd: email@gmail.com (tuỳ chọn)"); self._inp_email.setMaxLength(100)
        self._inp_address = QLineEdit(); self._inp_address.setPlaceholderText("Địa chỉ (tuỳ chọn)"); self._inp_address.setMaxLength(200)
        self._inp_note    = QTextEdit()
        self._inp_note.setPlaceholderText("Ghi chú thêm về khách hàng (tuỳ chọn)...")
        self._inp_note.setFixedHeight(72)

        form.addRow(L("Họ và tên *"),    self._inp_name)
        form.addRow(L("Số điện thoại *"), self._inp_phone)
        form.addRow(L("Email"),           self._inp_email)
        form.addRow(L("Địa chỉ"),        self._inp_address)
        form.addRow(L("Ghi chú"),         self._inp_note)

        hint = QLabel("(*) Bắt buộc. SĐT không được trùng với khách hàng khác.")
        hint.setObjectName("hintLabel")

        cl.addLayout(form)
        cl.addWidget(hint)

        # Error
        self._lbl_error = QLabel()
        self._lbl_error.setObjectName("errorLabel")
        self._lbl_error.setWordWrap(True)
        self._lbl_error.setVisible(False)
        cl.addWidget(self._lbl_error)

        cl.addWidget(_sep())

        # Buttons
        btn_row = QHBoxLayout(); btn_row.addStretch()

        btn_cancel = QPushButton("Hủy bỏ"); btn_cancel.setObjectName("cancelBtn")
        btn_cancel.setFixedHeight(38); btn_cancel.setMinimumWidth(100)
        btn_cancel.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_cancel.clicked.connect(self.reject)

        self._btn_save = QPushButton(
            "💾  Lưu lại" if self._is_edit else "✅  Thêm khách hàng"
        )
        self._btn_save.setObjectName("saveBtn")
        self._btn_save.setFixedHeight(38); self._btn_save.setMinimumWidth(150)
        self._btn_save.setCursor(Qt.CursorShape.PointingHandCursor)
        self._btn_save.clicked.connect(self._on_save)

        btn_row.addWidget(btn_cancel); btn_row.addSpacing(8); btn_row.addWidget(self._btn_save)
        cl.addLayout(btn_row)
        root.addWidget(card)

    def _fill_data(self) -> None:
        self._inp_name.setText(self._edit.get("full_name", ""))
        self._inp_phone.setText(self._edit.get("phone", ""))
        self._inp_email.setText(self._edit.get("email", "") or "")
        self._inp_address.setText(self._edit.get("address", "") or "")
        self._inp_note.setPlainText(self._edit.get("note", "") or "")

    # ── Validate phía UI ─────────────────────────────────────────────────────

    def _on_save(self) -> None:
        self.clear_error()
        if not self._inp_name.text().strip():
            self.show_error("Họ và tên không được để trống.")
            self._inp_name.setFocus(); return
        if not self._inp_phone.text().strip():
            self.show_error("Số điện thoại không được để trống.")
            self._inp_phone.setFocus(); return
        self.accept()

    def show_error(self, msg: str) -> None:
        self._lbl_error.setText("⚠  " + msg); self._lbl_error.setVisible(True)

    def clear_error(self) -> None:
        self._lbl_error.setVisible(False)

    # ── Getters ──────────────────────────────────────────────────────────────

    def get_full_name(self) -> str: return self._inp_name.text().strip()
    def get_phone(self)     -> str: return self._inp_phone.text().strip()
    def get_email(self)     -> str: return self._inp_email.text().strip()
    def get_address(self)   -> str: return self._inp_address.text().strip()
    def get_note(self)      -> str: return self._inp_note.toPlainText().strip()


# Helpers
def _sep() -> QFrame:
    f = QFrame(); f.setFixedHeight(1)
    f.setStyleSheet(f"background: {COLOR_BORDER}; border: none;")
    return f
