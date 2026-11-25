# ALPHA PC MONITOR

Application Windows locale de surveillance matérielle — ALPHA TECHNOLOGY.

## Première livraison (socle fonctionnel)
Tableau de bord réel CPU/RAM/disques/réseau/processus, collecte périodique, historique SQLite, export CSV, tests automatisés et workflows Windows CI/build. Les températures, détails GPU et SMART ne sont pas simulés : ils restent indiqués indisponibles tant que leurs interfaces matérielles dédiées ne sont pas intégrées.

## Prérequis
Windows 10/11 64 bits, Python 3.12.

## Installation développeur
```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements-dev.txt
python -m app.main
```

## Tests
```powershell
python -m pytest -q
```

## Compilation EXE
```powershell
pyinstaller --noconfirm --clean --windowed --name ALPHA-PC-MONITOR packaging/alpha_pc_monitor.spec
```

Le dossier distribué sera `dist/ALPHA-PC-MONITOR/`. L'installateur Inno Setup est défini dans `installer/alpha-pc-monitor.iss`.

## Confidentialité
Aucun compte, serveur distant, télémétrie ni transmission applicative. Les données et la base SQLite restent sur le PC. Le réseau est uniquement mesuré via les compteurs locaux Windows.
