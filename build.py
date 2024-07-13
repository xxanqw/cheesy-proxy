from os import system

system('python -m nuitka --standalone --windows-icon-from-ico=icons/icon.png --include-data-dir=icons=icons --enable-plugin=pyqt6 --windows-console-mode=disable --product-name="cheesy proxy" --product-version=1.0.0.0 --file-description="Very easy wireproxy client" --copyright="©️2024 xxanqw" -o "cheesy proxy" main.py')