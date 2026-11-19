import sqlite3
import random
import math
from datetime import datetime, timedelta

random.seed(42)
DB_NAME = "airlines.db"

# ---------- Static reference data ----------
airlines = [
    (1, "IndiGo", "6E"), (2, "Air India", "AI"), (3, "SpiceJet", "SG"),
    (4, "Vistara", "UK"), (5, "Akasa Air", "QP"), (6, "AirAsia India", "I5"),
]

airports = [  # id, iata, name, city, lat, lon
    (1, "DEL", "Indira Gandhi Intl", "Delhi", 28.56, 77.10),
    (2, "BOM", "Chhatrapati Shivaji Intl", "Mumbai", 19.09, 72.87),
    (3, "BLR", "Kempegowda Intl", "Bengaluru", 13.20, 77.71),
    (4, "MAA", "Chennai Intl", "Chennai", 12.99, 80.17),
    (5, "CCU", "Netaji Subhas Chandra Bose Intl", "Kolkata", 22.65, 88.45),
    (6, "HYD", "Rajiv Gandhi Intl", "Hyderabad", 17.24, 78.43),
    (7, "AMD", "Sardar Vallabhbhai Patel Intl", "Ahmedabad", 23.07, 72.63),
    (8, "PNQ", "Pune Airport", "Pune", 18.58, 73.92),
    (9, "GOI", "Dabolim Airport", "Goa", 15.38, 73.83),
    (10, "COK", "Cochin Intl", "Kochi", 10.15, 76.39),
    (11, "JAI", "Jaipur Intl", "Jaipur", 26.82, 75.81),
    (12, "IXC", "Chandigarh Intl", "Chandigarh", 30.67, 76.79),
]

aircraft_models = [("Airbus A320", 180), ("Airbus A321", 222),
                   ("Boeing 737-800", 189), ("ATR 72", 78), ("Airbus A320neo", 186)]

first_names = ["Aarav", "Vivaan", "Aditya", "Arjun", "Rohan", "Ishaan", "Kabir", "Dev",
               "Ananya", "Diya", "Isha", "Meera", "Priya", "Riya", "Saanvi", "Kavya",
               "Gurleen", "Harpreet", "Simran", "Neha", "Karan", "Raj", "Sneha", "Tanvi"]
last_names = ["Sharma", "Verma", "Singh", "Patel", "Reddy", "Iyer", "Nair", "Gupta",
              "Mehta", "Khan", "Das", "Kaur", "Joshi", "Bose", "Rao", "Malhotra"]


def haversine(lat1, lon1, lat2, lon2):
    r = 6371
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dphi = p2 - p1
    dlmb = math.radians(lon2 - lon1)
    a = math.sin(dphi / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dlmb / 2) ** 2
    return round(2 * r * math.asin(math.sqrt(a)))


# ---------- Build DB ----------
conn = sqlite3.connect(DB_NAME)
cur = conn.cursor()

cur.executescript("""
DROP TABLE IF EXISTS bookings;
DROP TABLE IF EXISTS flights;
DROP TABLE IF EXISTS passengers;
DROP TABLE IF EXISTS aircraft;
DROP TABLE IF EXISTS airports;
DROP TABLE IF EXISTS airlines;

CREATE TABLE airlines (
    airline_id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    iata_code TEXT NOT NULL
);
CREATE TABLE airports (
    airport_id INTEGER PRIMARY KEY,
    iata_code TEXT NOT NULL,
    name TEXT NOT NULL,
    city TEXT NOT NULL,
    latitude REAL,
    longitude REAL
);
CREATE TABLE aircraft (
    aircraft_id INTEGER PRIMARY KEY,
    airline_id INTEGER REFERENCES airlines(airline_id),
    model TEXT NOT NULL,
    capacity INTEGER NOT NULL
);
CREATE TABLE flights (
    flight_id INTEGER PRIMARY KEY,
    flight_number TEXT NOT NULL,
    airline_id INTEGER REFERENCES airlines(airline_id),
    aircraft_id INTEGER REFERENCES aircraft(aircraft_id),
    origin_id INTEGER REFERENCES airports(airport_id),
    destination_id INTEGER REFERENCES airports(airport_id),
    departure_time TEXT NOT NULL,
    arrival_time TEXT NOT NULL,
    distance_km INTEGER,
    status TEXT NOT NULL,          -- On Time / Delayed / Cancelled
    delay_minutes INTEGER DEFAULT 0
);
CREATE TABLE passengers (
    passenger_id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    age INTEGER,
    gender TEXT,
    home_city TEXT
);
CREATE TABLE bookings (
    booking_id INTEGER PRIMARY KEY,
    flight_id INTEGER REFERENCES flights(flight_id),
    passenger_id INTEGER REFERENCES passengers(passenger_id),
    seat_class TEXT NOT NULL,      -- Economy / Premium / Business
    fare REAL NOT NULL,
    booking_date TEXT NOT NULL
);
""")

cur.executemany("INSERT INTO airlines VALUES (?,?,?)", airlines)
cur.executemany("INSERT INTO airports VALUES (?,?,?,?,?,?)", airports)

# Aircraft: 5-8 per airline
aircraft_rows, aid = [], 1
for al in airlines:
    for _ in range(random.randint(5, 8)):
        model, cap = random.choice(aircraft_models)
        aircraft_rows.append((aid, al[0], model, cap))
        aid += 1
cur.executemany("INSERT INTO aircraft VALUES (?,?,?,?)", aircraft_rows)

# Passengers
cities = [a[3] for a in airports]
passenger_rows = []
for pid in range(1, 1501):
    passenger_rows.append((
        pid,
        f"{random.choice(first_names)} {random.choice(last_names)}",
        random.randint(18, 75),
        random.choice(["M", "F"]),
        random.choice(cities),
    ))
cur.executemany("INSERT INTO passengers VALUES (?,?,?,?,?)", passenger_rows)

# Flights (2024-01-01 to 2024-12-31)
airport_by_id = {a[0]: a for a in airports}
flight_rows = []
start = datetime(2024, 1, 1)
for fid in range(1, 2001):
    airline = random.choice(airlines)
    ac = random.choice([a for a in aircraft_rows if a[1] == airline[0]])
    o, d = random.sample(range(1, len(airports) + 1), 2)
    dist = haversine(airport_by_id[o][4], airport_by_id[o][5],
                     airport_by_id[d][4], airport_by_id[d][5])
    dep = start + timedelta(days=random.randint(0, 365),
                            hours=random.randint(5, 23),
                            minutes=random.choice([0, 10, 20, 30, 40, 50]))
    duration = int(dist / 750 * 60) + 30  # rough minutes

    r = random.random()
    if r < 0.05:
        status, delay = "Cancelled", 0
    elif r < 0.30:
        status, delay = "Delayed", random.randint(15, 240)
    else:
        status, delay = "On Time", 0

    arr = dep + timedelta(minutes=duration + delay)
    flight_rows.append((
        fid, f"{airline[2]}{random.randint(100, 999)}", airline[0], ac[0], o, d,
        dep.strftime("%Y-%m-%d %H:%M"), arr.strftime("%Y-%m-%d %H:%M"),
        dist, status, delay,
    ))
cur.executemany("INSERT INTO flights VALUES (?,?,?,?,?,?,?,?,?,?,?)", flight_rows)

# Bookings
booking_rows, bid = [], 1
for f in flight_rows:
    if f[9] == "Cancelled":
        continue
    cap = next(a[3] for a in aircraft_rows if a[0] == f[3])
    n = int(cap * random.uniform(0.5, 0.95) / 4)  # sampled bookings per flight
    dep_dt = datetime.strptime(f[6], "%Y-%m-%d %H:%M")
    for _ in range(n):
        seat = random.choices(["Economy", "Premium", "Business"], [75, 15, 10])[0]
        base = 2000 + f[8] * 4.5
        mult = {"Economy": 1.0, "Premium": 1.6, "Business": 2.8}[seat]
        fare = round(base * mult * random.uniform(0.8, 1.4), 2)
        booked = dep_dt - timedelta(days=random.randint(1, 90))
        booking_rows.append((bid, f[0], random.randint(1, 1500), seat, fare,
                             booked.strftime("%Y-%m-%d")))
        bid += 1
cur.executemany("INSERT INTO bookings VALUES (?,?,?,?,?,?)", booking_rows)

conn.commit()

for t in ["airlines", "airports", "aircraft", "flights", "passengers", "bookings"]:
    print(t, cur.execute(f"SELECT COUNT(*) FROM {t}").fetchone()[0])
conn.close()
print(f"\nCreated {DB_NAME}")
