# Substrate Write and Run Python Example

## Getting Started

To begin using this project, you'll need to obtain an API key from Substrate. Follow these steps to get started:

1. **Visit the Substrate API**: Navigate to the following URL to retrieve your API key:
   - [https://substrate.run](https://substrate.run)

2. **Input Your API Key**: Once you have your API key, you can input it into the application during startup when prompted.

3. Do a `pip install substrate`

## Running the Code

This project allows you to write and execute Python functions dynamically using the Substrate API. Here’s how it works:

1. **Function Creation**: You can create new functions by providing a description of what the function should do. The application will write the code for you.

2. **Executing Functions**: After defining the functions, you can run them directly from the command line interface. The application will prompt you to select which function to run.

### Example Usage
- To create a function, enter a description in the prompt when asked. The application will handle the rest, including writing the code and ensuring it runs without errors. 
- After the function is created, you will see an option to run it; simply follow the prompt to input any needed parameters.

### Interaction Example
```
python main.py
```

```
Do you want me write a function? (y/n): y
Describe the function to write: This function should calculate the Body Mass Index (BMI) of a person. It should take two parameters: weight in kilograms and height in meters. The function should return the calculated BMI value rounded to one decimal place.
Code:
def calculate_bmi(weight, height):
    return round(weight / (height ** 2), 1)

# Example usage:
calculate_bmi(70, 1.75)
Arguments: ["weight", "height"]
Pip install strings: []
Function name: calculate_bmi
Syntax validation passed: No syntax errors found.
Available functions:
1. calculate_bmi.calculate_bmi
2. fib_sequence.fib_sequence
3. markdown.markdown
Enter the number of the function you want to run: 1
You selected: calculate_bmi.calculate_bmi
Enter value for 'weight': 200
Enter value for 'height': 2
50.0
```
