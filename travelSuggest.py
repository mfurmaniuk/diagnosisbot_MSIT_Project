# Defining some data types
user_name: str
budget: str
activity: str
climate: str
response: str
want_suggestions: bool = True

def greeter():
    """Function to greet the User"""
    print("Hello!  I am your Travel Suggester, unsure where to go?")
    print("I'm here to give some suggestions depending on your choices.")


def get_travel_input():
    """Function to get the travel options"""
    global user_name, budget, activity, climate
    user_name = input("What's your name? ") # Store for personalization in the future
    print(user_name + "please select from the following travel options.")
    print("When you are done, enter bye.")
    print("Are you looking for a High Cost or a Budget trip? ")
    budget = input("Enter High or Low: ")
    print("Do you seek Adventure, Relaxation or Culture?")
    activity = input("Enter Adventure, Relaxation or Culture: ")
    print("What kind of climate are you looking to be in Warm, Cold, or Tropical?")
    climate = input("Enter Warm, Cold, or Tropical: ")
    # Change travel options to lower case before proceeding
    check_input(budget.lower(), activity.lower(), climate.lower())


def check_input(budget, activity, climate):
    global response
    """Function to check the input values"""
    if budget == "bye" or activity == "bye" or climate == "bye":
        response = "Thank you for trying Travel Suggester, bon voyage!"
        global want_suggestions
        want_suggestions = False
    else:
        travel_suggestions(budget, activity, climate)


def travel_suggestions(budget, activity, climate):
    """Function to display the Travel Options"""
    global response
    if budget == "high":
        if activity == "adventure":
            if climate == "warm":
                response = "May I suggest a golfing trip in the Carolinas"
            elif climate == "cold":
                response = "A ski trip in the Swiss Alps might be a good option"
            elif climate == "tropical":
                response = "Scuba diving in the Carribean might be for you"
            else:
                response = "Please enter an appropriate climate"
        elif activity == "relaxation":
            if climate == "warm":
                response = "A private beach on the West Coast of the US might be a good fit"
            elif climate == "cold":
                response = "Seeing the polar bear migration in Canada could be for you"
            elif climate == "tropical":
                response = "A private beach on a private island might be good option"
            else:
                response = "Please enter an appropriate climate"
        elif activity == "culture":
            if climate == "warm":
                response = "A wine and food tour in France may be the ticket"
            elif climate == "cold":
                response = "A helicopter tour of the Swiss Alps sounds exciting"
            elif climate == "tropical":
                response = "Museum and food tour of the South Sea could be fun"
            else:
                response = "Please enter an appropriate climate"
        else:
            response = "Please enter an appropriate activity."
    elif budget == "low":
        if activity == "adventure":
            if climate == "warm":
                response = "A hiking tour of the Appalachians sounds good"
            elif climate == "cold":
                response = "A snow shoe trek in Montana could be fun"
            elif climate == "tropical":
                response = "Hiking tour in the high desert sounds like a match"
            else:
                response = "Please enter an appropriate climate"
        elif activity == "relaxation":
            if climate == "warm":
                response = "Try a biking tour in Holland"
            elif climate == "cold":
                response = "A Smores trip if Vermont lodges"
            elif climate == "tropical":
                response = "Airboat tour of the Everglades"
            else:
                response = "Please enter an appropriate climate"
        elif activity == "culture":
            if climate == "warm":
                response = "Let's try a New York City museum tour"
            elif climate == "cold":
                response = "A walking tour of Canadian museums"
            elif climate == "tropical":
                response = "A walking tour of the Florida Keys might be fun"
            else:
                response = "Please enter an appropriate climate"
        else:
            response = "Please enter an appropriate activity"
    else:
        response = "Please enter an appropriate budget."
    

def main():
    """Main function to run the Travel Suggester"""
    greeter()
    
    while want_suggestions:
        get_travel_input()
        print(user_name + ", " + response)


if __name__ == "__main__":
    main()
