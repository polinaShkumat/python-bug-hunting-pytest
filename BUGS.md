# Bug report

19 of the 42 tests fail on `src/original.py`. All of them pass on `src/fixed.py`.
Run `TARGET=original pytest` to reproduce.

## cancel_by_booking_ref (cinema booking system)

| # | Bug | What could happen | Fix |
|---|-----|-------------------|-----|
| 1 | **The booking reference is asked for but never checked.** The function cancels the first booking that matches the customer's *name*. | Typing a reference that does not exist (`99`) still cancels a real booking. A customer can cancel a booking they did not mean to, and the wrong one is refunded. This is a *broken access control* problem (OWASP Top 10, A01). | Match on both `booking_ref` **and** `customer_name`. |
| 2 | Letters typed as the reference or the quantity crash the program (`int("abc")`). | The whole booking system stops on one typo. | `try/except ValueError` around both inputs. |
| 3 | The refund is not rounded: `333 * 0.8` prints as `266.40000000000003€`. | Confusing receipts; float errors build up in the stored total. | `round(..., 2)` and print with `:.2f`. |

## parse_person (CSV record parser)

| # | Bug | What could happen | Fix |
|---|-----|-------------------|-----|
| 4 | Age `0` is accepted. | Unrealistic records end up in the statistics. | Valid range is now 1–120. |
| 5 | ID `0` and negative IDs are accepted. | Broken identifiers. | ID must be greater than 0. |
| 6 | An empty name is accepted. | Records without a name. | Name is checked like the city. |
| 7 | `nan` and `1e999` are accepted as scores. Python's `float()` turns them into *not-a-number* and *infinity*. | One bad row makes every average, min and max meaningless. | Reject with `math.isnan` / `math.isinf`. |
| 8 | Weak email check (`@gmail.com` passes). | Invalid contact data. | Reuse the stricter `check_email`. |
| 9 | A non-string input (`None`) raises `AttributeError` instead of `ValueError`. | Code that catches `ValueError` to skip bad rows crashes instead. | Type check first, always raise `ValueError`. |

## check_email

| # | Bug | Fix |
|---|-----|-----|
| 10 | Spaces inside the address are allowed (`an na@gmail.com`). | Reject spaces. |
| 11 | Two dots in a row in the domain are allowed (`gmail..com`). | Reject `..`. |
| 12 | No length limit (a 300-character address passes). | Max 254 characters (the limit from the email standard). |
| 13 | `None` / numbers raise `AttributeError` instead of `ValueError`. | Type check first. |
