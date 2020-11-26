"""

"""
import json
import os
import subprocess
from time import sleep

from pip._vendor import requests


# First run:
#   cd sempre
#   ./interactive/run @mode=voxelurn -server -interactive


def ask(params):
    root = "http://localhost:8410/sempre"
    url = f"{root}?q={params}"
    r = requests.get(url, auth=('user', 'pass'))
    if r.status_code != 200:
        raise Exception(f"Bad status code: {r.status_code}")
    return r.json()

# cd sempre
# ./interactive/run @mode=voxelurn -server -interactive
os.chdir("../sempre")
proc = subprocess.Popen(
    ["./run", "@mode=simple"],
    stdin=subprocess.PIPE, stdout=subprocess.PIPE
)


sleep(2)
out, err = proc.communicate(b"3 + 4\n", timeout=2)
out = bytes.decode(out, 'utf-8')
for i in out.split('\n'):
    print(i)


def run_voxelurn_server():
    pass

def showcase_basic_queries():
    with open("../sempre/interactive/queries/sidaw.json") as f:
        lines = f.readlines()
    queries = [json.loads(l.strip()) for l in lines]
    for q in queries:
        params = q['q']
        result = ask(params)
        print(">", params)
        print("<", result)
        sleep(2)