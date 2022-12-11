import interactions.api.models.presence as presence
from models import davinci3 as AIModel
import interactions
import json
import os

# External file to store secrets
try:
    with open("./secrets.json", 'r') as secretsFile:
        secrets = json.loads(secretsFile.read())
except:
    print("Error: Invalid secrets.json")
    exit(1)


# Initialise AI model and Discord Bot
#aiModel = AIModel(secrets)
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

PerUserAIModels = {}
PerChannelAIModels = {}
PerDMAIModels = {}

def getAIModel(guildID, userID, channelID=None, secondaryIDType="perUser"):
    if (guildID != None):
        if (secondaryIDType == "perChannel"): # Shared per channel (also works)
            return PerChannelAIModels.setdefault(guildID, {}).setdefault(channelID, AIModel(secrets))
        elif (secondaryIDType == "perUser"): # Per user, but on server
            return PerUserAIModels.setdefault(guildID, {}).setdefault(userID, AIModel(secrets))
    else:
        return PerDMAIModels.setdefault(userID, AIModel(secrets))

# HELP #
helpEmbed = interactions.Embed(
    title="How To Use Virtu",
    description="Virtu is an AI-Powered Chatbot.\nVirtu remembers what you told it, it has per-user history unique to each server via / commands, it can also be used in a per-channel mode via the use of $ and $$ prefixes, try using $$help or /help",
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
            value="Prefix which can be used instead of /chat (per channel memory)",
            inline=False
        ),
        interactions.EmbedField(
            name="$$ <command>",
            value="Prefix which can be used instead of / for per channel memory",
            inline=False
        )
    ],
    footer=interactions.EmbedFooter(text="Virtu v0.0.3-BETA")
)

def quotePrompt(prompt):
    quotes = []
    for line in prompt.strip().split('\n'):
        quotes.append( '> **' + line + '**' )

    return '\n'.join(quotes)

# REGISTER COMMANDS #
# Reset command
@bot.command(
    name='reset',
    description="Reset Virtu's memory",
)
async def resetMemory(ctx: interactions.CommandContext):
    getAIModel( ctx.guild_id, ctx.user.id ).resetMemory()
    await ctx.send(">**MEMORY RESET**")


# Help Command
@bot.command(
    name='help',
    description='Plz help me'
)
async def help(ctx: interactions.CommandContext):
    await ctx.send(content='', embeds=[helpEmbed], ephemeral=True)


# Initialise Command
initialisationTextPromptChoices = []
initialisationPromptChoices = []
for promptFile in os.listdir("./initialisationPrompts/"):
    if (promptFile.split('.')[-1] == 'txt'):
        initialisationPromptChoices.append(interactions.Choice(
            name='.'.join(promptFile.split('.')[:-1]),
            value='.'.join(promptFile.split('.')[:-1])
        ))
        initialisationTextPromptChoices.append('.'.join(promptFile.split('.')[:-1]))

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
    await ctx.defer(False)
    getAIModel( ctx.guild_id, ctx.user.id ).resetMemory()
    response = getAIModel( ctx.guild_id, ctx.user.id ).processInitialisationPrompt(prompt)
    await ctx.send(quotePrompt(prompt) + "\n\n" + response)


# Chat command
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
    await ctx.defer(False)

    response = getAIModel( ctx.guild_id, ctx.user.id ).processPrompt(prompt)
    await ctx.send(quotePrompt(prompt) + "\n\n" + response)

# History command
@bot.command(
    name='history',
    description='View Virtu\'s Memory'
)
async def viewHistory(ctx: interactions.CommandContext):
    await ctx.defer(ephemeral=True)
    responses = []
    responseIndex = 0
    responseLength = 0
    for historyItem in getAIModel( ctx.guild_id, ctx.user.id ).memory:
        if (responseLength + len(historyItem) > 2000):
            responseIndex += 1

        try:
            responses[responseIndex] += '\n' + historyItem
        except:
            responses.append('\n' + historyItem)
        responseLength += len(historyItem)

    #await ctx.send(responses[0])
    for response in responses:
        await ctx.send(response, ephemeral=True)



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
            if (message.content[1] == '$'): # Special per-channel command
                command = message.content[2:].strip().split(' ')[0]
                if (command == "help"):
                    returnedMessage = await message.reply(quotePrompt(message.content[2:].strip()) + "\n\nPlease wait...")
                    await returnedMessage.edit(content='', embeds=[helpEmbed])

                elif (command == "chat"):
                    returnedMessage = await message.reply(quotePrompt(message.content[2:].strip()) + "\n\nPlease wait...")
                    response = getAIModel( message.guild_id, message.author.id, message.channel_id, "perChannel" ).processPrompt(message.content[1:])
                    await returnedMessage.edit("> " + message.content[1:] + '\n' + response)

                elif (command == "reset"):
                    returnedMessage = await message.reply(quotePrompt(message.content[2:].strip()) + "\n\nPlease wait...")
                    response = getAIModel( message.guild_id, message.author.id, message.channel_id, "perChannel" ).resetMemory()
                    await returnedMessage.edit("> MEMORY RESET")

                elif (command == "initialise"):
                    returnedMessage = await message.reply(quotePrompt(message.content[2:].strip()) + "\n\nPlease wait...")
                    if (' '.join(message.content[2:].strip().split(' ')[1:]) in initialisationTextPromptChoices):
                        getAIModel( message.guild_id, message.author.id, message.channel_id, "perChannel" ).resetMemory()
                        response = getAIModel( message.guild_id, message.author.id, message.channel_id, "perChannel" ).processInitialisationPrompt(' '.join(message.content.replace('$$', '').strip().split(' ')[1:]))
                        await returnedMessage.edit(quotePrompt(' '.join(message.content[2:].strip().split(' ')[1:])) + '\n\n' + response)
                    else:
                        await returnedMessage.edit(quotePrompt(' '.join(message.content[2:].strip().split(' ')[1:])) + '\n\n' + "Error: No such initialisor")

                elif (command == "history"):
                    returnedMessage = await message.reply(quotePrompt(message.content[2:].strip()) + "\n\nPlease wait...")
                    responses = []
                    responseIndex = 0
                    responseLength = 0
                    for historyItem in getAIModel( message.guild_id, message.author.id, message.channel_id, "perChannel" ).memory:
                        if (responseLength + len(historyItem) > 2000):
                            responseIndex += 1

                        try:
                            responses[responseIndex] += '\n' + historyItem
                        except:
                            responses.append('\n' + historyItem)
                        responseLength += len(historyItem)

                    for response in responses:
                        await message.reply(response)

            else:
                returnedMessage = await message.reply(quotePrompt(message.content[1:]) + "\n\nPlease wait...")
                response = getAIModel( message.guild_id, message.author.id, message.channel_id, "perChannel" ).processPrompt(message.content[1:])
                await returnedMessage.edit(quotePrompt(message.content[1:]) + '\n\n' + response)
    except interactions.api.error.LibraryException as e:
        print(e)

bot.start()
print("Bot ready")