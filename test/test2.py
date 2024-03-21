import json
from os import environ
from subprocess import run


env = {}
env["config"] = str(json.dumps({"1": "''"}, ensure_ascii=False))
run(["python3", "script.py"], env=env)
