"""Puts flights data in the database."""
from datetime import time, date, timedelta
from random import randint, choice, sample
from string import ascii_uppercase, digits

from django.core.management.base import BaseCommand
from website.models import Plane, Flight, Captain, Ticket

PLANES_COUNT = 50
FLIGHTS_COUNT = 50
CAPTAINS_COUNT = 100
MIN_SEATS = 20
MAX_SEATS = 400
MIN_PRICE = 70
MAX_PRICE = 1500
DAYS = 50
START_DATE = date(day=20, month=4, year=2018)

FIRST_NAMES = [
    'Emil',
    'Ling',
    'Bud',
    'Dortha',
    'Jenny',
    'Melinda',
    'Rufina',
    'Emerson',
    'Marx',
    'Treena',
    'Dorene',
    'Heidy',
    'Audrie',
    'Hellen',
    'Alethea',
    'Alaine',
    'Everette',
    'Vivian',
    'Fe',
    'Janet',
    'Yen',
    'Kris',
    'Edna',
    'Mickey',
    'Carley',
    'Palmira',
    'Lorraine',
    'Cammy',
    'Anitra',
    'Toney',
    'Kasie',
    'Marline',
    'Lindsy',
    'Margarita',
    'Nguyet',
    'Nigel',
    'Craig',
    'Geri',
    'Carman',
    'Latesha',
    'Claribel',
    'Devon',
    'Chet',
    'Jeanene',
    'Dimple',
    'Carolina',
    'Miki',
    'Babette',
    'Raleigh',
    'Kaitlin'
]

LAST_NAMES = [
    'Hughes',
    'Scott',
    'Frazier',
    'Conway',
    'Salas',
    'Lopez',
    'Shepherd',
    'Payne',
    'Vaughn',
    'Foster',
    'Gomez',
    'Salinas',
    'Barr',
    'Gutierrez',
    'Gilbert',
    'Skinner',
    'Phillips',
    'Simpson',
    'Herman',
    'Mosley',
    'Santiago',
    'Kent',
    'Garrett',
    'Townsend',
    'Dawson',
    'Reeves',
    'Phelps',
    'Cortez',
    'Howe',
    'Fischer',
    'Stafford',
    'Poole',
    'Ray',
    'French',
    'Armstrong',
    'Vega',
    'Buck',
    'Pugh',
    'Bowen',
    'Haas',
    'Barry',
    'Riddle',
    'Kelley',
    'Lynn',
    'Houston',
    'Kaiser',
    'Greene',
    'Pratt',
    'Underwood',
    'Faulkner'
]

AIRPORTS = [
    'Kraków',
    'Warsaw',
    'London',
    'Philadelphia',
    'Washington',
    'New York',
    'Amsterdam',
    'Paris',
    'Seattle',
    'Honolulu',
    'Pearl City',
    'Hilo',
    'Kailua',
    'Barcelona',
    'Waipahu',
    'Kaneohe',
    'Mililani Town',
    'Kahului',
    'Mililani Mauka',
    'Kihei',
    'Makakilo',
    'Wahiawa',
    'Wailuku',
    'Kapolei',
    'Halawa',
    'Waimalu',
    'Waianae',
    'Nanakuli',
    'Kailua',
    'Lahaina',
    'Waipio',
    'Kapaa',
    'Kalaoa',
    'Maili',
    'Aiea',
    'Holualoa',
    'Ocean Pointe',
    'Makuha',
    'Haiku-Pauwela',
    'Pukalani',
    'Seoul',
    'Tokyo'
]


class Command(BaseCommand):
    """Runs after terminal command: python manage.py populate."""
    def handle(self, *args, **kwargs):  # pylint: disable=unused-argument
        clear_data()
        generate_data()


def clear_data():
    """Removes current data from the database."""
    Plane.objects.all().delete()   # pylint: disable=no-member
    Flight.objects.all().delete()   # pylint: disable=no-member
    Ticket.objects.all().delete()   # pylint: disable=no-member
    Captain.objects.all().delete()   # pylint: disable=no-member


def generate_planes():
    """Generates planes with ids like AB123"""
    planes = []
    plane_ids = set()

    while len(plane_ids) < PLANES_COUNT:
        plane_id = ''
        # pylint: disable=unused-variable
        for i in range(0, 2):  # first generates two uppercase letters
            plane_id += choice(ascii_uppercase)
        # pylint: disable=unused-variable
        for i in range(0, 3):  # then generates three digits
            plane_id += choice(digits)

        # generates multiples of 10 in range from 20 to 400
        seats = randint(MIN_SEATS/10, MAX_SEATS/10) * 10

        if plane_id not in plane_ids:
            # pylint: disable=no-member
            planes.append(Plane.objects.create(id=plane_id, seats=seats))
            plane_ids.add(plane_id)

    return planes


def random_hours(count):
    """Returns sorted list of >count< unique hours"""
    numbers = set()
    while len(numbers) != count:
        numbers.add(randint(0, 23))

    numbers = list(numbers)
    numbers.sort()
    hours = []
    for i in range(0, count):
        hours.append(time(hour=numbers[i]))

    return hours


def generate_flights(planes):
    """Generates random flights for planes passed as argument"""
    current_date = START_DATE
    for i in range(0, DAYS):
        captains = Captain.objects.all()
        captains_seq = sample(range(0, Captain.objects.count()), PLANES_COUNT)
        pos_in_seq = 0
        for plane in planes:
            hours = random_hours(4)
            pos = sample(range(0, len(AIRPORTS)), 3)
            airport1 = AIRPORTS[pos[0]]     # pylint: disable=invalid-sequence-index
            airport2 = AIRPORTS[pos[1]]     # pylint: disable=invalid-sequence-index
            airport3 = AIRPORTS[pos[2]]     # pylint: disable=invalid-sequence-index
            captain = captains[captains_seq[pos_in_seq]]

            Flight.objects.create(
                airport_from=airport1,
                airport_to=airport2,
                day_from=current_date,
                time_from=hours[0],
                day_to=current_date,
                time_to=hours[1],
                price=randint(MIN_PRICE, MAX_PRICE),
                plane=plane,
                captain=captain
            )
            Flight.objects.create(
                airport_from=airport2,
                airport_to=airport3,
                day_from=current_date,
                time_from=hours[2],
                day_to=current_date,
                time_to=hours[3],
                price=randint(MIN_PRICE, MAX_PRICE),
                plane=plane,
                captain=captain
            )

            pos_in_seq += 1
        current_date += timedelta(days=1)


def generate_captains():
    """Generates captains of flight crews"""
    names_set = set()
    while len(names_set) != CAPTAINS_COUNT:
        first_name = FIRST_NAMES[randint(0, len(FIRST_NAMES) - 1)]
        last_name = LAST_NAMES[randint(0, len(LAST_NAMES) - 1)]

        names_set.add((first_name, last_name))

    for i in range(0, CAPTAINS_COUNT):
        name = names_set.pop()
        Captain.objects.create(first_name=name[0], last_name=name[1])


def generate_data():
    """Generates sample data and fills the database."""
    planes = generate_planes()
    generate_captains()
    generate_flights(planes)
