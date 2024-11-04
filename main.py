import sys
import os
import subprocess
import psutil
import configparser
import locale as pylocale
from PySide6.QtWidgets import (
    QApplication, QSystemTrayIcon, QMenu, QDialog, QVBoxLayout, QLabel,
    QLineEdit, QPushButton, QMessageBox, QFileDialog, QHBoxLayout
)
from PySide6.QtGui import QIcon, QAction
from PySide6.QtCore import QTranslator, QLocale, QObject, Qt
from win32com.client import Dispatch

class SettingsDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle(self.tr('Settings'))
        self.setFixedSize(400, 100)
        self.client_conf_path_edit = QLineEdit()
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        config_layout = QHBoxLayout()

        label = QLabel(self.tr('Path to client.conf:'))
        browse_button = QPushButton(self.tr('Browse'))
        browse_button.clicked.connect(self.browse_client_conf_path)

        config_layout.addWidget(self.client_conf_path_edit)
        config_layout.addWidget(browse_button)

        layout.addWidget(label)
        layout.addLayout(config_layout)

        save_button = QPushButton(self.tr('Save'))
        save_button.clicked.connect(self.save_settings)
        layout.addWidget(save_button)

        self.setLayout(layout)

    def browse_client_conf_path(self):
        path, _ = QFileDialog.getOpenFileName(
            self,
            self.tr('Choose client.conf'),
            'C:\\',
            self.tr('Config files (*.conf)')
        )
        if path:
            self.client_conf_path_edit.setText(path)

    def save_settings(self):
        client_conf_path = self.client_conf_path_edit.text()

        if not os.path.exists(client_conf_path):
            QMessageBox.critical(
                self,
                self.tr('Error'),
                self.tr('Invalid path')
            )
            return

        config = configparser.ConfigParser()
        config['Settings'] = {'client_conf_path': client_conf_path}

        with open('settings.ini', 'w') as settings_file:
            config.write(settings_file)

        QMessageBox.information(
            self,
            self.tr('Success'),
            self.tr('Settings saved successfully')
        )

    def closeEvent(self, event):
        self.hide()
        event.ignore()

class SystemTrayApp(QObject):
    def __init__(self):
        super().__init__()
        self.app = QApplication.instance()
        self.tray_icon = QSystemTrayIcon(QIcon('icons/app.png'), self.app)
        self.tray_icon.setToolTip(self.tr('cheesy proxy - Idle'))
        self.tray_icon.setVisible(True)

        self.create_menu()
        self.proxy_process = None
        self.wireproxy_path = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'wireproxy.exe')
        self.client_conf_path = None
        self.settings_dialog = SettingsDialog()
        self.load_settings()
        self.check_proxy_status()
        self.set_autostart_status()
        self.validate_settings()

    def create_menu(self):
        menu = QMenu()

        self.start_action = QAction(self.tr('Start'), self.app)
        self.start_action.setIcon(QIcon('icons/start.png'))
        self.start_action.triggered.connect(self.start_proxy)
        menu.addAction(self.start_action)

        self.stop_action = QAction(self.tr('Stop'), self.app)
        self.stop_action.setIcon(QIcon('icons/stop.png'))
        self.stop_action.triggered.connect(self.stop_proxy)
        self.stop_action.setEnabled(False)
        menu.addAction(self.stop_action)

        menu.addSeparator()

        self.autostart_action = QAction(self.tr('Autostart'), self.app)
        self.autostart_action.setCheckable(True)
        self.autostart_action.triggered.connect(self.toggle_autostart)
        menu.addAction(self.autostart_action)

        self.settings_action = QAction(self.tr('Settings'), self.app)
        self.settings_action.setIcon(QIcon('icons/settings.png'))
        self.settings_action.triggered.connect(self.show_settings_dialog)
        menu.addAction(self.settings_action)

        menu.addSeparator()

        exit_action = QAction(self.tr('Exit'), self.app)
        exit_action.setIcon(QIcon('icons/app.png'))
        exit_action.triggered.connect(self.exit_app)
        menu.addAction(exit_action)

        self.tray_icon.setContextMenu(menu)

    def start_proxy(self):
        if not self.proxy_process:
            if self.wireproxy_path and self.client_conf_path:
                try:
                    self.proxy_process = subprocess.Popen(
                        [self.wireproxy_path, '-c', self.client_conf_path, '-s'],
                        creationflags=subprocess.CREATE_NO_WINDOW
                    )
                    self.start_action.setEnabled(False)
                    self.stop_action.setEnabled(True)
                    self.tray_icon.setToolTip(self.tr('cheesy proxy - Running'))
                    self.tray_icon.showMessage(
                        self.tr('cheesy proxy'),
                        self.tr('Proxy started successfully'),
                        QSystemTrayIcon.Information
                    )
                except Exception as e:
                    self.show_error(self.tr('Error starting proxy'), str(e))
            else:
                self.show_error(
                    self.tr('Configuration Error'),
                    self.tr('wireproxy.exe or client.conf path is invalid.')
                )

    def stop_proxy(self):
        if self.proxy_process:
            self.proxy_process.terminate()
            self.proxy_process = None
            self.start_action.setEnabled(True)
            self.stop_action.setEnabled(False)
            self.tray_icon.setToolTip(self.tr('cheesy proxy - Idle'))
            self.tray_icon.showMessage(
                self.tr('cheesy proxy'),
                self.tr('Proxy stopped successfully'),
                QSystemTrayIcon.Information
            )

    def exit_app(self):
        self.stop_proxy()
        self.app.quit()

    def load_settings(self):
        if os.path.exists('settings.ini'):
            config = configparser.ConfigParser()
            config.read('settings.ini')
            self.client_conf_path = config.get('Settings', 'client_conf_path', fallback=None)
        else:
            self.show_settings_dialog()
            self.validate_settings()

    def show_settings_dialog(self):
        if self.client_conf_path:
            self.settings_dialog.client_conf_path_edit.setText(self.client_conf_path)
        if self.settings_dialog.exec():
            self.client_conf_path = self.settings_dialog.client_conf_path_edit.text()
            self.save_settings()

    def save_settings(self):
        config = configparser.ConfigParser()
        config['Settings'] = {'client_conf_path': self.client_conf_path}
        with open('settings.ini', 'w') as settings_file:
            config.write(settings_file)
        self.validate_settings()

    def check_proxy_status(self):
        for proc in psutil.process_iter(['pid', 'name']):
            if proc.info.get('name') == 'wireproxy.exe':
                proc.kill()
                break
        self.start_action.setEnabled(True)
        self.stop_action.setEnabled(False)

    def set_autostart_status(self):
        shell = Dispatch('WScript.Shell')
        startup_folder = shell.SpecialFolders('Startup')
        shortcut_path = os.path.join(startup_folder, 'cheesy proxy.lnk')
        if os.path.exists(shortcut_path):
            self.autostart_action.setChecked(True)
            self.start_proxy()
        else:
            self.autostart_action.setChecked(False)

    def toggle_autostart(self):
        shell = Dispatch('WScript.Shell')
        startup_folder = shell.SpecialFolders('Startup')
        shortcut_path = os.path.join(startup_folder, 'cheesy proxy.lnk')
        target_path = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'cheesy proxy.exe')

        if self.autostart_action.isChecked():
            shortcut = shell.CreateShortCut(shortcut_path)
            shortcut.Targetpath = target_path
            shortcut.WorkingDirectory = os.path.dirname(target_path)
            shortcut.save()
        else:
            if os.path.exists(shortcut_path):
                os.remove(shortcut_path)

    def validate_settings(self):
        if not os.path.exists('settings.ini') or not self.client_conf_path:
            self.start_action.setEnabled(False)
            self.stop_action.setEnabled(False)
            self.autostart_action.setEnabled(False)
        else:
            self.start_action.setEnabled(True)
            self.autostart_action.setEnabled(True)

    def show_error(self, title, message):
        QMessageBox.critical(None, title, message)

def is_already_running():
    current_pid = os.getpid()
    for proc in psutil.process_iter(['pid', 'name']):
        if proc.info.get('name') == 'cheesy proxy.exe' and proc.pid != current_pid:
            return True
    return False

if __name__ == '__main__':
    if is_already_running():
        sys.exit(0)

    app = QApplication(sys.argv)
    translator = QTranslator()
    locale = pylocale.getlocale()[0]
    locale_dict = {None: 'en_US', 'English_UnitedStates': 'en_US', 'Ukrainian_Ukraine': 'uk_UA'}
    true_locale = locale_dict.get(locale, 'en_US')
    if translator.load(f"i18n/{true_locale}.qm"):
        app.installTranslator(translator)

    app.setWindowIcon(QIcon('icons/app.png'))
    app.setStyle('Fusion')

    tray_app = SystemTrayApp()
    sys.exit(app.exec())