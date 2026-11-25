"""Build the operational ordering variant."""
import runpy
from pathlib import Path
runpy.run_path(str(Path(__file__).with_name("build_operational_ordering.py")),run_name="__main__")

runpy.run_path(str(Path(__file__).with_name("organize_ordering.py")),run_name="__main__")
