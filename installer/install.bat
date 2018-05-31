python -OO -m PyInstaller --log-level=WARN ^
    --onefile --console ^
    --name="Delphin Automation" ^
    --icon=RIBuild_logo.ico ^
    --noconfirm ^
    --clean ^
    ../delphin_6_automation/main.py