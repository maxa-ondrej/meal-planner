import json


type Json = dict[str, str | Json | list[Json]]


def parse_json(s: str) -> Json:
    return json.loads(s)


def to_json(d: Json) -> str:
    return json.dumps(d, indent=2)
