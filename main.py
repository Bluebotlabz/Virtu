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


# Initialize AI model and Discord Bot
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
    description="Resets Virtu's memory",
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
                value="Chat with me, I will respond to your prompts and try to answer questions",
                inline=False
            ),
            interactions.EmbedField(
                name="/reset",
                value="Resets my memory, who did you say you were again?",
                inline=False
            ),
            interactions.EmbedField(
                name="$ <prompt>",
                value="Prefix which can be used instead of /chat",
                inline=False
            )
        ],
        footer=interactions.api.models.message.EmbedFooter(text="Virtu v0.0.1-BETA")
    )
    await ctx.send(embeds=[helpEmbed], ephemeral=True)

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
    #print("Prompt recieved: " + prompt)
    response = aiModel.processPrompt(prompt)
    await ctx.send("> " + prompt + "\n" + response)



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
        await channel.get_message(message.id) # This return value isn't even being used but it fixes things???

        if (message.content[0] == '$'):
            #print("Prompt recieved: " + message.content[1:])
            response = aiModel.processPrompt(message.content[1:])
            await message.reply("> " + message.content[1:] + '\n' + response)
    except interactions.api.error.LibraryException:
        pass

bot.start()
print("Bot ready")