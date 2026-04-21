"""CustomerDetailDialog — Xem chi tiết + lịch sử phiếu dịch vụ."""
from __future__ import annotations
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QFrame, QTableWidget, QTableWidgetItem,
    QHeaderView, QScrollArea, QWidget,
)
from config.settings import (
    BG_APP, BG_SURFACE, FG_PRIMARY, FG_MUTED, COLOR_BORDER,
    COLOR_TEAL, COLOR_TEAL_PALE, COLOR_TEAL_LIGHT,
    COLOR_SUCCESS, COLOR_SUCCESS_BG, COLOR_DANGER, COLOR_DANGER_BG,
    COLOR_WARNING, COLOR_WARNING_BG, COLOR_INFO_BG, COLOR_CYAN,
    ORDER_STATUS_LABELS, ORDER_STATUS_BG, ORDER_STATUS_COLORS,
)


class CustomerDetailDialog(QDialog):
    def __init__(self, parent=None, *, customer_row, order_history: list) -> None:
        super().__init__(parent)
        self._cust    = customer_row
        self._orders  = order_history
        self.setWindowTitle(f"Chi tiết khách hàng — {customer_row['full_name']}")
        self.setModal(True)
        self.setMinimumWidth(760)
        self.setMinimumHeight(560)
        self.setStyleSheet(f"""
            QDialog {{ background: {BG_APP}; }}
            QLabel  {{ background: transparent; border: none; }}
            QFrame#infoCard, QFrame#historyCard {{
                background: {BG_SURFACE};
                border: 1px solid {COLOR_BORDER};
                border-radius: 14px;
            }}
            QTableWidget {{
                background: {BG_SURFACE}; color: {FG_PRIMARY};
                gridline-color: {COLOR_BORDER}; border: none;
                font-size: 12px;
                alternate-background-color: #F8FAFC;
                selection-background-color: {COLOR_TEAL_PALE};
                selection-color: {FG_PRIMARY};
            }}
            QHeaderView::section {{
                background: #F1F5F9; color: {FG_PRIMARY};
                padding: 7px 8px; border: none;
                border-bottom: 1px solid {COLOR_BORDER};
                border-right: 1px solid {COLOR_BORDER};
                font-weight: 600; font-size: 11px;
            }}
            QTableWidget::item {{ padding: 5px 6px; }}
        """)
        self._build_ui()

    def _build_ui(self) -> None:
        root = QVBoxLayout(self)
        root.setContentsMargins(20, 20, 20, 20)
        root.setSpacing(14)

        # ── Info card ────────────────────────────────────────────────────────
        info_card = QFrame(); info_card.setObjectName("infoCard")
        info_lay  = QVBoxLayout(info_card)
        info_lay.setContentsMargins(24, 20, 24, 20)
        info_lay.setSpacing(12)

        # Header: avatar + tên
        hdr = QHBoxLayout(); hdr.setSpacing(16)
        avatar = QLabel(self._cust["full_name"][0].upper())
        avatar.setFixedSize(52, 52)
        avatar.setAlignment(Qt.AlignmentFlag.AlignCenter)
        avatar.setStyleSheet(f"""
            background: {COLOR_TEAL_LIGHT}; color: white;
            border-radius: 26px; font-size: 22px; font-weight: 700;
            border: none;
        """)

        name_col = QVBoxLayout(); name_col.setSpacing(2)
        lbl_name = QLabel(self._cust["full_name"])
        lbl_name.setStyleSheet(f"font-size: 17px; font-weight: 800; color: {FG_PRIMARY};")
        status_text = "✅ Đang hoạt động" if self._cust["is_active"] else "⛔ Đã ẩn"
        status_color = COLOR_SUCCESS if self._cust["is_active"] else COLOR_DANGER
        lbl_status = QLabel(status_text)
        lbl_status.setStyleSheet(f"font-size: 12px; color: {status_color}; font-weight: 600;")
        name_col.addWidget(lbl_name); name_col.addWidget(lbl_status)

        hdr.addWidget(avatar); hdr.addLayout(name_col, 1)
        info_lay.addLayout(hdr)

        sep = _sep(); info_lay.addWidget(sep)

        # Stats row
        order_count  = self._cust["order_count"] if self._cust["order_count"] else 0
        total_spent  = self._cust["total_spent"] if self._cust["total_spent"] else 0
        stats_row = QHBoxLayout(); stats_row.setSpacing(12)
        stats_row.addWidget(_stat_card("📋 Tổng phiếu", str(order_count), "#EFF6FF", "#1D4ED8"))
        stats_row.addWidget(_stat_card("💰 Tổng chi tiêu", f"{total_spent:,} đ", "#F0FDF4", "#065F46"))
        stats_row.addWidget(_stat_card("📅 Ngày đăng ký", (self._cust["created_at"] or "")[:10], "#FFF7ED", "#92400E"))
        info_lay.addLayout(stats_row)

        # Fields
        fields_row = QHBoxLayout(); fields_row.setSpacing(24)
        col_l = QVBoxLayout(); col_l.setSpacing(8)
        col_r = QVBoxLayout(); col_r.setSpacing(8)

        def _field(label, val, col):
            w = QVBoxLayout(); w.setSpacing(2)
            lk = QLabel(label); lk.setStyleSheet(f"color: {FG_MUTED}; font-size: 11px; font-weight: 600;")
            lv = QLabel(str(val) if val else "—"); lv.setStyleSheet(f"color: {FG_PRIMARY}; font-size: 13px;")
            lv.setWordWrap(True)
            w.addWidget(lk); w.addWidget(lv)
            col.addLayout(w)

        _field("SỐ ĐIỆN THOẠI",  self._cust["phone"], col_l)
        _field("ĐỊA CHỈ",        self._cust["address"] if self._cust["address"] else "", col_l)
        _field("EMAIL",           self._cust["email"] if self._cust["email"] else "",   col_r)
        _field("GHI CHÚ",        self._cust["note"] if self._cust["note"] else "",    col_r)

        fields_row.addLayout(col_l, 1); fields_row.addLayout(col_r, 1)
        info_lay.addLayout(fields_row)
        root.addWidget(info_card)

        # ── History card ──────────────────────────────────────────────────────
        hist_card = QFrame(); hist_card.setObjectName("historyCard")
        hist_lay  = QVBoxLayout(hist_card)
        hist_lay.setContentsMargins(20, 16, 20, 16)
        hist_lay.setSpacing(12)

        lbl_hist = QLabel(f"📋 Lịch sử phiếu dịch vụ ({len(self._orders)} phiếu)")
        lbl_hist.setStyleSheet(f"font-size: 14px; font-weight: 700; color: {FG_PRIMARY};")
        hist_lay.addWidget(lbl_hist)

        if self._orders:
            cols = ["Mã phiếu", "Trạng thái", "Thiết bị", "Ngày nhận", "Tổng tiền", "KTV"]
            tbl = QTableWidget(len(self._orders), len(cols))
            tbl.setHorizontalHeaderLabels(cols)
            tbl.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
            tbl.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
            tbl.verticalHeader().setVisible(False)
            tbl.setAlternatingRowColors(True)
            tbl.setShowGrid(True)

            hdr_view = tbl.horizontalHeader()
            hdr_view.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
            hdr_view.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
            hdr_view.setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
            hdr_view.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
            hdr_view.setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)
            hdr_view.setSectionResizeMode(5, QHeaderView.ResizeMode.ResizeToContents)

            for r, row in enumerate(self._orders):
                tbl.setRowHeight(r, 36)
                status = row["status"]
                status_label = ORDER_STATUS_LABELS.get(status, status)
                device = f"{row['device_type']} {row.get('device_brand') or ''}".strip()

                def _c(col, text, align=Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter):
                    item = QTableWidgetItem(text)
                    item.setTextAlignment(align)
                    tbl.setItem(r, col, item)

                _c(0, row["order_no"])
                _c(1, status_label)
                _c(2, device)
                _c(3, (row["received_at"] or "")[:10])
                _c(4, f"{row['total_amount']:,} đ", Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
                _c(5, row.get("assigned_staff") or "—")

                # Màu badge cho cột trạng thái
                item_status = tbl.item(r, 1)
                if item_status:
                    item_status.setForeground(__import__("PySide6.QtGui", fromlist=["QColor"]).QColor(
                        ORDER_STATUS_COLORS.get(status, FG_PRIMARY)
                    ))

            tbl.setMaximumHeight(250)
            hist_lay.addWidget(tbl)
        else:
            lbl_empty = QLabel("Chưa có phiếu dịch vụ nào.")
            lbl_empty.setAlignment(Qt.AlignmentFlag.AlignCenter)
            lbl_empty.setStyleSheet(f"color: {FG_MUTED}; font-size: 13px; padding: 24px;")
            hist_lay.addWidget(lbl_empty)

        root.addWidget(hist_card, 1)

        # ── Bottom button ─────────────────────────────────────────────────────
        btn_close = QPushButton("Đóng")
        btn_close.setFixedHeight(38); btn_close.setFixedWidth(120)
        btn_close.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_close.setStyleSheet(f"""
            QPushButton {{
                background: {COLOR_TEAL}; color: white; border: none;
                border-radius: 8px; font-size: 13px; font-weight: 600;
            }}
            QPushButton:hover {{ background: #0D9488; }}
        """)
        btn_close.clicked.connect(self.accept)

        btn_row = QHBoxLayout(); btn_row.addStretch(); btn_row.addWidget(btn_close)
        root.addLayout(btn_row)


# ── Helpers ──────────────────────────────────────────────────────────────────

def _sep() -> QFrame:
    f = QFrame(); f.setFixedHeight(1)
    f.setStyleSheet(f"background: {COLOR_BORDER}; border: none;")
    return f


def _stat_card(label: str, value: str, bg: str, fg: str) -> QFrame:
    card = QFrame()
    card.setStyleSheet(f"""
        QFrame {{ background: {bg}; border: 1px solid rgba(0,0,0,0.06);
                 border-radius: 10px; border: none; }}
        QLabel {{ background: transparent; border: none; }}
    """)
    lay = QVBoxLayout(card); lay.setContentsMargins(14, 12, 14, 12); lay.setSpacing(4)
    lbl_label = QLabel(label)
    lbl_label.setStyleSheet(f"color: {FG_MUTED}; font-size: 11px; font-weight: 600;")
    lbl_value = QLabel(value)
    lbl_value.setStyleSheet(f"color: {fg}; font-size: 15px; font-weight: 700;")
    lay.addWidget(lbl_label); lay.addWidget(lbl_value)
    return card
