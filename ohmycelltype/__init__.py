import json
import os

CONFIG = f"{os.environ.get('HOME')}/ohmycelltype.json"

def get_llm_config_value(provider ,config = CONFIG):
    data = load_json(config)
    return data[provider]


def write_json(dict, out):
    json_str = json.dumps(dict, indent=4,ensure_ascii=False)
    with open(out,"w",encoding='utf-8') as fd:
        fd.write(json_str)

def load_json(file):
    with open(file,encoding='utf-8') as fd:
        return json.load(fd)