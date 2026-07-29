"""
Dual-Channel RTL Analyzer
オーディオ機器単体の純粋な処理レイテンシーを自動測定するデスクトップアプリケーション

接続方法:
  L OUT → L IN (基準チャンネル・直結)
  R OUT → 測定対象機材 → R IN (測定チャンネル)

Author: Generated with PySide6, sounddevice, numpy, scipy, matplotlib
"""

import sys
import os
import csv
import datetime
import time
import traceback
from pathlib import Path

import numpy as np
from scipy import signal as sp_signal

import sounddevice as sd

import matplotlib
matplotlib.use("QtAgg")
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

# Matplotlibフォント設定 (日本語文字化け防止: Windows向け)
_JP_FONT_CANDIDATES = ["Yu Gothic", "Meiryo", "MS Gothic", "Hiragino Sans",
                        "Noto Sans CJK JP", "DejaVu Sans"]
for _f in _JP_FONT_CANDIDATES:
    try:
        matplotlib.font_manager.findfont(_f, fallback_to_default=False)
        matplotlib.rcParams["font.family"] = _f
        break
    except Exception:
        pass
matplotlib.rcParams["axes.unicode_minus"] = False

from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QFormLayout, QGridLayout, QLabel, QLineEdit, QComboBox,
    QPushButton, QProgressBar, QDialog, QScrollArea,
    QGroupBox, QSizePolicy, QMessageBox, QFrame, QSplitter,
    QSpacerItem, QButtonGroup
)
from PySide6.QtCore import (
    Qt, QThread, Signal, QObject, QSize, QRect, QPointF, QRectF
)
from PySide6.QtGui import (
    QPainter, QPen, QColor, QFont, QBrush, QPainterPath,
    QLinearGradient, QPixmap, QPalette
)


# ---------------------------------------------------------------------------
# カラーパレット & スタイル定数
# ---------------------------------------------------------------------------
COLORS = {
    "bg_dark":        "#0D1117",
    "bg_medium":      "#161B22",
    "bg_light":       "#21262D",
    "bg_card":        "#1C2128",
    "accent_blue":    "#58A6FF",
    "accent_purple":  "#BC8CFF",
    "accent_green":   "#3FB950",
    "accent_orange":  "#D29922",
    "accent_red":     "#F85149",
    "accent_cyan":    "#39D353",
    "text_primary":   "#E6EDF3",
    "text_secondary": "#8B949E",
    "text_muted":     "#484F58",
    "border":         "#30363D",
    "border_hover":   "#58A6FF",
    "l_ch_color":     "#58A6FF",
    "r_ch_color":     "#BC8CFF",
}

APP_STYLESHEET = f"""
QMainWindow, QWidget {{
    background-color: {COLORS['bg_dark']};
    color: {COLORS['text_primary']};
    font-family: 'Segoe UI', 'Helvetica Neue', Arial, sans-serif;
    font-size: 13px;
}}

QGroupBox {{
    background-color: {COLORS['bg_card']};
    border: 1px solid {COLORS['border']};
    border-radius: 8px;
    margin-top: 16px;
    padding: 12px 8px 8px 8px;
    font-weight: 600;
    font-size: 12px;
    color: {COLORS['text_secondary']};
    letter-spacing: 0.5px;
}}
QGroupBox::title {{
    subcontrol-origin: margin;
    subcontrol-position: top left;
    padding: 0 8px;
    left: 12px;
    top: 3px;
    color: {COLORS['accent_blue']};
}}

QComboBox {{
    background-color: {COLORS['bg_light']};
    border: 1px solid {COLORS['border']};
    border-radius: 6px;
    padding: 6px 12px;
    color: {COLORS['text_primary']};
    min-height: 28px;
    selection-background-color: {COLORS['accent_blue']};
}}
QComboBox:hover {{
    border-color: {COLORS['border_hover']};
}}
QComboBox:focus {{
    border-color: {COLORS['accent_blue']};
    outline: none;
}}
QComboBox::drop-down {{
    border: none;
    width: 24px;
}}
QComboBox::down-arrow {{
    image: none;
    border-left: 5px solid transparent;
    border-right: 5px solid transparent;
    border-top: 6px solid {COLORS['text_secondary']};
    width: 0;
    height: 0;
    margin-right: 8px;
}}
QComboBox QAbstractItemView {{
    background-color: {COLORS['bg_medium']};
    border: 1px solid {COLORS['border']};
    border-radius: 6px;
    selection-background-color: {COLORS['accent_blue']};
    color: {COLORS['text_primary']};
    padding: 4px;
}}

QLineEdit {{
    background-color: {COLORS['bg_light']};
    border: 1px solid {COLORS['border']};
    border-radius: 6px;
    padding: 6px 12px;
    color: {COLORS['text_primary']};
    min-height: 28px;
    selection-background-color: {COLORS['accent_blue']};
}}
QLineEdit:hover {{
    border-color: {COLORS['border_hover']};
}}
QLineEdit:focus {{
    border-color: {COLORS['accent_blue']};
    outline: none;
}}

QPushButton {{
    background-color: {COLORS['bg_light']};
    border: 1px solid {COLORS['border']};
    border-radius: 6px;
    padding: 8px 20px;
    color: {COLORS['text_primary']};
    font-weight: 500;
    min-height: 32px;
}}
QPushButton:hover {{
    background-color: {COLORS['bg_medium']};
    border-color: {COLORS['accent_blue']};
    color: {COLORS['accent_blue']};
}}
QPushButton:pressed {{
    background-color: {COLORS['bg_dark']};
}}
QPushButton:disabled {{
    color: {COLORS['text_muted']};
    border-color: {COLORS['text_muted']};
    background-color: {COLORS['bg_dark']};
}}

QPushButton#btn_measure {{
    background-color: {COLORS['accent_blue']};
    border: none;
    color: {COLORS['bg_dark']};
    font-weight: 700;
    font-size: 14px;
    border-radius: 8px;
    min-height: 40px;
    padding: 10px 32px;
}}
QPushButton#btn_measure:hover {{
    background-color: #79BAFF;
    color: {COLORS['bg_dark']};
}}
QPushButton#btn_measure:disabled {{
    background-color: {COLORS['text_muted']};
    color: {COLORS['bg_dark']};
}}

QPushButton#btn_level {{
    background-color: transparent;
    border: 1px solid {COLORS['accent_purple']};
    color: {COLORS['accent_purple']};
    border-radius: 6px;
    min-height: 36px;
    padding: 8px 20px;
    font-weight: 500;
}}
QPushButton#btn_level:hover {{
    background-color: rgba(188, 140, 255, 0.1);
}}
QPushButton#btn_level:disabled {{
    color: {COLORS['text_muted']};
    border-color: {COLORS['text_muted']};
}}

QPushButton#btn_csv, QPushButton#btn_png {{
    background-color: transparent;
    border: 1px solid {COLORS['border']};
    color: {COLORS['text_secondary']};
    border-radius: 6px;
    font-size: 12px;
    padding: 6px 16px;
    min-height: 30px;
}}
QPushButton#btn_csv:hover, QPushButton#btn_png:hover {{
    border-color: {COLORS['accent_green']};
    color: {COLORS['accent_green']};
    background-color: rgba(63, 185, 80, 0.1);
}}
QPushButton#btn_csv:disabled, QPushButton#btn_png:disabled {{
    color: {COLORS['text_muted']};
    border-color: {COLORS['text_muted']};
}}

QProgressBar {{
    background-color: {COLORS['bg_dark']};
    border: 1px solid {COLORS['border']};
    border-radius: 4px;
    text-align: center;
    color: {COLORS['text_primary']};
    font-size: 11px;
    min-height: 16px;
    max-height: 16px;
}}
QProgressBar::chunk {{
    background-color: qlineargradient(
        x1:0, y1:0, x2:1, y2:0,
        stop:0 {COLORS['accent_blue']},
        stop:1 {COLORS['accent_purple']}
    );
    border-radius: 3px;
}}

QScrollArea {{
    border: none;
    background-color: transparent;
}}
QScrollBar:vertical {{
    background: {COLORS['bg_dark']};
    width: 8px;
    border-radius: 4px;
}}
QScrollBar::handle:vertical {{
    background: {COLORS['border']};
    border-radius: 4px;
    min-height: 20px;
}}
QScrollBar::handle:vertical:hover {{
    background: {COLORS['text_secondary']};
}}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
    height: 0;
}}

QFrame#separator {{
    background-color: {COLORS['border']};
    max-height: 1px;
    min-height: 1px;
}}
"""


# ---------------------------------------------------------------------------
# 接続解説ダイアログ
# ---------------------------------------------------------------------------
class ConnectionDiagramWidget(QWidget):
    """QPainterで接続概念図を描画するウィジェット"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumSize(680, 380)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        w = self.width()
        h = self.height()

        # 背景
        painter.fillRect(0, 0, w, h, QColor(COLORS["bg_medium"]))

        font_label = QFont("Segoe UI", 9, QFont.Bold)
        font_small  = QFont("Segoe UI", 8)
        font_ch     = QFont("Segoe UI", 8, QFont.Bold)
        font_title  = QFont("Segoe UI", 10, QFont.Bold)

        ai_w, ai_h    = 130, 110
        dut_w, dut_h  = 120, 70
        block_r       = 8

        ai_x   = 40
        dut_x  = (w - dut_w) // 2
        ai2_x  = w - ai_w - 40

        # ブロックY座標
        ai_l_y = 60
        r_y    = 240
        dut_y  = r_y - 10
        ai_r_y = r_y - 15

        # AI (送出側) ブロック
        grad1 = QLinearGradient(ai_x, ai_l_y, ai_x + ai_w, ai_l_y + ai_h)
        grad1.setColorAt(0, QColor("#1E3A5F"))
        grad1.setColorAt(1, QColor("#0D2137"))
        painter.setBrush(QBrush(grad1))
        painter.setPen(QPen(QColor(COLORS["accent_blue"]), 2))
        painter.drawRoundedRect(ai_x, ai_l_y, ai_w, ai_h, block_r, block_r)

        painter.setFont(font_title)
        painter.setPen(QColor(COLORS["accent_blue"]))
        painter.drawText(QRect(ai_x, ai_l_y + 6, ai_w, 22),
                         Qt.AlignHCenter | Qt.AlignVCenter, "Audio Interface")
        painter.setFont(font_small)
        painter.setPen(QColor(COLORS["text_secondary"]))
        painter.drawText(QRect(ai_x, ai_l_y + 26, ai_w, 16),
                         Qt.AlignHCenter | Qt.AlignVCenter, "(送出側)")

        # ポート描画ヘルパー
        def draw_port_right(px, py, label, color):
            painter.setPen(QPen(QColor(color), 1.5))
            painter.setBrush(QBrush(QColor(color)))
            painter.drawEllipse(px - 5, py - 5, 10, 10)
            painter.setFont(font_ch)
            painter.setPen(QColor(color))
            painter.drawText(QRect(px - 58, py - 10, 50, 20),
                             Qt.AlignRight | Qt.AlignVCenter, label)

        def draw_port_left(px, py, label, color):
            painter.setPen(QPen(QColor(color), 1.5))
            painter.setBrush(QBrush(QColor(color)))
            painter.drawEllipse(px - 5, py - 5, 10, 10)
            painter.setFont(font_ch)
            painter.setPen(QColor(color))
            painter.drawText(QRect(px + 10, py - 10, 60, 20),
                             Qt.AlignLeft | Qt.AlignVCenter, label)

        # 送出ポート
        out_l_x = ai_x + ai_w
        out_l_y = ai_l_y + 50
        out_r_x = ai_x + ai_w
        out_r_y = ai_l_y + 80
        draw_port_right(out_l_x, out_l_y, "L OUT", COLORS["l_ch_color"])
        draw_port_right(out_r_x, out_r_y, "R OUT", COLORS["r_ch_color"])

        # AI (受音側) ブロック
        grad2 = QLinearGradient(ai2_x, ai_r_y, ai2_x + ai_w, ai_r_y + ai_h)
        grad2.setColorAt(0, QColor("#1E3A5F"))
        grad2.setColorAt(1, QColor("#0D2137"))
        painter.setBrush(QBrush(grad2))
        painter.setPen(QPen(QColor(COLORS["accent_blue"]), 2))
        painter.drawRoundedRect(ai2_x, ai_r_y, ai_w, ai_h, block_r, block_r)

        painter.setFont(font_title)
        painter.setPen(QColor(COLORS["accent_blue"]))
        painter.drawText(QRect(ai2_x, ai_r_y + 6, ai_w, 22),
                         Qt.AlignHCenter | Qt.AlignVCenter, "Audio Interface")
        painter.setFont(font_small)
        painter.setPen(QColor(COLORS["text_secondary"]))
        painter.drawText(QRect(ai2_x, ai_r_y + 26, ai_w, 16),
                         Qt.AlignHCenter | Qt.AlignVCenter, "(受音側)")

        # 受音ポート
        in_l_x = ai2_x
        in_l_y = ai_r_y + 50
        in_r_x = ai2_x
        in_r_y = ai_r_y + 80
        draw_port_left(in_l_x, in_l_y, "L IN", COLORS["l_ch_color"])
        draw_port_left(in_r_x, in_r_y, "R IN", COLORS["r_ch_color"])

        # DUT ブロック
        grad3 = QLinearGradient(dut_x, dut_y, dut_x + dut_w, dut_y + dut_h)
        grad3.setColorAt(0, QColor("#3D1A5E"))
        grad3.setColorAt(1, QColor("#1E0A30"))
        painter.setBrush(QBrush(grad3))
        painter.setPen(QPen(QColor(COLORS["accent_purple"]), 2))
        painter.drawRoundedRect(dut_x, dut_y, dut_w, dut_h, block_r, block_r)

        painter.setFont(font_title)
        painter.setPen(QColor(COLORS["accent_purple"]))
        painter.drawText(QRect(dut_x, dut_y + 4, dut_w, 24),
                         Qt.AlignHCenter | Qt.AlignVCenter, "DUT")
        painter.setFont(font_small)
        painter.setPen(QColor(COLORS["text_secondary"]))
        painter.drawText(QRect(dut_x, dut_y + 26, dut_w, 18),
                         Qt.AlignHCenter | Qt.AlignVCenter, "(測定対象機材)")

        dut_in_x  = dut_x
        dut_in_y  = dut_y + dut_h // 2
        dut_out_x = dut_x + dut_w
        dut_out_y = dut_y + dut_h // 2
        draw_port_left(dut_in_x, dut_in_y, "IN", COLORS["accent_purple"])
        draw_port_right(dut_out_x, dut_out_y, "OUT", COLORS["accent_purple"])

        # 配線 — ブラシをリセットして塗りつぶしを防止
        pen_l = QPen(QColor(COLORS["l_ch_color"]), 2.5, Qt.SolidLine)
        pen_r = QPen(QColor(COLORS["r_ch_color"]), 2.5, Qt.SolidLine)
        painter.setBrush(Qt.NoBrush)

        # L ch 配線 (直結) — strokePathで線のみ描画
        painter.setPen(pen_l)
        mid_l_y = out_l_y - 30
        path_l = QPainterPath()
        path_l.moveTo(out_l_x, out_l_y)
        path_l.lineTo(out_l_x + 36, out_l_y)
        path_l.lineTo(out_l_x + 36, mid_l_y)
        path_l.lineTo(in_l_x - 36, mid_l_y)
        path_l.lineTo(in_l_x - 36, in_l_y)
        path_l.lineTo(in_l_x, in_l_y)
        painter.strokePath(path_l, pen_l)
        self._draw_arrow(painter, pen_l,
                         QPointF(in_l_x - 12, in_l_y),
                         QPointF(in_l_x, in_l_y))
        painter.setBrush(Qt.NoBrush)

        lbl_mid_x = (out_l_x + in_l_x) // 2
        painter.setFont(font_label)
        painter.setPen(QColor(COLORS["l_ch_color"]))
        painter.drawText(QRect(lbl_mid_x - 85, mid_l_y - 22, 170, 18),
                         Qt.AlignHCenter, "Direct / 直結 (Ref)")

        # R ch: R OUT → DUT IN
        painter.setPen(pen_r)
        path_r1 = QPainterPath()
        path_r1.moveTo(out_r_x, out_r_y)
        path_r1.lineTo(dut_in_x, dut_in_y)
        painter.strokePath(path_r1, pen_r)
        self._draw_arrow(painter, pen_r,
                         QPointF(dut_in_x - 12, dut_in_y),
                         QPointF(dut_in_x, dut_in_y))
        painter.setBrush(Qt.NoBrush)

        # R ch: DUT OUT → R IN
        painter.setPen(pen_r)
        path_r2 = QPainterPath()
        path_r2.moveTo(dut_out_x, dut_out_y)
        path_r2.lineTo(in_r_x, in_r_y)
        painter.strokePath(path_r2, pen_r)
        self._draw_arrow(painter, pen_r,
                         QPointF(in_r_x - 12, in_r_y),
                         QPointF(in_r_x, in_r_y))
        painter.setBrush(Qt.NoBrush)

        mid_x_r1 = (out_r_x + dut_in_x) // 2
        mid_y_r1 = (out_r_y + dut_in_y) // 2
        painter.setFont(font_label)
        painter.setPen(QColor(COLORS["r_ch_color"]))
        painter.drawText(QRect(int(mid_x_r1) - 60, int(mid_y_r1) - 20, 120, 16),
                         Qt.AlignHCenter, "DUT Path / 測定対象")

        # 凡例
        legend_x, legend_y = 40, h - 50
        painter.setPen(pen_l)
        painter.drawLine(legend_x, legend_y + 6, legend_x + 30, legend_y + 6)
        painter.setFont(font_small)
        painter.setPen(QColor(COLORS["l_ch_color"]))
        painter.drawText(legend_x + 36, legend_y + 11,
                         "L ch : Reference / 基準信号（直結）")

        painter.setPen(pen_r)
        painter.drawLine(legend_x, legend_y + 26, legend_x + 30, legend_y + 26)
        painter.setPen(QColor(COLORS["r_ch_color"]))
        painter.drawText(legend_x + 36, legend_y + 31,
                         "R ch : DUT Signal / 測定信号（DUT経由）")

    def _draw_arrow(self, painter, pen, p1, p2):
        dx = p2.x() - p1.x()
        dy = p2.y() - p1.y()
        length = (dx**2 + dy**2) ** 0.5
        if length < 1e-6:
            return
        ux, uy = dx / length, dy / length
        arr_len, arr_half = 10, 5
        ax = p2.x() - ux * arr_len
        ay = p2.y() - uy * arr_len
        px = -uy * arr_half
        py =  ux * arr_half
        painter.setPen(pen)
        painter.setBrush(QBrush(pen.color()))
        path = QPainterPath()
        path.moveTo(p2)
        path.lineTo(ax + px, ay + py)
        path.lineTo(ax - px, ay - py)
        path.closeSubpath()
        painter.drawPath(path)


class SetupDialog(QDialog):
    """測定環境の構築ダイアログ"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("測定環境の構築 / Measurement Setup")
        self.setMinimumSize(740, 600)
        self.setModal(True)
        self.setStyleSheet(f"QDialog {{ background-color: {COLORS['bg_dark']}; }}")
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(16)
        layout.setContentsMargins(24, 24, 24, 24)

        title = QLabel("測定環境の構築 / Measurement Setup")
        title.setStyleSheet(
            f"font-size: 20px; font-weight: 700; color: {COLORS['text_primary']};"
        )
        layout.addWidget(title)

        diagram = ConnectionDiagramWidget()
        diagram.setMinimumHeight(360)
        layout.addWidget(diagram)

        info_frame = QFrame()
        info_frame.setStyleSheet(f"""
            QFrame {{
                background-color: {COLORS['bg_light']};
                border: 1px solid {COLORS['border']};
                border-radius: 8px;
            }}
        """)
        info_layout = QVBoxLayout(info_frame)
        info_layout.setContentsMargins(16, 12, 16, 12)
        info_layout.setSpacing(8)

        instructions = [
            ("① L ch (基準 / Reference)", COLORS["l_ch_color"],
             "Connect L OUT → L IN with a short cable (direct / 直結). "
             "This signal serves as the timing reference for onset detection."),
            ("② R ch (測定対象 / DUT)", COLORS["r_ch_color"],
             "Connect R OUT → DUT Input → DUT Output → R IN. "
             "The processing latency of the DUT is measured along this path."),
            ("③ 注意事項 / Note", COLORS["accent_orange"],
             'Run “Level Check” and confirm both L/R ch levels are in range '
             '(-36 dBFS to -1 dBFS) before starting measurement.'),
        ]

        for heading, color, text in instructions:
            row = QHBoxLayout()
            lbl_head = QLabel(heading)
            lbl_head.setStyleSheet(
                f"color: {color}; font-weight: 700; font-size: 12px; min-width: 165px;"
            )
            lbl_head.setAlignment(Qt.AlignTop)
            lbl_text = QLabel(text)
            lbl_text.setWordWrap(True)
            lbl_text.setStyleSheet(
                f"color: {COLORS['text_secondary']}; font-size: 12px;"
            )
            row.addWidget(lbl_head)
            row.addWidget(lbl_text, 1)
            info_layout.addLayout(row)

        layout.addWidget(info_frame)

        btn_close = QPushButton("Close")
        btn_close.setFixedWidth(120)
        btn_close.clicked.connect(self.accept)
        row_btn = QHBoxLayout()
        row_btn.addStretch()
        row_btn.addWidget(btn_close)
        layout.addLayout(row_btn)


# ---------------------------------------------------------------------------
# Matplotlib 波形プロット
# ---------------------------------------------------------------------------
class WaveformCanvas(FigureCanvas):
    """L/R ch 波形を上下2段で表示する Matplotlib キャンバス"""

    def __init__(self, parent=None):
        self.fig = Figure(figsize=(10, 5), dpi=100, facecolor=COLORS["bg_card"])
        super().__init__(self.fig)
        self.setParent(parent)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.setMinimumHeight(300)
        self._last_plot_params = None
        self._init_axes()

    def _init_axes(self):
        self.fig.clear()
        self.ax_l, self.ax_r = self.fig.subplots(2, 1, sharex=True)
        for ax in (self.ax_l, self.ax_r):
            ax.set_facecolor(COLORS["bg_medium"])
            ax.tick_params(colors=COLORS["text_secondary"], labelsize=9)
            for spine in ax.spines.values():
                spine.set_edgecolor(COLORS["border"])
            ax.grid(True, color=COLORS["border"], linewidth=0.5, alpha=0.8)

        self.ax_l.set_ylabel("Amplitude", color=COLORS["text_secondary"], fontsize=9)
        self.ax_r.set_ylabel("Amplitude", color=COLORS["text_secondary"], fontsize=9)
        self.ax_r.set_xlabel("Time (ms)", color=COLORS["text_secondary"], fontsize=9)
        self.ax_l.set_title("L ch (Reference / 基準信号)",
                             color=COLORS["l_ch_color"], fontsize=10, pad=6, fontweight="bold")
        self.ax_r.set_title("R ch (DUT / 測定信号)",
                             color=COLORS["r_ch_color"], fontsize=10, pad=6, fontweight="bold")
        self.fig.text(0.5, 0.97, "— 波形プロット (測定後に表示されます / Waveform Plot) —",
                      ha="center", va="top",
                      color=COLORS["text_muted"], fontsize=9)
        self.fig.tight_layout(rect=[0, 0, 1, 0.97])
        self.draw()

    def plot_waveforms(self, l_data: np.ndarray, r_data: np.ndarray,
                       sample_rate: int, delta_samples: int, latency_ms: float,
                       l_onset_idx: int = None, r_onset_idx: int = None,
                       device_name: str = "—",
                       scale_factor: float = 1.0):
        self._last_plot_params = (l_data, r_data, sample_rate, delta_samples, latency_ms,
                                  l_onset_idx, r_onset_idx, device_name)
        self.fig.clear()
        self.ax_l, self.ax_r = self.fig.subplots(2, 1, sharex=True)

        for ax in (self.ax_l, self.ax_r):
            ax.set_facecolor(COLORS["bg_medium"])
            ax.tick_params(colors=COLORS["text_secondary"], labelsize=9)
            for spine in ax.spines.values():
                spine.set_edgecolor(COLORS["border"])
            ax.grid(True, color=COLORS["border"], linewidth=0.5, alpha=0.7)

        n_samples = len(l_data)

        # ── オンセット位置 (フォールバック: ピーク) ──
        if l_onset_idx is None:
            l_onset_idx = int(np.argmax(np.abs(l_data)))
        if r_onset_idx is None:
            r_onset_idx = int(np.argmax(np.abs(r_data)))

        # 基準信号(L ch検出位置)を 0.0 ms とした時間軸
        time_ms = (np.arange(n_samples) - l_onset_idx) / sample_rate * 1000.0
        l_onset_ms = 0.0
        r_onset_ms = (r_onset_idx - l_onset_idx) / sample_rate * 1000.0

        # ── 横軸スパン計算 (L onset を画面左から20%に固定し、scale_factor でスパンを拡大)
        onset_diff = r_onset_ms - l_onset_ms
        if onset_diff > 0:
            base_span = onset_diff / 0.40
        else:
            base_span = max(10.0, time_ms[-1] - time_ms[0])

        current_span = base_span * scale_factor
        x_min = -0.20 * current_span
        x_max = x_min + current_span
        x_min = max(x_min, time_ms[0])
        x_max = min(x_max, time_ms[-1])

        # L ch プロット
        self.ax_l.plot(time_ms, l_data,
                       color=COLORS["l_ch_color"], linewidth=0.9, alpha=0.9)
        self.ax_l.set_ylabel("Amplitude", color=COLORS["text_secondary"], fontsize=9)
        self.ax_l.set_title("L ch (Ref / 基準)",
                             color=COLORS["l_ch_color"], fontsize=10, pad=6, fontweight="bold")
        self.ax_l.set_ylim(-1.1, 1.1)
        self.ax_l.set_xlim(x_min, x_max)

        # R ch プロット
        self.ax_r.plot(time_ms, r_data,
                       color=COLORS["r_ch_color"], linewidth=0.9, alpha=0.9)
        self.ax_r.set_ylabel("Amplitude", color=COLORS["text_secondary"], fontsize=9)
        self.ax_r.set_xlabel("Time (ms)", color=COLORS["text_secondary"], fontsize=9)
        self.ax_r.set_title("R ch (DUT / 測定)",
                             color=COLORS["r_ch_color"], fontsize=10, pad=6, fontweight="bold")
        self.ax_r.set_ylim(-1.1, 1.1)
        self.ax_r.set_xlim(x_min, x_max)

        # L ch オンセット縦線 (赤破線) — L ch の立ち上がり
        for ax in (self.ax_l, self.ax_r):
            ax.axvline(l_onset_ms, color=COLORS["accent_red"],
                       linewidth=1.4, linestyle="--", alpha=0.9,
                       label="L onset (Ref)")

        # R ch オンセット縦線 (オレンジ破線) — R ch の立ち上がり
        for ax in (self.ax_l, self.ax_r):
            ax.axvline(r_onset_ms, color="#FF8C69",
                       linewidth=1.4, linestyle="--", alpha=0.9,
                       label="R onset (DUT)")

        # 注釈テキスト
        visible_span = x_max - x_min
        ann_offset   = visible_span * 0.04
        ann_x = r_onset_ms + ann_offset
        if ann_x > x_min + visible_span * 0.80:
            ann_x = r_onset_ms - ann_offset * 5
            arrow_style = "<-"
        else:
            arrow_style = "->"

        ann_y = 0.72
        self.ax_r.annotate(
            f"  onset delta = {delta_samples} samples\n  Latency = {latency_ms:.3f} ms",
            xy=(r_onset_ms, ann_y),
            xytext=(ann_x, ann_y),
            fontsize=9,
            color=COLORS["accent_orange"],
            fontweight="bold",
            arrowprops=dict(arrowstyle=arrow_style,
                            color=COLORS["accent_orange"], lw=1.2),
            bbox=dict(boxstyle="round,pad=0.4", facecolor=COLORS["bg_dark"],
                      edgecolor=COLORS["accent_orange"], alpha=0.88)
        )

        self.fig.tight_layout(rect=[0, 0, 1, 0.93])
        self.fig.text(
            0.5, 0.99,
            f"Device: {device_name}",
            ha="center", va="top",
            color=COLORS["accent_blue"], fontsize=11, fontweight="bold"
        )
        self.fig.text(
            0.5, 0.965,
            f"Best trial latency: {latency_ms:.3f} ms",
            ha="center", va="top",
            color=COLORS["text_secondary"], fontsize=9
        )
        self.draw()

    def set_scale(self, scale_factor: float):
        if self._last_plot_params is not None:
            self.plot_waveforms(*self._last_plot_params, scale_factor=scale_factor)


# ---------------------------------------------------------------------------
# 測定ワーカー (QThread)
# ---------------------------------------------------------------------------
class MeasureWorker(QThread):
    """非同期測定処理スレッド"""

    progress    = Signal(int, str)
    trial_done  = Signal(int, float, int, int, np.ndarray, np.ndarray)
    finished_ok = Signal(list)
    error       = Signal(str)

    def __init__(self, in_dev: int, out_dev: int,
                 sample_rate: int, trials: int, interval: float,
                 trigger_percent: float = 0.01):
        super().__init__()
        self.in_dev          = in_dev
        self.out_dev         = out_dev
        self.sample_rate     = sample_rate
        self.trials          = trials
        self.interval        = interval
        self.trigger_percent = trigger_percent   # R ch のピーク対比閾値 (0.0≤1.0)
        self._stop_flag      = False

    def stop(self):
        self._stop_flag = True

    def _make_signal(self) -> np.ndarray:
        duration_samples = max(int(self.sample_rate * 0.5), 24000)
        buf = np.zeros((duration_samples, 2), dtype=np.float32)

        click_len = max(int(self.sample_rate * 0.001), 8)
        t = np.linspace(-3, 3, click_len)
        click = np.exp(-t**2).astype(np.float32)
        click /= np.max(np.abs(click))

        offset = 16
        end    = offset + click_len
        buf[offset:end, 0] = click
        buf[offset:end, 1] = click
        return buf

    @staticmethod
    def _find_onset(signal: np.ndarray,
                    search_start: int = 0,
                    trigger_percent: float = 0.01) -> int:
        """
        信号ピークに対する割合 trigger_percent で閾値を計算し、
        search_start 以降で最初に閾値を超えるサンプルを返す。
        ノイズ倒而に依存せず、DUT 信号の大きさに相対的な判定であるため、
        ノイズ環境に左右されない。
        """
        region = np.abs(signal[search_start:])
        if len(region) == 0:
            return search_start

        sig_peak  = float(np.max(region))
        threshold = max(sig_peak * trigger_percent, 1e-6)

        above = np.where(region > threshold)[0]

        if len(above) == 0:
            return search_start + int(np.argmax(region))

        return search_start + int(above[0])

    def _calc_latency(self, rec: np.ndarray):
        """
        L ch / R ch ともオンセット検出で遅延を計算。

        両 ch ともピークパーセンテージ閾値で検出。
        - L ch (基準ガウシアン): 常に 1% 固定（ガウシアンは明確な信号のため精度十分）
        - R ch (DUT):  UIで設定した trigger_percent を使用
        - 両者共オンセット検出にすることでガウシアン立ち上がり時間（絇0.5ms）の
          系統誤差を相殮させる。
        →  Latency = R_onset − L_onset
        """
        l_ch = rec[:, 0].astype(np.float64)
        r_ch = rec[:, 1].astype(np.float64)

        # L ch: オンセット検出 - ガウシアンは明確なので 1% 固定
        l_onset = self._find_onset(l_ch,
                                   search_start=0,
                                   trigger_percent=0.01)

        # R ch: オンセット検出 - UIで設定した閾値割合を使用、l_onset 以降を検索
        r_onset = self._find_onset(r_ch,
                                   search_start=l_onset,
                                   trigger_percent=self.trigger_percent)

        delta_n    = max(0, r_onset - l_onset)
        latency_ms = (delta_n / self.sample_rate) * 1000.0
        return latency_ms, delta_n, l_onset, r_onset

    def run(self):
        latencies = []
        sig = self._make_signal()

        for i in range(self.trials):
            if self._stop_flag:
                break

            self.progress.emit(i, f"Trial {i + 1} / {self.trials}...")

            try:
                rec = sd.playrec(
                    sig,
                    samplerate=self.sample_rate,
                    channels=2,
                    input_mapping=[1, 2],
                    output_mapping=[1, 2],
                    device=(self.in_dev, self.out_dev),
                    dtype="float32",
                    blocking=True
                )
            except Exception as e:
                self.error.emit(f"Audio Error (Trial {i + 1}):\n{e}")
                return

            try:
                latency_ms, delta_n, l_onset, r_onset = self._calc_latency(rec)
            except Exception as e:
                self.error.emit(f"Analysis Error (Trial {i + 1}):\n{e}")
                return

            latencies.append(latency_ms)
            self.trial_done.emit(i, latency_ms, l_onset, r_onset,
                                 rec[:, 0].copy(), rec[:, 1].copy())

            if i < self.trials - 1 and not self._stop_flag:
                time.sleep(self.interval)

        if latencies:
            self.finished_ok.emit(latencies)
        else:
            self.error.emit("No valid data acquired.")


class LevelCheckWorker(QThread):
    """レベルチェック用ワーカー"""

    result = Signal(float, float)
    error  = Signal(str)

    def __init__(self, in_dev: int, out_dev: int, sample_rate: int):
        super().__init__()
        self.in_dev      = in_dev
        self.out_dev     = out_dev
        self.sample_rate = sample_rate

    def run(self):
        duration_sec = 0.5
        n_samples    = int(self.sample_rate * duration_sec)

        t   = np.linspace(0, duration_sec, n_samples, endpoint=False)
        ref = (np.sin(2 * np.pi * 1000 * t) * 0.25).astype(np.float32)
        sig = np.column_stack([ref, ref])

        try:
            rec = sd.playrec(
                sig,
                samplerate=self.sample_rate,
                channels=2,
                input_mapping=[1, 2],
                output_mapping=[1, 2],
                device=(self.in_dev, self.out_dev),
                dtype="float32",
                blocking=True
            )
        except Exception as e:
            self.error.emit(f"Level Check Error:\n{e}")
            return

        def peak_dbfs(ch_data):
            peak = np.max(np.abs(ch_data))
            return float(20 * np.log10(max(peak, 1e-9)))

        self.result.emit(peak_dbfs(rec[:, 0]), peak_dbfs(rec[:, 1]))


# ---------------------------------------------------------------------------
# メインウィンドウ
# ---------------------------------------------------------------------------
class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Dual-Channel RTL Analyzer")
        self.setMinimumSize(1080, 820)
        self.resize(1200, 900)

        self._latencies:   list[float]                          = []
        self._trial_waves: list[tuple[float, np.ndarray, np.ndarray]] = []
        self._sample_rate: int                                  = 48000
        self._worker:      MeasureWorker | None                 = None
        self._level_worker: LevelCheckWorker | None             = None

        self._build_ui()
        self._refresh_devices()

    # ------------------------------------------------------------------ UI --
    def _build_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        root = QVBoxLayout(central)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        root.addWidget(scroll)

        content = QWidget()
        scroll.setWidget(content)
        lay = QVBoxLayout(content)
        lay.setContentsMargins(20, 16, 20, 20)
        lay.setSpacing(14)

        lay.addWidget(self._build_header())

        sep = QFrame(); sep.setObjectName("separator")
        lay.addWidget(sep)

        top_row = QHBoxLayout()
        top_row.setSpacing(14)
        top_row.addWidget(self._build_config_zone(), 3)
        top_row.addWidget(self._build_control_zone(), 2)
        lay.addLayout(top_row)

        lay.addWidget(self._build_level_zone())
        lay.addWidget(self._build_results_zone())
        lay.addWidget(self._build_waveform_zone())
        lay.addWidget(self._build_export_zone())

    def _build_header(self) -> QWidget:
        w = QWidget()
        lay = QHBoxLayout(w)
        lay.setContentsMargins(0, 4, 0, 4)

        col = QVBoxLayout(); col.setSpacing(2)
        t1 = QLabel(
            f'<span style="font-size:26px; font-weight:800; color:{COLORS["text_primary"]};">'
            'Dual-Channel RTL Analyzer</span>'
            '&nbsp;&nbsp;'
            '<a href="https://www.isamutheguitar.com"'
            ' style="font-size:13px; font-weight:500;'
            f' color:{COLORS["accent_blue"]}; text-decoration:none;">'
            'by ISAMU the Guitar</a>'
        )
        t1.setTextFormat(Qt.RichText)
        t1.setOpenExternalLinks(True)
        t2 = QLabel("Audio RTL Latency Measurement Tool / レイテンシー測定ツール")
        t2.setStyleSheet(f"font-size: 13px; color: {COLORS['text_secondary']};")
        col.addWidget(t1); col.addWidget(t2)
        lay.addLayout(col, 1)

        btn = QPushButton("⚙  測定環境の構築 / Setup")
        btn.setFixedHeight(40)
        btn.setStyleSheet(f"""
            QPushButton {{
                background-color: transparent;
                border: 1px solid {COLORS['accent_blue']};
                color: {COLORS['accent_blue']};
                border-radius: 8px;
                padding: 8px 20px;
                font-size: 13px; font-weight: 600;
            }}
            QPushButton:hover {{ background-color: rgba(88,166,255,0.12); }}
        """)
        btn.clicked.connect(self._show_setup_dialog)
        lay.addWidget(btn)
        return w

    def _build_config_zone(self) -> QGroupBox:
        box = QGroupBox("Configuration")
        form = QFormLayout(box)
        form.setSpacing(10)
        form.setContentsMargins(12, 20, 12, 12)
        form.setLabelAlignment(Qt.AlignRight | Qt.AlignVCenter)

        def lbl(t):
            l = QLabel(t)
            l.setStyleSheet(f"color: {COLORS['text_secondary']}; font-size: 12px;")
            return l

        self.edit_device_name = QLineEdit("Target_Device")
        form.addRow(lbl("Device Name:"), self.edit_device_name)

        self.combo_in = QComboBox(); self.combo_in.setMinimumWidth(220)
        form.addRow(lbl("Input Device:"), self.combo_in)

        self.combo_out = QComboBox()
        form.addRow(lbl("Output Device:"), self.combo_out)

        self.combo_sr = QComboBox()
        for sr in [44100, 48000, 88200, 96000, 192000]:
            self.combo_sr.addItem(f"{sr} Hz", sr)
        self.combo_sr.setCurrentIndex(1)
        form.addRow(lbl("Sample Rate:"), self.combo_sr)

        self.combo_trials = QComboBox()
        for t in [1, 3, 10, 30, 100]:
            self.combo_trials.addItem(str(t), t)
        self.combo_trials.setCurrentIndex(2)
        form.addRow(lbl("Trials:"), self.combo_trials)

        self.combo_interval = QComboBox()
        for label, val in [("0.5 s", 0.5), ("1.0 s", 1.0), ("2.0 s", 2.0), ("5.0 s", 5.0)]:
            self.combo_interval.addItem(label, val)
        self.combo_interval.setCurrentIndex(1)
        form.addRow(lbl("Interval:"), self.combo_interval)

        return box

    def _build_control_zone(self) -> QGroupBox:
        box = QGroupBox("Control")
        lay = QVBoxLayout(box)
        lay.setSpacing(10); lay.setContentsMargins(16, 20, 16, 16)

        # Trigger Option Row
        row_trig = QHBoxLayout()
        lbl_trig = QLabel("Trigger:")
        lbl_trig.setStyleSheet(f"color: {COLORS['text_secondary']}; font-size: 12px;")
        self.combo_trigger = QComboBox()
        for label, val in [
            ("Auto (1%)",  0.01),
            ("3%",         0.03),
            ("5%",         0.05),
            ("10%",        0.10),
            ("20%",        0.20),
            ("30%",        0.30),
        ]:
            self.combo_trigger.addItem(label, val)
        self.combo_trigger.setCurrentIndex(0)   # Auto (1%) がデフォルト
        row_trig.addWidget(lbl_trig)
        row_trig.addWidget(self.combo_trigger, 1)
        lay.addLayout(row_trig)

        self.btn_level = QPushButton("🎚  Level Check")
        self.btn_level.setObjectName("btn_level")
        self.btn_level.clicked.connect(self._start_level_check)
        lay.addWidget(self.btn_level)

        self.btn_measure = QPushButton("▶  Start Measurement")
        self.btn_measure.setObjectName("btn_measure")
        self.btn_measure.clicked.connect(self._toggle_measurement)
        lay.addWidget(self.btn_measure)

        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100); self.progress_bar.setValue(0)
        lay.addWidget(self.progress_bar)

        self.lbl_status = QLabel("待機中")
        self.lbl_status.setAlignment(Qt.AlignCenter)
        self.lbl_status.setStyleSheet(f"color: {COLORS['text_muted']}; font-size: 11px;")
        lay.addWidget(self.lbl_status)

        lay.addStretch()
        return box

    def _build_level_zone(self) -> QGroupBox:
        box = QGroupBox("Level Status")
        lay = QHBoxLayout(box)
        lay.setContentsMargins(16, 20, 16, 12); lay.setSpacing(24)

        def make_ch(label):
            col = QVBoxLayout(); col.setSpacing(4)
            lc = QLabel(label)
            lc.setStyleSheet(
                f"font-size: 11px; color: {COLORS['text_muted']}; font-weight: 600;"
            )
            lc.setAlignment(Qt.AlignCenter)
            ld = QLabel("--- dBFS")
            ld.setStyleSheet(
                f"font-size: 18px; font-weight: 700; color: {COLORS['text_secondary']};"
            )
            ld.setAlignment(Qt.AlignCenter)
            lm = QLabel("—")
            lm.setStyleSheet(f"font-size: 11px; color: {COLORS['text_muted']};")
            lm.setAlignment(Qt.AlignCenter); lm.setWordWrap(True)
            col.addWidget(lc); col.addWidget(ld); col.addWidget(lm)
            w = QWidget(); w.setLayout(col)
            return w, ld, lm

        wl, self.lbl_l_db, self.lbl_l_msg = make_ch("L ch (基準: Reference)")
        wr, self.lbl_r_db, self.lbl_r_msg = make_ch("R ch (測定対象: DUT)")
        sep = QFrame(); sep.setFrameShape(QFrame.VLine)
        sep.setStyleSheet(f"color: {COLORS['border']};")
        lay.addWidget(wl); lay.addWidget(sep); lay.addWidget(wr)
        return box

    def _build_results_zone(self) -> QGroupBox:
        box = QGroupBox("Measurement Results")
        outer = QVBoxLayout(box)
        outer.setContentsMargins(16, 20, 16, 16); outer.setSpacing(12)

        self.lbl_result_device = QLabel("—")
        self.lbl_result_device.setStyleSheet(
            f"font-size: 14px; font-weight: 600; color: {COLORS['accent_blue']}; padding: 4px 0;"
        )
        outer.addWidget(self.lbl_result_device)

        grid = QGridLayout(); grid.setSpacing(8)
        stats = [
            ("Mean",    "mean"),
            ("Max",     "max"),
            ("Min",     "min"),
            ("Std Dev", "std"),
        ]
        self._stat_labels: dict[str, QLabel] = {}

        for col_idx, (key, attr) in enumerate(stats):
            card = QFrame()
            card.setStyleSheet(f"""
                QFrame {{
                    background-color: {COLORS['bg_light']};
                    border: 1px solid {COLORS['border']};
                    border-radius: 8px;
                }}
            """)
            cl = QVBoxLayout(card); cl.setSpacing(2); cl.setContentsMargins(12, 10, 12, 10)

            lk = QLabel(key)
            lk.setStyleSheet(
                f"font-size: 10px; color: {COLORS['text_muted']}; font-weight: 600;"
            )
            lk.setAlignment(Qt.AlignCenter)

            lv = QLabel("—")
            lv.setAlignment(Qt.AlignCenter)
            lv.setStyleSheet(
                f"font-size: 22px; font-weight: 700; color: {COLORS['text_primary']};"
            )

            lu = QLabel("ms")
            lu.setAlignment(Qt.AlignCenter)
            lu.setStyleSheet(f"font-size: 11px; color: {COLORS['text_muted']};")

            cl.addWidget(lk); cl.addWidget(lv); cl.addWidget(lu)
            grid.addWidget(card, 0, col_idx)
            self._stat_labels[attr] = lv

        outer.addLayout(grid)
        return box

    def _build_waveform_zone(self) -> QGroupBox:
        box = QGroupBox("Waveform Plot")
        lay = QVBoxLayout(box); lay.setContentsMargins(12, 16, 12, 12); lay.setSpacing(10)

        # 時間軸拡縮ボタン行 (x1, x2, x4)
        row_scale = QHBoxLayout()
        lbl_scale = QLabel("Time Axis Span / 時間軸拡大:")
        lbl_scale.setStyleSheet(f"color: {COLORS['text_secondary']}; font-size: 12px; font-weight: 600;")
        row_scale.addWidget(lbl_scale)

        self.btn_scale_x1 = QPushButton("x1")
        self.btn_scale_x2 = QPushButton("x2")
        self.btn_scale_x4 = QPushButton("x4")

        self.btn_scale_group = QButtonGroup(self)
        self.btn_scale_group.setExclusive(True)

        for btn, factor in [(self.btn_scale_x1, 1.0), (self.btn_scale_x2, 2.0), (self.btn_scale_x4, 4.0)]:
            btn.setCheckable(True)
            btn.setFixedHeight(26)
            btn.setFixedWidth(54)
            btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: {COLORS['bg_medium']};
                    border: 1px solid {COLORS['border']};
                    color: {COLORS['text_secondary']};
                    border-radius: 4px;
                    font-size: 12px;
                    font-weight: 700;
                }}
                QPushButton:checked {{
                    background-color: {COLORS['accent_blue']};
                    color: #ffffff;
                    border: 1px solid {COLORS['accent_blue']};
                }}
                QPushButton:hover:!checked {{
                    background-color: rgba(88,166,255,0.18);
                    color: {COLORS['text_primary']};
                }}
            """)
            self.btn_scale_group.addButton(btn)
            row_scale.addWidget(btn)

        self.btn_scale_x1.setChecked(True)
        self.btn_scale_group.buttonClicked.connect(self._on_waveform_scale_changed)
        row_scale.addStretch()
        lay.addLayout(row_scale)

        self.canvas = WaveformCanvas()
        lay.addWidget(self.canvas)
        return box

    def _build_export_zone(self) -> QGroupBox:
        box = QGroupBox("Export")
        lay = QHBoxLayout(box); lay.setContentsMargins(16, 16, 16, 12); lay.setSpacing(12)

        self.btn_csv = QPushButton("📊  CSV")
        self.btn_csv.setObjectName("btn_csv"); self.btn_csv.setEnabled(False)
        self.btn_csv.clicked.connect(self._export_csv)

        self.btn_png = QPushButton("🖼  Waveform Image")
        self.btn_png.setObjectName("btn_png"); self.btn_png.setEnabled(False)
        self.btn_png.clicked.connect(self._export_png)

        lay.addWidget(self.btn_csv); lay.addWidget(self.btn_png); lay.addStretch()
        return box

    # --------------------------------------------------------- デバイス一覧 --
    def _refresh_devices(self):
        try:
            devices = sd.query_devices()
        except Exception as e:
            QMessageBox.critical(self, "デバイスエラー",
                                 f"オーディオデバイスを取得できませんでした:\n{e}")
            return

        self.combo_in.clear(); self.combo_out.clear()

        try:
            default_in  = sd.default.device[0]
            default_out = sd.default.device[1]
        except Exception:
            default_in = default_out = -1

        for idx, dev in enumerate(devices):
            name = f"[{idx}] {dev['name']}"
            if dev["max_input_channels"] > 0:
                self.combo_in.addItem(name, idx)
                if idx == default_in:
                    self.combo_in.setCurrentIndex(self.combo_in.count() - 1)
            if dev["max_output_channels"] > 0:
                self.combo_out.addItem(name, idx)
                if idx == default_out:
                    self.combo_out.setCurrentIndex(self.combo_out.count() - 1)

    # ------------------------------------------------------------ ダイアログ --
    def _show_setup_dialog(self):
        SetupDialog(self).exec()

    # -------------------------------------------------------- レベルチェック --
    def _start_level_check(self):
        in_idx, out_idx = self._get_device_indices()
        if in_idx is None:
            return

        self.btn_level.setEnabled(False)
        self.btn_measure.setEnabled(False)
        self.lbl_status.setText("Level Check running...")
        self._update_level_labels(None, None)

        sr = self.combo_sr.currentData()
        self._level_worker = LevelCheckWorker(in_idx, out_idx, sr)
        self._level_worker.result.connect(self._on_level_result)
        self._level_worker.error.connect(self._on_level_error)
        self._level_worker.finished.connect(self._on_level_finished)
        self._level_worker.start()

    def _on_level_result(self, l_db: float, r_db: float):
        self._update_level_labels(l_db, r_db)

    def _update_level_labels(self, l_db, r_db):
        def classify(db, lbl_db_w, lbl_msg_w):
            if db is None:
                lbl_db_w.setText("--- dBFS")
                lbl_db_w.setStyleSheet(
                    f"font-size: 18px; font-weight: 700; color: {COLORS['text_secondary']};"
                )
                lbl_msg_w.setText("—")
                lbl_msg_w.setStyleSheet(f"font-size: 11px; color: {COLORS['text_muted']};")
                return
            lbl_db_w.setText(f"{db:.1f} dBFS")
            if db < -36:
                color = COLORS["accent_orange"]
                msg   = "レベル小 / Level Low  (ゲインを上げてください / Raise gain)"
            elif db > -1:
                color = COLORS["accent_red"]
                msg   = "レベル大 / Level High  (ゲインを下げてください / Lower gain)"
            else:
                color = COLORS["accent_green"]
                msg   = "✓  適正 / OK"
            lbl_db_w.setStyleSheet(
                f"font-size: 18px; font-weight: 700; color: {color};"
            )
            lbl_msg_w.setText(msg)
            lbl_msg_w.setStyleSheet(f"font-size: 11px; color: {color};")

        classify(l_db, self.lbl_l_db, self.lbl_l_msg)
        classify(r_db, self.lbl_r_db, self.lbl_r_msg)

    def _on_level_error(self, msg: str):
        QMessageBox.warning(self, "Level Check Error", msg)

    def _on_level_finished(self):
        self.btn_level.setEnabled(True)
        self.btn_measure.setEnabled(True)
        self.lbl_status.setText("Level Check complete")

    # ------------------------------------------------------ 測定シーケンス --
    def _get_device_indices(self):
        in_idx  = self.combo_in.currentData()
        out_idx = self.combo_out.currentData()
        if in_idx is None:
            QMessageBox.warning(self, "Device Not Selected",
                                 "Please select an input device.")
            return None, None
        if out_idx is None:
            QMessageBox.warning(self, "Device Not Selected",
                                 "Please select an output device.")
            return None, None
        return in_idx, out_idx

    def _toggle_measurement(self):
        if self._worker and self._worker.isRunning():
            self._stop_measurement()
        else:
            self._start_measurement()

    def _start_measurement(self):
        in_idx, out_idx = self._get_device_indices()
        if in_idx is None:
            return

        # リセット
        self._latencies.clear(); self._trial_waves.clear()
        for attr in self._stat_labels:
            self._stat_labels[attr].setText("—")
        self.lbl_result_device.setText("—")
        self.canvas._init_axes()
        self.btn_csv.setEnabled(False); self.btn_png.setEnabled(False)

        sr           = self.combo_sr.currentData()
        trials       = self.combo_trials.currentData()
        interval     = self.combo_interval.currentData()
        trig_percent = self.combo_trigger.currentData()
        self._sample_rate = sr

        self.progress_bar.setRange(0, trials)
        self.progress_bar.setValue(0)
        self.btn_measure.setText("⏹  Stop")
        self.btn_level.setEnabled(False)
        self.lbl_status.setText("Starting measurement...")

        self._worker = MeasureWorker(in_idx, out_idx, sr, trials, interval, trig_percent)
        self._worker.progress.connect(self._on_trial_progress)
        self._worker.trial_done.connect(self._on_trial_done)
        self._worker.finished_ok.connect(self._on_measure_finished)
        self._worker.error.connect(self._on_measure_error)
        self._worker.start()


    def _stop_measurement(self):
        if self._worker:
            self._worker.stop()
            self._worker.wait(3000)
        self._reset_control_state()
        self.lbl_status.setText("Measurement stopped")

    def _reset_control_state(self):
        self.btn_measure.setText("▶  Start Measurement")
        self.btn_level.setEnabled(True)
        self.progress_bar.setValue(0)

    def _on_trial_progress(self, idx: int, msg: str):
        self.progress_bar.setValue(idx + 1)
        self.lbl_status.setText(msg)

    def _on_trial_done(self, idx: int, latency_ms: float,
                       l_onset: int, r_onset: int,
                       l_data: np.ndarray, r_data: np.ndarray):
        delta_n = max(0, r_onset - l_onset)
        self._latencies.append(latency_ms)
        # (latency_ms, delta_n, l_onset_idx, r_onset_idx, l_data, r_data)
        self._trial_waves.append((latency_ms, delta_n, l_onset, r_onset, l_data, r_data))

    def _on_measure_finished(self, latencies: list):
        self._reset_control_state()

        arr   = np.array(latencies, dtype=np.float64)
        mean_ = float(np.mean(arr))
        max_  = float(np.max(arr))
        min_  = float(np.min(arr))
        std_  = float(np.std(arr, ddof=1)) if len(arr) > 1 else 0.0

        dev_name = self.edit_device_name.text().strip() or "Target_Device"
        self.lbl_result_device.setText(f"Device: {dev_name}")
        self._stat_labels["mean"].setText(f"{mean_:.3f}")
        self._stat_labels["max"].setText(f"{max_:.3f}")
        self._stat_labels["min"].setText(f"{min_:.3f}")
        self._stat_labels["std"].setText(f"{std_:.3f}")
        self.lbl_status.setText(
            f"Measurement complete — {len(latencies)} trials  Mean: {mean_:.3f} ms"
        )

        # 平均値に最も近い試行
        diffs = [abs(lm - mean_) for lm, _, _, _, _, _ in self._trial_waves]
        best  = int(np.argmin(diffs))
        best_lat, best_delta_n, best_l_on, best_r_on, best_l, best_r = \
            self._trial_waves[best]

        scale = self._get_waveform_scale_factor()
        self.canvas.plot_waveforms(best_l, best_r, self._sample_rate,
                                   best_delta_n, best_lat,
                                   best_l_on, best_r_on,
                                   device_name=dev_name,
                                   scale_factor=scale)

        self.btn_csv.setEnabled(True)
        self.btn_png.setEnabled(True)

    def _get_waveform_scale_factor(self) -> float:
        if hasattr(self, "btn_scale_x2") and self.btn_scale_x2.isChecked():
            return 2.0
        elif hasattr(self, "btn_scale_x4") and self.btn_scale_x4.isChecked():
            return 4.0
        return 1.0

    def _on_waveform_scale_changed(self, button):
        scale = self._get_waveform_scale_factor()
        self.canvas.set_scale(scale)

    def _on_measure_error(self, msg: str):
        self._reset_control_state()
        self.lbl_status.setText("Error")
        QMessageBox.critical(self, "Measurement Error", msg)

    # ------------------------------------------------------------ エクスポート --
    def _downloads_path(self) -> Path:
        return Path.home() / "Downloads"

    def _base_filename(self) -> str:
        name = self.edit_device_name.text().strip() or "Target_Device"
        ts   = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        return f"{name}_{ts}"

    def _export_csv(self):
        if not self._latencies:
            QMessageBox.warning(self, "No Data", "No measurement data available."); return

        path = self._downloads_path() / f"{self._base_filename()}.csv"
        arr  = np.array(self._latencies, dtype=np.float64)
        mean_ = float(np.mean(arr))
        max_  = float(np.max(arr))
        min_  = float(np.min(arr))
        std_  = float(np.std(arr, ddof=1)) if len(arr) > 1 else 0.0

        try:
            with open(path, "w", newline="", encoding="utf-8-sig") as f:
                w = csv.writer(f)
                w.writerow(["Dual-Channel RTL Analyzer -- Measurement Results"])
                w.writerow([])
                w.writerow(["Device Name",        self.edit_device_name.text().strip()])
                w.writerow(["Sample Rate (Hz)",   self._sample_rate])
                w.writerow(["Trials",            len(self._latencies)])
                w.writerow(["Trigger Condition", self.combo_trigger.currentText()])
                w.writerow(["Export DateTime",
                             datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")])
                w.writerow([])
                w.writerow(["Statistics"])
                w.writerow(["Mean (ms)",    f"{mean_:.4f}"])
                w.writerow(["Max  (ms)",    f"{max_:.4f}"])
                w.writerow(["Min  (ms)",    f"{min_:.4f}"])
                w.writerow(["Std Dev (ms)", f"{std_:.4f}"])
                w.writerow([])
                w.writerow(["Trial", "Samples", "Latency (ms)"])
                for i, (lat, dn, _lo, _ro, _l, _r) in enumerate(self._trial_waves, 1):
                    w.writerow([i, dn, f"{lat:.4f}"])
        except Exception as e:
            QMessageBox.critical(self, "CSV Export Error",
                                 f"Failed to write file:\n{e}")
            return

        QMessageBox.information(self, "CSV Export Complete", f"Saved to:\n{path}")

    def _export_png(self):
        if not self._latencies:
            QMessageBox.warning(self, "No Data", "No measurement data available."); return

        path = self._downloads_path() / f"{self._base_filename()}.png"
        try:
            self.canvas.fig.savefig(
                str(path), dpi=150, bbox_inches="tight",
                facecolor=COLORS["bg_card"]
            )
        except Exception as e:
            QMessageBox.critical(self, "Waveform Image Save Error",
                                 f"Failed to save image:\n{e}")
            return

        QMessageBox.information(self, "Waveform Image Saved",
                                f"Saved to:\n{path}")

    # ------------------------------------------------------ クリーンアップ --
    def closeEvent(self, event):
        if self._worker and self._worker.isRunning():
            self._worker.stop(); self._worker.wait(2000)
        if self._level_worker and self._level_worker.isRunning():
            self._level_worker.wait(2000)
        event.accept()


# ---------------------------------------------------------------------------
# エントリポイント
# ---------------------------------------------------------------------------
def main():
    QApplication.setHighDpiScaleFactorRoundingPolicy(
        Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
    )
    os.environ.setdefault("QT_ENABLE_HIGHDPI_SCALING", "1")

    app = QApplication(sys.argv)
    app.setApplicationName("Dual-Channel RTL Analyzer")
    app.setApplicationVersion("1.0.0")
    app.setStyleSheet(APP_STYLESHEET)

    font = app.font()
    font.setFamily("Segoe UI")
    font.setPointSize(10)
    app.setFont(font)

    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
