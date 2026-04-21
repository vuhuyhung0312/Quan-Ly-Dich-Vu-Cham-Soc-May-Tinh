"""UserFormDialog — Popup thêm / chỉnh sửa nhân viên."""
from __future__ import annotations
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout,
    QLabel, QLineEdit, QPushButton, QComboBox,
    QFrame, QCheckBox,
)
from config.settings import (
    BG_SURFACE, BG_APP, FG_PRIMARY, FG_MUTED, COLOR_BORDER,
    COLOR_TEAL, COLOR_TEAL_PALE, COLOR_DANGER, COLOR_DANGER_BG,
    FORM_INPUT_BG, FORM_INPUT_FG, FORM_INPUT_PLACEHOLDER,
)

_STYLESHEET = f"""
    QDialog {{ background: {BG_APP}; }}
    QFrame#card {{
        background: {BG_SURFACE};
        border: 1px solid {COLOR_BORDER};
        border-radius: 14px;
    }}
    QLabel {{ background: transparent; border: none; }}
    QLabel#dialogTitle {{
        font-size: 17px; font-weight: 800; color: {FG_PRIMARY};
    }}
    QLabel#fieldLabel {{
        font-size: 13px; font-weight: 600; color: {FG_PRIMARY};
    }}
    QLabel#hintLabel {{
        font-size: 11px; color: {FG_MUTED};
    }}
    QLabel#errorLabel {{
        font-size: 12px; color: {COLOR_DANGER};
        background: {COLOR_DANGER_BG};
        border: 1px solid #FECACA;
        border-radius: 8px;
        padding: 8px 12px;
    }}
    QLineEdit {{
        background: {FORM_INPUT_BG};
        color: {FORM_INPUT_FG};
        border: 1px solid {COLOR_BORDER};
        border-radius: 8px;
        padding: 8px 12px;
        font-size: 13px;
    }}
    QLineEdit:focus {{ border: 1.5px solid {COLOR_TEAL}; }}
    QLineEdit::placeholder {{ color: {FORM_INPUT_PLACEHOLDER}; }}
    QLineEdit:disabled {{
        background: #F1F5F9; color: {FG_MUTED};
        border-color: {COLOR_BORDER};
    }}
    QComboBox {{
        background: {FORM_INPUT_BG};
        color: {FORM_INPUT_FG};
        border: 1px solid {COLOR_BORDER};
        border-radius: 8px;
        padding: 8px 12px;
        font-size: 13px;
    }}
    QComboBox:focus {{ border: 1.5px solid {COLOR_TEAL}; }}
    QComboBox::drop-down {{ border: none; width: 26px; }}
    QComboBox QAbstractItemView {{
        background: {BG_SURFACE}; color: {FG_PRIMARY};
        border: 1px solid {COLOR_BORDER};
        selection-background-color: {COLOR_TEAL_PALE};
        selection-color: {FG_PRIMARY};
        outline: none;
    }}
    QPushButton#cancelBtn {{
        background: white; color: {FG_MUTED};
        border: 1px solid {COLOR_BORDER};
        border-radius: 8px; font-size: 13px; font-weight: 600;
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


class UserFormDialog(QDialog):
    """
    Popup thêm hoặc chỉnh sửa tài khoản nhân viên.

    Mode:
    - edit_data=None  → mode Thêm mới
    - edit_data={...} → mode Sửa (username bị lock, không đổi được)
    """

    def __init__(
        self,
        parent=None,
        edit_data: dict | None = None,
    ) -> None:
        super().__init__(parent)
        self._edit = edit_data
        self._is_edit = edit_data is not None
        title = "✏️  Chỉnh sửa nhân viên" if self._is_edit else "➕  Thêm nhân viên mới"
        self.setWindowTitle(title)
        self.setModal(True)
        self.setFixedWidth(500)
        self.setStyleSheet(_STYLESHEET)
        self._build_ui()
        if self._is_edit:
            self._fill_data(edit_data)  # type: ignore[arg-type]

    # ── Build ────────────────────────────────────────────────────────────────

    def _build_ui(self) -> None:
        root = QVBoxLayout(self)
        root.setContentsMargins(20, 20, 20, 20)
        root.setSpacing(0)

        card = QFrame()
        card.setObjectName("card")
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(28, 24, 28, 24)
        card_layout.setSpacing(16)

        # Title
        title_row = QHBoxLayout()
        lbl_icon  = QLabel("👤")
        lbl_icon.setStyleSheet("font-size: 22px;")
        lbl_title = QLabel(
            "Chỉnh sửa tài khoản" if self._is_edit else "Tạo tài khoản mới"
        )
        lbl_title.setObjectName("dialogTitle")
        title_row.addWidget(lbl_icon)
        title_row.addWidget(lbl_title, 1)
        card_layout.addLayout(title_row)

        # Divider
        sep = QFrame()
        sep.setFixedHeight(1)
        sep.setStyleSheet(f"background: {COLOR_BORDER}; border: none;")
        card_layout.addWidget(sep)

        # Form
        form = QFormLayout()
        form.setSpacing(14)
        form.setLabelAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        form.setFieldGrowthPolicy(QFormLayout.FieldGrowthPolicy.ExpandingFieldsGrow)

        def _lbl(text: str) -> QLabel:
            l = QLabel(text)
            l.setObjectName("fieldLabel")
            return l

        # Username
        self._inp_username = QLineEdit()
        self._inp_username.setPlaceholderText("vd: ktv_minh  (3-30 ký tự)")
        self._inp_username.setMaxLength(30)
        if self._is_edit:
            self._inp_username.setEnabled(False)
            self._inp_username.setToolTip("Tên đăng nhập không thể thay đổi sau khi tạo.")
        form.addRow(_lbl("Tên đăng nhập *"), self._inp_username)

        # Họ tên
        self._inp_fullname = QLineEdit()
        self._inp_fullname.setPlaceholderText("vd: Nguyễn Văn An")
        self._inp_fullname.setMaxLength(100)
        form.addRow(_lbl("Họ và tên *"), self._inp_fullname)

        # Vai trò
        self._cmb_role = QComboBox()
        self._cmb_role.addItem("Kỹ thuật viên (STAFF)", "STAFF")
        self._cmb_role.addItem("Quản trị viên (ADMIN)", "ADMIN")
        form.addRow(_lbl("Vai trò *"), self._cmb_role)

        card_layout.addLayout(form)

        # Password section
        pwd_sep = QFrame()
        pwd_sep.setFixedHeight(1)
        pwd_sep.setStyleSheet(f"background: {COLOR_BORDER}; border: none;")
        card_layout.addWidget(pwd_sep)

        pwd_title = QLabel(
            "🔒  Đặt lại mật khẩu" if self._is_edit else "🔒  Mật khẩu ban đầu"
        )
        pwd_title.setStyleSheet(
            f"font-size: 13px; font-weight: 700; color: {FG_PRIMARY};"
        )
        card_layout.addWidget(pwd_title)

        if self._is_edit:
            hint = QLabel("Để trống nếu không muốn thay đổi mật khẩu.")
            hint.setObjectName("hintLabel")
            card_layout.addWidget(hint)

        pwd_form = QFormLayout()
        pwd_form.setSpacing(12)
        pwd_form.setLabelAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        pwd_form.setFieldGrowthPolicy(QFormLayout.FieldGrowthPolicy.ExpandingFieldsGrow)

        self._inp_password = _PasswordField(
            placeholder="Tối thiểu 6 ký tự" if not self._is_edit else "Mật khẩu mới (tuỳ chọn)"
        )
        if not self._is_edit:
            self._inp_confirm = _PasswordField(placeholder="Nhập lại mật khẩu")
            pwd_form.addRow(_lbl("Mật khẩu *"),    self._inp_password)
            pwd_form.addRow(_lbl("Xác nhận *"),    self._inp_confirm)
        else:
            self._inp_confirm = None  # type: ignore[assignment]
            pwd_form.addRow(_lbl("Mật khẩu mới"), self._inp_password)

        card_layout.addLayout(pwd_form)

        # Error label
        self._lbl_error = QLabel()
        self._lbl_error.setObjectName("errorLabel")
        self._lbl_error.setWordWrap(True)
        self._lbl_error.setVisible(False)
        card_layout.addWidget(self._lbl_error)

        # Buttons
        sep2 = QFrame()
        sep2.setFixedHeight(1)
        sep2.setStyleSheet(f"background: {COLOR_BORDER}; border: none;")
        card_layout.addWidget(sep2)

        btn_row = QHBoxLayout()
        btn_row.addStretch()

        btn_cancel = QPushButton("Hủy bỏ")
        btn_cancel.setObjectName("cancelBtn")
        btn_cancel.setFixedHeight(38)
        btn_cancel.setMinimumWidth(100)
        btn_cancel.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_cancel.clicked.connect(self.reject)

        self._btn_save = QPushButton("💾  Lưu lại" if self._is_edit else "✅  Tạo tài khoản")
        self._btn_save.setObjectName("saveBtn")
        self._btn_save.setFixedHeight(38)
        self._btn_save.setMinimumWidth(140)
        self._btn_save.setCursor(Qt.CursorShape.PointingHandCursor)
        self._btn_save.clicked.connect(self._on_save)

        btn_row.addWidget(btn_cancel)
        btn_row.addSpacing(8)
        btn_row.addWidget(self._btn_save)
        card_layout.addLayout(btn_row)

        root.addWidget(card)

    # ── Helpers ──────────────────────────────────────────────────────────────

    def _fill_data(self, data: dict) -> None:
        self._inp_username.setText(data.get("username", ""))
        self._inp_fullname.setText(data.get("full_name", ""))
        role = data.get("role", "STAFF")
        idx = self._cmb_role.findData(role)
        if idx >= 0:
            self._cmb_role.setCurrentIndex(idx)

    def show_error(self, msg: str) -> None:
        self._lbl_error.setText("⚠  " + msg)
        self._lbl_error.setVisible(True)

    def clear_error(self) -> None:
        self._lbl_error.setVisible(False)

    # ── Validate phía client ─────────────────────────────────────────────────

    def _on_save(self) -> None:
        self.clear_error()
        username  = self._inp_username.text().strip()
        full_name = self._inp_fullname.text().strip()
        role      = self._cmb_role.currentData()
        password  = self._inp_password.text()
        confirm   = self._inp_confirm.text() if self._inp_confirm else ""

        # Validate cơ bản phía UI
        if not self._is_edit and not username:
            self.show_error("Tên đăng nhập không được để trống.")
            self._inp_username.setFocus()
            return
        if not full_name:
            self.show_error("Họ và tên không được để trống.")
            self._inp_fullname.setFocus()
            return
        if not self._is_edit:
            if not password:
                self.show_error("Vui lòng nhập mật khẩu ban đầu.")
                return
            if len(password) < 6:
                self.show_error("Mật khẩu phải có ít nhất 6 ký tự.")
                return
            if password != confirm:
                self.show_error("Mật khẩu xác nhận không khớp.")
                return
        else:
            if password and len(password) < 6:
                self.show_error("Mật khẩu mới phải có ít nhất 6 ký tự.")
                return

        self.accept()

    # ── Public getters (controller đọc) ──────────────────────────────────────

    def get_username(self) -> str:
        return self._inp_username.text().strip().lower()

    def get_full_name(self) -> str:
        return self._inp_fullname.text().strip()

    def get_role(self) -> str:
        return self._cmb_role.currentData()

    def get_password(self) -> str:
        return self._inp_password.text()


# ── Widget ô mật khẩu nhỏ gọn ────────────────────────────────────────────────

class _PasswordField(QFrame):
    def __init__(self, placeholder: str = "", parent=None) -> None:
        super().__init__(parent)
        self.setStyleSheet(f"""
            QFrame {{
                background: {FORM_INPUT_BG};
                border: 1px solid {COLOR_BORDER};
                border-radius: 8px;
            }}
            QFrame:focus-within {{
                border: 1.5px solid {COLOR_TEAL};
            }}
        """)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(12, 0, 8, 0)
        layout.setSpacing(6)
        self._edit = QLineEdit()
        self._edit.setPlaceholderText(placeholder)
        self._edit.setEchoMode(QLineEdit.EchoMode.Password)
        self._edit.setFrame(False)
        self._edit.setStyleSheet(f"""
            QLineEdit {{
                background: transparent; border: none;
                font-size: 13px; color: {FORM_INPUT_FG};
            }}
            QLineEdit::placeholder {{ color: {FORM_INPUT_PLACEHOLDER}; }}
        """)
        btn = QPushButton("👁")
        btn.setFixedSize(28, 28)
        btn.setCursor(Qt.CursorShape.PointingHandCursor)
        btn.setStyleSheet(f"""
            QPushButton {{
                background: transparent; border: none;
                color: {FG_MUTED}; font-size: 14px;
            }}
            QPushButton:hover {{ color: {COLOR_TEAL}; }}
        """)
        btn.clicked.connect(self._toggle)
        layout.addWidget(self._edit, 1)
        layout.addWidget(btn)

    def _toggle(self) -> None:
        if self._edit.echoMode() == QLineEdit.EchoMode.Password:
            self._edit.setEchoMode(QLineEdit.EchoMode.Normal)
        else:
            self._edit.setEchoMode(QLineEdit.EchoMode.Password)

    def text(self) -> str:
        return self._edit.text()

    def clear(self) -> None:
        self._edit.clear()
