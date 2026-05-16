TRANSITIONS = {
    "NEW": {
        "PAY_OK": "PAID",
        "PAY_FAIL": "CANCELLED",
        "CANCEL": "CANCELLED",
    },
    "PAID": {
        "COMPLETE": "DONE",
        "CANCEL": "CANCELLED",
        "PAY_FAIL": "CANCELLED",
    },
    "DONE": {},
    "CANCELLED": {},
}


def next_state(state: str, event: str) -> str:
    return TRANSITIONS.get(state, {}).get(event, state)


def cancel_reserve():
    return True


def cancel_reserve_with_retry():
    while True:
        if cancel_reserve():
            return True


def run_invoice_saga(payment_ok: bool) -> str:
    state = "NEW"

    if payment_ok:
        state = next_state(state, "PAY_OK")
        return next_state(state, "COMPLETE")

    state = next_state(state, "PAY_FAIL")
    cancel_reserve_with_retry()
    return state
