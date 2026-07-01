@echo off
echo Compilation de Team Analyser v2 en .exe...
echo Assurez-vous d'avoir installe PyInstaller (pip install pyinstaller)

python -m PyInstaller --onefile --windowed --icon=NONE --name "TeamAnalyser_v2" main.py

echo.
echo Le fichier .exe a ete genere dans le dossier "dist" !
pause
