import time

def substrate_function(func):
    func.is_substrate_function = True
    return func

@substrate_function
def wait_and_say_hello():
    # Wait for 90 seconds
    time.sleep(90)
    # Return the message "hello"
    return "hello"


