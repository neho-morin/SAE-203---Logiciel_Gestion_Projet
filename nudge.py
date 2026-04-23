import sys
import os
import json
from datetime import datetime, date, timedelta
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QLineEdit, QComboBox, QDateEdit, QTableWidget,
    QTableWidgetItem, QHeaderView, QFrame, QScrollArea, QDialog,
    QDialogButtonBox, QFormLayout, QTextEdit, QMessageBox, QStackedWidget,
    QGridLayout, QSizePolicy, QSpacerItem
)
from PyQt6.QtCore import Qt, QDate, QTimer, pyqtSignal
from PyQt6.QtGui import QFont, QColor, QPalette, QPainter, QPen, QBrush

from database.db import init_db
import services.project_service as project_service
import services.task_service as task_service
import services.user_service as user_service
import services.relance_service as relance_service
import services.scheduler_service as scheduler_service

# ── Couleurs ──────────────────────────────────────────────────────────────────
BG         = "#f5f3ef"
SURFACE    = "#ffffff"
SURFACE2   = "#faf8f5"
BORDER     = "#e8e3db"
TEXT       = "#1a1714"
MUTED      = "#7a726a"
ACCENT     = "#2d6a4f"
ACCENT_L   = "#e8f5ee"
DANGER     = "#c0392b"
DANGER_L   = "#fdf0ef"
WARNING    = "#d68910"
WARNING_L  = "#fef9ec"
INFO       = "#1a6891"
INFO_L     = "#eaf4fb"

STATUS_COLORS = {
    "À faire":         (SURFACE2,  MUTED,   "#bbb"),
    "En cours":        (INFO_L,    INFO,    INFO),
    "Terminée":        (ACCENT_L,  ACCENT,  ACCENT),
    "En retard":       (DANGER_L,  DANGER,  DANGER),
    "Terminée proche": (WARNING_L, WARNING, WARNING),
}

PRIORITY_COLORS = {
    "Basse":    "#7a726a",
    "Moyenne":  "#1a6891",
    "Haute":    "#d68910",
    "Critique": "#c0392b",
}

# ── Données (chargées depuis SQLite) ─────────────────────────────────────────
projects        = []
tasks           = []
responsables    = []
relance_history = []


def load_all():
    global projects, tasks, responsables, relance_history
    projects        = project_service.get_all()
    tasks           = task_service.get_all()
    responsables    = user_service.get_all()
    relance_history = relance_service.get_recent()


def today_str():
    return date.today().isoformat()

def fmt_date(iso):
    if not iso:
        return "—"
    try:
        d = date.fromisoformat(iso)
        months = ["janv.","févr.","mars","avr.","mai","juin",
                  "juil.","août","sept.","oct.","nov.","déc."]
        return f"{d.day} {months[d.month-1]} {d.year}"
    except:
        return iso

def infer_statut(task):
    if task["statut"] == "Terminée":
        return "Terminée"
    try:
        diff = (date.fromisoformat(task["echeance"]) - date.today()).days
    except:
        return task["statut"]
    if diff < 0:
        return "En retard"
    if diff <= 2:
        return "Terminée proche"
    return task["statut"]

# ── Style global ──────────────────────────────────────────────────────────────
GLOBAL_STYLE = f"""
QMainWindow, QWidget {{
    background-color: {BG};
    font-family: 'Segoe UI', Arial, sans-serif;
    font-size: 13px;
    color: {TEXT};
}}
QScrollArea {{ border: none; background: transparent; }}
QScrollBar:vertical {{
    background: {BG}; width: 8px; border-radius: 4px;
}}
QScrollBar::handle:vertical {{
    background: {BORDER}; border-radius: 4px; min-height: 20px;
}}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{ height: 0; }}
"""

def btn_style(bg=ACCENT, color="#fff", border=None):
    bd = border or bg
    hover = "#245a42" if bg == ACCENT else "#d0ccc6"
    return f"""
        QPushButton {{
            background: {bg}; color: {color};
            border: 1.5px solid {bd}; border-radius: 8px;
            padding: 7px 16px; font-weight: 700; font-size: 12px;
        }}
        QPushButton:hover {{ background: {hover}; }}
        QPushButton:disabled {{ opacity: 0.4; }}
    """

def input_style():
    return f"""
        QLineEdit, QComboBox, QDateEdit, QTextEdit {{
            background: {SURFACE2}; border: 1.5px solid {BORDER};
            border-radius: 8px; padding: 7px 10px;
            font-size: 13px; color: {TEXT};
        }}
        QLineEdit:focus, QComboBox:focus, QDateEdit:focus, QTextEdit:focus {{
            border-color: {ACCENT};
        }}
        QComboBox::drop-down {{ border: none; width: 24px; }}
    """

# ── Widgets réutilisables ─────────────────────────────────────────────────────
class Badge(QLabel):
    def __init__(self, statut, parent=None):
        super().__init__(statut, parent)
        bg, color, _ = STATUS_COLORS.get(statut, (SURFACE2, MUTED, MUTED))
        self.setStyleSheet(f"""
            QLabel {{
                background: {bg}; color: {color};
                border-radius: 10px; padding: 2px 10px;
                font-size: 11px; font-weight: 700;
            }}
        """)
        self.setFixedHeight(22)

class PriorityBadge(QLabel):
    def __init__(self, priority, parent=None):
        super().__init__(priority, parent)
        color = PRIORITY_COLORS.get(priority, MUTED)
        self.setStyleSheet(f"""
            QLabel {{
                background: transparent; color: {color};
                font-size: 11px; font-weight: 700;
                border: 1.5px solid {color}; border-radius: 10px;
                padding: 2px 8px;
            }}
        """)

class Card(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet(f"""
            QFrame {{
                background: {SURFACE}; border-radius: 12px;
                border: 1.5px solid {BORDER};
            }}
        """)

class SectionLabel(QLabel):
    def __init__(self, text, parent=None):
        super().__init__(text.upper(), parent)
        self.setStyleSheet(f"color: {MUTED}; font-size: 9px; font-weight: 700; letter-spacing: 1px;")

class KpiCard(QFrame):
    def __init__(self, icon, label, value, parent=None):
        super().__init__(parent)
        self.setStyleSheet(f"background: {SURFACE2}; border-radius: 10px; border: 1px solid {BORDER};")
        self.setFixedHeight(80)
        lay = QVBoxLayout(self)
        lay.setContentsMargins(10, 8, 10, 8)
        lay.setSpacing(2)
        self.icon_lbl  = QLabel(icon)
        self.icon_lbl.setStyleSheet("font-size: 18px; border: none;")
        self.val_lbl   = QLabel(str(value))
        self.val_lbl.setStyleSheet(f"font-size: 20px; font-weight: 800; color: {TEXT}; border: none;")
        self.label_lbl = QLabel(label)
        self.label_lbl.setStyleSheet(f"font-size: 10px; color: {MUTED}; border: none;")
        for w in [self.icon_lbl, self.val_lbl, self.label_lbl]:
            w.setAlignment(Qt.AlignmentFlag.AlignCenter)
            lay.addWidget(w)

    def update_value(self, v):
        self.val_lbl.setText(str(v))

# ── Donut widget ──────────────────────────────────────────────────────────────
class DonutWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.pct = 0
        self.setFixedSize(100, 100)

    def set_pct(self, pct):
        self.pct = pct
        self.update()

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        r = 35
        cx, cy = 50, 50
        pen = QPen(QColor(BORDER), 8)
        pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        p.setPen(pen)
        p.drawEllipse(cx - r, cy - r, r*2, r*2)
        if self.pct > 0:
            pen2 = QPen(QColor(ACCENT), 8)
            pen2.setCapStyle(Qt.PenCapStyle.RoundCap)
            p.setPen(pen2)
            span = int(-self.pct / 100 * 360 * 16)
            p.drawArc(cx - r, cy - r, r*2, r*2, 90 * 16, span)
        p.setPen(QColor(TEXT))
        font = QFont("Segoe UI", 12, QFont.Weight.Bold)
        p.setFont(font)
        p.drawText(0, 0, 100, 100, Qt.AlignmentFlag.AlignCenter, f"{self.pct}%")

# ── Dialogs ───────────────────────────────────────────────────────────────────
class ProjectDialog(QDialog):
    def __init__(self, project=None, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Nouveau projet" if not project else "Modifier le projet")
        self.setMinimumWidth(400)
        self.setStyleSheet(GLOBAL_STYLE + input_style())
        lay = QVBoxLayout(self)
        lay.setSpacing(8)

        title = QLabel("📁 " + ("Nouveau projet" if not project else "Modifier le projet"))
        title.setStyleSheet(f"font-size: 15px; font-weight: 800; color: {TEXT};")
        lay.addWidget(title)

        form = QFormLayout()
        form.setSpacing(8)
        self.name = QLineEdit(project["nom"] if project else "")
        self.name.setPlaceholderText("Ex : Projet SAE, Stage…")
        self.desc = QTextEdit(project.get("description","") if project else "")
        self.desc.setFixedHeight(80)
        self.desc.setPlaceholderText("Description (optionnel)")
        self.date_fin = QDateEdit()
        self.date_fin.setCalendarPopup(True)
        self.date_fin.setDisplayFormat("dd/MM/yyyy")
        if project and project.get("date_fin"):
            self.date_fin.setDate(QDate.fromString(project["date_fin"], "yyyy-MM-dd"))
        else:
            self.date_fin.setDate(QDate.currentDate().addDays(30))

        form.addRow("Nom *", self.name)
        form.addRow("Description", self.desc)
        form.addRow("Date de fin", self.date_fin)
        lay.addLayout(form)

        btns = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        btns.accepted.connect(self.accept)
        btns.rejected.connect(self.reject)
        btns.button(QDialogButtonBox.StandardButton.Ok).setStyleSheet(btn_style())
        btns.button(QDialogButtonBox.StandardButton.Cancel).setStyleSheet(btn_style(BORDER, TEXT))
        lay.addWidget(btns)

    def get_data(self):
        return {
            "nom": self.name.text().strip(),
            "description": self.desc.toPlainText().strip(),
            "date_fin": self.date_fin.date().toString("yyyy-MM-dd"),
        }

class ResponsableDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Nouveau responsable")
        self.setMinimumWidth(360)
        self.setStyleSheet(GLOBAL_STYLE + input_style())
        lay = QVBoxLayout(self)

        title = QLabel("👤 Nouveau responsable")
        title.setStyleSheet(f"font-size: 15px; font-weight: 800;")
        lay.addWidget(title)

        form = QFormLayout()
        self.name  = QLineEdit(); self.name.setPlaceholderText("Prénom Nom")
        self.email = QLineEdit(); self.email.setPlaceholderText("email@example.com")
        self.role  = QComboBox()
        self.role.addItems(["Développeur", "Chef de projet", "Designer", "Testeur", "Autre"])
        form.addRow("Nom *", self.name)
        form.addRow("Email", self.email)
        form.addRow("Rôle", self.role)
        lay.addLayout(form)

        btns = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        btns.accepted.connect(self.accept)
        btns.rejected.connect(self.reject)
        btns.button(QDialogButtonBox.StandardButton.Ok).setStyleSheet(btn_style())
        btns.button(QDialogButtonBox.StandardButton.Cancel).setStyleSheet(btn_style(BORDER, TEXT))
        lay.addWidget(btns)

    def get_data(self):
        return {
            "nom": self.name.text().strip(),
            "email": self.email.text().strip(),
            "role": self.role.currentText(),
        }

class TaskDialog(QDialog):
    def __init__(self, project_id, task=None, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Nouvelle tâche" if not task else "Modifier la tâche")
        self.setMinimumWidth(420)
        self.setStyleSheet(GLOBAL_STYLE + input_style())
        lay = QVBoxLayout(self)
        lay.setSpacing(8)

        title = QLabel("➕ " + ("Nouvelle tâche" if not task else "Modifier la tâche"))
        title.setStyleSheet(f"font-size: 15px; font-weight: 800;")
        lay.addWidget(title)

        form = QFormLayout()
        form.setSpacing(8)

        self.title_input = QLineEdit(task["titre"] if task else "")
        self.title_input.setPlaceholderText("Nom de la tâche")

        self.desc = QTextEdit(task.get("description","") if task else "")
        self.desc.setFixedHeight(70)
        self.desc.setPlaceholderText("Description (optionnel)")

        self.resp_combo = QComboBox()
        self.resp_combo.addItem("— Non attribué —", None)
        for r in responsables:
            self.resp_combo.addItem(f"{r['nom']} ({r['role']})", r["id"])
        if task and task.get("responsable_id"):
            idx = self.resp_combo.findData(task["responsable_id"])
            if idx >= 0:
                self.resp_combo.setCurrentIndex(idx)

        self.echeance = QDateEdit()
        self.echeance.setCalendarPopup(True)
        self.echeance.setDisplayFormat("dd/MM/yyyy")
        if task and task.get("echeance"):
            self.echeance.setDate(QDate.fromString(task["echeance"], "yyyy-MM-dd"))
        else:
            self.echeance.setDate(QDate.currentDate().addDays(7))

        self.priorite = QComboBox()
        self.priorite.addItems(["Basse", "Moyenne", "Haute", "Critique"])
        if task:
            self.priorite.setCurrentText(task.get("priorite", "Moyenne"))
        else:
            self.priorite.setCurrentText("Moyenne")

        self.statut = QComboBox()
        self.statut.addItems(["À faire", "En cours", "Terminée"])
        if task:
            self.statut.setCurrentText(task.get("statut", "À faire"))

        form.addRow("Titre *", self.title_input)
        form.addRow("Description", self.desc)
        form.addRow("Responsable", self.resp_combo)
        form.addRow("Échéance", self.echeance)
        form.addRow("Priorité", self.priorite)
        form.addRow("Statut", self.statut)
        lay.addLayout(form)

        btns = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        btns.accepted.connect(self.accept)
        btns.rejected.connect(self.reject)
        btns.button(QDialogButtonBox.StandardButton.Ok).setStyleSheet(btn_style())
        btns.button(QDialogButtonBox.StandardButton.Cancel).setStyleSheet(btn_style(BORDER, TEXT))
        lay.addWidget(btns)

    def get_data(self):
        resp_id = self.resp_combo.currentData()
        resp_name = None
        if resp_id:
            r = next((r for r in responsables if r["id"] == resp_id), None)
            if r: resp_name = r["nom"]
        return {
            "titre": self.title_input.text().strip(),
            "description": self.desc.toPlainText().strip(),
            "responsable_id": resp_id,
            "responsable": resp_name,
            "echeance": self.echeance.date().toString("yyyy-MM-dd"),
            "priorite": self.priorite.currentText(),
            "statut": self.statut.currentText(),
        }

class RelanceDialog(QDialog):
    def __init__(self, task, parent=None):
        super().__init__(parent)
        self.task = task
        self.setWindowTitle("Relance par mail")
        self.setMinimumWidth(460)
        self.setStyleSheet(GLOBAL_STYLE + input_style())
        lay = QVBoxLayout(self)
        lay.setSpacing(8)

        title = QLabel(f"📧 Relance — {task['titre']}")
        title.setStyleSheet(f"font-size: 15px; font-weight: 800;")
        lay.addWidget(title)

        # Mode simulation toggle
        self.sim_btn = QPushButton("🔵 Mode : Simulation")
        self.sim_mode = True
        self.sim_btn.setStyleSheet(btn_style(INFO_L, INFO))
        self.sim_btn.clicked.connect(self.toggle_sim)
        lay.addWidget(self.sim_btn)

        resp = next((r for r in responsables if r["id"] == task.get("responsable_id")), None)
        form = QFormLayout()
        self.to_input = QLineEdit(resp["email"] if resp else "")
        self.to_input.setPlaceholderText("email@example.com")
        self.msg_input = QTextEdit()
        self.msg_input.setPlainText(
            f"Bonjour,\n\nLa tâche suivante est en retard :\n"
            f"- {task['titre']}\n"
            f"- Échéance initiale : {fmt_date(task['echeance'])}\n\n"
            f"Merci de prendre les mesures nécessaires rapidement.\n\nCordialement"
        )
        self.msg_input.setFixedHeight(160)
        form.addRow("Destinataire", self.to_input)
        form.addRow("Message", self.msg_input)
        lay.addLayout(form)

        btns = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        btns.button(QDialogButtonBox.StandardButton.Ok).setText("Envoyer")
        btns.accepted.connect(self.accept)
        btns.rejected.connect(self.reject)
        btns.button(QDialogButtonBox.StandardButton.Ok).setStyleSheet(btn_style())
        btns.button(QDialogButtonBox.StandardButton.Cancel).setStyleSheet(btn_style(BORDER, TEXT))
        lay.addWidget(btns)

    def toggle_sim(self):
        self.sim_mode = not self.sim_mode
        if self.sim_mode:
            self.sim_btn.setText("🔵 Mode : Simulation")
            self.sim_btn.setStyleSheet(btn_style(INFO_L, INFO))
        else:
            self.sim_btn.setText("🟢 Mode : Réel (SMTP)")
            self.sim_btn.setStyleSheet(btn_style(ACCENT_L, ACCENT))

    def get_data(self):
        return {
            "email": self.to_input.text().strip(),
            "message": self.msg_input.toPlainText(),
            "simulation": self.sim_mode,
        }

# ── Onboarding ────────────────────────────────────────────────────────────────
class OnboardingDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Bienvenue sur Nudge")
        self.setMinimumSize(500, 420)
        self.setStyleSheet(f"""
            QDialog {{ background: qlineargradient(x1:0,y1:0,x2:1,y2:1,
                stop:0 #1a3a2a, stop:0.5 #2d6a4f, stop:1 #1a4a3a); }}
        """)
        self.step = 0
        self.steps = [
            ("📁", "Créez vos projets",
             "Organisez votre travail en projets distincts.\nChaque projet a ses tâches, responsables et échéances.",
             "Exemple : Projet SAE, Stage, Projet Personnel…"),
            ("✅", "Ajoutez vos tâches",
             "Créez des tâches avec responsable, priorité et échéance.\nL'app détecte automatiquement les retards.",
             "Les tâches proches de l'échéance passent en « Terminée proche »."),
            ("📧", "Relancez par mail",
             "Envoyez des relances en un clic.\nMode simulation disponible pour les démonstrations.",
             "Le bouton « Relancer » cible automatiquement la première tâche en retard."),
        ]
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(40, 30, 40, 30)
        self.build_ui()

    def build_ui(self):
        # Clear tout proprement (layouts + widgets)
        while self.main_layout.count():
            item = self.main_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
            elif item.layout():
                while item.layout().count():
                    sub = item.layout().takeAt(0)
                    if sub.widget(): sub.widget().deleteLater()

        icon, title, desc, tip = self.steps[self.step]

        # Logo
        logo_row = QHBoxLayout()
        logo_lbl = QLabel("✳ NUDGE")
        logo_lbl.setStyleSheet("color: white; font-size: 18px; font-weight: 800; letter-spacing: 2px;")
        logo_row.addStretch()
        logo_row.addWidget(logo_lbl)
        logo_row.addStretch()
        self.main_layout.addLayout(logo_row)
        self.main_layout.addSpacing(16)

        # Card
        card = QFrame()
        card.setStyleSheet(f"background: rgba(255,255,255,0.97); border-radius: 18px; border: none;")
        card_lay = QVBoxLayout(card)
        card_lay.setContentsMargins(32, 28, 32, 28)
        card_lay.setSpacing(12)

        # Dots
        dots_row = QHBoxLayout()
        dots_row.addStretch()
        for i in range(len(self.steps)):
            dot = QLabel()
            if i == self.step:
                dot.setFixedSize(24, 8)
                dot.setStyleSheet(f"background: {ACCENT}; border-radius: 4px;")
            else:
                dot.setFixedSize(8, 8)
                dot.setStyleSheet(f"background: {BORDER}; border-radius: 4px;")
            dots_row.addWidget(dot)
        dots_row.addStretch()
        card_lay.addLayout(dots_row)

        icon_lbl = QLabel(icon)
        icon_lbl.setStyleSheet("font-size: 48px; border: none;")
        icon_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        card_lay.addWidget(icon_lbl)

        title_lbl = QLabel(title)
        title_lbl.setStyleSheet(f"font-size: 20px; font-weight: 800; color: {TEXT}; border: none;")
        title_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        card_lay.addWidget(title_lbl)

        desc_lbl = QLabel(desc)
        desc_lbl.setStyleSheet(f"font-size: 13px; color: {MUTED}; border: none;")
        desc_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        desc_lbl.setWordWrap(True)
        card_lay.addWidget(desc_lbl)

        tip_frame = QFrame()
        tip_frame.setStyleSheet(f"background: {ACCENT_L}; border-radius: 10px; border: none;")
        tip_lay = QHBoxLayout(tip_frame)
        tip_lbl = QLabel(f"💡  {tip}")
        tip_lbl.setStyleSheet(f"font-size: 12px; color: {ACCENT}; font-weight: 600; border: none;")
        tip_lbl.setWordWrap(True)
        tip_lay.addWidget(tip_lbl)
        card_lay.addWidget(tip_frame)

        # Buttons
        btn_row = QHBoxLayout()
        prev_btn = QPushButton("← Précédent")
        prev_btn.setStyleSheet(btn_style(BORDER, TEXT))
        prev_btn.setEnabled(self.step > 0)
        prev_btn.clicked.connect(self.prev_step)

        step_lbl = QLabel(f"{self.step+1} / {len(self.steps)}")
        step_lbl.setStyleSheet(f"color: {MUTED}; font-size: 11px; border: none;")
        step_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)

        is_last = self.step == len(self.steps) - 1
        next_btn = QPushButton("Commencer 🚀" if is_last else "Suivant →")
        next_btn.setStyleSheet(btn_style())
        next_btn.clicked.connect(self.accept if is_last else self.next_step)

        btn_row.addWidget(prev_btn)
        btn_row.addStretch()
        btn_row.addWidget(step_lbl)
        btn_row.addStretch()
        btn_row.addWidget(next_btn)
        card_lay.addLayout(btn_row)

        self.main_layout.addWidget(card)
        self.main_layout.addSpacing(10)

        skip = QPushButton("Passer l'introduction")
        skip.setStyleSheet("QPushButton { background: transparent; color: rgba(255,255,255,0.45); border: none; font-size: 12px; } QPushButton:hover { color: white; }")
        skip.clicked.connect(self.accept)
        self.main_layout.addWidget(skip, alignment=Qt.AlignmentFlag.AlignCenter)

    def next_step(self):
        self.step += 1
        self.build_ui()

    def prev_step(self):
        self.step -= 1
        self.build_ui()

# ── Sidebar ───────────────────────────────────────────────────────────────────
class Sidebar(QFrame):
    project_selected = pyqtSignal(int)
    add_project      = pyqtSignal()
    add_responsable  = pyqtSignal()
    go_home          = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedWidth(200)
        self.setStyleSheet(f"QFrame {{ background: {SURFACE}; border-right: 1.5px solid {BORDER}; border-radius: 0; }}")
        self.active_project = None
        lay = QVBoxLayout(self)
        lay.setContentsMargins(10, 16, 10, 16)
        lay.setSpacing(4)

        # Logo (cliquable → accueil)
        logo = QLabel("✳  Nudge")
        logo.setStyleSheet(f"""
            font-size: 15px; font-weight: 800; color: {TEXT};
            padding: 0 4px; letter-spacing: -0.3px;
        """)
        logo.setCursor(Qt.CursorShape.PointingHandCursor)
        logo.setToolTip("Retour à l'accueil")
        logo.mousePressEvent = lambda e: self.go_home.emit()
        lay.addWidget(logo)
        lay.addSpacing(14)

        # Projects
        lay.addWidget(SectionLabel("Projets"))
        self.proj_container = QVBoxLayout()
        self.proj_container.setSpacing(1)
        lay.addLayout(self.proj_container)

        add_proj = QPushButton("+ Ajouter un projet")
        add_proj.setStyleSheet(f"""
            QPushButton {{ background: transparent; color: {MUTED}; border: 1.5px dashed {BORDER};
                border-radius: 8px; padding: 5px 8px; font-size: 11px; text-align: left; }}
            QPushButton:hover {{ color: {ACCENT}; border-color: {ACCENT}; }}
        """)
        add_proj.clicked.connect(self.add_project.emit)
        lay.addWidget(add_proj)
        lay.addSpacing(14)

        # Responsables
        lay.addWidget(SectionLabel("Responsables"))
        self.resp_label = QLabel("Aucun responsable")
        self.resp_label.setStyleSheet(f"color: {MUTED}; font-size: 11px; padding: 2px 4px;")
        self.resp_label.setWordWrap(True)
        lay.addWidget(self.resp_label)

        add_resp = QPushButton("+ Ajouter un responsable")
        add_resp.setStyleSheet(f"""
            QPushButton {{ background: transparent; color: {MUTED}; border: 1.5px dashed {BORDER};
                border-radius: 8px; padding: 5px 8px; font-size: 11px; text-align: left; }}
            QPushButton:hover {{ color: {ACCENT}; border-color: {ACCENT}; }}
        """)
        add_resp.clicked.connect(self.add_responsable.emit)
        lay.addWidget(add_resp)
        lay.addSpacing(14)

        # History
        lay.addWidget(SectionLabel("Dernières relances"))
        self.history_container = QVBoxLayout()
        self.history_container.setSpacing(3)
        lay.addLayout(self.history_container)

        lay.addStretch()

    def refresh(self, active_id=None):
        if active_id is not None:
            self.active_project = active_id

        # Projects
        while self.proj_container.count():
            item = self.proj_container.takeAt(0)
            if item.widget(): item.widget().deleteLater()

        for p in projects:
            btn = QPushButton(p["nom"])
            is_active = p["id"] == self.active_project
            btn.setStyleSheet(f"""
                QPushButton {{
                    background: {"#e8f5ee" if is_active else "transparent"};
                    color: {ACCENT if is_active else TEXT};
                    font-weight: {"700" if is_active else "400"};
                    border: none; border-radius: 8px;
                    padding: 6px 8px; text-align: left; font-size: 13px;
                }}
                QPushButton:hover {{ background: {ACCENT_L}; color: {ACCENT}; }}
            """)
            btn.clicked.connect(lambda _, pid=p["id"]: self.project_selected.emit(pid))
            self.proj_container.addWidget(btn)

        # Responsables
        if responsables:
            names = ", ".join(r["nom"] for r in responsables[:3])
            if len(responsables) > 3:
                names += f" +{len(responsables)-3}"
            self.resp_label.setText(names)
        else:
            self.resp_label.setText("Aucun responsable")

        # History
        while self.history_container.count():
            item = self.history_container.takeAt(0)
            if item.widget(): item.widget().deleteLater()

        for h in relance_history[:3]:
            frame = QFrame()
            frame.setStyleSheet(f"background: {SURFACE2}; border-radius: 8px; border: none;")
            fl = QVBoxLayout(frame)
            fl.setContentsMargins(8, 5, 8, 5)
            fl.setSpacing(1)
            email_lbl = QLabel(f"✉ {h['email']}")
            email_lbl.setStyleSheet(f"color: {MUTED}; font-size: 10px; border: none;")
            task_lbl  = QLabel(h["taskTitle"])
            task_lbl.setStyleSheet(f"font-weight: 700; font-size: 11px; border: none;")
            date_lbl  = QLabel(fmt_date(h["date"]))
            date_lbl.setStyleSheet(f"color: {MUTED}; font-size: 10px; border: none;")
            for w in [email_lbl, task_lbl, date_lbl]:
                w.setWordWrap(False)
                fl.addWidget(w)
            self.history_container.addWidget(frame)

# ── Dashboard panel ───────────────────────────────────────────────────────────
class DashboardPanel(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedWidth(230)
        self.setStyleSheet(f"QFrame {{ background: {SURFACE}; border-left: 1.5px solid {BORDER}; border-radius: 0; }}")
        lay = QVBoxLayout(self)
        lay.setContentsMargins(14, 14, 14, 14)
        lay.setSpacing(10)

        title = QLabel("Tableau de bord")
        title.setStyleSheet(f"font-size: 13px; font-weight: 800; color: {TEXT};")
        lay.addWidget(title)

        # KPIs
        kpi_grid = QGridLayout()
        kpi_grid.setSpacing(7)
        self.kpi_projects = KpiCard("📁", "Projets", 0)
        self.kpi_tasks    = KpiCard("📋", "Tâches", 0)
        kpi_grid.addWidget(self.kpi_projects, 0, 0)
        kpi_grid.addWidget(self.kpi_tasks, 0, 1)
        lay.addLayout(kpi_grid)

        # Donut
        donut_frame = QFrame()
        donut_frame.setStyleSheet(f"background: {SURFACE2}; border-radius: 12px; border: 1px solid {BORDER};")
        donut_lay = QVBoxLayout(donut_frame)
        donut_lay.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.donut = DonutWidget()
        self.pct_lbl = QLabel("0% Avancement")
        self.pct_lbl.setStyleSheet(f"font-weight: 700; font-size: 12px; color: {TEXT}; border: none;")
        self.pct_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.term_lbl = QLabel("0/0 terminées")
        self.term_lbl.setStyleSheet(f"color: {MUTED}; font-size: 11px; border: none;")
        self.term_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        donut_lay.addWidget(self.donut, alignment=Qt.AlignmentFlag.AlignCenter)
        donut_lay.addWidget(self.pct_lbl)
        donut_lay.addWidget(self.term_lbl)
        lay.addWidget(donut_frame)

        # Stats
        stats_grid = QGridLayout()
        stats_grid.setSpacing(5)
        self.stat_retard  = self._stat("0", "Retard",  DANGER)
        self.stat_afaire  = self._stat("0", "À faire", MUTED)
        self.stat_proche  = self._stat("0", "Proche",  WARNING)
        stats_grid.addWidget(self.stat_retard, 0, 0)
        stats_grid.addWidget(self.stat_afaire, 0, 1)
        stats_grid.addWidget(self.stat_proche, 0, 2)
        lay.addLayout(stats_grid)

        lay.addStretch()

    def _stat(self, val, label, color):
        f = QFrame()
        f.setStyleSheet(f"background: {SURFACE2}; border-radius: 10px; border: 1px solid {BORDER};")
        fl = QVBoxLayout(f)
        fl.setContentsMargins(4, 7, 4, 7)
        fl.setSpacing(2)
        vl = QLabel(val)
        vl.setStyleSheet(f"font-size: 17px; font-weight: 800; color: {color}; border: none;")
        vl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        ll = QLabel(label)
        ll.setStyleSheet(f"font-size: 9px; color: {MUTED}; border: none;")
        ll.setAlignment(Qt.AlignmentFlag.AlignCenter)
        fl.addWidget(vl)
        fl.addWidget(ll)
        f._val_lbl = vl
        return f

    def refresh(self):
        self.kpi_projects.update_value(len(projects))
        self.kpi_tasks.update_value(len(tasks))
        terminated = sum(1 for t in tasks if t["statut"] == "Terminée")
        total = len(tasks)
        pct = round((terminated / total) * 100) if total else 0
        self.donut.set_pct(pct)
        self.pct_lbl.setText(f"{pct}% Avancement")
        self.term_lbl.setText(f"{terminated}/{total} terminées")
        self.stat_retard._val_lbl.setText(str(sum(1 for t in tasks if infer_statut(t) == "En retard")))
        self.stat_afaire._val_lbl.setText(str(sum(1 for t in tasks if infer_statut(t) == "À faire")))
        self.stat_proche._val_lbl.setText(str(sum(1 for t in tasks if infer_statut(t) == "Terminée proche")))

# ── Task Detail Dialog ────────────────────────────────────────────────────────
class TaskDetailDialog(QDialog):
    def __init__(self, task, parent=None):
        super().__init__(parent)
        self.task = task
        self.setWindowTitle(f"Détail — {task['titre']}")
        self.setMinimumSize(500, 480)
        self.setStyleSheet(GLOBAL_STYLE + input_style())
        lay = QVBoxLayout(self)
        lay.setSpacing(10)
        lay.setContentsMargins(24, 22, 24, 22)

        # Header
        st = infer_statut(task)
        header = QHBoxLayout()
        title_lbl = QLabel(task["titre"])
        title_lbl.setStyleSheet(f"font-size: 18px; font-weight: 800; color: {TEXT};")
        title_lbl.setWordWrap(True)
        header.addWidget(title_lbl, stretch=1)
        header.addWidget(Badge(st))
        lay.addLayout(header)

        # Separator
        sep = QFrame()
        sep.setFrameShape(QFrame.Shape.HLine)
        sep.setStyleSheet(f"color: {BORDER};")
        lay.addWidget(sep)

        # Properties grid
        grid = QGridLayout()
        grid.setSpacing(10)
        grid.setColumnMinimumWidth(0, 120)

        def prop_label(text):
            l = QLabel(text)
            l.setStyleSheet(f"font-size: 10px; font-weight: 700; color: {MUTED}; text-transform: uppercase; letter-spacing: 0.5px;")
            return l

        def val_label(text, color=TEXT):
            l = QLabel(text or "—")
            l.setStyleSheet(f"font-size: 13px; color: {color}; font-weight: 500;")
            l.setWordWrap(True)
            return l

        # Responsable
        resp_name = task.get("responsable") or "Non attribué"
        resp_obj = next((r for r in responsables if r["nom"] == resp_name), None)
        resp_str = f"{resp_name}" + (f"  ·  {resp_obj['role']}" if resp_obj else "")
        grid.addWidget(prop_label("Responsable"), 0, 0)
        grid.addWidget(val_label(resp_str), 0, 1)

        # Email
        email_str = resp_obj["email"] if resp_obj and resp_obj.get("email") else "—"
        grid.addWidget(prop_label("Email"), 1, 0)
        grid.addWidget(val_label(email_str, INFO), 1, 1)

        # Échéance
        diff = None
        try:
            diff = (date.fromisoformat(task["echeance"]) - date.today()).days
        except:
            pass
        ech_color = DANGER if st == "En retard" else WARNING if st == "Terminée proche" else TEXT
        ech_extra = ""
        if diff is not None:
            if diff < 0:   ech_extra = f"  ({abs(diff)} jour{'s' if abs(diff)>1 else ''} de retard)"
            elif diff == 0: ech_extra = "  (aujourd'hui)"
            elif diff <= 2: ech_extra = f"  (dans {diff} jour{'s' if diff>1 else ''})"
        grid.addWidget(prop_label("Échéance"), 2, 0)
        grid.addWidget(val_label(fmt_date(task.get("echeance","")) + ech_extra, ech_color), 2, 1)

        # Priorité
        grid.addWidget(prop_label("Priorité"), 3, 0)
        prio = task.get("priorite", "Moyenne")
        grid.addWidget(val_label(prio, PRIORITY_COLORS.get(prio, MUTED)), 3, 1)

        # Projet
        proj = next((p for p in projects if p["id"] == task.get("project_id")), None)
        grid.addWidget(prop_label("Projet"), 4, 0)
        grid.addWidget(val_label(proj["nom"] if proj else "—"), 4, 1)

        lay.addLayout(grid)

        # Description
        sep2 = QFrame()
        sep2.setFrameShape(QFrame.Shape.HLine)
        sep2.setStyleSheet(f"color: {BORDER};")
        lay.addWidget(sep2)

        lay.addWidget(prop_label("Description"))
        desc_text = task.get("description") or "Aucune description."
        desc_lbl = QLabel(desc_text)
        desc_lbl.setStyleSheet(f"""
            font-size: 13px; color: {TEXT if task.get('description') else MUTED};
            background: {SURFACE2}; border-radius: 8px;
            padding: 10px 12px; border: 1px solid {BORDER};
        """)
        desc_lbl.setWordWrap(True)
        desc_lbl.setMinimumHeight(60)
        lay.addWidget(desc_lbl)

        # Relances liées
        linked = [h for h in relance_history if h["taskTitle"] == task["titre"]]
        if linked:
            sep3 = QFrame()
            sep3.setFrameShape(QFrame.Shape.HLine)
            sep3.setStyleSheet(f"color: {BORDER};")
            lay.addWidget(sep3)
            lay.addWidget(prop_label(f"Relances envoyées ({len(linked)})"))
            for h in linked[:3]:
                hl = QLabel(f"✉  {h['email']}  ·  {fmt_date(h['date'])}  ·  {h.get('mode','—')}")
                hl.setStyleSheet(f"font-size: 11px; color: {MUTED}; background: {SURFACE2}; border-radius: 6px; padding: 5px 10px;")
                lay.addWidget(hl)

        lay.addStretch()

        # Buttons
        btn_row = QHBoxLayout()
        edit_btn = QPushButton("✏️  Modifier")
        edit_btn.setStyleSheet(btn_style(BORDER, TEXT))
        edit_btn.clicked.connect(self.on_edit)
        close_btn = QPushButton("Fermer")
        close_btn.setStyleSheet(btn_style())
        close_btn.clicked.connect(self.accept)
        btn_row.addWidget(edit_btn)
        btn_row.addStretch()
        btn_row.addWidget(close_btn)
        lay.addLayout(btn_row)

    def on_edit(self):
        dlg = TaskDialog(self.task["project_id"], task=self.task, parent=self)
        if dlg.exec() == QDialog.DialogCode.Accepted:
            data = dlg.get_data()
            task_service.update(
                self.task["id"],
                titre=data["titre"],
                description=data["description"],
                responsable_id=data["responsable_id"],
                echeance=data["echeance"],
                priorite=data["priorite"],
                statut=data["statut"],
            )
            load_all()
        self.accept()

# ── Main task area ────────────────────────────────────────────────────────────
class TaskArea(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.active_project_id = None
        self.filter_statut = "Tous"
        self.search_text = ""
        lay = QVBoxLayout(self)
        lay.setContentsMargins(20, 16, 20, 16)
        lay.setSpacing(12)

        # Top bar
        top = QHBoxLayout()
        self.project_title = QLabel("Sélectionnez un projet")
        self.project_title.setStyleSheet(f"font-size: 17px; font-weight: 800; color: {TEXT};")
        self.add_task_btn = QPushButton("+ Ajouter une tâche")
        self.add_task_btn.setStyleSheet(btn_style())
        self.add_task_btn.clicked.connect(self.on_add_task)
        top.addWidget(self.project_title)
        top.addStretch()
        top.addWidget(self.add_task_btn)
        lay.addLayout(top)

        # Search + filters
        search_row = QHBoxLayout()
        self.search = QLineEdit()
        self.search.setPlaceholderText("Rechercher une tâche…")
        self.search.setStyleSheet(input_style().split("QTextEdit")[0])
        self.search.textChanged.connect(self.on_search)
        search_row.addWidget(self.search)
        lay.addLayout(search_row)

        # Filter buttons
        filter_row = QHBoxLayout()
        filter_row.setSpacing(5)
        self.filter_btns = {}
        for s in ["Tous", "À faire", "En cours", "Terminée", "En retard", "Terminée proche"]:
            btn = QPushButton(s)
            btn.setCheckable(True)
            btn.setChecked(s == "Tous")
            btn.setStyleSheet(self._filter_style(s == "Tous"))
            btn.clicked.connect(lambda _, st=s, b=btn: self.on_filter(st))
            self.filter_btns[s] = btn
            filter_row.addWidget(btn)
        filter_row.addStretch()
        lay.addLayout(filter_row)

        # Table
        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels(["Titre", "Responsable", "Priorité", "Échéance", "Statut", "Actions"])
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(5, QHeaderView.ResizeMode.Fixed)
        self.table.setColumnWidth(5, 130)
        self.table.verticalHeader().setVisible(False)
        self.table.setShowGrid(False)
        self.table.setAlternatingRowColors(True)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.table.setStyleSheet(f"""
            QTableWidget {{
                background: {SURFACE}; border: 1.5px solid {BORDER};
                border-radius: 12px; gridline-color: transparent;
            }}
            QHeaderView::section {{
                background: {SURFACE2}; color: {MUTED};
                font-size: 10px; font-weight: 700; text-transform: uppercase;
                padding: 8px 13px; border: none; border-bottom: 1.5px solid {BORDER};
            }}
            QTableWidget::item {{ padding: 8px 13px; }}
            QTableWidget::item:alternate {{ background: {SURFACE2}; }}
            QTableWidget::item:selected {{ background: {ACCENT_L}; color: {TEXT}; }}
        """)
        self.table.setToolTip("Double-cliquez sur une ligne pour voir les détails")
        self.table.cellDoubleClicked.connect(self.on_row_double_click)
        lay.addWidget(self.table)

        # Empty state (aucune tâche dans un projet)
        self.empty_widget = QWidget()
        empty_lay = QVBoxLayout(self.empty_widget)
        empty_lay.setAlignment(Qt.AlignmentFlag.AlignCenter)
        empty_icon = QLabel("✅")
        empty_icon.setStyleSheet("font-size: 48px;")
        empty_icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.empty_title = QLabel("Aucune tâche")
        self.empty_title.setStyleSheet(f"font-size: 17px; font-weight: 800; color: {TEXT};")
        self.empty_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.empty_desc = QLabel("Ajoutez des tâches pour commencer le suivi.")
        self.empty_desc.setStyleSheet(f"color: {MUTED}; font-size: 13px;")
        self.empty_desc.setAlignment(Qt.AlignmentFlag.AlignCenter)
        empty_add = QPushButton("+ Ajouter une tâche")
        empty_add.setStyleSheet(btn_style())
        empty_add.clicked.connect(self.on_add_task)
        for w in [empty_icon, self.empty_title, self.empty_desc, empty_add]:
            empty_lay.addWidget(w)
        lay.addWidget(self.empty_widget)
        self.empty_widget.hide()

        # Home screen (accueil — cartes projets)
        self.home_widget = QWidget()
        self.home_widget.setStyleSheet("background: transparent;")
        home_outer = QVBoxLayout(self.home_widget)
        home_outer.setContentsMargins(0, 20, 0, 0)
        home_outer.setSpacing(20)

        welcome = QLabel("Bonjour 👋 Quel projet aujourd'hui ?")
        welcome.setStyleSheet(f"font-size: 20px; font-weight: 800; color: {TEXT};")
        welcome.setAlignment(Qt.AlignmentFlag.AlignCenter)
        home_outer.addWidget(welcome)

        sub = QLabel("Cliquez sur un projet pour voir ses tâches.")
        sub.setStyleSheet(f"font-size: 13px; color: {MUTED};")
        sub.setAlignment(Qt.AlignmentFlag.AlignCenter)
        home_outer.addWidget(sub)

        # Scroll area pour les cartes
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { border: none; background: transparent; }")
        cards_container = QWidget()
        cards_container.setStyleSheet("background: transparent;")
        self.cards_layout = QGridLayout(cards_container)
        self.cards_layout.setSpacing(14)
        self.cards_layout.setContentsMargins(20, 10, 20, 10)
        scroll.setWidget(cards_container)
        home_outer.addWidget(scroll)

        lay.addWidget(self.home_widget)
        self.home_widget.hide()

    def show_home(self):
        """Affiche l'écran d'accueil avec les cartes projets."""
        self.active_project_id = None
        self.project_title.setText("Sélectionnez un projet")
        self.add_task_btn.hide()
        self.search.hide()
        for btn in self.filter_btns.values():
            btn.hide()
        self.table.hide()
        self.empty_widget.hide()

        # Rebuild project cards
        while self.cards_layout.count():
            item = self.cards_layout.takeAt(0)
            if item.widget(): item.widget().deleteLater()

        if not projects:
            no_proj = QLabel("Aucun projet.\nCréez-en un depuis la barre latérale.")
            no_proj.setStyleSheet(f"color: {MUTED}; font-size: 13px;")
            no_proj.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.cards_layout.addWidget(no_proj, 0, 0)
        else:
            for i, p in enumerate(projects):
                p_tasks = [t for t in tasks if t.get("project_id") == p["id"]]
                total = len(p_tasks)
                done  = sum(1 for t in p_tasks if t["statut"] == "Terminée")
                retard = sum(1 for t in p_tasks if infer_statut(t) == "En retard")
                pct = round((done / total) * 100) if total else 0

                card = QFrame()
                card.setFixedSize(200, 160)
                card.setCursor(Qt.CursorShape.PointingHandCursor)
                card.setStyleSheet(f"""
                    QFrame {{
                        background: {SURFACE}; border-radius: 14px;
                        border: 1.5px solid {BORDER};
                    }}
                    QFrame:hover {{
                        border-color: {ACCENT}; background: {ACCENT_L};
                    }}
                """)
                cl = QVBoxLayout(card)
                cl.setContentsMargins(16, 14, 16, 14)
                cl.setSpacing(6)

                icon_lbl = QLabel("📁")
                icon_lbl.setStyleSheet("font-size: 26px; border: none;")
                name_lbl = QLabel(p["nom"])
                name_lbl.setStyleSheet(f"font-size: 14px; font-weight: 800; color: {TEXT}; border: none;")
                name_lbl.setWordWrap(True)
                tasks_lbl = QLabel(f"{total} tâche{'s' if total != 1 else ''} · {pct}% fait")
                tasks_lbl.setStyleSheet(f"font-size: 11px; color: {MUTED}; border: none;")

                if retard > 0:
                    retard_lbl = QLabel(f"⚠ {retard} en retard")
                    retard_lbl.setStyleSheet(f"font-size: 11px; color: {DANGER}; font-weight: 700; border: none;")
                else:
                    retard_lbl = QLabel("✓ À jour")
                    retard_lbl.setStyleSheet(f"font-size: 11px; color: {ACCENT}; font-weight: 700; border: none;")

                for w in [icon_lbl, name_lbl, tasks_lbl, retard_lbl]:
                    cl.addWidget(w)

                # Rendre la carte cliquable
                pid = p["id"]
                card.mousePressEvent = lambda e, pid=pid: self.window().on_project_selected(pid)

                row, col = divmod(i, 3)
                self.cards_layout.addWidget(card, row, col)

        self.home_widget.show()

    def _show_task_view(self):
        """Affiche la vue tâches (barre de recherche, filtres, table)."""
        self.add_task_btn.show()
        self.search.show()
        for btn in self.filter_btns.values():
            btn.show()
        self.home_widget.hide()

    def _filter_style(self, active):
        if active:
            return f"QPushButton {{ padding: 3px 11px; border-radius: 20px; border: 1.5px solid {ACCENT}; background: {ACCENT_L}; color: {ACCENT}; font-size: 11px; font-weight: 700; }}"
        return f"QPushButton {{ padding: 3px 11px; border-radius: 20px; border: 1.5px solid {BORDER}; background: transparent; color: {MUTED}; font-size: 11px; font-weight: 700; }} QPushButton:hover {{ border-color: {ACCENT}; color: {ACCENT}; }}"

    def on_filter(self, statut):
        self.filter_statut = statut
        for s, btn in self.filter_btns.items():
            btn.setStyleSheet(self._filter_style(s == statut))
        self.refresh()

    def on_search(self, text):
        self.search_text = text
        self.refresh()

    def on_add_task(self):
        if not self.active_project_id:
            QMessageBox.warning(self, "Attention", "Sélectionnez d'abord un projet.")
            return
        dlg = TaskDialog(self.active_project_id, parent=self)
        if dlg.exec() == QDialog.DialogCode.Accepted:
            data = dlg.get_data()
            if not data["titre"]:
                return
            task_service.create(
                project_id=self.active_project_id,
                titre=data["titre"],
                description=data["description"],
                responsable_id=data["responsable_id"],
                echeance=data["echeance"],
                priorite=data["priorite"],
                statut=data["statut"],
            )
            load_all()
            self.refresh()
            self.window().refresh_all()

    def set_project(self, project_id):
        self.active_project_id = project_id
        p = next((p for p in projects if p["id"] == project_id), None)
        self.project_title.setText(f"Tâches — {p['nom']}" if p else "")
        self._show_task_view()
        self.refresh()

    def refresh(self):
        proj_tasks = [t for t in tasks if t.get("project_id") == self.active_project_id]
        filtered = [t for t in proj_tasks
                    if (self.filter_statut == "Tous" or infer_statut(t) == self.filter_statut)
                    and (not self.search_text or self.search_text.lower() in t["titre"].lower())]

        if not proj_tasks:
            self.table.hide()
            self.empty_widget.show()
            return

        self.empty_widget.hide()
        self.table.show()
        self.table.setRowCount(len(filtered))

        for row, task in enumerate(filtered):
            st = infer_statut(task)
            self.table.setItem(row, 0, QTableWidgetItem(task["titre"]))

            # Responsable cliquable
            resp_widget = QWidget()
            resp_lay = QHBoxLayout(resp_widget)
            resp_lay.setContentsMargins(6, 2, 6, 2)
            resp_combo = QComboBox()
            resp_combo.addItem("Non attribué")
            for r in responsables:
                resp_combo.addItem(f"{r['nom']}")
            current_resp = task.get("responsable") or "Non attribué"
            idx = resp_combo.findText(current_resp)
            if idx >= 0:
                resp_combo.setCurrentIndex(idx)
            resp_combo.setStyleSheet(f"""
                QComboBox {{
                    background: transparent; border: none;
                    font-size: 12px; color: {TEXT}; padding: 2px 4px;
                }}
                QComboBox:hover {{
                    background: {ACCENT_L}; border-radius: 6px;
                    border: 1px solid {ACCENT};
                }}
                QComboBox::drop-down {{ border: none; width: 16px; }}
            """)
            resp_combo.currentTextChanged.connect(lambda val, t=task: self._update_resp(t, val))
            resp_lay.addWidget(resp_combo)
            self.table.setCellWidget(row, 1, resp_widget)

            self.table.setCellWidget(row, 2, PriorityBadge(task.get("priorite","Moyenne")))
            date_item = QTableWidgetItem(fmt_date(task.get("echeance","")))
            if st == "En retard":
                date_item.setForeground(QColor(DANGER))
            self.table.setItem(row, 3, date_item)

            # Statut cliquable
            st_widget = QWidget()
            st_lay = QHBoxLayout(st_widget)
            st_lay.setContentsMargins(4, 2, 4, 2)
            st_combo = QComboBox()
            statuts = ["À faire", "En cours", "Terminée"]
            for s in statuts:
                st_combo.addItem(s)
            base_statut = task.get("statut", "À faire")
            si = st_combo.findText(base_statut)
            if si >= 0:
                st_combo.setCurrentIndex(si)
            bg, color, _ = STATUS_COLORS.get(st, STATUS_COLORS["À faire"])
            st_combo.setStyleSheet(f"""
                QComboBox {{
                    background: {bg}; color: {color};
                    border-radius: 10px; padding: 2px 10px;
                    font-size: 11px; font-weight: 700; border: none;
                }}
                QComboBox:hover {{ border: 1px solid {color}; }}
                QComboBox::drop-down {{ border: none; width: 16px; }}
            """)
            st_combo.currentTextChanged.connect(lambda val, t=task: self._update_statut(t, val))
            st_lay.addWidget(st_combo)
            self.table.setCellWidget(row, 4, st_widget)

            # Actions
            actions = QWidget()
            act_lay = QHBoxLayout(actions)
            act_lay.setContentsMargins(4, 2, 4, 2)
            act_lay.setSpacing(4)

            edit_btn = QPushButton("✏️")
            edit_btn.setFixedSize(28, 26)
            edit_btn.setStyleSheet(btn_style(BORDER, TEXT))
            edit_btn.setToolTip("Modifier")
            edit_btn.clicked.connect(lambda _, t=task: self.on_edit_task(t))

            del_btn = QPushButton("🗑")
            del_btn.setFixedSize(28, 26)
            del_btn.setStyleSheet(btn_style(DANGER_L, DANGER))
            del_btn.setToolTip("Supprimer")
            del_btn.clicked.connect(lambda _, t=task: self.on_delete_task(t))

            act_lay.addWidget(edit_btn)

            if st == "En retard":
                rel_btn = QPushButton("📧")
                rel_btn.setFixedSize(28, 26)
                rel_btn.setStyleSheet(btn_style(DANGER_L, DANGER))
                rel_btn.setToolTip("Relancer")
                rel_btn.clicked.connect(lambda _, t=task: self.on_relance(t))
                act_lay.addWidget(rel_btn)

            act_lay.addWidget(del_btn)
            self.table.setCellWidget(row, 5, actions)
            self.table.setRowHeight(row, 46)

    def on_row_double_click(self, row, col):
        proj_tasks = [t for t in tasks if t.get("project_id") == self.active_project_id]
        filtered = [t for t in proj_tasks
                    if (self.filter_statut == "Tous" or infer_statut(t) == self.filter_statut)
                    and (not self.search_text or self.search_text.lower() in t["titre"].lower())]
        if row < len(filtered):
            dlg = TaskDetailDialog(filtered[row], parent=self)
            dlg.exec()
            self.refresh()
            self.window().refresh_all()

    def _update_statut(self, task, val):
        task_service.update_statut(task["id"], val)
        load_all()
        self.refresh()
        self.window().refresh_all()

    def _update_resp(self, task, val):
        if val == "Non attribué":
            task_service.update_responsable(task["id"], None)
        else:
            r = next((r for r in responsables if r["nom"] == val), None)
            if r:
                task_service.update_responsable(task["id"], r["id"])
        load_all()
        self.window().refresh_all()

    def on_edit_task(self, task):
        dlg = TaskDialog(task["project_id"], task=task, parent=self)
        if dlg.exec() == QDialog.DialogCode.Accepted:
            data = dlg.get_data()
            task_service.update(
                task["id"],
                titre=data["titre"],
                description=data["description"],
                responsable_id=data["responsable_id"],
                echeance=data["echeance"],
                priorite=data["priorite"],
                statut=data["statut"],
            )
            load_all()
            self.refresh()
            self.window().refresh_all()

    def on_delete_task(self, task):
        reply = QMessageBox.question(self, "Confirmer", f"Supprimer « {task['titre']} » ?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            task_service.delete(task["id"])
            load_all()
            self.refresh()
            self.window().refresh_all()

    def on_relance(self, task):
        dlg = RelanceDialog(task, parent=self)
        if dlg.exec() == QDialog.DialogCode.Accepted:
            data = dlg.get_data()
            mode = "Simulation" if data["simulation"] else "Réel"
            masked = data["email"][:3] + "***" + data["email"][data["email"].find("@"):] if "@" in data["email"] else data["email"]
            relance_service.log(task["id"], task["titre"], masked, mode)
            load_all()
            msg = f"✅ Relance simulée pour {data['email']}" if data["simulation"] else f"📧 Mail envoyé à {data['email']}"
            QMessageBox.information(self, "Relance", msg)
            self.window().refresh_all()

# ── Main Window ───────────────────────────────────────────────────────────────
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Nudge — Suivi de projet")
        self.setMinimumSize(1100, 680)
        self.setStyleSheet(GLOBAL_STYLE)

        central = QWidget()
        self.setCentralWidget(central)
        main_lay = QHBoxLayout(central)
        main_lay.setContentsMargins(0, 0, 0, 0)
        main_lay.setSpacing(0)

        self.sidebar   = Sidebar()
        self.task_area = TaskArea()
        self.dashboard = DashboardPanel()

        # Topbar wrapper
        content = QWidget()
        content_lay = QVBoxLayout(content)
        content_lay.setContentsMargins(0, 0, 0, 0)
        content_lay.setSpacing(0)

        # Topbar
        topbar = QFrame()
        topbar.setStyleSheet(f"background: {SURFACE}; border-bottom: 1.5px solid {BORDER}; border-radius: 0;")
        topbar.setFixedHeight(50)
        tb_lay = QHBoxLayout(topbar)
        tb_lay.setContentsMargins(18, 0, 18, 0)

        self.global_search = QLineEdit()
        self.global_search.setPlaceholderText("Rechercher une tâche…")
        self.global_search.setStyleSheet(f"""
            QLineEdit {{ background: {SURFACE2}; border: 1.5px solid {BORDER};
                border-radius: 8px; padding: 5px 12px; font-size: 13px; color: {TEXT}; }}
        """)
        self.global_search.setFixedWidth(280)

        guide_btn = QPushButton("Guide")
        guide_btn.setStyleSheet(btn_style(BORDER, TEXT))
        guide_btn.clicked.connect(self.show_onboarding)

        self.relance_btn = QPushButton("📧  Relancer par mail")
        self.relance_btn.setStyleSheet(btn_style())
        self.relance_btn.clicked.connect(self.on_relance_global)

        tb_lay.addWidget(self.global_search)
        tb_lay.addStretch()
        tb_lay.addWidget(guide_btn)
        tb_lay.addWidget(self.relance_btn)

        content_lay.addWidget(topbar)

        # Body
        body = QHBoxLayout()
        body.setContentsMargins(0, 0, 0, 0)
        body.setSpacing(0)
        body.addWidget(self.task_area)
        body.addWidget(self.dashboard)
        content_lay.addLayout(body)

        main_lay.addWidget(self.sidebar)
        main_lay.addWidget(content)

        # Signals
        self.sidebar.project_selected.connect(self.on_project_selected)
        self.sidebar.add_project.connect(self.on_add_project)
        self.sidebar.add_responsable.connect(self.on_add_responsable)
        self.sidebar.go_home.connect(self.on_go_home)

        # Onboarding une seule fois
        config_path = os.path.join(os.path.expanduser("~"), ".nudge_config.json")
        already_seen = False
        if os.path.exists(config_path):
            try:
                with open(config_path, "r") as f:
                    already_seen = json.load(f).get("onboarding_done", False)
            except:
                pass
        if not already_seen:
            self.show_onboarding()
            try:
                with open(config_path, "w") as f:
                    json.dump({"onboarding_done": True}, f)
            except:
                pass

        # Afficher l'accueil au démarrage
        self.task_area.show_home()

    def on_go_home(self):
        self.task_area.show_home()
        self.sidebar.refresh(None)
        self.dashboard.refresh()

    def show_onboarding(self):
        dlg = OnboardingDialog(self)
        dlg.exec()

    def on_project_selected(self, pid):
        self.task_area.set_project(pid)
        self.sidebar.refresh(pid)

    def on_add_project(self):
        dlg = ProjectDialog(parent=self)
        if dlg.exec() == QDialog.DialogCode.Accepted:
            data = dlg.get_data()
            if not data["nom"]:
                return
            p = project_service.create(data["nom"], data["description"], data.get("date_fin", ""))
            load_all()
            self.refresh_all()
            self.on_project_selected(p["id"])

    def on_add_responsable(self):
        dlg = ResponsableDialog(parent=self)
        if dlg.exec() == QDialog.DialogCode.Accepted:
            data = dlg.get_data()
            if not data["nom"]:
                return
            try:
                user_service.create(data["nom"], data["email"], data["role"])
            except Exception:
                QMessageBox.warning(self, "Erreur", "Cet email est déjà utilisé.")
                return
            load_all()
            self.refresh_all()

    def on_relance_global(self):
        en_retard = [t for t in tasks if infer_statut(t) == "En retard"]
        if not en_retard:
            QMessageBox.information(self, "Relance", "Aucune tâche en retard pour l'instant.")
            return
        self.task_area.on_relance(en_retard[0])

    def refresh_all(self):
        self.sidebar.refresh()
        self.dashboard.refresh()
        if self.task_area.active_project_id:
            self.task_area.refresh()
        elif self.task_area.home_widget.isVisible():
            self.task_area.show_home()

# ── Entry point ───────────────────────────────────────────────────────────────
if __name__ == "__main__":
    init_db()
    load_all()
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    window = MainWindow()
    window.show()
    scheduler_service.start(run_immediately=True)
    exit_code = app.exec()
    scheduler_service.stop()
    sys.exit(exit_code)
