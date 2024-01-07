import yaml

with open("config.yml", "r") as file:
    config = yaml.safe_load(file)

def get(path:str):
    keys = path.split(".")
    target = config
    for key in keys:
        target = target[key]
    return target



