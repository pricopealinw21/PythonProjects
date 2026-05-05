from _future_ import annotations

from dataclasses import dataclass
from itertools import combinations

EPS = 1e-9


@dataclass(frozen=True)
class Punct:
    x: float
    y: float


def determinant(a: Punct, b: Punct, c: Punct) -> float:
    return a.x * (b.y - c.y) + b.x * (c.y - a.y) + c.x * (a.y - b.y)


def sunt_coliniare(a: Punct, b: Punct, c: Punct, eps: float = EPS) -> bool:
    return abs(determinant(a, b, c)) <= eps


def genereaza_triplete(puncte: list[Punct]):
    for indici in combinations(range(len(puncte)), 3):
        yield indici


def gaseste_triplete_coliniare(puncte: list[Punct]) -> list[tuple[tuple[int, int, int], tuple[Punct, Punct, Punct]]]:
    rezultate: list[tuple[tuple[int, int, int], tuple[Punct, Punct, Punct]]] = []

    for i, j, k in genereaza_triplete(puncte):
        triplet = (puncte[i], puncte[j], puncte[k])
        if sunt_coliniare(*triplet):
            rezultate.append(((i, j, k), triplet))

    return rezultate


def exemplu_coliniaritate() -> None:
    puncte = [
        Punct(0, 0),
        Punct(1, 1),
        Punct(2, 2),
        Punct(0, 3),
        Punct(3, 0),
        Punct(4, 4),
    ]

    rezultate = gaseste_triplete_coliniare(puncte)

    print("Puncte:")
    for index, punct in enumerate(puncte):
        print(f"P{index} = ({punct.x}, {punct.y})")

    print("\nTriplete coliniare gasite:")
    if not rezultate:
        print("Nu exista trei puncte coliniare.")
        return

    for (i, j, k), (a, b, c) in rezultate:
        print(
            f"Indici: ({i}, {j}, {k}) -> "
            f"({a.x}, {a.y}), ({b.x}, {b.y}), ({c.x}, {c.y})"
        )


if _name_ == "_main_":
    exemplu_coliniaritate()