SETUP INSTRUCTIONS:
+   Install latest version of python on your server if not installed already using command "apt install python3".
+   Install pip3 using command "apt install python3-pip".
+   Now change the directory to the folder where all the bot files are.
+   Install the required modules using "pip3 install -r requirements.txt".
+   Install chromium browser using "apt install chromium-browser".
+   Install chromedriver using "apt install chromium-chromedriver".
+   Type command "whereis chromedriver" and it show the location of chromedriver on the system.
+   Rename the sample-config.json file to config.json file.
+   Open the config.json file and enter the chromedriver location.
+   Create a new discord bot add to server and enter the bot token in config.json file.
+   Enter the channel id in config.json file.
+   Run the bot using command "python3 main.py".
+   The bot should now be online.