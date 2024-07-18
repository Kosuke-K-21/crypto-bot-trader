import yaml
from pathlib import Path

here = Path(__file__).parent
BASE_SETTINGS_FILE = here / "settings.yaml"

with open(BASE_SETTINGS_FILE, "r") as f:
    base_settings = yaml.safe_load(f)

print(base_settings)
