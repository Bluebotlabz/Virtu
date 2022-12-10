import interactions.api.models.presence as presence
from models import davinci3 as AIModel
import interactions
import json
import time

# External file to store secrets
try:
    with open("./secrets.json", 'r') as secretsFile:
        secrets = json.loads(secretsFile.read())
except:
    print("Error: Invalid secrets.json")
    exit(1)


# Initialise AI model and Discord Bot
aiModel = AIModel(secrets)
botPresence = presence.ClientPresence(
    activities=[
        presence.PresenceActivity(
            name="Chat With Virtu",
            type=presence.PresenceActivityType.GAME,
            application_id=1051152682833936485,
        )
    ],
    status='online'
)
bot = interactions.Client(token=secrets["token"], presence=botPresence)

# REGISTER COMMANDS #
@bot.command(
    name='reset',
    description="Reset Virtu's memory",
)
async def resetMemory(ctx: interactions.CommandContext):
    aiModel.resetMemory()
    await ctx.send("> MEMORY RESET")

@bot.command(
    name='help',
    description='Plz help me'
)
async def help(ctx: interactions.CommandContext):
    helpEmbed = interactions.Embed(
        title="Help",
        color=5793266,
        fields=[
            interactions.EmbedField(
                name="/help",
                value="Shows this help",
                inline=False
            ),
            interactions.EmbedField(
                name="/chat <prompt>",
                value="Chat with Virtu. Virtu will respond to your prompts and try to answer questions",
                inline=False
            ),
            interactions.EmbedField(
                name="/initialise",
                value="Resets Virtu's memory, but then initialises me using a premade prompt",
                inline=False
            ),
            interactions.EmbedField(
                name="/reset",
                value="Resets Virtu's memory, who did you say you were again?",
                inline=False
            ),
            interactions.EmbedField(
                name="/history",
                value="View Virtu's memory",
                inline=False
            ),
            interactions.EmbedField(
                name="$ <prompt>",
                value="Prefix which can be used instead of /chat",
                inline=False
            )
        ],
        footer=interactions.EmbedFooter(text="Virtu v0.0.3-BETA")
    )
    await ctx.send(embeds=[helpEmbed], ephemeral=True)


initialisationPromptChoices = []
for initialisationPrompt in aiModel.initialisationPrompts.keys():
    initialisationPromptChoices.append(interactions.Choice(
        name=initialisationPrompt,
        value=initialisationPrompt
    ))

@bot.command(
    name='initialise',
    description='Reset Virtu\'s memory and initialise a premade prompt',
    options=[
        interactions.Option(
            name="prompt",
            description="What prompt do you want to use to initialise the AI?",
            type=interactions.OptionType.STRING,
            required=True,
            choices=initialisationPromptChoices
        )
    ]
)
async def initialise(ctx: interactions.CommandContext, prompt):
    message = await ctx.send("> " + prompt + "\nPlease wait...")
    aiModel.resetMemory()
    response = aiModel.processInitialisationPrompt(prompt)
    await message.edit("> " + prompt + "\n" + response)

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
    message = await ctx.send("> " + prompt + "\nPlease wait...")

    response = aiModel.processPrompt(prompt)
    await message.edit("> " + prompt + "\n" + response)

@bot.command(
    name='history',
    description='View Virtu\'s Memory'
)
async def chat(ctx: interactions.CommandContext):
    message = await ctx.send("\nPlease wait...")
    
    responses = []
    responseIndex = 0
    responseLength = 0
    for historyItem in aiModel.memory:
        if (responseLength + len(historyItem) > 2000):
            responseIndex += 1

        try:
            responses[responseIndex] += '\n' + historyItem
        except:
            responses.append('\n' + historyItem)
        responseLength += len(historyItem)

    await message.edit(responses[0])
    for response in responses[1]:
        await ctx.send(response)



# EVENT STUFF #
@bot.event(name="on_start")
async def onStart():
    print("Bot Ready.")

# Prefix compatability for easier usage
@bot.event(name="on_message_create")
async def prefixHandler(message: interactions.api.models.message.Message):
    try:
        # Make message.content actually work (won't work without this)
        channel = await message.get_channel()
        message = await channel.get_message(message.id)

        if (len(message.content) > 0 and message.content[0] == '$'):
            returnedMessage = await message.reply("> " + message.content[1:] + "\nPlease wait...")
            response = aiModel.processPrompt(message.content[1:])
            await returnedMessage.edit("> " + message.content[1:] + '\n' + response)
    except interactions.api.error.LibraryException:
        pass

bot.start()
print("Bot ready")