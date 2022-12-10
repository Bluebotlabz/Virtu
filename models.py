import openai
import re

# Handle all the AI Stuff
class davinci3():
    def __init__(self, secrets):
        # Initialize OpenAI
        openai.api_key = secrets["openai_api_key"]
        engines = openai.Engine.list()
        ## for engine in engines.data:
        ##     if (engine.object == "engine" and engine.ready):
        ##         print(engine.id)

        # Initialize "addons"
        self.memory = [
            "Assistant is a large language model trained by OpenAI. knowledge cutoff: 2021-09 Current date: December 10 2022 Browsing: disabled"
        ]

    # Reset memory
    def resetMemory(self):
        self.memory = self.memory[:1]

    # Actual AI part
    def processPrompt(self, prompt):
        # Add prompt to memory
        self.memory.append("User: " + prompt)

        # Haha big brain go brrrrrrr
        completion = openai.Completion.create(
            engine='text-davinci-003',
            prompt='\n'.join(self.memory), #prompt
            temperature=0.5,
            max_tokens=128,
            top_p=1,
            frequency_penalty=0,
            presence_penalty=0,
        )
        
        response = completion.choices[0].text
        if (len(response.strip()) >= 9 and response.strip().lower()[:9] == "response: "):
            response = re.sub('response: ', '', response, 1, re.I)
        elif (len(response.strip()) >= 9 and response.strip().lower()[:9] == "response:"):
            response = re.sub('response:', '', response, 1, re.I)
        elif ("response:" in response.lower()):
            response = re.sub('response:', '', response, 1, re.I)

        print("Response: " + response)

        # Add response to memory and return it
        self.memory.append("Response: " + response)

        return response