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

# Global, per-user settings (such as premium mode)
PerUserSettings = {}
defaultUserSettings = {"premiumMode": False, "apiKey": secrets["openai_api_key"], "defaultMemory": "perUser"}

# AI Models
PerUserAIModels = {}
PerChannelAIModels = {}
PerDMAIModels = {}

def getAIModel(guildID, userID, channelID=None, memoryType="perUser"):
    if (guildID != None):
        if (memoryType == "default"):
            memoryType = PerUserSettings.setdefault(userID, defaultUserSettings)["defaultMemory"]

        if (memoryType == "perChannel"): # Shared per channel (also works)
            aiModel = PerChannelAIModels.setdefault(guildID, {}).setdefault(channelID, AIModel(secrets["openai_api_key"]))
            aiModel.premiumMode = PerUserSettings.setdefault(userID, defaultUserSettings)["premiumMode"]
            aiModel.apiKey = PerUserSettings.setdefault(userID, defaultUserSettings)["apiKey"]
        elif (memoryType == "perUser"): # Per user, but on server
            aiModel = PerUserAIModels.setdefault(guildID, {}).setdefault(userID, AIModel(secrets["openai_api_key"]))
            aiModel.premiumMode = PerUserSettings.setdefault(userID, defaultUserSettings)["premiumMode"]
            aiModel.apiKey = PerUserSettings.setdefault(userID, defaultUserSettings)["apiKey"]
    else:
        aiModel = PerDMAIModels.setdefault(userID, AIModel(secrets["openai_api_key"]))
        aiModel.premiumMode = PerUserSettings.setdefault(userID, defaultUserSettings)["premiumMode"]
        aiModel.apiKey = PerUserSettings.setdefault(userID, defaultUserSettings)["apiKey"]

    return aiModel

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
    if (len(prompt) > 500):
        prompt = prompt[:497] + '...'
    quotes = []
    for line in prompt.strip().split('\n'):
        quotes.append( '> **' + line + '**' )

    return '\n'.join(quotes)

def splitMessage(text):
    responses = []
    responseIndex = 0
    responseLength = 0

    for line in text.strip().split('\n'):
        if (responseLength + len(line) > 2000 or (line == text.strip().split('\n')[0] and responseLength + len(line) > 1500)):
            responseIndex += 1

        try:
            responses[responseIndex] += '\n' + line
        except:
            if (line != '' and line.strip() != ''):
                responses.append('\n' + line)
        responseLength += len(line)
    
    return responses

# REGISTER COMMANDS #
# Reset command
@bot.command(
    name='reset',
    description="Reset Virtu's memory",
    options=[
        interactions.Option(
            name="memory-type",
            converter="memoryType",
            description="Which memory/chat history should this command affect?",
            type=interactions.OptionType.STRING,
            required=False,
            choices=[
                interactions.Choice(name='Per-Channel History', value='perChannel'),
                interactions.Choice(name='Per-User History', value='perUser')
            ]
        )
    ]
)
async def resetMemory(ctx: interactions.CommandContext, memoryType='default'):
    getAIModel( ctx.guild_id, ctx.user.id, ctx.channel_id, memoryType ).resetMemory()
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
        ),
        interactions.Option(
            name="memory-type",
            converter="memoryType",
            description="Which memory/chat history should this command affect?",
            type=interactions.OptionType.STRING,
            required=False,
            choices=[
                interactions.Choice(name='Per-Channel History', value='perChannel'),
                interactions.Choice(name='Per-User History', value='perUser')
            ]
        )
    ]
)
async def initialise(ctx: interactions.CommandContext, prompt, memoryType='default'):
    await ctx.defer(False)
    getAIModel( ctx.guild_id, ctx.user.id, ctx.channel_id, memoryType ).resetMemory()
    response = getAIModel( ctx.guild_id, ctx.user.id, ctx.channel_id, memoryType ).processInitialisationPrompt(prompt)

    responses = splitMessage(response)
    await ctx.send(quotePrompt(prompt) + "\n\n" + responses[0])
    for response in responses[1:]:
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
        interactions.Option(
            name="memory-type",
            converter="memoryType",
            description="Which memory/chat history should this command affect?",
            type=interactions.OptionType.STRING,
            required=False,
            choices=[
                interactions.Choice(name='Per-Channel History', value='perChannel'),
                interactions.Choice(name='Per-User History', value='perUser')
            ]
        )
    ],
)
async def chat(ctx: interactions.CommandContext, prompt, memoryType='default'):
    await ctx.defer(False)

    response = getAIModel( ctx.guild_id, ctx.user.id, ctx.channel_id, memoryType ).processPrompt(prompt)

    responses = splitMessage(response)
    await ctx.send(quotePrompt(prompt) + "\n\n" + responses[0])
    channel = await ctx.get_channel()
    for response in responses[1:]:
        channel.send(response)

# Bruh command
@bot.command(
    name='sprudermode',
    description='Can you please not?',
    options=[
        interactions.Option(
            name="prompt",
            description="What do you want to break Virtu with?",
            type=interactions.OptionType.STRING,
            required=True
        ),
        interactions.Option(
            name="messages",
            description="How many messages should this go on for?",
            type=interactions.OptionType.INTEGER,
            required=True
        ),
        interactions.Option(
            name="memory-type",
            converter="memoryType",
            description="Which memory/chat history should this command affect?",
            type=interactions.OptionType.STRING,
            required=False,
            choices=[
                interactions.Choice(name='Per-Channel History', value='perChannel'),
                interactions.Choice(name='Per-User History', value='perUser')
            ]
        )
    ],
)
async def spruderMode(ctx: interactions.CommandContext, prompt, messages, memoryType='default'):
    # Can you please not?

    # Loading message
    await ctx.defer(False)

    # Message to reply to
    replyMessage = None

    # Loop messages
    for i in range(messages):
        # Use AI
        response = getAIModel( ctx.guild_id, ctx.user.id, ctx.channel_id, memoryType ).processPrompt(prompt)
        responses = splitMessage(response) # Discord msg limit

        if (replyMessage == None): # Send first message
            await ctx.send(quotePrompt(prompt) + "\n\n" + responses[0])
        else:
            replyMessage = await replyMessage.reply(quotePrompt(prompt) + "\n\n" + responses[0]) # Otherwise, reply to last message

        for response in responses[1:]: # Actually for the message length limit stuff
            if (replyMessage == None):
                await ctx.send(response)
            else:
                replyMessage = await replyMessage.reply(response)

        prompt = response

# History command
@bot.command(
    name='history',
    description='View Virtu\'s Memory',
    options=[
        interactions.Option(
            name="memory-type",
            converter="memoryType",
            description="Which memory/chat history should this command affect?",
            type=interactions.OptionType.STRING,
            required=False,
            choices=[
                interactions.Choice(name='Per-Channel History', value='perChannel'),
                interactions.Choice(name='Per-User History', value='perUser')
            ]
        )
    ]
)
async def viewHistory(ctx: interactions.CommandContext, memoryType='default'):
    await ctx.defer(ephemeral=True)
    response = ''
    for historyItem in getAIModel( ctx.guild_id, ctx.user.id, ctx.channel_id, memoryType ).memory:
        response += '\n' + historyItem
    
    responses = splitMessage(response)
        

    #await ctx.send(responses[0])
    for response in responses:
            await ctx.send(response, ephemeral=True)

# Chat import command
@bot.command(
    name='import',
    description='Import ChatGPT conversation into Virtu',
    options=[
        interactions.Option(
            name="memory-type",
            converter="memoryType",
            description="Which memory/chat history should this command affect?",
            type=interactions.OptionType.STRING,
            required=False,
            choices=[
                interactions.Choice(name='Per-Channel History', value='perChannel'),
                interactions.Choice(name='Per-User History', value='perUser')
            ]
        )
    ]
)
async def importHistory(ctx: interactions.CommandContext, jsonChat=None, memoryType='default'):
    #if (jsonChat and jsonChat.strip() != ''):
    #    await ctx.deferred(ephemeral=True)
    #    response = getAIModel( ctx.guild_id, ctx.user.id, ctx.channel_id, memoryType ).importMemory(json.loads(jsCommand))
    #    await ctx.send(response)
    #else:
    components = [
        interactions.Button(
            style=interactions.ButtonStyle.PRIMARY,
            custom_id="virtu.memory.import.importJSONButton." + memoryType,
            label="Import JSON History"
        )
    ]
    jsCommand = 'var conversationElements=document.querySelector(".flex.flex-col.items-center.text-sm.h-full").children,convo=[];for(const conversationElement of conversationElements)if(conversationElement.children.length>0){var e=conversationElement.children[0].children[conversationElement.children[0].children.length-1].children[0].children[0];e.children.length>0?convo.push(e.children[0].children[0].innerHTML):convo.push(e.innerHTML)}console.log("Paste the following into Virtu:"),console.log(JSON.stringify(convo));'
    await ctx.send("Use the following command in the JS console to extract chatGPT code:\n`" + jsCommand + "`\n\nThen press the button below:", components=components)

### START IMPORT
@bot.component("virtu.memory.import.importJSONButton.default")
async def memoryImportJSONButton(ctx):
    modal = interactions.Modal(
        title="Import Memory",
        custom_id="virtu.memory.import.importJSONmodal.default",
        components=[
            interactions.TextInput(
                style=interactions.TextStyleType.SHORT,
                custom_id="virtu.memory.import.importJSONModal.JSONText",
                label="Memory JSON",
                placeholder="Memory JSON"
            )
        ]
    )

    await ctx.popup(modal)

@bot.component("virtu.memory.import.importJSONButton.perUser")
async def memoryImportJSONButton(ctx):
    modal = interactions.Modal(
        title="Import Memory",
        custom_id="virtu.memory.import.importJSONmodal.perUser",
        components=[
            interactions.TextInput(
                style=interactions.TextStyleType.SHORT,
                custom_id="virtu.memory.import.importJSONModal.JSONText",
                label="Memory JSON",
                placeholder="Memory JSON"
            )
        ]
    )

    await ctx.popup(modal)

@bot.component("virtu.memory.import.importJSONButton.perChannel")
async def memoryImportJSONButton(ctx):
    modal = interactions.Modal(
        title="Import Memory",
        custom_id="virtu.memory.import.importJSONmodal.perChannel",
        components=[
            interactions.TextInput(
                style=interactions.TextStyleType.SHORT,
                custom_id="virtu.memory.import.importJSONModal.JSONText",
                label="Memory JSON",
                placeholder="Memory JSON"
            )
        ]
    )

    await ctx.popup(modal)

@bot.modal("virtu.memory.import.importJSONmodal.default")
async def memoryImportJSONModal(ctx, memoryJSON):
    try:
        response = getAIModel( ctx.guild_id, ctx.user.id, ctx.channel_id, "default" ).importMemory(json.loads(memoryJSON))
    except Exception as e:
        response = "Error Importing Chat: " + str(e)

    await ctx.send(response)

@bot.modal("virtu.memory.import.importJSONmodal.perChannel")
async def memoryImportJSONModal(ctx, memoryJSON):
    try:
        response = getAIModel( ctx.guild_id, ctx.user.id, ctx.channel_id, "perChannel" ).importMemory(json.loads(memoryJSON))
    except Exception as e:
        response = "Error Importing Chat: " + str(e)

    await ctx.send(response)

@bot.modal("virtu.memory.import.importJSONmodal.perMemory")
async def memoryImportJSONModal(ctx, memoryJSON):
    try:
        response = getAIModel( ctx.guild_id, ctx.user.id, ctx.channel_id, "perMemory" ).importMemory(json.loads(memoryJSON))
    except Exception as e:
        response = "Error Importing Chat: " + str(e)

    await ctx.send(response)
### END IMPORT
    
### Config stuff
# Config command
@bot.command(
    name='config',
    description='Change Virtu Settings',
    options=[
        interactions.Option(name='virtu_premium', description="virtu_premium", type=interactions.OptionType.SUB_COMMAND),
        interactions.Option(name='default_memory', description="default_memory", type=interactions.OptionType.SUB_COMMAND),
        interactions.Option(name='wipe_data', description="wipe_data", type=interactions.OptionType.SUB_COMMAND),
        interactions.Option(name='ai_model', description="ai_model", type=interactions.OptionType.SUB_COMMAND, options=[interactions.Option(name="memory_type",converter="memorytype",description="Which memory/chat history should this command affect?",type=interactions.OptionType.STRING,required=False,choices=[interactions.Choice(name='Per-Channel History', value='perChannel'),interactions.Choice(name='Per-User History', value='perUser')] )]),
        interactions.Option(name='ai_parameters', description="ai_parameters", type=interactions.OptionType.SUB_COMMAND, options=[interactions.Option(name="memory_type",converter="memorytype",description="Which memory/chat history should this command affect?",type=interactions.OptionType.STRING,required=False,choices=[interactions.Choice(name='Per-Channel History', value='perChannel'),interactions.Choice(name='Per-User History', value='perUser')] )]),
    ]
)
async def configCommand(ctx: interactions.CommandContext, sub_command, memorytype="default"):
    if (sub_command == "virtu_premium"):
        if (PerUserSettings.setdefault(ctx.user.id, defaultUserSettings)["premiumMode"]):
            components = [
                interactions.Button(
                    style=interactions.ButtonStyle.PRIMARY,
                    custom_id="virtu.config.premium.openModal",
                    label="Update Your API Key"
                ),
                interactions.Button(
                    style=interactions.ButtonStyle.SECONDARY,
                    custom_id="virtu.config.premium.removePremium",
                    label="Remove Virtu Premium"
                )
            ]
            await ctx.send('__Virtu Premium__\nYou already have Virtu Premium, you can remove it or update your API Key', components=components)
        else:
            components = [
                interactions.Button(
                    style=interactions.ButtonStyle.PRIMARY,
                    custom_id="virtu.config.premium.openModal",
                    label="Enter API Key"
                )
            ]
            await ctx.send('__Virtu Premium__\nClick on the button and enter your API key to enable Virtu Premium', components=components)
    elif (sub_command == "default_memory"):
        components = [
            interactions.SelectMenu(
                custom_id="virtu.config.memory.default",
                options=[
                    interactions.SelectOption(label='Per-Channel History', value='perChannel'),
                    interactions.SelectOption(label='Per-User History', value='perUser')
                ],
                min_values=1,
                max_values=1
            )
        ]
        await ctx.send('__Default Memory__\nHow would you like your conversations to be saved by default?\n`(this can be manually overriden via / command arguments)`', components=components)
    elif (sub_command == "wipe_data"):
        components = [
            interactions.Button(
                style=interactions.ButtonStyle.DANGER,
                custom_id="virtu.config.wipe.wipeDataButton",
                label="WIPE DATA"
            )
        ]
        await ctx.send('__WIPE DATA__\nWipe All Your Conversation Histories, Settings And All User Data\n**__THIS CANNOT BE UNDONE__**', components=components)
    elif (sub_command == "ai_model"):
        availableModels = {
            "text-davinci-003": "text-davinci-003;" + memorytype,
            "text-davinci-002": "text-davinci-002;" + memorytype,
            "text-davinci-001": "text-davinci-001;" + memorytype,
            "cushman-codex": "code-cushman-001;" + memorytype,
            "davinci-codex": "code-davinci-002;" + memorytype,
            "Base GPT-3 Babbage": "babbage;" + memorytype,
            "Base GPT-3 Curie": "curie;" + memorytype,
            "Base GPT-3 Ada": "ada;" + memorytype,
            "Base GPT-3 DaVinci": "davinci;" + memorytype
        }

        modelOptions = []
        for modelName in list(availableModels.keys()):
            modelOptions.append(interactions.SelectOption(label=modelName, value=availableModels[modelName]))

        components = [
            interactions.SelectMenu(
                custom_id="virtu.config.aimodel",
                options=modelOptions,
                min_values=1,
                max_values=1
            )
        ]
        await ctx.send('__AI Model__\nWhich OpenAI model do you want Virtu to use?\nMore info: https://beta.openai.com/docs/models/overview\n`Default: text-davinci-003`', components=components)

### START VIRTU PREMIUM
@bot.component("virtu.config.premium.openModal")
async def premiumModeModalButton(ctx):
    modal = interactions.Modal(
        title="Virtu Premium",
        custom_id="virtu.config.premium.apiModal",
        components=[
            interactions.TextInput(
                style=interactions.TextStyleType.SHORT,
                custom_id="virtu.config.premium.apiModal.apiKey",
                label="API Key",
                placeholder="API Key"
            )
        ]
    )

    await ctx.popup(modal)

@bot.component("virtu.config.premium.removePremium")
async def premiumModeModalButton(ctx):
    PerUserSettings.setdefault(ctx.user.id, defaultUserSettings)["premiumMode"] = False
    PerUserSettings.setdefault(ctx.user.id, defaultUserSettings)["apiKey"] = secrets["openai_api_key"]
    await ctx.send("Premium Mode Disabled :(", ephemeral=True)

@bot.modal("virtu.config.premium.apiModal")
async def virtuPremiumModalResponse(ctx, premiumModeAPIKey):
    if (getAIModel( ctx.guild_id, ctx.user.id, ctx.channel_id, 'default' ).enablePremiumMode(premiumModeAPIKey)):
        PerUserSettings.setdefault(ctx.user.id, defaultUserSettings)["premiumMode"] = True
        PerUserSettings.setdefault(ctx.user.id, defaultUserSettings)["apiKey"] = premiumModeAPIKey
        await ctx.send("Premium Mode Enabled!!!", ephemeral=True)
    else:
        await ctx.send("Invalid API Key Detected\n`you trying to pull something here?`", ephemeral=True)
### END VIRTU PREMIUM

### START DEFAULT MEMORY
@bot.component("virtu.config.memory.default")
async def setDefaultMemory(ctx, defaultMemory):
    PerUserSettings[ctx.user.id] = defaultUserSettings
    await ctx.send("Default Memory Set To: [" + str(defaultMemory[0]) + "]", ephemeral=True)
### END DEFAULT MEMORY

### START WIPE DATA
@bot.component("virtu.config.wipe.wipeDataButton")
async def wipeUserData(ctx):
    PerUserSettings[ctx.user.id] = defaultUserSettings
    PerDMAIModels[ctx.user.id] = AIModel(secrets["openai_api_key"])
    PerUserAIModels.setdefault(ctx.guild_id, {})[ctx.user.id] = AIModel(secrets["openai_api_key"])
    await ctx.send("All Data Has Been Wiped\n`what did you do?`", ephemeral=True)
### END WIPE DATA

### START AI MODEL
@bot.component("virtu.config.aimodel")
async def changeAIModel(ctx, modelSelection):
    getAIModel( ctx.guild_id, ctx.user.id, ctx.channel_id, modelSelection[0].split(';')[1] ).config["engine"] = modelSelection[0].split(';')[0]
    await ctx.send("AI Model Updated")
### END AI MODEL



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

        try:
            guild = await message.get_guild()
            guildID = guild.id
        except:
            guildID = None
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

                    responses = splitMessage(response)
                    await returnedMessage.edit("> " + message.content[1:] + '\n' + responses[0])
                    for response in responses[1:]:
                        channel = await message.get_channel()
                        await channel.send(response)

                elif (command == "reset"):
                    returnedMessage = await message.reply(quotePrompt(message.content[2:].strip()) + "\n\nPlease wait...")
                    response = getAIModel( message.guild_id, message.author.id, message.channel_id, "perChannel" ).resetMemory()
                    await returnedMessage.edit("> MEMORY RESET")

                elif (command == "initialise"):
                    returnedMessage = await message.reply(quotePrompt(message.content[2:].strip()) + "\n\nPlease wait...")
                    if (' '.join(message.content[2:].strip().split(' ')[1:]) in initialisationTextPromptChoices):
                        getAIModel( message.guild_id, message.author.id, message.channel_id, "perChannel" ).resetMemory()
                        response = getAIModel( message.guild_id, message.author.id, message.channel_id, "perChannel" ).processInitialisationPrompt(' '.join(message.content.replace('$$', '').strip().split(' ')[1:]))
                        responses = splitMessage(response)

                        await returnedMessage.edit(quotePrompt(' '.join(message.content[2:].strip().split(' ')[1:])) + '\n\n' + responses[0])
                        for response in responses[1:]:
                            channel = await message.get_channel()
                            await channel.send(response)
                    else:
                        await returnedMessage.edit(quotePrompt(' '.join(message.content[2:].strip().split(' ')[1:])) + '\n\n' + "Error: No such initialisor")

                elif (command == "history"):
                    returnedMessage = await message.reply(quotePrompt(message.content[2:].strip()) + "\n\nPlease wait...")
                    response = ''
                    for historyItem in getAIModel( message.guild_id, message.author.id, message.channel_id, "perChannel" ).memory:
                        response += '\n' + historyItem

                    responses = splitMessage(response)
                    await returnedMessage.edit(responses[0])
                    for response in responses[1:]:
                        channel = await message.get_channel()
                        await channel.send(response)

            else:
                returnedMessage = await message.reply(quotePrompt(message.content[1:]) + "\n\nPlease wait...")
                response = getAIModel( guildID, message.author.id, channel.id, "perChannel" ).processPrompt(message.content[1:])
                await returnedMessage.edit(quotePrompt(message.content[1:]) + '\n\n' + response)
    except interactions.api.error.LibraryException as e:
        print(e)

bot.start()
print("Bot ready")