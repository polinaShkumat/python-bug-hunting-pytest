"""Test suite for check_email, parse_person and cancel_by_booking_ref.

By default the tests run against src/fixed.py.
Run them against the buggy version to see every bug the tests catch:

    TARGET=original pytest
"""
import copy
import importlib
import os
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))
funcs = importlib.import_module(os.environ.get("TARGET", "fixed"))


# ---------- 1) check_email ----------

@pytest.mark.parametrize(
    "email, expected",
    [
        ("anna@gmail.com", "anna@gmail.com"),
        ('  "anna@gmail.com"  ', "anna@gmail.com"),
        ("bob.smith@hhs.nl", "bob.smith@hhs.nl"),
    ],
)
def test_check_email_valid(email, expected):
    assert funcs.check_email(email) == expected


@pytest.mark.parametrize(
    "email",
    [
        "",                       # empty
        "None",                   # missing value
        "anna.gmail.com",         # no @
        "anna@@gmail.com",        # two @
        "@gmail.com",             # nothing before @
        "anna@gmail",             # no dot in domain
        "an na@gmail.com",        # space inside
        "anna@gmail..com",        # two dots in a row
        "a" * 300 + "@gmail.com", # too long
        None,                     # wrong type
        12345,                    # wrong type
    ],
)
def test_check_email_invalid(email):
    with pytest.raises(ValueError):
        funcs.check_email(email)


# ---------- 2) parse_person ----------

@pytest.mark.parametrize(
    "line, expected",
    [
        ("1,Anna,25,Delft,anna@gmail.com,88.5",
         {"id": 1, "name": "Anna", "age": 25, "city": "Delft",
          "email": "anna@gmail.com", "score": 88.5}),
        (' 2 , "Bob" , 30 , "Leiden" , bob@hhs.nl , 70 ',
         {"id": 2, "name": "Bob", "age": 30, "city": "Leiden",
          "email": "bob@hhs.nl", "score": 70.0}),
        ("3,Eva,1,Delft,eva@gmail.com,0",          # minimum age
         {"id": 3, "name": "Eva", "age": 1, "city": "Delft",
          "email": "eva@gmail.com", "score": 0.0}),
        ("4,Tom,120,Delft,tom@gmail.com,100",      # maximum age
         {"id": 4, "name": "Tom", "age": 120, "city": "Delft",
          "email": "tom@gmail.com", "score": 100.0}),
    ],
)
def test_parse_person_valid(line, expected):
    assert funcs.parse_person(line) == expected


@pytest.mark.parametrize(
    "line",
    [
        "",                                   # empty line
        "1,Anna,25",                          # too few fields
        "1,Anna,twenty,Delft,a@b.com,50",     # age is not a number
        "1,Anna,0,Delft,a@b.com,50",          # age 0
        "1,Anna,121,Delft,a@b.com,50",        # age above 120
        "0,Anna,25,Delft,a@b.com,50",         # ID 0
        "-3,Anna,25,Delft,a@b.com,50",        # negative ID
        "1,,25,Delft,a@b.com,50",             # no name
        "1,Anna,25,None,a@b.com,50",          # no city
        "1,Anna,25,Delft,a@b.com,nan",        # score is nan
        "1,Anna,25,Delft,a@b.com,1e999",      # huge number -> inf
        "1,Anna,25,Delft,@gmail.com,50",      # bad email
        None,                                 # wrong type
    ],
)
def test_parse_person_invalid(line):
    with pytest.raises(ValueError):
        funcs.parse_person(line)


# ---------- 3) cancel_by_booking_ref ----------

START_MOVIES = {
    "Inception": {"3PM": {"seats": 44, "total_seats": 50, "price": 250}},
    "Barbie":    {"8PM": {"seats": 7,  "total_seats": 10, "price": 333}},
}
START_BOOKINGS = [
    [1, "Anna", "Inception", "3PM", 2, 500],
    [2, "Anna", "Inception", "3PM", 3, 750],
    [3, "Bob",  "Inception", "3PM", 1, 250],
    [4, "Eva",  "Barbie",    "8PM", 3, 999],
]


def run_cancel(monkeypatch, answers):
    # fresh data before every test
    funcs.movies.clear()
    funcs.movies.update(copy.deepcopy(START_MOVIES))
    funcs.bookings.clear()
    funcs.bookings.extend(copy.deepcopy(START_BOOKINGS))

    # replace input() so the function reads answers from a list instead of the keyboard
    answers = iter(answers)
    monkeypatch.setattr("builtins.input", lambda prompt="": next(answers))

    funcs.cancel_by_booking_ref()


def find_booking(ref):  # find a booking by its reference number
    for b in funcs.bookings:
        if b[0] == ref:
            return b
    return None


@pytest.mark.parametrize(
    "answers, ref, expected_booking",
    [
        (["Bob", "3", "1"], 3, None),                                    # cancel everything
        (["Anna", "1", "1"], 1, [1, "Anna", "Inception", "3PM", 1, 250]), # cancel 1 of 2
        (["Anna", "2", "3"], 2, None),                                   # Anna's second booking
        (["Eva", "4", "1"], 4, [4, "Eva", "Barbie", "8PM", 2, 666]),   # price with decimals
    ],
)
def test_cancel_valid(monkeypatch, answers, ref, expected_booking):
    run_cancel(monkeypatch, answers)
    assert find_booking(ref) == expected_booking


@pytest.mark.parametrize(
    "answers",
    [
        ["Bob", "1", "1"],      # someone else's booking (access control)
        ["Anna", "99", "1"],    # booking does not exist
        ["Anna", "1", "0"],     # quantity 0
        ["Anna", "1", "5"],     # more than booked
        ["Anna", "abc"],        # letters instead of a number
        ["Anna", "1", "two"],   # letters instead of a quantity
    ],
)
def test_cancel_nothing_changes(monkeypatch, answers):
    run_cancel(monkeypatch, answers)
    assert funcs.bookings == START_BOOKINGS


def test_cancel_refund_rounded(monkeypatch, capsys):  # capsys captures what was printed
    run_cancel(monkeypatch, ["Eva", "4", "1"])
    output = capsys.readouterr().out
    assert "266.40€" in output