# Function: calculate_bmi
# Arguments:
#   ["weight", "height"]
# Pip install strings:
#   []

pip_install_strings = []



def substrate_function(func):
    func.is_substrate_function = True
    return func

@substrate_function
def calculate_bmi(weight, height):
	return round(weight / (height ** 2), 1)

# Example usage:
calculate_bmi(70, 1.75)
