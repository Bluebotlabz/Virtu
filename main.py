import interactions.api.models.presence as presence
from models import OpenAICompletionModel as AIModel
import interactions
import json
import time
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
helpEmbedFree = interactions.Embed(
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
            name="/import",
            value="Import a ChatGPT thread into Virtu",
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
            name="/config <config option>",
            value="Configure Virtu settings and parameters",
            inline=False
        ),
        interactions.EmbedField(
            name="$ <prompt>",
            value="Prefix which can be used instead of /chat (always uses per channel memory)",
            inline=False
        ),
        interactions.EmbedField(
            name="⭐ /initialise <initialiser>",
            value="[REQUIRES VIRUT PREMIUM] Resets Virtu's memory, but then initialises it using a premade prompt",
            inline=False
        ),
        interactions.EmbedField(
            name="⭐ /retry",
            value="[REQUIRES VIRTU PREMIUM] Retry the last prompt, same a ChatGPT \"try again\" button",
            inline=False
        ),
        interactions.EmbedField(
            name="⭐ /sprudermode <prompt> <messages>",
            value="[REQUIRES VIRTU PREMIUM] Allow the AI to talk to itself via shared history, <prompt> defines its prompt and <messages> defines the number of messages",
            inline=False
        ),
        interactions.EmbedField(
            name="Note",
            value="Many / commands also have an optional memoryType parameter for you to choose which memory type to use, this can be configured via /config default_memory and is ignored for DMs",
            inline=False
        ),
        interactions.EmbedField(
            name="⭐GET VIRTU PREMIUM⭐",
            value="⭐Unlock more commands such as /sprudermode, remove all timeouts and help support the bot by using /config virtu_premium⭐",
            inline=False
        )
    ],
    footer=interactions.EmbedFooter(text="Virtu v1.0.0")
)

helpEmbedPremium = interactions.Embed(
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
            name="/import",
            value="Import a ChatGPT thread into Virtu",
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
            name="/config <config option>",
            value="Configure Virtu settings and parameters",
            inline=False
        ),
        interactions.EmbedField(
            name="$ <prompt>",
            value="Prefix which can be used instead of /chat (always uses per channel memory)",
            inline=False
        ),
        interactions.EmbedField(
            name="/initialise <initialiser>",
            value="[WARNING: CAN USE A LOT OF API QUOTA] Resets Virtu's memory, but then initialises it using a premade prompt",
            inline=False
        ),
        interactions.EmbedField(
            name="/retry",
            value="Retry the last prompt, same a ChatGPT \"try again\" button",
            inline=False
        ),
        interactions.EmbedField(
            name="/sprudermode <prompt> <messages>",
            value="[WARNING: USES A LOT OF API QUOTA] Allow the AI to talk to itself via shared history, <prompt> defines its prompt and <messages> defines the number of messages",
            inline=False
        ),
        interactions.EmbedField(
            name="Note",
            value="Many / commands also have an optional memoryType parameter for you to choose which memory type to use, this can be configured via /config default_memory and is ignored for DMs",
            inline=False
        ),
        interactions.EmbedField(
            name="THANK YOU!!!",
            value="⭐Thank you for providing your API key⭐",
            inline=False
        )
    ],
    footer=interactions.EmbedFooter(text="Virtu ⭐PREMIUM⭐ v1.0.0")
)

def quotePrompt(prompt):
    if (len(prompt) > 500):
        prompt = prompt[:497] + '...'
    quotes = []
    for line in prompt.strip().split('\n'):
        quotes.append( '> **' + line + '**' )

    return '\n'.join(quotes)

def splitMessage(text):
    """
    This function splits a message into multiple parts if it is too long.
    :param text: The text to split
    :return: An array of strings representing the split message
    """
    responses = [] # Array to store the split messages
    responseIndex = 0 # Index of the current response
    responseLength = 0 # Length of the current response

    # Iterate through each line of the message
    for line in text.strip().split('\n'):
        # If the length of the line is greater than 2000 characters, or if it is the first response and the length is greater than 1500 characters, move to the next response
        if (responseLength + len(line) >= 2000 or (line == text.strip().split('\n')[0] and responseLength + len(line) >= 1500)):
            responseIndex += 1

        # If the line is longer than 2000 characters, split it into multiple lines
        while len(line) > 2000:
            # If the response index is within the range of the responses array, add the line to the existing response
            if responseIndex < len(responses):
                responses[responseIndex] += '\n' + line[:2000]
            # Otherwise, create a new response
            else:
                if (line != '' and line.strip() != ''):
                    responses.append('\n' + line[:2000])
            line = line[2000:]
            responseLength = 0

        # If the response index is within the range of the responses array, add the line to the existing response
        if responseIndex < len(responses):
            responses[responseIndex] += '\n' + line
        # Otherwise, create a new response
        else:
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
    if (PerUserSettings.setdefault(ctx.user.id, defaultUserSettings)["premiumMode"]):
        await ctx.send(content='', embeds=[helpEmbedPremium], ephemeral=True)
    else:
        await ctx.send(content='', embeds=[helpEmbedFree], ephemeral=True)

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
    if (not getAIModel( ctx.guild_id, ctx.user.id, ctx.channel_id, memoryType ).premiumMode):
        await ctx.send("You must have Virtu Premium to use this command\nVirtu premium removes timeouts, allows access to extra commands and more!\n\nGet it via `/config virtu_premium`")
        return

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
    if (not getAIModel( ctx.guild_id, ctx.user.id, ctx.channel_id, memoryType ).premiumMode):
        await ctx.send("You must have Virtu Premium to use this command\nVirtu premium removes timeouts, allows access to extra commands and more!\n\nGet it via `/config virtu_premium`")
        return

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

# Try-again command
@bot.command(
    name='retry',
    description='Regenerate the last prompt',
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
async def redoPrompt(ctx: interactions.CommandContext, memoryType='default'):
    if (not getAIModel( ctx.guild_id, ctx.user.id, ctx.channel_id, memoryType ).premiumMode):
        await ctx.send("You must have Virtu Premium to use this command\nVirtu premium removes timeouts, allows access to extra commands and more!\n\nGet it via `/config virtu_premium`")
        return

    await ctx.defer(ephemeral=True)

    lastPrompt = getAIModel( ctx.guild_id, ctx.user.id, ctx.channel_id, memoryType ).memory[-2]
    getAIModel( ctx.guild_id, ctx.user.id, ctx.channel_id, memoryType ).memory = getAIModel( ctx.guild_id, ctx.user.id, ctx.channel_id, memoryType ).memory[:-2]
    
    response = getAIModel( ctx.guild_id, ctx.user.id, ctx.channel_id, memoryType ).processPrompt(lastPrompt)

    responses = splitMessage(response)
    await ctx.send(quotePrompt(lastPrompt) + "\n\n" + responses[0])
    channel = await ctx.get_channel()
    for response in responses[1:]:
        channel.send(response)

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
            custom_id="virtu.memory.import.importJSONButton:" + memoryType,
            label="Import JSON History"
        )
    ]
    jsCommand = 'var conversationElements=document.querySelector(".flex.flex-col.items-center.text-sm.h-full").children,convo=[];for(const conversationElement of conversationElements)if(conversationElement.children.length>0){var e=conversationElement.children[0].children[conversationElement.children[0].children.length-1].children[0].children[0];e.children.length>0?convo.push(e.children[0].children[0].innerHTML):convo.push(e.innerHTML)}console.log("Paste the following into Virtu:"),console.log(JSON.stringify(convo));'
    await ctx.send("Use the following command in the JS console to extract chatGPT code:\n`" + jsCommand + "`\n\nThen press the button below:", components=components)

### START IMPORT
@bot.component("virtu.memory.import.importJSONButton:perChannel")
@bot.component("virtu.memory.import.importJSONButton:perUser")
@bot.component("virtu.memory.import.importJSONButton:default")
async def memoryImportJSONButton(ctx):
    modal = interactions.Modal(
        title="Import Memory",
        custom_id="virtu.memory.import.importJSONmodal:" + ctx.data.custom_id.split(':')[-1],
        components=[
            interactions.TextInput(
                style=interactions.TextStyleType.SHORT,
                custom_id="virtu.memory.import.importJSONModal.JSONText",
                label="Memory JSON",
                placeholder="Memory JSON",
                required=True
            )
        ]
    )

    await ctx.popup(modal)

@bot.modal("virtu.memory.import.importJSONmodal:perChannel")
@bot.modal("virtu.memory.import.importJSONmodal:perMemory")
@bot.modal("virtu.memory.import.importJSONmodal:default")
async def memoryImportJSONModal(ctx, memoryJSON):
    try:
        response = getAIModel( ctx.guild_id, ctx.user.id, ctx.channel_id, ctx.data.custom_id.split(':')[-1] ).importMemory(json.loads(memoryJSON))
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
        interactions.Option(name='virtu_premium', description="⭐VIRTU PREMIUM⭐", type=interactions.OptionType.SUB_COMMAND),
        interactions.Option(name='default_memory', description="Configure Default Memory Used For / Commands", type=interactions.OptionType.SUB_COMMAND),
        interactions.Option(name='wipe_data', description="Wipe All Virtu Data", type=interactions.OptionType.SUB_COMMAND),
        interactions.Option(name='ai_model', description="Change Virtu's AI Model", type=interactions.OptionType.SUB_COMMAND, options=[interactions.Option(name="memory_type",converter="memorytype",description="Which memory/chat history should this command affect?",type=interactions.OptionType.STRING,required=False,choices=[interactions.Choice(name='Per-Channel History', value='perChannel'),interactions.Choice(name='Per-User History', value='perUser')] )]),
        interactions.Option(name='ai_parameters', description="Adjust Virtu's AI Model Parameters", type=interactions.OptionType.SUB_COMMAND, options=[interactions.Option(name="memory_type",converter="memorytype",description="Which memory/chat history should this command affect?",type=interactions.OptionType.STRING,required=False,choices=[interactions.Choice(name='Per-Channel History', value='perChannel'),interactions.Choice(name='Per-User History', value='perUser')] )]),
        interactions.Option(name='reset_ai_parameters', description="Reset Virtu's AI Model Parameters", type=interactions.OptionType.SUB_COMMAND, options=[interactions.Option(name="memory_type",converter="memorytype",description="Which memory/chat history should this command affect?",type=interactions.OptionType.STRING,required=False,choices=[interactions.Choice(name='Per-Channel History', value='perChannel'),interactions.Choice(name='Per-User History', value='perUser')] )]),
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
            await ctx.send('__Virtu Premium__\nClick on the button and enter your API key to enable Virtu Premium\n\nYou can generate an API Key (also known as a "secret key") here: https://beta.openai.com/account/api-keys', components=components)
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
            "text-davinci-003": "text-davinci-003:" + memorytype,
            "text-davinci-002": "text-davinci-002:" + memorytype,
            "text-davinci-001": "text-davinci-001:" + memorytype,
            "cushman-codex": "code-cushman-001:" + memorytype,
            "davinci-codex": "code-davinci-002:" + memorytype,
            "Base GPT-3 Babbage": "babbage:" + memorytype,
            "Base GPT-3 Curie": "curie:" + memorytype,
            "Base GPT-3 Ada": "ada:" + memorytype,
            "Base GPT-3 DaVinci": "davinci:" + memorytype
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
    elif (sub_command == "ai_parameters"):
        configOptions = getAIModel( ctx.guild_id, ctx.user.id, ctx.channel_id, memorytype ).config
        components = []
        for configOption in configOptions.keys():
            if (not configOption in ["engine", "useMemory"]):
                components.append(interactions.Button(style=interactions.ButtonStyle.PRIMARY, label=configOption, custom_id="virtu.config.aiParameters.parameter:" + configOption + ":" + memorytype))

        await ctx.send("__AI Parameters__\nClick on a button to change any of the AI Model's parameters", components=components)
    elif (sub_command == "reset_ai_parameters"):
        components = [
            interactions.Button(
                style=interactions.ButtonStyle.DANGER,
                custom_id="virtu.config.aiParameters.resetParameters:" + memorytype,
                label="RESET AI PARAMETERS"
            )
        ]
        await ctx.send('__RESET AI PARAMETERS__\nResets your AI Model\'s parameters\n**__THIS CANNOT BE UNDONE__**', components=components)

### START AI PARAMETERS
@bot.component("virtu.config.aiParameters.parameter:temperature:default")
@bot.component("virtu.config.aiParameters.parameter:max_tokens:default")
@bot.component("virtu.config.aiParameters.parameter:top_p:default")
@bot.component("virtu.config.aiParameters.parameter:frequency_penalty:default")
@bot.component("virtu.config.aiParameters.parameter:presence_penalty:default")
@bot.component("virtu.config.aiParameters.parameter:temperature:perChannel")
@bot.component("virtu.config.aiParameters.parameter:max_tokens:perChannel")
@bot.component("virtu.config.aiParameters.parameter:top_p:perChannel")
@bot.component("virtu.config.aiParameters.parameter:frequency_penalty:perChannel")
@bot.component("virtu.config.aiParameters.parameter:presence_penalty:perChannel")
@bot.component("virtu.config.aiParameters.parameter:temperature:perUser")
@bot.component("virtu.config.aiParameters.parameter:max_tokens:perUser")
@bot.component("virtu.config.aiParameters.parameter:top_p:perUser")
@bot.component("virtu.config.aiParameters.parameter:frequency_penalty:perUser")
@bot.component("virtu.config.aiParameters.parameter:presence_penalty:perUser")
async def handleAIParameterChange(ctx):
    parameterToChange = ctx.data.custom_id.split(':')[-2]
    memoryType = ctx.data.custom_id.split(':')[-1]

    modal = interactions.Modal(
        title="Change " + parameterToChange,
        custom_id="virtu.config.aiParameters.parameter.modal:" + parameterToChange + ":" + memoryType,
        components=[
            interactions.TextInput(style=interactions.TextStyleType.SHORT, label=parameterToChange, custom_id="virtu.config.aiParameters.parameter.textInput", required=True)
        ]
    )

    await ctx.popup(modal)

@bot.modal("virtu.config.aiParameters.parameter.modal:temperature:default")
@bot.modal("virtu.config.aiParameters.parameter.modal:max_tokens:default")
@bot.modal("virtu.config.aiParameters.parameter.modal:top_p:default")
@bot.modal("virtu.config.aiParameters.parameter.modal:frequency_penalty:default")
@bot.modal("virtu.config.aiParameters.parameter.modal:presence_penalty:default")
@bot.modal("virtu.config.aiParameters.parameter.modal:temperature:perChannel")
@bot.modal("virtu.config.aiParameters.parameter.modal:max_tokens:perChannel")
@bot.modal("virtu.config.aiParameters.parameter.modal:top_p:perChannel")
@bot.modal("virtu.config.aiParameters.parameter.modal:frequency_penalty:perChannel")
@bot.modal("virtu.config.aiParameters.parameter.modal:presence_penalty:perChannel")
@bot.modal("virtu.config.aiParameters.parameter.modal:temperature:perUser")
@bot.modal("virtu.config.aiParameters.parameter.modal:max_tokens:perUser")
@bot.modal("virtu.config.aiParameters.parameter.modal:top_p:perUser")
@bot.modal("virtu.config.aiParameters.parameter.modal:frequency_penalty:perUser")
@bot.modal("virtu.config.aiParameters.parameter.modal:presence_penalty:perUser")
async def handleAIParameterModalResponse(ctx, parameterResult):
    parameterToChange = ctx.data.custom_id.split(':')[-2]
    memoryType = ctx.data.custom_id.split(':')[-1]
    
    inputTypes = {
        "temperature": (0, 1, 'float'),
        "top_p": (0, 1, 'float'),
        "frequency_penalty": (-2, 2, 'float'),
        "presence_penalty": (-2, 2, 'float')
    }

    if (inputTypes[parameterToChange][-1] == 'float'):
        try:
            if (float(parameterResult) >= inputTypes[parameterToChange][0] and int(parameterResult) <= inputTypes[parameterToChange][1]):
                getAIModel( ctx.guild_id, ctx.user.id, ctx.channel_id, memoryType ).config[parameterToChange] = float(parameterResult)
                response = "[" + parameterToChange + "] successfuly set to [" + parameterResult + "]"
            else:
                response = "Error, invalid value, value must be a float between [" + str(inputTypes[parameterToChange][0]) + "] and [" + str(inputTypes[parameterToChange][1]) + "]\n`Did you even read the docs?`"
        except:
            response = "Error, invalid value, value must be a float between [" + str(inputTypes[parameterToChange][0]) + "] and [" + str(inputTypes[parameterToChange][1]) + "]\n`Did you even read the docs?`"

    await ctx.send(response, ephemeral=True)

### END AI PARAMETERS

### START WIPE AI PARAMETERS
@bot.component("virtu.config.aiParameters.resetParameters:default")
@bot.component("virtu.config.aiParameters.resetParameters:perUser")
@bot.component("virtu.config.aiParameters.resetParameters:perChannel")
async def wipeUserData(ctx):
    memoryType = ctx.data.custom_id.split(':')[-1]
    getAIModel( ctx.guild_id, ctx.user.id, ctx.channel_id, memoryType ).config = getAIModel( ctx.guild_id, ctx.user.id, ctx.channel_id, memoryType ).defaultConfig
    await ctx.send("All AI Model Parameter Settings have been wiped\n`what did you do now?`", ephemeral=True)
### END WIPE AI PARAMETERS

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
                placeholder="API Key",
                required=True
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
        getAIModel( ctx.guild_id, ctx.user.id, ctx.channel_id, 'default' ).timeout = time.time()
        getAIModel( ctx.guild_id, ctx.user.id, ctx.channel_id, 'perUser' ).timeout = time.time()
        getAIModel( ctx.guild_id, ctx.user.id, ctx.channel_id, 'perChannel' ).timeout = time.time()
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
    getAIModel( ctx.guild_id, ctx.user.id, ctx.channel_id, modelSelection[0].split(':')[-1] ).config["engine"] = modelSelection[0].split(':')[0]
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
            if (len(message.content) > 1 and message.content[1] == '$'):
                message.reply("You are trying to use a legacy per-channel command, this has been replaced by an optional argument in / commands, see `/help` for more info")
            else:
                returnedMessage = await message.reply(quotePrompt(message.content[1:]) + "\n\nPlease wait...")
                responses = splitMessage(getAIModel( guildID, message.author.id, channel.id, "perChannel" ).processPrompt(message.content[1:]))

                await returnedMessage.edit(quotePrompt(message.content[1:]) + '\n\n' + responses[0])
                for response in responses[1:]:
                    channel.send(response)
    except interactions.api.error.LibraryException as e:
        print(e)

bot.start()
print("Bot ready")