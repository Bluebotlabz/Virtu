import interactions
import openai
import json

# External file to store secrets
try:
    with open("./secrets.json", 'r') as secretsFile:
        secrets = json.loads(secretsFile.read())
except:
    print("Error: Invalid secrets.json")
    exit(1)

# Handle all the AI Stuff
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

        # Add response to memory and return it
        self.memory.append("Response: " + completion.choices[0].text)

        response = completion.choices[0].text
        if (len(response.strip()) >= 9 and response[:9].strip().lower() == "response:"):
            response = response[9:]

        return response


# Initialize class and Discord Bot
aiModel = AIModel()
bot = interactions.Client(token=secrets["token"])



# REGISTER COMMANDS #
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
    await ctx.send("> " + prompt + "\n" + response)



# EVENT STUFF #
@bot.event(name="on_start")
async def onStart():
    print("Bot Ready.")

# Prefix compatability for easier usage
@bot.event(name="on_message_create")
async def prefixHandler(message: interactions.api.models.message.Message):
    # Make message.content actually work (won't work without this)
    channel = await message.get_channel()
    await channel.get_message(message.id) # This return value isn't even being used but it fixes things???

    if (message.content[0] == '$'):
        print("Prompt recieved: " + message.content[1:])
        response = aiModel.processPrompt(message.content[1:])
        await message.reply("> " + message.content[1:] + response)


bot.start()
print("Bot ready")