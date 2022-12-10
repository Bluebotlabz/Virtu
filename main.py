import interactions
import openai
import json

try:
    with open("./secrets.json", 'r') as secretsFile:
        secrets = json.loads(secretsFile.read())
except:
    print("Error: Invalid secrets.json")
    exit(1)

class AIModel():
    def __init__(self):
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
    def resetMemory(self):
        self.memory = self.memory[:1]
    def processPrompt(self, prompt):
        self.memory.append("User: " + prompt)

        completion = openai.Completion.create(
            engine='text-davinci-003',
            prompt='\n'.join(self.memory) #prompt
        )

        self.memory.append("Response: " + completion.choices[0].text)

        return completion.choices[0].text


aiModel = AIModel()
bot = interactions.Client(token=secrets["token"])

@bot.command(
    name='reset',
    description="Resets Virtu's memory",
)
async def resetMemory(ctx: interactions.CommandContext):
    aiModel.resetMemory()
    await ctx.send("`: MEMORY RESET :`")

@bot.command(
    name='help',
    description='Plz help me'
)
async def help(ctx: interactions.CommandContext):
    helpMessage = """
    I am Virtu, I am an AI bot made to diss OpenAI's browser
    `v0.0.0-ALPHA`

    I have *many* commands which you can use

    /help           - Prints this output
    /chat <prompt>  - Chat with my brain
    /reset          - Kill my brain
    """
    ctx.send(helpMessage, ephemeral=True)

@bot.command(
    name='chat',
    description='Chat with Virtu!',
    options=[
        interactions.Option(
            name="prompt",
            description="What do you want to say to Virtu?",
            type=interactions.OptionType.STRING,
            required=True
        ),
    ],
)
async def chat(ctx: interactions.CommandContext, prompt):
    print("Prompt recieved: " + prompt)
    response = aiModel.processPrompt(prompt)
    await ctx.send(">" + prompt + "\n\n" + response)

@bot.event(name="on_start")
async def onStart():
    print("Bot Ready.")

@bot.event(name="on_")
async def prefixHandler():


bot.start()
print("Bot ready")