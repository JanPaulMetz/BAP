## esp_project

# VCP driver: 
The ESP32-WROOM devboard needs a Virtual COM Port (VCP) driver installed on the PC in order to communicate: https://www.silabs.com/developers/usb-to-uart-bridge-vcp-drivers?tab=downloads
Download and unzip the zipped folder. Open te folder and right click "silabser.inf" and click "install". You can check in "Windows Device Manager"->"Ports" wheter the ESP32 is recognized as COM : Silicon Labs CP210x USB to UART Bridge

# ESP-IDF: 
This project makes use of the ESP-IDF extension in vscode. For setting up vscode ESP-IDF extension follow these steps:
1. Install ESP-IDF through vscode according to: https://github.com/espressif/vscode-esp-idf-extension/blob/master/docs/tutorial/install.md
2. Navigate to the command palette and enter 'Add vscode configuration folder'. This creates a .vscode folder in the root folder. It should contain 4 json files: c_pp_properties, launch, settings and tasks. Check wheter the esp-idf configurations are included, such as compiler path in the c_pp_properties.json file. 
3. Select comport, build and flash in the icon bar. When comport is not found, you should check first if the driver is installed properly by checking the Device Manager. 
