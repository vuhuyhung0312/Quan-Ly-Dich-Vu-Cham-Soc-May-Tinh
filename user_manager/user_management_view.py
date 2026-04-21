"""
UserManagementView — Quản lý nhân viên (Admin only).

Layout:
  ┌─────────────────────────────────────────────────────┐
  │  Tiêu đề + mô tả                                   │
  ├────────────[Filter bar]─────────────────────────────┤
  │  🔍 Tìm kiếm | Vai trò combo | Trạng thái combo   │
  │                              [＋ Thêm nhân viên]   │
  ├─────────────────────────────────────────────────────┤
  │  Table: Username | Họ tên | Vai trò | Trạng thái   │
  │         Ngày tạo | Cập nhật | [Xem][Sửa][Ẩn/Hiện] │
  ├─────────────────────────────────────────────────────┤
  │  ← Trước    Trang 1/3 (25 bản ghi)    Tiếp theo → │
  └─────────────────────────────────────────────────────┘
"""
from __future__ import annotations
from PySide6.QtCore import Signal, Qt, QSize
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QTableWidget, QTableWidgetItem, QPushButton,
    QLineEdit, QComboBox, QHeaderView, QFrame,
    QSizePolicy,
)
from config.settings import (
    BG_APP, BG_SURFACE, FG_PRIMARY, FG_MUTED,
    COLOR_BORDER, COLOR_TEAL, COLOR_TEAL_PALE, COLOR_TEAL_LIGHT,
    COLOR_SUCCESS, COLOR_SUCCESS_BG, COLOR_DANGER, COLOR_DANGER_BG,
    COLOR_WARNING, COLOR_WARNING_BG,
    FORM_INPUT_BG, FORM_INPUT_FG, FORM_INPUT_PLACEHOLDER,
)

_PAGE_SIZE = 10   # số hàng mỗi trang


class UserManagementView(QWidget):
    # ── Signals phát cho Controller ──────────────────────────────────────────
    new_user_requested     = Signal()
    edit_user_requested    = Signal(int)   # user_id
    detail_user_requested  = Signal(int)
    toggle_active_requested = Signal(int, bool)  # (user_id, current_is_active)
    filter_changed         = Signal()
    page_changed           = Signal(int)   # new_page (1-indexed)

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._current_page  = 1
        self._total_pages   = 1
        self._total_records = 0
        self._build_ui()

    # ══════════════════════════════════════════════════════════════════════════
    # Build UI
    # ══════════════════════════════════════════════════════════════════════════

    def _build_ui(self) -> None:
        self.setStyleSheet(f"""
            QWidget {{ background: {BG_APP}; color: {FG_PRIMARY};
                       font-family: 'Segoe UI', sans-serif; font-size: 14px; }}
            QLabel {{ background: transparent; border: none; }}
            QLabel#pageTitle {{
                font-size: 20px; font-weight: 800; color: {FG_PRIMARY};
                letter-spacing: -0.3px;
            }}
            QLabel#pageDesc {{ font-size: 13px; color: {FG_MUTED}; }}

            /* Filter bar */
            QFrame#filterBar {{
                background: {BG_SURFACE};
                border: 1px solid {COLOR_BORDER};
                border-radius: 12px;
            }}
            QLineEdit, QComboBox {{
                background: {FORM_INPUT_BG}; color: {FORM_INPUT_FG};
                border: 1px solid {COLOR_BORDER}; border-radius: 8px;
                padding: 7px 12px; font-size: 13px;
            }}
            QLineEdit:focus, QComboBox:focus {{ border: 1.5px solid {COLOR_TEAL}; }}
            QLineEdit::placeholder {{ color: {FORM_INPUT_PLACEHOLDER}; }}
            QComboBox::drop-down {{ border: none; width: 26px; }}
            QComboBox QAbstractItemView {{
                background: {BG_SURFACE}; color: {FG_PRIMARY};
                border: 1px solid {COLOR_BORDER};
                selection-background-color: {COLOR_TEAL_PALE};
                selection-color: {FG_PRIMARY}; outline: none;
            }}

            /* Table */
            QTableWidget {{
                background: {BG_SURFACE}; color: {FG_PRIMARY};
                gridline-color: {COLOR_BORDER};
                border: 1px solid {COLOR_BORDER}; border-radius: 10px;
                selection-background-color: {COLOR_TEAL_PALE};
                selection-color: {FG_PRIMARY}; font-size: 13px;
                alternate-background-color: #F8FAFC;
            }}
            QTableWidget::item {{ padding: 0px 6px; }}
            QHeaderView::section {{
                background: #F1F5F9; color: {FG_PRIMARY};
                padding: 9px 8px; border: none;
                border-bottom: 1px solid {COLOR_BORDER};
                border-right: 1px solid {COLOR_BORDER};
                font-weight: 600; font-size: 12px;
            }}
            QHeaderView::section:last {{ border-right: none; }}

            /* Buttons */
            QPushButton#primaryBtn {{
                background: {COLOR_TEAL}; color: white; border: none;
                border-radius: 8px; padding: 0 20px;
                font-size: 13px; font-weight: 600;
            }}
            QPushButton#primaryBtn:hover {{ background: #0D9488; }}

            QPushButton#pageBtn {{
                background: {BG_SURFACE}; color: {FG_PRIMARY};
                border: 1px solid {COLOR_BORDER}; border-radius: 8px;
                padding: 6px 14px; font-size: 13px; font-weight: 600;
            }}
            QPushButton#pageBtn:hover {{ background: {COLOR_TEAL_PALE}; }}
            QPushButton#pageBtn:disabled {{
                color: #CBD5E1; background: #F1F5F9;
            }}

            /* Scrollbar */
            QScrollBar:vertical {{
                background: transparent; width: 8px; margin: 0;
            }}
            QScrollBar::handle:vertical {{
                background: rgba(15,118,110,0.25);
                border-radius: 4px; min-height: 28px;
            }}
            QScrollBar::handle:vertical:hover {{
                background: rgba(15,118,110,0.45);
            }}
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{ height: 0; }}
        """)

        root = QVBoxLayout(self)
        root.setContentsMargins(28, 24, 28, 20)
        root.setSpacing(16)

        # ── Header ──────────────────────────────────────────────────────────
        hdr_row = QHBoxLayout()
        col_title = QVBoxLayout()
        lbl_title = QLabel("👤 Quản Lý Nhân Viên")
        lbl_title.setObjectName("pageTitle")
        lbl_desc = QLabel("Tạo, cập nhật và quản lý tài khoản Quản trị viên và Kỹ thuật viên.")
        lbl_desc.setObjectName("pageDesc")
        col_title.addWidget(lbl_title)
        col_title.addWidget(lbl_desc)

        btn_new = QPushButton("＋  Thêm nhân viên")
        btn_new.setObjectName("primaryBtn")
        btn_new.setFixedHeight(38)
        btn_new.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_new.clicked.connect(self.new_user_requested)

        hdr_row.addLayout(col_title, 1)
        hdr_row.addWidget(btn_new)
        root.addLayout(hdr_row)

        # ── Filter bar ───────────────────────────────────────────────────────
        filter_bar = QFrame()
        filter_bar.setObjectName("filterBar")
        filter_layout = QHBoxLayout(filter_bar)
        filter_layout.setContentsMargins(16, 12, 16, 12)
        filter_layout.setSpacing(10)

        self._search = QLineEdit()
        self._search.setPlaceholderText("🔍  Tìm theo tên đăng nhập hoặc họ tên...")
        self._search.setFixedHeight(36)
        self._search.setMinimumWidth(280)

        self._cmb_role = QComboBox()
        self._cmb_role.setFixedHeight(36)
        self._cmb_role.setFixedWidth(200)
        self._cmb_role.addItem("Tất cả vai trò", "")
        self._cmb_role.addItem("👤 Kỹ thuật viên", "STAFF")
        self._cmb_role.addItem("🔑 Quản trị viên", "ADMIN")

        self._cmb_active = QComboBox()
        self._cmb_active.setFixedHeight(36)
        self._cmb_active.setFixedWidth(180)
        self._cmb_active.addItem("Tất cả trạng thái", "all")
        self._cmb_active.addItem("Hoạt động", "active")
        self._cmb_active.addItem("Đã ẩn",          "inactive")

        btn_reset = QPushButton("↺  Đặt lại")
        btn_reset.setFixedHeight(36)
        btn_reset.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_reset.setStyleSheet(f"""
            QPushButton {{
                background: white; color: {FG_MUTED};
                border: 1px solid {COLOR_BORDER}; border-radius: 8px;
                font-size: 13px; padding: 0 14px;
            }}
            QPushButton:hover {{ background: #F1F5F9; color: {COLOR_TEAL}; }}
        """)
        btn_reset.clicked.connect(self._reset_filters)

        filter_layout.addWidget(self._search, 1)
        filter_layout.addWidget(self._cmb_role)
        filter_layout.addWidget(self._cmb_active)
        filter_layout.addWidget(btn_reset)
        root.addWidget(filter_bar)

        # ── Table ────────────────────────────────────────────────────────────
        cols = ["#", "Tên đăng nhập", "Họ và tên", "Vai trò",
                "Trạng thái", "Ngày tạo", "Cập nhật", "Thao tác"]
        self._table = QTableWidget(0, len(cols))
        self._table.setObjectName("dataTable")
        self._table.setHorizontalHeaderLabels(cols)
        self._table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self._table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self._table.setAlternatingRowColors(True)
        self._table.verticalHeader().setVisible(False)
        self._table.setShowGrid(True)
        self._table.setWordWrap(False)

        hdr = self._table.horizontalHeader()
        hdr.setSectionResizeMode(0, QHeaderView.ResizeMode.Fixed)
        self._table.setColumnWidth(0, 40)   # #

        hdr.setSectionResizeMode(1, QHeaderView.ResizeMode.Fixed)
        self._table.setColumnWidth(1, 130)  # Tên đăng nhập

        hdr.setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        # Họ và tên — Stretch nhưng table scroll horizontal nếu quá hẹp

        hdr.setSectionResizeMode(3, QHeaderView.ResizeMode.Fixed)
        self._table.setColumnWidth(3, 145)  # Vai trò — đủ cho "Quản trị viên"

        hdr.setSectionResizeMode(4, QHeaderView.ResizeMode.Fixed)
        self._table.setColumnWidth(4, 130)  # Trạng thái — đủ cho "Hoạt động"

        hdr.setSectionResizeMode(5, QHeaderView.ResizeMode.Fixed)
        self._table.setColumnWidth(5, 100)  # Ngày tạo

        hdr.setSectionResizeMode(6, QHeaderView.ResizeMode.Fixed)
        self._table.setColumnWidth(6, 100)  # Cập nhật

        hdr.setSectionResizeMode(7, QHeaderView.ResizeMode.Fixed)
        self._table.setColumnWidth(7, 118)  # Thao tác (3 nút)
        hdr.setMinimumSectionSize(40)

        root.addWidget(self._table)

        # ── Phân trang ───────────────────────────────────────────────────────
        pg_bar = QHBoxLayout()
        pg_bar.setSpacing(10)

        self._btn_prev = QPushButton("← Trước")
        self._btn_prev.setObjectName("pageBtn")
        self._btn_prev.setFixedHeight(34)
        self._btn_prev.setCursor(Qt.CursorShape.PointingHandCursor)
        self._btn_prev.clicked.connect(self._go_prev)

        self._lbl_page = QLabel("Trang 1 / 1  •  0 bản ghi")
        self._lbl_page.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._lbl_page.setStyleSheet(f"color: {FG_MUTED}; font-size: 13px;")

        self._btn_next = QPushButton("Tiếp theo →")
        self._btn_next.setObjectName("pageBtn")
        self._btn_next.setFixedHeight(34)
        self._btn_next.setCursor(Qt.CursorShape.PointingHandCursor)
        self._btn_next.clicked.connect(self._go_next)

        pg_bar.addStretch()
        pg_bar.addWidget(self._btn_prev)
        pg_bar.addWidget(self._lbl_page)
        pg_bar.addWidget(self._btn_next)
        pg_bar.addStretch()
        root.addLayout(pg_bar)

        # ── Kết nối filter ───────────────────────────────────────────────────
        self._search.textChanged.connect(self._on_filter_changed)
        self._cmb_role.currentIndexChanged.connect(self._on_filter_changed)
        self._cmb_active.currentIndexChanged.connect(self._on_filter_changed)

    # ══════════════════════════════════════════════════════════════════════════
    # Filter helpers
    # ══════════════════════════════════════════════════════════════════════════

    def _on_filter_changed(self) -> None:
        self._current_page = 1
        self.filter_changed.emit()

    def _reset_filters(self) -> None:
        self._search.blockSignals(True)
        self._cmb_role.blockSignals(True)
        self._cmb_active.blockSignals(True)
        self._search.clear()
        self._cmb_role.setCurrentIndex(0)
        self._cmb_active.setCurrentIndex(0)
        self._search.blockSignals(False)
        self._cmb_role.blockSignals(False)
        self._cmb_active.blockSignals(False)
        self._current_page = 1
        self.filter_changed.emit()

    # ══════════════════════════════════════════════════════════════════════════
    # Pagination helpers
    # ══════════════════════════════════════════════════════════════════════════

    def _go_prev(self) -> None:
        if self._current_page > 1:
            self._current_page -= 1
            self.page_changed.emit(self._current_page)

    def _go_next(self) -> None:
        if self._current_page < self._total_pages:
            self._current_page += 1
            self.page_changed.emit(self._current_page)

    def _update_pagination(self) -> None:
        self._lbl_page.setText(
            f"Trang {self._current_page} / {max(self._total_pages, 1)}"
            f"  •  {self._total_records} bản ghi"
        )
        self._btn_prev.setEnabled(self._current_page > 1)
        self._btn_next.setEnabled(self._current_page < self._total_pages)

    # ══════════════════════════════════════════════════════════════════════════
    # Public API (Controller gọi)
    # ══════════════════════════════════════════════════════════════════════════

    def get_search(self) -> str:
        return self._search.text().strip()

    def get_role_filter(self) -> str:
        return self._cmb_role.currentData() or ""

    def get_active_filter(self) -> str:
        return self._cmb_active.currentData() or "all"

    def get_current_page(self) -> int:
        return self._current_page

    def get_page_size(self) -> int:
        return _PAGE_SIZE

    def load_users(self, rows: list, total: int) -> None:
        """Nạp dữ liệu vào bảng và cập nhật phân trang."""
        import math
        self._total_records = total
        self._total_pages   = max(math.ceil(total / _PAGE_SIZE), 1)
        self._update_pagination()

        self._table.setRowCount(0)
        self._table.setRowCount(len(rows))

        for r_idx, row in enumerate(rows):
            self._table.setRowHeight(r_idx, 46)
            offset = (_PAGE_SIZE * (self._current_page - 1)) + r_idx + 1
            _cell(self._table, r_idx, 0, str(offset), align="center")
            _cell(self._table, r_idx, 1, row["username"])
            _cell(self._table, r_idx, 2, row["full_name"])

            # Badge vai trò
            role_label = "Quản trị viên" if row["role"] == "ADMIN" else "Kỹ thuật viên"
            role_widget = _badge(
                role_label,
                bg="#DBEAFE" if row["role"] == "ADMIN" else "#D1FAE5",
                fg="#1D4ED8" if row["role"] == "ADMIN" else "#065F46",
            )
            self._table.setCellWidget(r_idx, 3, role_widget)

            # Badge trạng thái
            is_active = bool(row["is_active"])
            status_widget = _badge(
                "Hoạt động" if is_active else "Đã ẩn",
                bg=COLOR_SUCCESS_BG if is_active else COLOR_DANGER_BG,
                fg=COLOR_SUCCESS    if is_active else COLOR_DANGER,
            )
            self._table.setCellWidget(r_idx, 4, status_widget)

            _cell(self._table, r_idx, 5, (row["created_at"] or "")[:10])
            _cell(self._table, r_idx, 6, (row["updated_at"] or "")[:10])

            # Cột thao tác
            action_widget = self._make_action_widget(
                user_id=row["id"],
                is_active=is_active,
            )
            self._table.setCellWidget(r_idx, 7, action_widget)

    def _make_action_widget(self, user_id: int, is_active: bool) -> QWidget:
        """Tạo widget chứa 3 nút Xem / Sửa / Ẩn-Hiện."""
        widget = QWidget()
        widget.setStyleSheet("background: transparent;")
        layout = QHBoxLayout(widget)
        layout.setContentsMargins(6, 4, 6, 4)
        layout.setSpacing(6)

        # Xem chi tiết
        btn_view = _action_button(
            "🔍", "Xem chi tiết",
            bg="#EFF6FF", fg="#1D4ED8", hover="#DBEAFE",
        )
        btn_view.clicked.connect(lambda _=False, uid=user_id: self.detail_user_requested.emit(uid))

        # Sửa
        btn_edit = _action_button(
            "✏️", "Chỉnh sửa",
            bg=COLOR_TEAL_PALE, fg=COLOR_TEAL, hover="#A7F3D0",
        )
        btn_edit.clicked.connect(lambda _=False, uid=user_id: self.edit_user_requested.emit(uid))

        # Ẩn / Hiện
        if is_active:
            btn_toggle = _action_button(
                "🚫", "Ẩn tài khoản",
                bg=COLOR_DANGER_BG, fg=COLOR_DANGER, hover="#FECACA",
            )
        else:
            btn_toggle = _action_button(
                "✅", "Hiện lại",
                bg=COLOR_SUCCESS_BG, fg=COLOR_SUCCESS, hover="#A7F3D0",
            )
        btn_toggle.clicked.connect(
            lambda _=False, uid=user_id, active=is_active:
                self.toggle_active_requested.emit(uid, active)
        )

        layout.addWidget(btn_view)
        layout.addWidget(btn_edit)
        layout.addWidget(btn_toggle)
        layout.addStretch()
        return widget


# ══════════════════════════════════════════════════════════════════════════════
# Utility helpers
# ══════════════════════════════════════════════════════════════════════════════

def _cell(
    table: QTableWidget,
    row: int,
    col: int,
    text: str,
    align: str = "left",
) -> None:
    item = QTableWidgetItem(text)
    if align == "center":
        item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
    table.setItem(row, col, item)


def _badge(text: str, bg: str, fg: str) -> QWidget:
    """Label badge căn giữa, màu bg/fg."""
    w = QWidget()
    w.setStyleSheet("background: transparent;")
    layout = QHBoxLayout(w)
    layout.setContentsMargins(6, 0, 6, 0)
    layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
    lbl = QLabel(text)
    lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
    lbl.setStyleSheet(f"""
        background: {bg}; color: {fg};
        font-size: 12px; font-weight: 600;
        border-radius: 20px; padding: 3px 10px;
        border: none;
    """)
    layout.addWidget(lbl)
    return w


def _action_button(
    icon: str, tooltip: str, bg: str, fg: str, hover: str
) -> QPushButton:
    btn = QPushButton(icon)
    btn.setFixedSize(QSize(30, 30))
    btn.setCursor(Qt.CursorShape.PointingHandCursor)
    btn.setToolTip(tooltip)
    btn.setStyleSheet(f"""
        QPushButton {{
            background: {bg}; color: {fg};
            border: none; border-radius: 6px;
            font-size: 14px;
        }}
        QPushButton:hover {{ background: {hover}; }}
    """)
    return btn
