import inspect
import sys
from pathlib import Path

from ..interfaces import ProcessQuickQueryProtocol

process_quick_query: ProcessQuickQueryProtocol | None = None
try:
    print("Trying to import QuickOSM")
    from qgis.utils import plugins  # type: ignore

    quick_osm_dir = Path(inspect.getfile(plugins["QuickOSM"].__class__)).parent / "core"  # type: ignore
    if quick_osm_dir and quick_osm_dir.exists():
        sys.path.append(str(quick_osm_dir))

    from process import process_quick_query  # type: ignore

    assert isinstance(process_quick_query, ProcessQuickQueryProtocol)
except Exception as e:
    pass


def generate_layers(prompt: str, create_new_map: bool) -> None: ...
