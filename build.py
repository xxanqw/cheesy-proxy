from os import system

system('python -m nuitka --standalone --windows-icon-from-ico=icons/icon.png --include-data-dir=icons=icons --windows-console-mode=disable --enable-plugin=pyqt6  --product-name="cheesy proxy" --product-version=1.0.1.0 --file-description="Very easy wireproxy client" --copyright="©️2024 xxanqw" -o "cheesy proxy" main.py')