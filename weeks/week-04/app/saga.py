def next_state(state: str, event: str) -> str:
    # Состояния: NEW, PAID, DONE, CANCELLED
    # События: CREATE, PAY_OK, PAY_FAIL, COMPLETE, CANCEL
    
    transitions = {
        'NEW': {
            'CREATE': 'NEW',
            'PAY_OK': 'PAID',      
            'PAY_FAIL': 'CANCELLED',
            'COMPLETE': 'NEW',
            'CANCEL': 'CANCELLED'
        },
        'PAID': {
            'CREATE': 'PAID',
            'PAY_OK': 'PAID',
            'PAY_FAIL': 'CANCELLED',
            'COMPLETE': 'DONE',
            'CANCEL': 'CANCELLED'
        },
        'DONE': {
            'CREATE': 'DONE',
            'PAY_OK': 'DONE',
            'PAY_FAIL': 'DONE',
            'COMPLETE': 'DONE',
            'CANCEL': 'DONE'
        },
        'CANCELLED': {
            'CREATE': 'CANCELLED',
            'PAY_OK': 'CANCELLED',
            'PAY_FAIL': 'CANCELLED',
            'COMPLETE': 'CANCELLED',
            'CANCEL': 'CANCELLED'
        }
    }
    
    if state not in transitions:
        return state
    if event not in transitions[state]:
        return state
        
    return transitions[state][event]