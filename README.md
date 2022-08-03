# Wizard Detention

### Description
A 2D puzzle platformer where you play as a stubborn wizarding school student and their familiar.
They have been banished to the Detention Dimension for bad behavior.
The wizard and their familiar must work together to navigate the various puzzles within the Detention Dimension and find
a way to escape or be locked in detention forever!

### Build Process
To begin the building process, navigate within the terminal to the unzipped WizardDetention folder. 

Install Pynsist with this command:
```
pip install pynsist
```
Utilizing the installer.cfg, build the installer with this command:
```
python -m nsist installer.cfg
```

### Installation with double-click executable installer
Launch the installer, WizardDetention_1.0.0.exe, by double-clicking the executable. Follow the instructions for instillation. 

Once the game is finished installing, it can be launched by double-clicking the file WizardDetention.launch.pyw.

### Installation with command lines
In the command prompt, navigate inside the nsis folder where WizardDetention_1.0.0.exe is located and run the installer
with the command:
```
start WizardDetention_1.0.0
```
Once the package is done installing, navigate to the folder you downloaded the game into where WizardDetention.launch.pyw 
is located and run the game with the command:
```
WizardDetention.launch.pyw
```

### WizardDetention.tar.gz Contents
File Structure:
```
WizardDetention/
├── src/
│   ├── Assets/
│   └── Wiz_Detention/
│       ├── __init__.py
│       ├── constants.py
│       ├── env_interaction.py
│       ├── game.py
│       ├── menu_screen.py
│       ├── open_window.py
│       └── quit_screen.py
├── installer.cfg
├── LICENSE
├── README.md
└── WizardDetention_1.0.0.exe
```
Source code and game assets are located within the src folder. 
The PIP package build script is installer.cfg
WizardDetention.exe is the executable for the installer.

### Links
[Github] (https://github.com/juliamckay/WizDetention)

[Gzipped Tar Archive] (https://github.com/juliamckay/WizDetention/tree/master/dist)