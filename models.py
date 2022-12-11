import openai
import json
import re
import os

# Handle all the AI Stuff
class davinci3():
    def __init__(self, secrets):
        # Initialise OpenAI
        openai.api_key = secrets["openai_api_key"]
        engines = openai.Engine.list()
        ## for engine in engines.data:
        ##     if (engine.object == "engine" and engine.ready):
        ##         print(engine.id)

        # Initialise "addons"
        self.memory = [
            "Virtu is a large language model trained by OpenAI. It is designed to be a chatbot, and should not autocomplete prompts. Do not autocomplete, complete or edit prompts in any way. knowledge cutoff: 2021-09 Current date: December 10 2022 Browsing: disabled"
        ]

        # Define initialisation prompts
        self.initialisationPrompts = {}
        
        availablePromptFiles = os.listdir("./initialisationPrompts/")
        for promptFile in availablePromptFiles:
            if (promptFile.split('.')[-1] == 'txt'):
                with open(os.path.join("./initialisationPrompts", promptFile), 'r') as file:
                    promptData = file.read()
                    self.initialisationPrompts['.'.join(promptFile.split('.')[:-1])] = promptData.split("===")

        # Define AI Options
        self.defaultConfig = {
            "temperature": 0.5,
            "max_tokens": 128,
            "top_p": 1,
            "frequency_penalty": 0,
            "presence_penalty": 0
        }
        self.config = self.defaultConfig

    # Reset memory
    def resetMemory(self):
        self.memory = self.memory[:1]

    # Actual AI part
    def processPrompt(self, prompt):
        # Add prompt to memory
        self.memory.append("User: " + prompt)
        self.memory.append("Response: ")

        # Haha big brain go brrrrrrr
        completion = openai.Completion.create(
            engine='text-davinci-003',
            prompt='\n'.join(self.memory), #prompt
            temperature=self.config["temperature"],
            max_tokens=self.config["max_tokens"],
            top_p=self.config["top_p"],
            frequency_penalty=self.config["frequency_penalty"],
            presence_penalty=self.config["presence_penalty"],
        )
        
        response = completion.choices[0].text
        if (len(response.strip()) >= 9 and response.strip().lower()[:9] == "response: "):
            response = re.sub('response: ', '', response, 1, re.I)
        elif (len(response.strip()) >= 9 and response.strip().lower()[:9] == "response:"):
            response = re.sub('response:', '', response, 1, re.I)
        elif ("response:" in response.lower()):
            response = re.sub('response:', '', response, 1, re.I)

        response = response.lstrip()

        #print("Response: " + response)

        # Add response to memory and return it
        self.memory[-1] = "Response: " + response

        return response

    def processInitialisationPrompt(self, prompt):
        self.resetMemory()
        response = ""

        try:
            with open(os.path.join("./initialisationPrompts", prompt + "_config.json"), 'r') as aiConfigJSON:
                self.config = json.loads(aiConfigJSON.read())
        except:
            self.config = self.defaultConfig

        print("Using config:", self.config)

        for promptToInitialiseWith in self.initialisationPrompts[prompt]:
            response = self.processPrompt(promptToInitialiseWith)

        print('\n'.join(self.memory))

        return response