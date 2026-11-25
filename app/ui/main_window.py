from pathlib import Path
from PySide6.QtCore import QTimer
from PySide6.QtWidgets import (QMainWindow,QWidget,QVBoxLayout,QHBoxLayout,QLabel,QGridLayout,
    QProgressBar,QPushButton,QFileDialog,QTableWidget,QTableWidgetItem,QTabWidget,QMessageBox,QSpinBox,QFormLayout)
import pyqtgraph as pg
from app.core.collector import SystemCollector
from app.database.history import HistoryStore
from app.services.exporter import export_snapshot_csv

def fmt_bytes(n):
    if n is None: return "Indisponible"
    n=float(n)
    for unit in ("o","Ko","Mo","Go","To"):
        if n < 1024 or unit == "To": return f"{n:.1f} {unit}"
        n /= 1024

def fmt_duration(sec):
    days, rem = divmod(int(max(0,sec)),86400); hours, rem = divmod(rem,3600); minutes,_ = divmod(rem,60)
    return f"{days} j {hours:02} h {minutes:02} min"

class Card(QWidget):
    def __init__(self,title):
        super().__init__(); self.value=QLabel("—"); self.value.setStyleSheet("font-size:24px;font-weight:700")
        self.detail=QLabel(""); self.bar=QProgressBar(); self.bar.setRange(0,100)
        layout=QVBoxLayout(self); layout.addWidget(QLabel(title)); layout.addWidget(self.value); layout.addWidget(self.bar); layout.addWidget(self.detail)
        self.setStyleSheet("QWidget{background:#202938;border-radius:10px;padding:7px;color:#f3f6fb}")
    def set_metric(self,value,pct=None,detail=""):
        self.value.setText(value); self.detail.setText(detail); self.bar.setVisible(pct is not None)
        if pct is not None: self.bar.setValue(int(max(0,min(100,pct))))

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__(); self.setWindowTitle("ALPHA PC MONITOR — ALPHA TECHNOLOGY"); self.resize(1180,780)
        self.collector=SystemCollector(); self.store=HistoryStore(Path.home()/"AppData/Local/AlphaTechnology/AlphaPCMonitor/history.sqlite3")
        self.last=None; self.cpu=[]; self.ram=[]; self._build()
        self.timer=QTimer(self); self.timer.timeout.connect(self.refresh); self.timer.start(1000); self.refresh()
    def _build(self):
        self.setStyleSheet("QMainWindow{background:#111827} QLabel{color:#e5e7eb} QPushButton{background:#2563eb;color:white;padding:8px;border-radius:6px} QTabWidget::pane{border:1px solid #374151} QTabBar::tab{background:#1f2937;color:#e5e7eb;padding:10px} QTabBar::tab:selected{background:#2563eb}")
        root=QWidget(); self.setCentralWidget(root); outer=QVBoxLayout(root)
        header=QHBoxLayout(); title=QLabel("ALPHA PC MONITOR"); title.setStyleSheet("font-size:26px;font-weight:800;color:#60a5fa")
        self.host=QLabel("Collecte en cours…"); header.addWidget(title); header.addStretch(); header.addWidget(self.host); outer.addLayout(header)
        tabs=QTabWidget(); outer.addWidget(tabs)
        dash=QWidget(); dl=QVBoxLayout(dash); grid=QGridLayout(); self.cards={}
        for i,(key,label) in enumerate([("cpu","Processeur"),("ram","Mémoire RAM"),("uptime","Fonctionnement"),("network","Réseau"),("disk","Activité disque"),("proc","Processus actifs")]):
            c=Card(label); self.cards[key]=c; grid.addWidget(c,i//3,i%3)
        dl.addLayout(grid); self.plot=pg.PlotWidget(title="Utilisation CPU et RAM (%)"); self.plot.setYRange(0,100); self.plot.showGrid(x=True,y=True,alpha=.25)
        self.cpu_line=self.plot.plot(pen=pg.mkPen("#38bdf8",width=2)); self.ram_line=self.plot.plot(pen=pg.mkPen("#a78bfa",width=2)); dl.addWidget(self.plot); tabs.addTab(dash,"Tableau de bord")
        diskpage=QWidget(); dlay=QVBoxLayout(diskpage); self.disk_table=QTableWidget(0,6); self.disk_table.setHorizontalHeaderLabels(["Volume","Montage","Type","Total","Libre","Occupation"]); dlay.addWidget(self.disk_table); tabs.addTab(diskpage,"Disques")
        infopage=QWidget(); il=QVBoxLayout(infopage); self.info=QLabel(); self.info.setWordWrap(True); il.addWidget(self.info); tabs.addTab(infopage,"Informations PC")
        settings=QWidget(); form=QFormLayout(settings); self.interval=QSpinBox(); self.interval.setRange(1,10); self.interval.setValue(1); self.interval.setSuffix(" seconde(s)"); self.interval.valueChanged.connect(lambda v:self.timer.setInterval(v*1000)); form.addRow("Fréquence",self.interval)
        btn=QPushButton("Exporter le dernier relevé CSV"); btn.clicked.connect(self.export_csv); form.addRow(btn); tabs.addTab(settings,"Paramètres")
        self.statusBar().showMessage("Surveillance locale active — aucune transmission de données.")
    def refresh(self):
        try:
            s=self.collector.collect(); self.last=s; self.store.add(s); self.host.setText(f"{s['host']} • {s['os']}")
            self.cards["cpu"].set_metric(f"{s['cpu_percent']:.1f} %",s["cpu_percent"],f"{s['cpu_count_physical']} cœurs / {s['cpu_count_logical']} threads")
            self.cards["ram"].set_metric(f"{s['ram_percent']:.1f} %",s["ram_percent"],f"{fmt_bytes(s['ram_used'])} / {fmt_bytes(s['ram_total'])}")
            self.cards["uptime"].set_metric(fmt_duration(s["uptime_seconds"]),None,f"Démarrage : {s['boot_time']}")
            self.cards["network"].set_metric(f"↓ {fmt_bytes(s['net_down_bps'])}/s",None,f"↑ {fmt_bytes(s['net_up_bps'])}/s")
            self.cards["disk"].set_metric(f"Lecture {fmt_bytes(s['disk_read_bps'])}/s",None,f"Écriture {fmt_bytes(s['disk_write_bps'])}/s")
            self.cards["proc"].set_metric(str(s["process_count"]),None,"Processus actifs")
            self.cpu=(self.cpu+[s["cpu_percent"]])[-120:]; self.ram=(self.ram+[s["ram_percent"]])[-120:]; self.cpu_line.setData(self.cpu); self.ram_line.setData(self.ram)
            self.disk_table.setRowCount(len(s["disks"]))
            for r,d in enumerate(s["disks"]):
                for col,val in enumerate([d["device"],d["mountpoint"],d["fstype"],fmt_bytes(d["total"]),fmt_bytes(d["free"]),f"{d['percent']:.1f} %"]): self.disk_table.setItem(r,col,QTableWidgetItem(str(val)))
            self.info.setText(f"Appareil : {s['host']}\nWindows : {s['os']}\nCœurs physiques : {s['cpu_count_physical']}\nThreads : {s['cpu_count_logical']}\nFréquence CPU : {s['cpu_frequency_mhz'] or 'Indisponible'} MHz\nRAM : {fmt_bytes(s['ram_total'])}\nDernier démarrage : {s['boot_time']}\nGPU : indisponible dans cette première version\nTempératures : capteurs dédiés non encore intégrés")
            self.statusBar().showMessage("Alerte : RAM fortement utilisée (≥ 90 %)." if s["ram_percent"]>=90 else "Surveillance locale active.")
        except Exception as e: self.statusBar().showMessage(f"Erreur de collecte : {e}")
    def export_csv(self):
        if not self.last: QMessageBox.warning(self,"Export","Aucune mesure disponible."); return
        path,_=QFileDialog.getSaveFileName(self,"Exporter","alpha-pc-monitor.csv","CSV (*.csv)")
        if path: export_snapshot_csv(self.last,path); QMessageBox.information(self,"Export","Export CSV terminé.")
