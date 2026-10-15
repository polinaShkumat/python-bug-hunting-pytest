"""Fixed versions of the functions in original.py.
Every change is marked with NEW or CHANGED.
See BUGS.md for the full list of bugs and why they matter.
"""
import math


# helper ----------

def clean(raw_value):
    return raw_value.strip().strip('"')


# check_email (Lab 4.1) ----------

def check_email(raw_email):
    if type(raw_email) != str:   # NEW: not text -> error
        raise ValueError("Email must be text")

    cleaned = clean(raw_email)
    if cleaned == "" or cleaned == "None":
        raise ValueError("Email is missing")
    if len(cleaned) > 254:   # NEW: too long
        raise ValueError("Email is too long")
    if " " in cleaned:   # NEW: no spaces inside
        raise ValueError(f"Email '{cleaned}' has a space")
    if cleaned.count("@") != 1:
        raise ValueError(f"Email '{cleaned}' must contain exactly one @")

    username, domain = cleaned.split("@")
    if username == "":
        raise ValueError(f"Email '{cleaned}' has nothing before the @")
    if "." not in domain or domain.startswith(".") or domain.endswith("."):
        raise ValueError(f"Email '{cleaned}' has an invalid domain")
    if ".." in domain:   # NEW: no double dots
        raise ValueError(f"Email '{cleaned}' has two dots in a row")
    return cleaned


# parse_person (Lab 4.2) ----------

def parse_person(line):
    if type(line) != str:   # NEW: not text -> error
        raise ValueError("Line must be text")

    parts = line.split(",")
    if len(parts) != 6:
        raise ValueError(f"expected 6 fields, got {len(parts)}")

    raw_id, name, raw_age, city, email, raw_score = parts
    name, city = clean(name), clean(city)

    try:
        person_id = int(clean(raw_id))
        age = int(clean(raw_age))
        score = float(clean(raw_score))
    except ValueError:
        raise ValueError("ID, Age or Score is not a number")

    if math.isnan(score) or math.isinf(score):   # NEW: "nan" and "1e999" are valid floats, but not real scores
        raise ValueError("score must be a real number")
    if person_id <= 0:   # NEW: ID must be positive
        raise ValueError("ID must be greater than 0")
    if name == "" or name == "None":   # NEW: check the name
        raise ValueError("name is missing")
    if age < 1 or age > 120:   # CHANGED: was age < 0
        raise ValueError(f"age {age} is not realistic")
    if city == "" or city == "None":
        raise ValueError("city is missing")

    email = check_email(email)   # CHANGED: use the better email check

    return {"id": person_id, "name": name, "age": age,
            "city": city, "email": email, "score": score}


# cancel_by_booking_ref (Lab 3.2) ----------

movies = {}
bookings = []   # [booking_ref, customer_name, movie, showtime, num_tickets, total_cost]


def cancel_by_booking_ref():
    global movies, bookings

    name = input("Enter customer name: ")
    try:   # NEW: letters don't crash the program
        ref = int(input("Enter booking reference: "))
    except ValueError:
        print("Booking reference must be a number.")
        return

    target = None
    for b in bookings:
        if b[0] == ref and b[1] == name:   # CHANGED: check the reference too
            target = b
            break

    if target is None:
        print("No matching booking found for this customer and reference.")
        return

    booking_ref, customer_name, title, showtime, num_tickets, total_cost = target
    price_per_ticket = total_cost / num_tickets

    try:   # NEW: letters don't crash the program
        cancel_qty = int(input(f"You have {num_tickets} ticket(s). How many to cancel? "))
    except ValueError:
        print("Quantity must be a number.")
        return

    if cancel_qty <= 0 or cancel_qty > num_tickets:
        print("Invalid quantity.")
        return

    refund = round(cancel_qty * price_per_ticket * 0.8, 2)   # CHANGED: round to cents
    movies[title][showtime]["seats"] += cancel_qty

    if cancel_qty == num_tickets:
        bookings.remove(target)
        print(f"Fully canceled booking {ref}. Refund: {refund:.2f}€")
    else:
        target[4] -= cancel_qty
        target[5] = round(target[5] - cancel_qty * price_per_ticket, 2)
        print(f"Canceled {cancel_qty} ticket(s) from booking {ref}. Refund: {refund:.2f}€")