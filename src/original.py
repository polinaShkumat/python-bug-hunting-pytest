"""Original versions of three functions, copied unchanged from earlier labs.
They contain the bugs documented in BUGS.md - do not use this file in real code.
"""

# from Lab 4.1 ----------

def clean(raw_value):
    return raw_value.strip().strip('"')


def check_email(raw_email):
    cleaned = clean(raw_email)
    if cleaned == "" or cleaned == "None":
        raise ValueError("Email is missing")
    if cleaned.count("@") != 1:
        raise ValueError(f"Email '{cleaned}' must contain exactly one @")

    username, domain = cleaned.split("@")
    if username == "":
        raise ValueError(f"Email '{cleaned}' has nothing before the @")
    if "." not in domain or domain.startswith(".") or domain.endswith("."):
        raise ValueError(f"Email '{cleaned}' has an invalid domain")
    return cleaned


# from Lab 4.2 ----------

def parse_person(line):
    parts = line.split(",")
    if len(parts) != 6:
        raise ValueError(f"expected 6 fields, got {len(parts)}")

    raw_id, name, raw_age, city, email, raw_score = parts
    name, city, email = clean(name), clean(city), clean(email)

    try:
        person_id = int(clean(raw_id))
        age = int(clean(raw_age))
        score = float(clean(raw_score))
    except ValueError:
        raise ValueError("ID, Age or Score is not a number")

    if age < 0 or age > 120:
        raise ValueError(f"age {age} is not realistic")
    if city == "" or city == "None":
        raise ValueError("city is missing")
    if email.count("@") != 1 or "." not in email.split("@")[1]:
        raise ValueError(f"invalid email '{email}'")

    return {"id": person_id, "name": name, "age": age,
            "city": city, "email": email, "score": score}


# from Lab 3.2 ----------

movies = {}
bookings = []   # [booking_ref, customer_name, movie, showtime, num_tickets, total_cost]


def cancel_by_booking_ref():
    global movies, bookings

    name = input("Enter customer name: ")
    ref = int(input("Enter booking reference: "))

    target = None
    found = []
    for b in bookings:
        if b[1] == name:
            found.append(b)
            target = b
            break

    if target is None:
        print("No matching booking found for this customer and reference.")
        return

    booking_ref, customer_name, title, showtime, num_tickets, total_cost = target
    price_per_ticket = total_cost / num_tickets

    cancel_qty = int(input(f"You have {num_tickets} ticket(s) on this booking. How many to cancel? "))
    if cancel_qty <= 0 or cancel_qty > num_tickets:
        print("Invalid quantity.")
        return

    refund = cancel_qty * price_per_ticket * 0.8
    movies[title][showtime]["seats"] += cancel_qty

    if cancel_qty == num_tickets:
        bookings.remove(target)
        print(f"Fully canceled booking {ref}. Refund: {refund}€")
    else:
        target[4] -= cancel_qty
        target[5] -= cancel_qty * price_per_ticket
        print(f"Canceled {cancel_qty} ticket(s) from booking {ref}. Refund: {refund}€")