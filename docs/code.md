# The Codebase

The codebase is structured as follows:

```
prettier_maps/
├── __init__.py
├── interfaces.py
├── metadata.txt
├── plugin.py
├── ui/
├── core/
├── config/
├── assets/
tests/
```

## Explaining the File Structure

### `interfaces.py`

This file contains some interfaces that are used to interact with the QGIS API. This creates dependency inversion between the plugin and the python QGIS API.

### `metadata.txt`

This file contains the metadata for the QGIS plugin.

### `plugin.py`

This file is the main entrypoint for QGIS.

### `ui/`

This directory contains the PYQT5 UI files for the QGIS plugin.

### `core/`

This directory contains the core logic for the QGIS plugin. This involves the layer manipulation logic

### `config/`

This directory contains the configuration for the QGIS plugin.

### `assets/`

This directory contains the assets for the QGIS plugin.


## Overview

With this file structure, we are practising good separation of concerns.