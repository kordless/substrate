# Function: fib_sequence
# Arguments:
#   ["n"]
# Pip install strings:
#   []

pip_install_strings = []



def substrate_function(func):
    func.is_substrate_function = True
    return func

@substrate_function
def fib_sequence(n):
    sequence = []
    a, b = 0, 1
    while len(sequence) < n:
        sequence.append(a)
        a, b = b, a + b
    return sequence
