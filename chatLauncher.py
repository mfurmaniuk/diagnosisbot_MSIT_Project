import re

# Define data types and variables
user_name: str
user_query: str
response: str
is_helpful: bool = True

# Sample product catalog for demonstration
product_catalog = {
    'children': True,
    'adults': True,
    'elderly': False
}


# Move the following to a Class and library functions when more structured
def greet_user():
    """Function to greet the user and introduce the chatbot."""
    print("Hello! I am your customer support chatbot.")
    print("How can I assist you today?")


def get_user_input():
    """Function to collect and store user input."""
    global user_name, user_query
    user_name = input("What's your name? ")  # Store user's name
    print(user_name + " if you wish assistance enter - help.")
    print(user_name + " if you wish to leave enter - bye")
    user_query = input(f"Hi {user_name}, please enter your query: ")  # Store user's query


def calculate_expression(expression: str) -> float:
    """Function to evaluate a simple arithmetic expression."""
    try:
        result = eval(expression)
        return result
    except Exception:
        return None


def compare_numbers(comparison: str) -> str:
    """Function to evaluate a comparison expression."""
    try:
        # Extract numbers and the operator from the comparison
        match = re.match(r'(\d+)\s*(==|!=|<|>)\s*(\d+)', comparison)
        if match:
            num1 = float(match.group(1))
            operator = match.group(2)
            num2 = float(match.group(3))

            # Evaluate the comparison based on the operator
            if operator == '==':
                return f"{num1} is equal to {num2}." if num1 == num2 else f"{num1} is not equal to {num2}."
            elif operator == '!=':
                return f"{num1} is not equal to {num2}." if num1 != num2 else f"{num1} is equal to {num2}."
            elif operator == '<':
                return f"{num1} is less than {num2}." if num1 < num2 else f"{num1} is not less than {num2}."
            elif operator == '>':
                return f"{num1} is greater than {num2}." if num1 > num2 else f"{num1} is not greater than {num2}."
    except Exception:
        return "I couldn't evaluate that comparison. Please re-enter your input."

    return "Invalid comparison format."


def evaluate_logical_expression(expression: str) -> str:
    """Function to evaluate a logical expression."""
    try:
        # Extract keywords and the logical operator from the expression
        match = re.match(r'(.*?)\s*(and|or|not)\s*(.*?)', expression, re.IGNORECASE)
        if match:
            operand1 = match.group(1).strip().lower()
            operator = match.group(2).strip().lower()
            operand2 = match.group(3).strip().lower()

            # Check the condition based on the operator
            if operator == 'and':
                return f"{operand1.capitalize()} and {operand2.capitalize()}: " \
                       f"{product_catalog.get(operand1, False) and product_catalog.get(operand2, False)}"
            elif operator == 'or':
                return f"{operand1.capitalize()} or {operand2.capitalize()}: " \
                       f"{product_catalog.get(operand1, False) or product_catalog.get(operand2, False)}"
            elif operator == 'not':
                return f"Not {operand1.capitalize()}: {not product_catalog.get(operand1, False)}"
    except Exception:
        pass

    return "I couldn't evaluate that logical expression. Please re-enter your input."


def respond_to_query():
    """Function to respond to user queries."""
    global response
    # Check if the user is asking for help or a calculation
    if "help" in user_query.lower():
        response = "I am here to help you! Please provide more details."
    elif "bye" in user_query.lower():
        response = "Goodbye! Have a great day!"
        global is_helpful
        is_helpful = False  # Change to False if the user wants to end the conversation
    elif re.search(r'\d+\s*[\+\-\*\/]\s*\d+', user_query):
        # Extract the arithmetic expression from the user query
        expression = re.search(r'\d+\s*[\+\-\*\/]\s*\d+', user_query).group()
        result = calculate_expression(expression)
        if result is not None:
            response = f"The result of {expression} is {result}."
        else:
            response = "I couldn't evaluate that expression. Please re-enter your input."
    elif re.search(r'\d+\s*(==|!=|<|>)\s*\d+', user_query):
        # Extract the comparison expression from the user query
        comparison = re.search(r'\d+\s*(==|!=|<|>)\s*\d+', user_query).group()
        response = compare_numbers(comparison)
    elif re.search(r'.*\b(and|or|not)\b.*', user_query, re.IGNORECASE):
        # Extract the logical expression from the user query
        logical_expr = re.search(r'.*\b(and|or|not)\b.*', user_query, re.IGNORECASE).group()
        response = evaluate_logical_expression(logical_expr)
    else:
        response = "I'm sorry, I didn't understand that. Can you please rephrase?"
# End of place to move to a Class and library functions when more structured


def main():
    """Main function to run the chatbot."""
    greet_user()

    while is_helpful:
        get_user_input()
        respond_to_query()
        print(response)


if __name__ == "__main__":
    main()
