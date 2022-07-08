# Wizard Detention

### Description
A 2D puzzle platformer where you play as a stubborn wizarding school student and their familiar.
They have been banished to the Detention Dimension for bad behavior.
The wizard and their familiar must work together to navigate the various puzzles within the Detention Dimension and find
a way to escape or be locked in detention forever!

### Installation
In the command prompt, navigate inside the nsis folder where WizardDetention_0.0.1.exe is located and run the installer
with the command:
```
start WizardDetention_0.0.1
```

Once the package is done installing, navigate to the folder you downloaded the game into where WizardDetention.launch.pyw 
is located and run the game with the command:
```
WizardDetention.launch.pyw
```
Or use the full file path to execute the command:
```
[FILE PATH]\WizardDetention.launch.pyw
```
If there are any issues running WizardDetention_0.0.1.exe or WizardDetention.launch from the command prompt,
both can be run by double-clicking them in the file explorer.
### Links
[Github] (https://github.com/juliamckay/WizDetention)

### WizardDetention.tar.gz Contents
File Structure:
```
WizardDetention/
├── src/
│   ├── Assets/
│   └── Wiz_Detention/
│       ├── __init__.py
│       ├── command.py
│       ├── constants.py
│       ├── env_interaction.py
│       ├── game.py
│       ├── menu_screen.py
│       ├── open_window.py
│       └── quit_screen.py
├── installer.cfg
├── README.md
└── WizardDetention_0.0.1.exe
```
Source code is located within the src folder. 
The PIP package build script is installer.cfg
WizardDetention_0.0.1.exe is the executable for the installer.
### For the Devs
Build the package:
```
python -m nsist installer.cfg
```