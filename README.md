Wizard Detention's README

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
├── src/
│   ├── Maps/
│   └── Wizard-Detention/
│       ├── __init__.py
│       ├── constants.py
│       ├── game.py
│       ├── menu_screen.py
│       └── open_window.py
└── tests/
```

Install the latest version of PyPA's build:
```
py -m pip install --upgrade build
```

Build the dist directory:
```
py -m build
```

Install twine to upload distribution packages:
```
py -m pip install --upgrade twine
```

Upload all archives under dist:
```
py -m twine upload --repository-url https://upload.pypi.org/legacy/ dist/*
```

Install pip package:
```
py -m pip install --index-url https://test.pypi.org/simple/ --no-deps WizardDetention==0.0.1
```