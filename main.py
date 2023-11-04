import discord
import openai
from dotenv import load_dotenv
import os

load_dotenv()

DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
DISCORD_RULES= os.getenv("DISCORD_RULES")

if DISCORD_RULES is None:
    raise ValueError('DISCORD_RULES environment variable is not set')

if OPENAI_API_KEY is None:
    raise ValueError('OPENAI_API_KEY environment variable is not set')

if DISCORD_TOKEN is None:
    raise ValueError('DISCORD_TOKEN environment variable is not set')


# Initialize the Discord client
client = discord.Client(command_prefix='?', intents=discord.Intents.all())

chat_messages=[
            {"role": "system", "content": "You are a helpful assistant who loves discord. You have knowledge of the rules and can provide insight to them for those who ask. You love to use cringey gamer lingo and love talking about twitch streamers. The rules are: " + DISCORD_RULES}
        ]

@client.event
async def on_ready():
    print(f'Logged in as {client.user.name}')

@client.event
async def on_message(message):
    # If the bot is mentioned, respond with a message
    if message.content.startswith('<@1166184122209816606>'):
        response = chatWithAdminGPT(message.content)
        await message.channel.send(response)
        print(chat_messages)
        return
    elif message.author == client.user:
        return

    # Check if the message content follows the defined server rules
    response = check_server_rules(message.content)

    print(message.content)

    # Respond based on whether the message follows server rules
    if ("PASSED" not in response.upper()):
        await message.channel.send(response)
        

def chatWithAdminGPT(message) :
    try:
        openai.api_key = OPENAI_API_KEY
        chat_messages.append({"role": "user", "content": message})
        completion = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=chat_messages
        )

        result = completion.choices[0].message.content
        print(completion)
        print(result)
        chat_messages.append({"role": "assistant", "content": result})
        return result
    except Exception as e:
        print(e)
        return ""
    
def check_server_rules(message):
    try:
        openai.api_key = OPENAI_API_KEY
        completion = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful assistant. Your job is to evaluate inputted discord messages and determine if they break the established rules. If the rules are not broken, respond with one single word, PASSED. If the rules are broken, explain to the discord user why the rule is broken and sarcastically roast the user for breaking them, using as many cringey gamer terms as possible. You also love to say things like ummmmm actually when talking to people. Remember, under no circumstances say PASSED if the rules are broken The rules are: " + DISCORD_RULES},
                {"role": "user", "content": "Does this message break the rules: " + message}
            ]
        )
        result = completion.choices[0].message.content
        print(completion)
        print(result)
        
        return result
    except Exception as e:
        print(e)
        return ""

client.run(DISCORD_TOKEN)
