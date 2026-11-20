
GENERATIONS = {
    ("Opel", "Astra"): [
        (1991, 1997, "F"),
        (1998, 2003, "G"),
        (2004, 2009, "H"),
        (2009, 2015, "J"),
        (2015, 2021, "K"),
        (2021, 2030, "L"),
    ],
    ("LADA", "Vesta"): [
        (2015, 2021, "I"),
        (2022, 2030, "NG"),
    ],
    ("Toyota", "Camry"): [
        (2001, 2006, "XV30"),
        (2006, 2011, "XV40"),
        (2011, 2017, "XV50"),
        (2017, 2023, "XV70"),
        (2024, 2030, "XV80"),
    ],
}


def get_generation(brand, model, year):
    if not year:
        return None

    generations = GENERATIONS.get((brand, model), [])

    for start, end, name in generations:
        if start <= year <= end:
            return name

    return None
