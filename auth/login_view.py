"""
Màn hình đăng nhập — layout 2 cột: Form (trái) + Brand (phải).
Ngược chiều so với dự án Đồ Gia Dụng.

Màu sắc: Teal / Cyan tươi sáng.
Animation: fade-in + slide nhẹ khi khởi động.
"""
from __future__ import annotations

from PySide6.QtCore import (
    Qt, QTimer, Signal,
    QPropertyAnimation, QEasingCurve, QPoint, Property,
)
from PySide6.QtGui import QColor, QLinearGradient, QPainter, QPaintEvent, QPainterPath
from PySide6.QtWidgets import (
    QFrame,
    QGraphicsDropShadowEffect,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)

from config.settings import (
    APP_TITLE, APP_VERSION,
    COLOR_TEAL, COLOR_TEAL_LIGHT, COLOR_TEAL_PALE,
    COLOR_CYAN_LIGHT, COLOR_SKY,
    BG_SURFACE, BG_APP,
    FG_PRIMARY, FG_MUTED,
    COLOR_BORDER, COLOR_DANGER, COLOR_DANGER_BG,
    FORM_INPUT_BG, FORM_INPUT_FG, FORM_INPUT_PLACEHOLDER,
)


def _no_stripes(lbl: QLabel) -> None:
    """Tránh nền vạch palette macOS."""
    lbl.setAutoFillBackground(False)


# ══════════════════════════════════════════════════════════════════════════════
# Ô nhập có viền đổi màu khi focus
# ══════════════════════════════════════════════════════════════════════════════

class _FocusLineEdit(QLineEdit):
    focus_in  = Signal()
    focus_out = Signal()

    def focusInEvent(self, event) -> None:  # noqa: N802
        super().focusInEvent(event)
        self.focus_in.emit()

    def focusOutEvent(self, event) -> None:  # noqa: N802
        super().focusOutEvent(event)
        self.focus_out.emit()


class _InputField(QFrame):
    """Khung ô nhập với icon emoji bên trái, viền đổi màu khi focus."""

    _STYLE_NORMAL = """
        QFrame#inputFrame {
            background: #F8FAFC;
            border: 1.5px solid #E2E8F0;
            border-radius: 12px;
        }
    """
    _STYLE_FOCUSED = f"""
        QFrame#inputFrame {{
            background: #FFFFFF;
            border: 2px solid {COLOR_TEAL_LIGHT};
            border-radius: 12px;
        }}
    """

    def __init__(
        self,
        icon: str,
        placeholder: str,
        echo_mode: QLineEdit.EchoMode = QLineEdit.EchoMode.Normal,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self.setObjectName("inputFrame")
        self.setFixedHeight(52)
        self._icon_lbl: QLabel | None = None
        self._build(icon, placeholder, echo_mode)

    def _build(self, icon: str, placeholder: str, echo_mode: QLineEdit.EchoMode) -> None:
        layout = QHBoxLayout(self)
        layout.setContentsMargins(14, 0, 14, 0)
        layout.setSpacing(10)

        if icon:
            self._icon_lbl = QLabel(icon)
            self._icon_lbl.setFixedWidth(22)
            self._icon_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self._icon_lbl.setStyleSheet(
                "font-size: 16px; background: transparent; border: none; color: #94A3B8;"
            )
            layout.addWidget(self._icon_lbl)

        self._edit = _FocusLineEdit()
        self._edit.setPlaceholderText(placeholder)
        self._edit.setEchoMode(echo_mode)
        self._edit.setFrame(False)
        self._edit.setStyleSheet(f"""
            QLineEdit {{
                background: transparent;
                border: none;
                font-size: 14px;
                color: {FORM_INPUT_FG};
            }}
            QLineEdit::placeholder {{ color: {FORM_INPUT_PLACEHOLDER}; }}
        """)
        self._edit.focus_in.connect(lambda: self._set_focused(True))
        self._edit.focus_out.connect(lambda: self._set_focused(False))
        layout.addWidget(self._edit, stretch=1)
        self.setStyleSheet(self._STYLE_NORMAL)

    @property
    def edit(self) -> QLineEdit:
        return self._edit

    def text(self) -> str:
        return self._edit.text()

    def clear(self) -> None:
        self._edit.clear()

    def _set_focused(self, focused: bool) -> None:
        self.setStyleSheet(self._STYLE_FOCUSED if focused else self._STYLE_NORMAL)
        if self._icon_lbl is not None:
            color = COLOR_TEAL if focused else "#94A3B8"
            self._icon_lbl.setStyleSheet(
                f"font-size: 16px; background: transparent; border: none; color: {color};"
            )


class _PasswordField(_InputField):
    """Ô mật khẩu + nút Hiện / Ẩn bên phải."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__("🔒", "Nhập mật khẩu...", QLineEdit.EchoMode.Password, parent)
        self._visible = False
        self._toggle = QPushButton("Hiện")
        self._toggle.setFixedHeight(28)
        self._toggle.setCursor(Qt.CursorShape.PointingHandCursor)
        self._toggle.setToolTip("Hiện hoặc ẩn mật khẩu")
        self._toggle.setStyleSheet(f"""
            QPushButton {{
                background: transparent; border: none;
                color: {COLOR_TEAL}; font-size: 12px; font-weight: 600;
                padding: 4px 8px; border-radius: 6px;
            }}
            QPushButton:hover {{ background: {COLOR_TEAL_PALE}; color: #0F766E; }}
        """)
        self._toggle.clicked.connect(self._toggle_visibility)
        self.layout().addWidget(self._toggle)

    def _toggle_visibility(self) -> None:
        self._visible = not self._visible
        if self._visible:
            self._edit.setEchoMode(QLineEdit.EchoMode.Normal)
            self._toggle.setText("Ẩn")
        else:
            self._edit.setEchoMode(QLineEdit.EchoMode.Password)
            self._toggle.setText("Hiện")


# ══════════════════════════════════════════════════════════════════════════════
# Cột trái — Form Panel (nền sáng, gradient nhẹ)
# ══════════════════════════════════════════════════════════════════════════════

class _FormPanel(QWidget):
    """Cột trái: gradient nhẹ F0FDFA→ECFEFF; card form trắng căn giữa."""

    login_requested = Signal(str, str)

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        self._build_ui()
        self._connect_signals()

    def paintEvent(self, event: QPaintEvent) -> None:  # noqa: N802
        """Vẽ nền gradient nhẹ teal→cyan."""
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        grad = QLinearGradient(0, 0, 0, float(self.height()))
        grad.setColorAt(0.0, QColor("#F0FDFA"))
        grad.setColorAt(1.0, QColor("#ECFEFF"))
        p.fillRect(self.rect(), grad)
        # Vài hình tròn trang trí góc
        p.setPen(Qt.PenStyle.NoPen)
        p.setBrush(QColor("#14B8A6" + "18"))
        p.drawEllipse(-60, -60, 200, 200)
        p.setBrush(QColor("#06B6D4" + "12"))
        p.drawEllipse(self.width() - 100, self.height() - 100, 180, 180)
        super().paintEvent(event)

    def _build_ui(self) -> None:
        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.addStretch(1)
        row = QHBoxLayout()
        row.addStretch(1)
        row.addWidget(self._build_card())
        row.addStretch(1)
        outer.addLayout(row)
        outer.addStretch(1)

    def _build_card(self) -> QWidget:
        card = QFrame()
        card.setObjectName("loginCard")
        card.setFixedWidth(420)
        card.setStyleSheet(f"""
            QFrame#loginCard {{
                background: {BG_SURFACE};
                border: 1px solid {COLOR_BORDER};
                border-radius: 20px;
            }}
            QFrame#loginCard QLabel {{
                background: transparent;
                border: none;
                padding: 0px;
            }}
        """)
        # Drop shadow
        shadow = QGraphicsDropShadowEffect(card)
        shadow.setBlurRadius(32)
        shadow.setOffset(0, 8)
        shadow.setColor(QColor(15, 118, 110, 45))
        card.setGraphicsEffect(shadow)

        layout = QVBoxLayout(card)
        layout.setContentsMargins(40, 40, 40, 36)
        layout.setSpacing(0)

        # Logo + tiêu đề
        logo = QLabel("🖥")
        logo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        logo.setStyleSheet("font-size: 40px; background: transparent; border: none;")
        _no_stripes(logo)

        greeting = QLabel("Chào mừng trở lại!")
        greeting.setAlignment(Qt.AlignmentFlag.AlignCenter)
        greeting.setStyleSheet(
            f"color: {FG_PRIMARY}; font-size: 22px; font-weight: 800;"
            " letter-spacing: -0.5px; background: transparent; border: none;"
        )
        _no_stripes(greeting)

        subtitle = QLabel("Đăng nhập để quản lý dịch vụ")
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        subtitle.setStyleSheet(
            f"color: {FG_MUTED}; font-size: 13px;"
            " background: transparent; border: none;"
        )
        _no_stripes(subtitle)

        layout.addWidget(logo)
        layout.addSpacing(8)
        layout.addWidget(greeting)
        layout.addSpacing(4)
        layout.addWidget(subtitle)
        layout.addSpacing(32)

        # Username
        lbl_user = QLabel("Tên đăng nhập")
        lbl_user.setStyleSheet(
            f"color: {FG_PRIMARY}; font-size: 13px; font-weight: 600;"
            " background: transparent; border: none;"
        )
        _no_stripes(lbl_user)
        self._username_field = _InputField("👤", "Nhập tên đăng nhập...")
        layout.addWidget(lbl_user)
        layout.addSpacing(6)
        layout.addWidget(self._username_field)
        layout.addSpacing(18)

        # Password
        lbl_pwd = QLabel("Mật khẩu")
        lbl_pwd.setStyleSheet(
            f"color: {FG_PRIMARY}; font-size: 13px; font-weight: 600;"
            " background: transparent; border: none;"
        )
        _no_stripes(lbl_pwd)
        self._password_field = _PasswordField()
        layout.addWidget(lbl_pwd)
        layout.addSpacing(6)
        layout.addWidget(self._password_field)
        layout.addSpacing(28)

        # Nút đăng nhập
        self._btn_login = QPushButton("  Đăng nhập")
        self._btn_login.setFixedHeight(50)
        self._btn_login.setCursor(Qt.CursorShape.PointingHandCursor)
        self._btn_login.setStyleSheet(f"""
            QPushButton {{
                background: qlineargradient(x1:0,y1:0,x2:1,y2:0,
                    stop:0 {COLOR_TEAL}, stop:1 {COLOR_CYAN_LIGHT});
                color: white;
                font-size: 15px;
                font-weight: 700;
                letter-spacing: 0.5px;
                border: none;
                border-radius: 12px;
            }}
            QPushButton:hover {{
                background: qlineargradient(x1:0,y1:0,x2:1,y2:0,
                    stop:0 #0D9488, stop:1 {COLOR_SKY});
            }}
            QPushButton:pressed {{
                background: qlineargradient(x1:0,y1:0,x2:1,y2:0,
                    stop:0 #0F766E, stop:1 #0284C7);
            }}
            QPushButton:disabled {{
                background: #E2E8F0;
                color: #94A3B8;
            }}
        """)
        btn_shadow = QGraphicsDropShadowEffect(self._btn_login)
        btn_shadow.setBlurRadius(20)
        btn_shadow.setOffset(0, 6)
        btn_shadow.setColor(QColor(20, 184, 166, 80))
        self._btn_login.setGraphicsEffect(btn_shadow)
        layout.addWidget(self._btn_login)
        layout.addSpacing(16)

        # Error label (ẩn mặc định)
        self._lbl_error = QLabel()
        self._lbl_error.setObjectName("loginErrorLabel")
        self._lbl_error.setWordWrap(True)
        self._lbl_error.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._lbl_error.setVisible(False)
        self._lbl_error.setStyleSheet(f"""
            QLabel {{
                color: {COLOR_DANGER};
                font-size: 13px;
                background: {COLOR_DANGER_BG};
                border: 1px solid #FECACA;
                border-radius: 10px;
                padding: 10px 14px;
            }}
        """)
        layout.addWidget(self._lbl_error)
        layout.addSpacing(12)

        ver = QLabel(f"{APP_TITLE}  •  v{APP_VERSION}")
        ver.setAlignment(Qt.AlignmentFlag.AlignCenter)
        ver.setStyleSheet(
            f"color: {FG_MUTED}; font-size: 11px;"
            " background: transparent; border: none;"
        )
        _no_stripes(ver)
        layout.addWidget(ver)

        return card

    def _connect_signals(self) -> None:
        self._btn_login.clicked.connect(self._on_login_clicked)
        self._password_field.edit.returnPressed.connect(self._on_login_clicked)
        self._username_field.edit.returnPressed.connect(
            lambda: self._password_field.edit.setFocus()
        )

    def _on_login_clicked(self) -> None:
        username = self._username_field.text().strip()
        password = self._password_field.text()
        self.login_requested.emit(username, password)

    # ── Public API ──────────────────────────────────────────────────────────

    def show_error(self, message: str) -> None:
        self._lbl_error.setText("⚠  " + message)
        self._lbl_error.setVisible(True)

    def clear_error(self) -> None:
        self._lbl_error.clear()
        self._lbl_error.setVisible(False)

    def set_loading(self, loading: bool) -> None:
        self._btn_login.setEnabled(not loading)
        self._btn_login.setText("⏳  Đang xử lý..." if loading else "  Đăng nhập")

    def clear_fields(self) -> None:
        self._username_field.clear()
        self._password_field.clear()


# ══════════════════════════════════════════════════════════════════════════════
# Cột phải — Brand Panel (gradient teal/cyan đậm)
# ══════════════════════════════════════════════════════════════════════════════

class _BrandPanel(QWidget):
    """Cột phải: gradient xanh teal→cyan đậm; tính năng, slogan."""

    _FEATURES = [
        ("🔧", "Nhận và theo dõi phiếu sửa chữa máy tính"),
        ("👤", "Quản lý thông tin khách hàng & thiết bị"),
        ("📊", "Thống kê doanh thu dịch vụ theo kỳ"),
        ("🛡", "Phân quyền Admin và Kỹ thuật viên"),
    ]

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self._build_ui()

    def paintEvent(self, event) -> None:  # noqa: N802
        """Gradient teal/cyan đậm + dots pattern + vòng tròn trang trí."""
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)

        grad = QLinearGradient(0, 0, float(self.width()), float(self.height()))
        grad.setColorAt(0.0,  QColor("#0C4A6E"))   # Sky 900
        grad.setColorAt(0.4,  QColor("#0369A1"))   # Sky 700
        grad.setColorAt(0.75, QColor("#0E7490"))   # Cyan 700
        grad.setColorAt(1.0,  QColor("#0F766E"))   # Teal 700
        p.fillRect(self.rect(), grad)

        # Vòng tròn trang trí
        p.setPen(Qt.PenStyle.NoPen)
        p.setBrush(QColor(255, 255, 255, 14))
        p.drawEllipse(-100, -100, 340, 340)
        p.setBrush(QColor(255, 255, 255, 9))
        p.drawEllipse(self.width() - 260, self.height() - 280, 400, 400)
        p.setBrush(QColor(255, 255, 255, 6))
        p.drawEllipse(self.width() - 80, 40, 200, 200)
        p.drawEllipse(10, self.height() - 160, 150, 150)

        # Dots pattern
        p.setPen(QColor(255, 255, 255, 20))
        for row in range(20, self.height(), 26):
            for col in range(20, self.width(), 26):
                p.drawEllipse(col - 1, row - 1, 2, 2)

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(52, 60, 52, 52)
        layout.setSpacing(0)

        # Icon
        lbl_icon = QLabel("🖥")
        lbl_icon.setStyleSheet(
            "font-size: 52px; background: transparent; border: none;"
        )

        line1 = QLabel("Chăm Sóc")
        line1.setStyleSheet(
            "color: #FFFFFF; font-size: 30px; font-weight: 800;"
            " background: transparent; border: none;"
        )
        line2 = QLabel("Máy Tính")
        line2.setStyleSheet(
            "color: #A5F3FC; font-size: 25px; font-weight: 700;"
            " background: transparent; border: none;"
        )

        layout.addWidget(lbl_icon)
        layout.addSpacing(8)
        layout.addWidget(line1)
        layout.addWidget(line2)
        layout.addSpacing(12)

        slogan = QLabel("Dịch vụ chuyên nghiệp — Khách hàng hài lòng")
        slogan.setStyleSheet(
            "color: rgba(165,243,252,0.85); font-size: 13px; font-style: italic;"
            " background: transparent; border: none;"
        )
        layout.addWidget(slogan)
        layout.addSpacing(36)

        sep = QFrame()
        sep.setFixedHeight(1)
        sep.setStyleSheet("background: rgba(255,255,255,0.18); border: none;")
        layout.addWidget(sep)
        layout.addSpacing(28)

        feat_title = QLabel("TÍNH NĂNG HỆ THỐNG")
        feat_title.setStyleSheet(
            "color: rgba(255,255,255,0.50); font-size: 10px; font-weight: 700;"
            " letter-spacing: 2px; background: transparent; border: none;"
        )
        layout.addWidget(feat_title)
        layout.addSpacing(18)

        for icon, text in self._FEATURES:
            row = QHBoxLayout()
            row.setSpacing(14)

            pill = QLabel(icon)
            pill.setFixedSize(32, 32)
            pill.setAlignment(Qt.AlignmentFlag.AlignCenter)
            pill.setStyleSheet(
                "font-size: 15px;"
                "background: rgba(255,255,255,0.15);"
                "border-radius: 8px;"
                "border: none;"
            )

            lbl = QLabel(text)
            lbl.setStyleSheet(
                "color: rgba(255,255,255,0.88); font-size: 13px;"
                " background: transparent; border: none;"
            )
            row.addWidget(pill)
            row.addWidget(lbl)
            row.addStretch()
            layout.addLayout(row)
            layout.addSpacing(12)

        layout.addStretch()

        copy = QLabel(f"© 2026  {APP_TITLE}  •  v{APP_VERSION}")
        copy.setStyleSheet(
            "color: rgba(255,255,255,0.32); font-size: 11px;"
            " background: transparent; border: none;"
        )
        layout.addWidget(copy)


# ══════════════════════════════════════════════════════════════════════════════
# LoginView — root: Form (trái 55%) + Brand (phải 45%)
# ══════════════════════════════════════════════════════════════════════════════

class LoginView(QWidget):
    """
    Layout đảo so với Đồ Gia Dụng:
    - Trái: Form Panel (nền sáng, card trắng)
    - Phải: Brand Panel (gradient teal/cyan đậm)
    """

    login_requested = Signal(str, str)

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setObjectName("loginRoot")
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self._opacity: float = 0.0
        self._build_ui()
        self._animate_in()

    # ── Build ───────────────────────────────────────────────────────────────

    def _build_ui(self) -> None:
        root = QHBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        self._form  = _FormPanel()
        brand       = _BrandPanel()

        self._form.login_requested.connect(self.login_requested)

        root.addWidget(self._form,  stretch=55)
        root.addWidget(brand,       stretch=45)

    # ── Fade-in animation khi mở ────────────────────────────────────────────

    def _get_opacity(self) -> float:
        return self._opacity

    def _set_opacity(self, val: float) -> None:
        self._opacity = val
        self.setWindowOpacity(val)

    opacity = Property(float, _get_opacity, _set_opacity)

    def _animate_in(self) -> None:
        """Fade-in nhẹ từ 0 → 1 khi màn hình xuất hiện."""
        self._anim = QPropertyAnimation(self, b"opacity", self)
        self._anim.setDuration(500)
        self._anim.setStartValue(0.0)
        self._anim.setEndValue(1.0)
        self._anim.setEasingCurve(QEasingCurve.Type.OutCubic)
        # Delay nhỏ để QApplication kịp render widget
        QTimer.singleShot(80, self._anim.start)

    # ── Public API (cho controller) ─────────────────────────────────────────

    def show_error(self, message: str) -> None:
        self._form.show_error(message)

    def clear_error(self) -> None:
        self._form.clear_error()

    def set_loading(self, loading: bool) -> None:
        self._form.set_loading(loading)

    def clear_fields(self) -> None:
        self._form.clear_fields()
