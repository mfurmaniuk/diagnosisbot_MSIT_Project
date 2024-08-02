from googletrans import Translator, LANGUAGES
 
class TriageBot:
    def __init__(self, name):
        self.name = name
        
    def translate_welcome(self):
        """Prompts for source and destination languages as well as a phrase to translate"""
        print("Welcome to the Translator!")
        print("For languages use values such as en - English, fr - French, es - Spanish")
        # Collect source and destination languages using previous list
        src_language = input("Enter the source language code: ")
        dest_language = input("Enter the language you wish to translate to: ")
        text = input("Enter the text to translate: ")
        translation = self.translate_to_language(text, src_language, dest_language)
        print(translation)
    
    def translate_to_language(self, text, src_language, dest_language):
        """Uses the following:
            text - phrase to translate
            src_language - language the phase is of
            dest_language - langauge to translate to
            
            returns translated phrase"""
        # Translate a string of text from a specific language to english
        translator = Translator()
        try:
            # Translate the text from the specified source language to destination language
            translation = translator.translate(text, src=src_language, dest=dest_language)
            return translation.text
        except Exception as e:
            return f"An error occurred: {e}"

    def chat(self):
        """Main entry function"""
        # Intro and prompt for function to perform
        print(f"Hi! I'm {self.name}. Type 'bye' to exit.")
        while True:
            user_input = input("Enter your need (translate / triage): ")
            # Call translation function
            if user_input == "translate":
                self.translate_welcome()
                # Call triage function, the real feature of the chatbot, not yet implemented
            elif user_input == "triage":
                print("Triage is coming, for now visit your physician.")
            # Exit
            elif user_input.lower() == "bye":
                print("Goodbye!")
                break
            else:
                print("Sorry I did not understand that, please try again.")

# Create an instance of the ChatBot class
triageBot = TriageBot("TriageBot")

# Start the chat
triageBot.chat()
