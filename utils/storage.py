import json, os

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")

def _load(name):
    path = os.path.join(DATA_DIR, f"{name}.json")
    if not os.path.exists(path):
        return {}
    with open(path, "r", encoding="utf-8") as f:
        try:
            return json.load(f)
        except Exception:
            return {}

def _save(name, data):
    path = os.path.join(DATA_DIR, f"{name}.json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def get(name): return _load(name)
def set(name, data): _save(name, data)
