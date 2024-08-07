from googletrans import Translator, LANGUAGES
 
class TriageBot:
    body_areas = ["ear", "nose", "throat", "head"]
    potential_illnesses = {
        "ear": "The ear can have many conditions from tinnitus, ear wax build-up, or hearing loss from age.",
        "nose": "The nose can cross illnesses from runny noses, congestion, allergies, to consistent nosebleeds.",
        "throat": "The throat can cross illnesses from colds, allergies, tonsillitus, to sore throat and laryngitus.",
        "head": "A headache or fever may come with other illnesses, and be focused on pain in the temples or a fever."
    }
    
    def __init__(self, name):
        self.name = name
    
    def collect_symptoms(self):
        """Collects a Users Symptoms and returns them as a list"""
        print("Please let us know your symptoms.  Add each one so they can be checked for a diagnosis later.")
        print("Add a symptom such as fever, congestions, etc for diagnosis, use an empty line to finish.")
        new_symptom = ''
        symptom_list = []
        while True:
            new_symptom = input("Your Symptom: ")
            if new_symptom == "":
                print("Thank you for letting me know how you feel.")
                break
            else:
                symptom_list.append(new_symptom)
                
        return symptom_list
        
    def triage_welcome(self):
        """Prompts for what area of the body a person is feeling sick from"""
        symptom_list = []
        print("You can check for illnesses in the following areas:")
        print(', '.join(self.body_areas))
        body_check = input("Please enter the body area you are feeling sick in: ")
        if body_check in self.body_areas:
            symptom_list = self.collect_symptoms()
            print("We can help you with looking for illnesses affecting the " + body_check)
            self.triage_check(body_check)
            print("We'll soon get to a diagnosis with your symptoms of: " + ', '.join(symptom_list))
        else:
            print("Sorry we don't currently have a way to check for illnesses in the " + body_check)
    
    def triage_check(self,body_check):
        """Matches the body area to initial conditions we can check for."""
        print(self.potential_illnesses[body_check])

    def chat(self):
        """Main entry function"""
        # Intro and prompt for function to perform
        while True:
            print(f"Welcome to {self.name} to help you with your health needs.")
            user_input = input("Would you like a diagnosis? (triage / bye): ")
            # Call triage function, the real feature of the chatbot
            if user_input == "triage":
                self.triage_welcome()
            elif user_input.lower() == "bye":
                print("Goodbye!")
                break
            else:
                print("Sorry I did not understand that, please try again.")

# Create an instance of the ChatBot class
triageBot = TriageBot("TriageBot")

# Start the chat
triageBot.chat()
