# Wizard Detention

### Description
A 2D puzzle platformer where you play as a stubborn wizarding school student and their familiar.
They have been banished to the Detention Dimension for bad behavior.
The wizard and their familiar must work together to navigate the various puzzles within the Detention Dimension and find
a way to escape or be locked in detention forever!

### Commands
Build the scripts:
```
py -m build
```

Install package:
```
py -m pip install Wiz_Detention
```

Run executable:
```
py -m pip install Wiz_Detention
```

### Links
[Github] (https://github.com/juliamckay/WizDetention)

[Installation package executable] (https://pypi.org/project/Wiz-Detention/)

### Other
Updating pip on Windows:
```
py -m pip install --upgrade pip
```

File structure:
```
WizDetention/
├── LICENSE
├── pyproject.toml
├── README.md
├── setup.cfg
├── src/
│   ├── Assets/
│   └── Wiz_Detention/
│       ├── __init__.py
│       ├── command.py
│       ├── constants.py
│       ├── game.py
│       ├── menu_screen.py
│       └── open_window.py
└── tests/
```

Install the latest version of PyPi's build:
```
py -m pip install --upgrade build
```

Install twine to upload distribution packages:
```
py -m pip install --upgrade twine
```

Upload all archives under dist:
```
py -m twine upload dist/*
```