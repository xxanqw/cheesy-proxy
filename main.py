import sys
import os
import subprocess
from PyQt6.QtWidgets import QApplication, QSystemTrayIcon, QMenu, QDialog, QVBoxLayout, QLabel, QLineEdit, QPushButton, QMessageBox, QFileDialog, QHBoxLayout
from PyQt6.QtGui import QIcon, QAction
import psutil
from win32com.client import Dispatch
import configparser

folder = os.path.dirname(os.path.abspath(__file__))

class SettingsDialog(QDialog):
    def __init__(self, parent=None):
        super(SettingsDialog, self).__init__(parent)
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Settings')
        self.setFixedSize(400, 150)
        self.app = QApplication.instance()

        layout = QVBoxLayout()
        wireguard_group = QHBoxLayout()
        config_group = QHBoxLayout()

        label1 = QLabel('Path to wireproxy.exe:')
        self.wireproxy_path_edit = QLineEdit()
        browse_button1 = QPushButton('Browse')
        browse_button1.clicked.connect(self.browse_wireproxy_path)
        layout.addWidget(label1)
        wireguard_group.addWidget(self.wireproxy_path_edit)
        wireguard_group.addWidget(browse_button1)
        layout.addLayout(wireguard_group)

        label2 = QLabel('Path to client.conf:')
        self.client_conf_path_edit = QLineEdit()
        browse_button2 = QPushButton('Browse')
        browse_button2.clicked.connect(self.browse_client_conf_path)
        layout.addWidget(label2)
        config_group.addWidget(self.client_conf_path_edit)
        config_group.addWidget(browse_button2)
        layout.addLayout(config_group)

        save_button = QPushButton('Save')
        save_button.clicked.connect(self.save_settings)
        layout.addWidget(save_button)

        self.setLayout(layout)

    def browse_wireproxy_path(self):
        path, _ = QFileDialog.getOpenFileName(self, 'Choose wireproxy.exe', '', 'WireProxy (wireproxy.exe)')
        if path:
            self.wireproxy_path_edit.setText(path)

    def browse_client_conf_path(self):
        path, _ = QFileDialog.getOpenFileName(self, 'Choose client.conf', '', 'Config files (*.conf)')
        if path:
            self.client_conf_path_edit.setText(path)

    def save_settings(self):
        wireproxy_path = self.wireproxy_path_edit.text()
        client_conf_path = self.client_conf_path_edit.text()

        if not os.path.exists(wireproxy_path) or not os.path.exists(client_conf_path):
            QMessageBox.critical(self, 'Error', 'Invalid path')
            return

        config = configparser.ConfigParser()
        config['Settings'] = {
            'wireproxy_path': wireproxy_path,
            'client_conf_path': client_conf_path
        }
        with open('settings.ini', 'w') as f:
            config.write(f)

        QMessageBox.information(self, 'Success', 'Settings saved successfully')

    def closeEvent(self, event):
        if self.wireproxy_path_edit.text() and self.client_conf_path_edit.text():
            if QMessageBox.question(self, 'Close', 'Do you want to save the settings?', QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No) == QMessageBox.StandardButton.Yes:
                self.save_settings()
                event.ignore()
                self.hide()
            else:
                event.ignore()
                self.hide()
        else:
            event.ignore()
            self.hide()


class SystemTrayApp:
    def __init__(self, app):
        self.app = app
        self.tray_icon = QSystemTrayIcon(self.app)
        self.tray_icon.setIcon(QIcon('icons/app.png'))
        self.tray_icon.setVisible(True)
        self.tray_icon.setToolTip('cheesy proxy - Idle')
        self.menu = QMenu()
        self.menu.addSection('cheesy proxy')
        self.start_action = QAction('Start')
        self.start_action.setIcon(QIcon('icons/start.png'))
        self.start_action.triggered.connect(self.start_proxy)
        self.menu.addAction(self.start_action)
        self.stop_action = QAction('Stop')
        self.stop_action.setIcon(QIcon('icons/stop.png'))
        self.stop_action.triggered.connect(self.stop_proxy)
        self.menu.addAction(self.stop_action)
        self.menu.addSeparator()
        self.start_at_login_action = QAction('Autostart')
        self.start_at_login_action.setCheckable(True)
        self.start_at_login_action.triggered.connect(self.toggle_start_at_login)
        self.menu.addAction(self.start_at_login_action)
        self.settings_action = QAction('Settings')
        self.settings_action.setIcon(QIcon('icons/settings.png'))
        self.settings_action.triggered.connect(self.show_settings_dialog)
        self.menu.addAction(self.settings_action)
        self.tray_icon.setContextMenu(self.menu)
        self.menu.addSeparator()
        self.exit_action = QAction('Exit')
        self.exit_action.setIcon(QIcon('icons/app.png'))
        self.exit_action.triggered.connect(self.exit_app)
        self.menu.addAction(self.exit_action)
        self.proxy_process = None
        self.wireproxy_path = None
        self.client_conf_path = None
        self.load_settings()
        self.check_proxy_status_on_startup()
        self.set_start_at_login_status()
        self.check_settings()
        self.settings_dialog = SettingsDialog()

    def start_proxy(self):
        if self.proxy_process is None:
            try:
                self.proxy_process = subprocess.Popen([self.wireproxy_path, '-c', self.client_conf_path, '-s'], creationflags=subprocess.CREATE_NO_WINDOW)
                self.start_action.setEnabled(False)
                self.stop_action.setEnabled(True)
                self.tray_icon.showMessage('cheesy proxy', 'Proxy started successfully', QSystemTrayIcon.MessageIcon.Information)
                self.tray_icon.setToolTip('cheesy proxy - Running')
            except FileNotFoundError:
                self.show_error_message('Error', 'wireproxy.exe or client.conf not found')
            except Exception as e:
                self.show_error_message('Error', str(e))

    def stop_proxy(self):
       if self.proxy_process is not None:
            try:
                self.proxy_process.terminate()
                self.proxy_process = None
                self.start_action.setEnabled(True)
                self.stop_action.setEnabled(False)
                self.tray_icon.showMessage('cheesy proxy', 'Proxy stopped successfully', QSystemTrayIcon.MessageIcon.Information)
                self.tray_icon.setToolTip('cheesy proxy - Idle')
            except Exception as e:
                self.show_error_message('Error', str(e))

    def exit_app(self):
        if self.proxy_process is not None:
            self.stop_proxy()
        self.app.quit()

    def load_settings(self):
        if os.path.exists('settings.ini'):
            config = configparser.ConfigParser()
            config.read('settings.ini')
            self.wireproxy_path = config.get('Settings', 'wireproxy_path', fallback=None)
            self.client_conf_path = config.get('Settings', 'client_conf_path', fallback=None)

    def show_settings_dialog(self):
        if self.wireproxy_path:
            self.settings_dialog.wireproxy_path_edit.setText(self.wireproxy_path)
        if self.client_conf_path:
            self.settings_dialog.client_conf_path_edit.setText(self.client_conf_path)
        if self.settings_dialog.show():
            self.wireproxy_path = self.settings_dialog.wireproxy_path_edit.text()
            self.client_conf_path = self.settings_dialog.client_conf_path_edit.text()
            self.save_settings()

    def save_settings(self):
        config = configparser.ConfigParser()
        config['Settings'] = {
            'wireproxy_path': self.wireproxy_path,
            'client_conf_path': self.client_conf_path
        }
        with open('settings.ini', 'w') as f:
            config.write(f)
        self.check_settings()

    def check_proxy_status_on_startup(self):
        for proc in psutil.process_iter(['pid', 'name']):
            try:
                info = proc.info
                if info['name'] == 'wireguard.exe':
                    self.proxy_process = proc
                    self.proxy_process.kill()
                    self.start_action.setEnabled(True)
                    self.stop_action.setEnabled(False)
                    self.tray_icon.setToolTip('cheesy proxy - Idle')
                    return
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                pass
        self.start_action.setEnabled(True)
        self.stop_action.setEnabled(False)
        self.tray_icon.setToolTip('cheesy proxy - Idle')

    def set_start_at_login_status(self):
        shell = Dispatch('WScript.Shell')
        startup_folder = shell.SpecialFolders('Startup')
        if os.path.exists(os.path.join(startup_folder, 'cheesy proxy.lnk')):
            self.start_at_login_action.setChecked(True)
            self.start_proxy()
        else:
            self.start_at_login_action.setChecked(False)

    def toggle_start_at_login(self):
        shell = Dispatch('WScript.Shell')
        startup_folder = shell.SpecialFolders('Startup')
        if self.start_at_login_action.isChecked():
            shortcut = shell.CreateShortCut(os.path.join(startup_folder, 'cheesy proxy.lnk'))
            shortcut.Targetpath = os.path.join(folder, 'cheesy proxy.exe')
            shortcut.WorkingDirectory = folder
            shortcut.save()
        else:
            os.remove(os.path.join(startup_folder, 'cheesy proxy.lnk'))

    def check_settings(self):
        if not os.path.exists('settings.ini'):
            self.start_action.setEnabled(False)
            self.stop_action.setEnabled(False)
            self.start_at_login_action.setEnabled(False)
            error_label = QLabel('Error: settings.ini not found')
            error_label.setStyleSheet('color: red')
            layout = QVBoxLayout()
            layout.addWidget(error_label)
            self.menu.setLayout(layout)
        else:
            self.start_action.setEnabled(True)
            self.stop_action.setEnabled(False)
            self.start_at_login_action.setEnabled(True)

    def show_error_message(self, title, message):
        QMessageBox.critical(self.tray_icon, title, message)

def is_running():
    for proc in psutil.process_iter(['pid', 'name']):
        try:
            info = proc.info
            if info['name'] == 'cheesy proxy.exe' and proc.pid != os.getpid():
                return True
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass
    return False

if __name__ == '__main__':
    if is_running():
        print("Cheesy Proxy is already running.")
        sys.exit(0)

    app = QApplication(sys.argv)
    app.setWindowIcon(QIcon('icons/app.png'))
    app.setStyle('Fusion')

    if not os.path.exists('settings.ini'):
        settings_dialog = SettingsDialog()
        if settings_dialog.exec():
            wireproxy_path = settings_dialog.wireproxy_path_edit.text()
            client_conf_path = settings_dialog.client_conf_path_edit.text()
            config = configparser.ConfigParser()
            config['Settings'] = {
                'wireproxy_path': wireproxy_path,
                'client_conf_path': client_conf_path
            }
            with open('settings.ini', 'w') as f:
                config.write(f)

    tray_app = SystemTrayApp(app)
    sys.exit(app.exec())