import sys
from PyQt5 import QtWidgets, QtGui
import requests
import configparser

debug = True

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

        self.wled_url = f"http://{self.config.get('settigs', 'wled_ip')}"
        self.off_preset = f"{self.config.get('settigs', 'off_preset')}"
        self.on_preset = f"{self.config.get('settigs', 'on_preset')}"
        self.on_power = self.config.getboolean('settigs', 'onPowerWLED')

        self.switch_on_icon = QtGui.QIcon("./src/switch-on.png")
        self.switch_off_icon = QtGui.QIcon("./src/switch-off.png")

        self.on = False

        response = requests.get(self.wled_url+"/json/state")

        if response.status_code == 200:
            data = response.json()
            current_preset = data["ps"]
        else:
            if debug:
                print("Unable to retrieve JSON data, response code:", response.status_code)
                sys.exit()

        if debug:
            print(f'WLED URL: {self.wled_url}')
            print("Current Preset:", current_preset)
            print(f'Presets: On {self.on_preset}, Off {self.off_preset}')

        self.power_on_action.setChecked(self.on_power)

        if self.on_power:
            if current_preset == int(self.off_preset):
                self.toggel_power_action.setIcon(self.switch_on_icon)
                requests.post(f'{self.wled_url}/json/state', json={"ps":self.on_preset})
                if debug:
                    print("Send a POST request with JSON {'ps': self.on_preset} to self.wled_url/json/state")
            elif current_preset == int(self.on_preset):
                self.toggel_power_action.setIcon(self.switch_on_icon)
            else:
                self.toggel_power_action.setIcon(self.switch_on_icon)
                requests.post(f'{self.wled_url}/json/state', json={"ps":self.on_preset})
                if debug:
                    print("Send a POST request with JSON {'ps': self.on_preset} to self.wled_url/json/state")

    def power_on(self):
        self.config.read('conf.ini')
        self.on_power = not self.on_power
        self.config.set('settigs', 'onPowerWLED', str(self.on_power))

        with open('conf.ini', 'w') as configfile:
            self.config.write(configfile)
        self.power_on_action.setChecked(self.on_power)

        if self.on_power:
            self.toggel_power_action.setIcon(self.switch_on_icon)
            requests.post(f'{self.wled_url}/json/state', json={"ps":self.on_preset})
            if debug:
                print("configured to power on after log in")
        else:
            if debug:
                print("configured to not power on after log in")
    
    def toggel_power(self):
        url = f'{self.wled_url}/json/state'
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            current_preset = data["ps"]
            if debug:
                print(f'Toggel current preset: {data["ps"]}')
        else:
            if debug:
                print("Unable to retrieve JSON data, response code:", response.status_code)

        if current_preset == int(self.off_preset):
            self.on = False
        elif current_preset == int(self.on_preset):
            self.on = True
        else:
            self.on = False

        if debug:
            print(f"ON (TRUE) Turnoff\nSet preset: {self.off_preset}") if self.on else print(f"ON (FALSE) turn on\nSet preset: {self.on_preset}")

        if self.on:
            self.toggel_power_action.setIcon(self.switch_off_icon)
            requests.post(f'{self.wled_url}/json/state', json={"ps":self.off_preset})
            self.on = False
        else:
            self.toggel_power_action.setIcon(self.switch_on_icon)
            requests.post(f'{self.wled_url}/json/state', json={"ps":self.on_preset})
            self.on = True

    def quit(self):
        sys.exit()
        
if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    icon = QtGui.QIcon("./src/favicon.ico")
    tray_icon = SystemTrayIcon(icon)
    tray_icon.show()
    sys.exit(app.exec_())