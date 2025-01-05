from dataclasses import asdict, fields, is_dataclass
import json

from python_client.src.project_types import PlayerNumber, PieceKind, Location

parseable = [
    (PlayerNumber.ONE, PieceKind("eevee"), Location(1, 2)),
    (PlayerNumber.TWO, PieceKind("turtwig"), Location(3, 4))
    ]

def to_string(data: list[tuple[PlayerNumber, PieceKind, Location]]) -> str:
    returnable: list[str] = []

    for item in data:
        returnable.append(f"{ item[0].value }-{ item[1].value }-{ item[2].row },{ item[2].col }")

    return " ".join(returnable)

def to_message(s: str) -> list[tuple[PlayerNumber, PieceKind, Location]]:
    intparser = lambda x : [int(i) for i in x]

    _tuples: list[str] = s.split(" ")

    _all: list[list[str]] = [item.split("-") for item in _tuples]

    _returnable = [
        (PlayerNumber(pnum), PieceKind(pkind), Location(*intparser(loc.split(","))))
        for pnum, pkind, loc in _all
        ]

    return _returnable

message = to_string(parseable)
result = to_message(message)

print(message)
print(result)
print(parseable == result)