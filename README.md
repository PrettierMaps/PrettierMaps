# JH02 Main - Prettier Maps 0.2.0

## Developing the plugin locally

### Running the plugin in QGIS

1. Install the plugin dependencies to your QGIS Python environment:

```bash
uv sync --all-groups
```

2. Create the QGIS zip file:

```bash
make zip_plugin
```

3. Install the plugin in QGIS (from ZIP)

### Running the plugin in your IDE

1. Install the plugin dependencies to your Python environment:

```bash
uv sync --all-groups
```

2. Run the `main.py` file.

```bash
python main.py
```