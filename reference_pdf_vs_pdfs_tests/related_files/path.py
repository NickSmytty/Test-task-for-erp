import os
import yaml


def find_project_root(filename='path_config.yaml'):
    current_dir = os.path.abspath(os.path.dirname(__file__))
    while current_dir != os.path.abspath(os.sep):
        if filename in os.listdir(current_dir):
            return current_dir
        current_dir = os.path.abspath(os.path.join(current_dir, os.pardir))
    raise FileNotFoundError(f"Could not find {filename} in any parent directory.")


def load_config():
    project_root = find_project_root()
    config_path = os.path.join(project_root, 'path_config.yaml')
    with open(config_path, 'r') as file:
        return yaml.safe_load(file)


def get_path(key: str) -> str:
    config = load_config()
    relative_path = config['paths'].get(key)
    if not relative_path:
        raise KeyError(f"Path for key '{key}' not found in config.")
    project_root = find_project_root()
    return os.path.join(project_root, relative_path)