import sys
from PyQt5 import QtWidgets, QtGui
import requests
import configparser

class SystemTrayIcon(QtWidgets.QSystemTrayIcon):
    def __init__(self, icon, parent=None):
        QtWidgets.QSystemTrayIcon.__init__(self, icon, parent)
        self.menu = QtWidgets.QMenu(parent)

        self.power_on_action = self.menu.addAction("On power WLED")
        self.power_on_action.setCheckable(True)
        self.power_on_action.triggered.connect(self.power_on)

        self.toggel_power_action = self.menu.addAction("Toggel WLED")
        self.toggel_power_action.setIcon(QtGui.QIcon("./src/switch-off.png"))
        self.toggel_power_action.triggered.connect(self.toggel_power)

        self.stop_action = self.menu.addAction("Quit")
        self.stop_action.triggered.connect(self.quit)

        self.setContextMenu(self.menu)
        
        self.config = configparser.ConfigParser()
        self.config.read('conf.ini')
        self.wled_ip = f"http://{self.config.get('settigs', 'wled_ip')}"
        self.on_power = self.config.getboolean('settigs', 'onPowerWLED')
        self.power_on_action.setChecked(self.on_power)

        if self.on_power:
            self.toggel_power_action.setIcon(QtGui.QIcon("./src/switch-on.png"))
            icon = QtGui.QIcon("./src/switch-on.png")
            requests.post(f'{self.wled_ip}/json/state', json={"on":True})

    def power_on(self):
        self.config.read('conf.ini')
        self.on_power = not self.on_power
        self.config.set('settigs', 'onPowerWLED', str(self.on_power))
        with open('conf.ini', 'w') as configfile:
            self.config.write(configfile)
        self.power_on_action.setChecked(self.on_power)
        if self.on_power:
            self.toggel_power_action.setIcon(QtGui.QIcon("./src/switch-on.png"))
            print("configured to power on after log in")
            requests.post(f'{self.wled_ip}/json/state', json={"on":True})
        else:
            print("configured to not power on after log in")
    
    def toggel_power(self):
        url = f'{self.wled_ip}/json/state'
        response = requests.get(url)
        data = response.json()
        on = bool(data["on"])
        if on:
            self.toggel_power_action.setIcon(QtGui.QIcon("./src/switch-off.png"))
            requests.post(f'{self.wled_ip}/json/state', json={"on":False})
        else:
            self.toggel_power_action.setIcon(QtGui.QIcon("./src/switch-on.png"))
            requests.post(f'{self.wled_ip}/json/state', json={"on":True})
        

    def quit(self):
        sys.exit()

app = QtWidgets.QApplication(sys.argv)
icon = QtGui.QIcon("./src/favicon.ico")
tray_icon = SystemTrayIcon(icon)
tray_icon.show()
sys.exit(app.exec_())
