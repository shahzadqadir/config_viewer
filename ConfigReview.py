#!/usr/bin/python3
from PyQt5.uic import loadUiType
from PyQt5.QtWidgets import QMainWindow, QApplication, QMessageBox
from sys import argv
from PyQt5.Qt import QTableWidgetItem, QWidget
import cisco

ui,_ = loadUiType('ConfigReview.ui')

class MainWindow(QMainWindow, ui):
    def __init__(self):
        self.hostname = ""
        self.protocol = ""
        self.username = ""
        self.password = ""
        self.device_type = ""
        self.display_set = False     
        
        QMainWindow.__init__(self)
        self.setupUi(self)
        self.populate_protocol_combo()
        self.populate_device_type_combo()
        self.button_handler()
        self.populate_commands_combo()
    
    def button_handler(self):
        self.btn_connect.clicked.connect(self.pull_device_info)
        self.btn_execute_command.clicked.connect(self.execute_command)
        self.combo_commands.activated.connect(self.update_edit_command)
        self.btn_display_set.clicked.connect(self.show_display_set)
        self.btn_exit.clicked.connect(self.close_application)
        
    def close_application(self):
        self.close()
    
    
    def populate_protocol_combo(self):
        protocols = ["Telent", "SSH"]
        for protocol in protocols:
            self.combo_protocol.addItem(protocol)
        
        # temparary until Telnet is not implemented
        # when telnet is implemetned, just remove below lines
        
        self.combo_protocol.setCurrentIndex(1)
        self.combo_protocol.setEnabled(False)
    
    def populate_device_type_combo(self):
        devices = ["Cisco IOS", "Junos"]
        for device in devices:
            self.combo_device_type.addItem(device)
    
    def show_display_set(self):
        self.display_set = True
        self.execute_command()
        
    
    def pull_device_info(self):
        
        #print(self.btn_connect.text())
        
#         if self.btn_connect.text() == "Disconnect":
#             self.edit_username.setEnabled(True)
#             self.edit_password.setEnabled(True)
#             self.label.setText("")
#             self.btn_connect.setText("Connect")
        
        self.hostname = self.edit_ip_add.text()
        self.protocol = self.combo_protocol.currentText()
        self.username = self.edit_username.text()
        self.password = self.edit_password.text()
        self.device_type = self.combo_device_type.currentText()
        device_type = self.combo_device_type.currentText()
        
            
        if cisco.connection_test(self.hostname, self.username, self.password) == True:
            
             # disable username/password fields
            self.edit_username.setEnabled(False)
            self.edit_password.setEnabled(False)
            # connected message instead of error
            self.label.setText("Connected")
            self.btn_connect.setEnabled(False)
            #self.btn_connect.setText("Disconnect")
            self.combo_device_type.setEnabled(False)
            
            if device_type == "Cisco IOS":           
        
                device_hostname = cisco.show_cmd_ssh(self.hostname, self.username, self.password, "show run | in hostname")                       
                device_hostname = device_hostname[0].split(' ')[1]
                self.lbl_hostname.setText(device_hostname)
               
                
                ios_version = cisco.show_cmd_ssh(self.hostname, self.username, self.password, "show version | in Version")
                ios_version = ios_version[0]
                self.lbl_ios_version.setText(ios_version)
    
                
                cpu_status = cisco.show_cmd_ssh(self.hostname, self.username, self.password, "show proc cpu | in CPU")
                cpu_status = cpu_status[0].strip('\n')       
                self.lbl_cpu_utilization.setText(cpu_status)
    
                
                uptime = cisco.show_cmd_ssh(self.hostname, self.username, self.password, "show version | in time")
                uptime = uptime[0].strip('\n')
                self.lbl_uptime.setText(uptime)
                
            elif device_type == "Junos":
                device_hostname = cisco.show_cmd_ssh(self.hostname, self.username, self.password, "show version | match Hostname")                       
                device_hostname = device_hostname[0].split(' ')[1]
                self.lbl_hostname.setText(device_hostname)
                
                ios_version = "before"
                ios_version = cisco.show_cmd_ssh(self.hostname, self.username, self.password, 'show version | match "Base OS Boot"')
                ios_version = ios_version[0]
                #print(ios_version)
                self.lbl_ios_version.setText(ios_version)
                
                uptime = cisco.show_cmd_ssh(self.hostname, self.username, self.password, "show system uptime")
                for output in uptime:
                    if "up" in output:
                        self.lbl_uptime.setText(output)

        else:
            self.label.setText("Couldn't connect, Check username/password, connectivity to host")
    
    def populate_commands_combo(self):
        commands = [
            "show running-config",
            "show configuration section",
            "show interfaces status",
            "show routing table",
            "show neighbors",
            "show arp",
            "custom command",            
            ]
        for command in commands:
            self.combo_commands.addItem(command)
    
    def update_edit_command(self):
        
        if self.combo_commands.currentText() == "show configuration section":
            self.edit_custom_command.setPlaceholderText("What section of configuration you want to view?")
            self.edit_custom_command.setEnabled(True)
        elif self.combo_commands.currentText() == "show routing table":
            self.edit_custom_command.setPlaceholderText("Enter prefix for details or leave empty")
            self.edit_custom_command.setEnabled(True)
        elif self.combo_commands.currentText() == "show neighbors":
            self.edit_custom_command.setPlaceholderText("Enter interface-id or detail keyword to see details or leave empty")
            self.edit_custom_command.setEnabled(True)
        elif self.combo_commands.currentText() == "show arp":
            self.edit_custom_command.setPlaceholderText("Enter IP or leave empty")
            self.edit_custom_command.setEnabled(True)
        elif self.combo_commands.currentText() == "custom command":
            self.edit_custom_command.setPlaceholderText("Enter custom command")
            self.edit_custom_command.setEnabled(True)
        else:
            self.edit_custom_command.setText("")
            self.edit_custom_command.setEnabled(False)
                                    
            
      
    
    def cisco_show_run(self):
        
        if self.device_type == "Cisco IOS":
            command = "show run"
        elif self.device_type == "Junos":
            if self.display_set == True:
                command = "show configuration | display set"
                self.display_set = False
            else:
                command = "show configuration"
            
        run_config = cisco.show_cmd_ssh(self.hostname, self.username, self.password, command)
        
        self.ptedit_cmd_output.clear()       
        for config in run_config:
            self.ptedit_cmd_output.appendPlainText(config.replace("\r","").strip('\n'))
    
    def cisco_show_run_section(self):
        
        section = self.edit_custom_command.text()
        
        if self.combo_device_type.currentText() == "Cisco IOS":
            if section:                          
                command = "Show run | section " + section
            else:
                command = "show run"
        elif self.combo_device_type.currentText() == "Junos":
            if self.display_set == True:
                command = "show configuration " + section + " | display set"
                self.display_set = False
            else:
                command = "show configuration " + section
        
        run_config = cisco.show_cmd_ssh(self.hostname, self.username, self.password, command)
        
        self.ptedit_cmd_output.clear()
        
        if run_config:         
            for config in run_config:            
                self.ptedit_cmd_output.appendPlainText(config.replace("\r","").strip('\n'))
        else:
            self.ptedit_cmd_output.appendPlainText("No configurations found for this section")
    
    def cisco_interfaces_status(self):
        
        if self.device_type == "Cisco IOS":                 
            run_config = cisco.show_cmd_ssh(self.hostname, self.username, self.password, "show ip int brief")
        elif self.device_type == "Junos":
            run_config = cisco.show_cmd_ssh(self.hostname, self.username, self.password, "show interface terse")
        
        self.ptedit_cmd_output.clear()
        
        if run_config:         
            for config in run_config:            
                self.ptedit_cmd_output.appendPlainText(config.replace("\r","").strip('\n'))
    
    def cisco_show_routing_table(self):
        
        if self.device_type == "Cisco IOS":
            command = "show ip route "
        elif self.device_type == "Junos":
            command = "show route "
        
        if self.edit_custom_command.text():
            command = command + self.edit_custom_command.text()        
        
        run_config = cisco.show_cmd_ssh(self.hostname, self.username, self.password, command)
        
        self.ptedit_cmd_output.clear()
        
        if run_config:         
            for config in run_config:            
                self.ptedit_cmd_output.appendPlainText(config.replace("\r","").strip('\n'))
    
    def cisco_show_cdp_neighbor(self):
        
        if self.device_type == "Cisco IOS":
            command = "show cdp neighbor "
        elif self.device_type == "Junos":
            command = "show lldp neighbor "
        
        if self.edit_custom_command.text():
            command = command + self.edit_custom_command.text()
        
        run_config = cisco.show_cmd_ssh(self.hostname, self.username, self.password, command)
        
        self.ptedit_cmd_output.clear()
        
        if run_config:         
            for config in run_config:            
                self.ptedit_cmd_output.appendPlainText(config.replace("\r","").strip('\n'))
        else:
                self.ptedit_cmd_output.appendPlainText("NO neighbors found")
    
    def cisco_show_arp(self):
        
        if self.device_type == "Cisco IOS":
            command = "show ip arp "
            if self.edit_custom_command.text():
                command = command + self.edit_custom_command.text()  
        elif self.device_type == "Junos":
            command = "show arp "
            if self.edit_custom_command.text():
                command = command + "hostname " + self.edit_custom_command.text()  
        
             
        
        run_config = cisco.show_cmd_ssh(self.hostname, self.username, self.password, command)
        
        self.ptedit_cmd_output.clear()
        
        if run_config:         
            for config in run_config:            
                self.ptedit_cmd_output.appendPlainText(config.replace("\r","").strip('\n'))
        else:
                self.ptedit_cmd_output.appendPlainText("No arp entry found for this host.")
                
    def cisco_custom_command(self):
               
        if self.edit_custom_command.text():
            command = self.edit_custom_command.text()
        else:
            self.edit_custom_command.setPlaceholderText("Please enter a command")
            return
        
        run_config = cisco.show_cmd_ssh(self.hostname, self.username, self.password, command)
        
        self.ptedit_cmd_output.clear()
        
        if run_config:         
            for config in run_config:            
                self.ptedit_cmd_output.appendPlainText(config.replace("\r","").strip('\n'))
        else:
                self.ptedit_cmd_output.appendPlainText("Invalid command")         
       
    
    def execute_command(self):
        
        if self.label.text() == "Connected":
            selection = self.combo_commands.currentText()
            device_type = self.combo_device_type.currentText()
            
            if selection == "show running-config":
                self.cisco_show_run()
            elif selection == "show configuration section":
                 self.cisco_show_run_section()
            elif selection == "show interfaces status":
                self.cisco_interfaces_status()
            elif selection == "show routing table":
                self.cisco_show_routing_table()
            elif selection == "show neighbors":
                self.cisco_show_cdp_neighbor()
            elif selection == "show arp":
                self.cisco_show_arp()
            else:
                self.cisco_custom_command()    
                
       
    



def main():
    
    app = QApplication(argv)
    
    myapp = MainWindow()
    myapp.show()
    
    app.exec_()
    
if __name__ == "__main__":
    main()


