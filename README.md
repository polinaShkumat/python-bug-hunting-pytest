# 🐞 Python Bug Hunting with pytest

I took three functions I wrote in earlier university labs, wrote a test suite
that attacks them with edge cases and bad input, and fixed every bug the tests found.

**Result: 19 of 42 tests fail on the original code → 42 of 42 pass after the fixes.**

The most interesting bug: the cinema booking system asked for a booking
reference but never checked it. It cancelled the first booking with a matching
customer name, so any made-up reference still cancelled a real booking. That is
a small example of *broken access control*, the #1 risk in the OWASP Top 10.

## What is tested

| Function | What it does | Tests |
|---|---|---|
| `check_email` | validates and cleans an email address | 14 |
| `parse_person` | turns one CSV line into a validated record | 17 |
| `cancel_by_booking_ref` | interactive ticket cancellation with refunds | 11 |

The full list of bugs, their impact and the fixes is in **[BUGS.md](BUGS.md)**.

## Testing techniques used

- **`@pytest.mark.parametrize`** – one test function runs over many inputs (valid, invalid, boundary values like age 1 and 120).
- **`pytest.raises`** – checks that bad input raises `ValueError` instead of crashing or being silently accepted.
- **`monkeypatch`** – replaces `input()` with a list of prepared answers, so an interactive function can be tested automatically.
- **`capsys`** – captures printed output to check the refund text.
- **Fresh state per test** – `copy.deepcopy` resets the shared bookings data before every test, so tests do not affect each other.
- **Before/after comparison** – the same suite runs against both versions, chosen with an environment variable.

## Project structure

```
python-bug-hunting-pytest/
├── src/
│   ├── original.py        # unchanged code with the bugs
│   └── fixed.py           # fixed code, every change marked NEW / CHANGED
├── tests/
│   └── test_functions.py  # 42 tests
├── BUGS.md                # bug report
└── requirements.txt
```

## How to run

```bash
pip install -r requirements.txt

pytest -v                    # run against the fixed version  -> 42 passed
TARGET=original pytest -v    # run against the original       -> 19 failed
```

On Windows (PowerShell): `$env:TARGET="original"; pytest -v`

## What I learned

- Code that "works" on normal input can still be wrong. Most bugs were only visible with edge cases: `0`, negative numbers, empty strings, `None`, `nan`.
- `float("nan")` and `float("1e999")` do not raise errors in Python, so number validation needs extra checks.
- Interactive functions are hard to test. `monkeypatch` makes it possible, but it also shows why separating input/output from logic makes code easier to test.
- Writing the tests **before** fixing the code made it easy to prove each fix actually worked.

## Tech

Python 3 · pytest
