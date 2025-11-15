from random import randint


def randint_exclude(min: int, max: int, exclude: int) -> int:
    rand = exclude
    while rand == exclude:
        rand = randint(min, max)

    return rand
