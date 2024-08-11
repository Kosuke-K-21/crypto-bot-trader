import os
import yaml
from pathlib import Path

here = Path(__file__).parent.parent  # main directory
SETTINGS_FILE = os.path.join(here, "settings.yaml")

with open(SETTINGS_FILE, "r") as f:
    base_settings = yaml.safe_load(f)

print(base_settings)
