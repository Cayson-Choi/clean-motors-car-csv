"""
Global Qt Style Sheet for 정기차량 관리 자동화.
Apply once with app.setStyleSheet(APP_STYLE).
"""

APP_STYLE = """
/* ── Global ──────────────────────────────────────────────── */
QWidget {
    font-family: 'Malgun Gothic', sans-serif;
    font-size: 14px;
    color: #1E293B;
    background: #F1F5F9;
}

/* ── Header bar ──────────────────────────────────────────── */
QFrame#header {
    background: #1E3A5F;
    border: none;
}
QLabel#title {
    color: white;
    font-size: 20px;
    font-weight: 700;
    background: transparent;
}
QLabel#subtitle {
    color: #CBD5E1;
    font-size: 12px;
    background: transparent;
}

/* ── Card ────────────────────────────────────────────────── */
QFrame#card {
    background: white;
    border: 1px solid #E2E8F0;
    border-radius: 12px;
}

/* ── Input widgets ───────────────────────────────────────── */
QListWidget, QLineEdit, QDateEdit {
    border: 1px solid #CBD5E1;
    border-radius: 6px;
    padding: 6px;
    background: white;
    font-size: 14px;
}
QListWidget::item:selected {
    background: #DBEAFE;
    color: #1E293B;
}
QDateEdit::drop-down {
    border: none;
    width: 20px;
}

/* ── Separator ───────────────────────────────────────────── */
QFrame[frameShape="4"] {   /* HLine */
    border: none;
    border-top: 1px solid #E2E8F0;
    background: transparent;
}

/* ── Primary button ──────────────────────────────────────── */
QPushButton#primary {
    background: #2563EB;
    color: white;
    font-weight: 700;
    font-size: 15px;
    min-height: 44px;
    border-radius: 8px;
    border: none;
    padding: 10px 18px;
}
QPushButton#primary:hover {
    background: #1D4ED8;
}
QPushButton#primary:pressed {
    background: #1E40AF;
}
QPushButton#primary:disabled {
    background: #93C5FD;
}

/* ── Secondary button (default QPushButton) ──────────────── */
QPushButton {
    background: white;
    color: #2563EB;
    border: 1px solid #CBD5E1;
    border-radius: 8px;
    min-height: 36px;
    padding: 10px 18px;
    font-size: 14px;
}
QPushButton:hover {
    background: #F8FAFC;
}
QPushButton:pressed {
    background: #EFF6FF;
}
QPushButton:disabled {
    color: #94A3B8;
    border-color: #E2E8F0;
}

/* ── Footer ──────────────────────────────────────────────── */
QFrame#footer {
    background: #E2E8F0;
    border: none;
}
QLabel#footer_text {
    color: #64748B;
    font-size: 11px;
    background: transparent;
}

/* ── QGroupBox (dedup groups) ────────────────────────────── */
QGroupBox {
    border: 1px solid #E2E8F0;
    border-radius: 8px;
    margin-top: 8px;
    font-weight: 600;
    background: white;
}
QGroupBox::title {
    subcontrol-origin: margin;
    subcontrol-position: top left;
    padding: 0 6px;
    color: #1E293B;
}

/* ── ScrollArea ──────────────────────────────────────────── */
QScrollArea {
    border: none;
    background: transparent;
}
QScrollArea > QWidget > QWidget {
    background: transparent;
}
"""
