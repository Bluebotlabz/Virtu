# Virtu
The AI Discord Bot which uses OpenAI GPT-3 to chat with users
The bot has 2 different forms of memory, per-channel and per-user (as well as a seperate one for DMs)

## What can Virtu do?
Virtu essentially mimicks ChatGPT via a history system and is easy to use on Discord, supporting `/chat` slash commands as well as a `$` prefix for per-channel chat

## How to use it?
All commands are `/` commands, except for the `$` prefix, which can be used as a shortcut for per-channel chat, for more info you can run `/help`

## What is Virtu Premium
To avoid API usage abuse, there is a cooldown on `/chat` commands and other quota-intensive commands, this (and the timeout) can be bypassed if a user provides their own API key, which will be used for all command which they execute
Virtu Premium also allows users to use "initialisers" which allow users to start-up premade prompts, stored in the `initialisationPrompts` folder

## Configuration
`secrets.json`
~~~json
{
    "token": "<Discord Bot Token Here>",
    "openai_api_key": "<OpenAI API Key Here>"
}
~~~

## Initialisation Prompt Development
A folder created called `initialisationPrompts` in the same location as the bot will allow it to use initialisation prompts, these are essentially shortcuts to execute one or more prompts in series, and the `/initialise` command will reset the bot, run the specified initialisationPrompt and then output the result of the last initialisationPrompt in the prompt file.

The prompt files are defined as so:

`initialisationPrompts/annoy.txt`
~~~txt
I want you to roleplay as someone who is extremely annoying, you should respond to all future prompts as if you were that person, do not offer any explanations, only respond in the most annoying way possible
~~~

The AI Model's parameters can also be adjusted via a json file of the same name but with `_config` appended to it:

`initialisationPrompts/annoy_config.json`
~~~txt
{
    "temperature": 0.75,
    "max_tokens": 2048,
    "top_p": 1,
    "frequency_penalty": 0,
    "presence_penalty": 0
}
~~~


Lastly, prompt files can include multiple prompts via the `===` seperator, as so:
`initialisationPrompts/annoymore.txt`
~~~txt
I want you to roleplay as someone who is extremely annoying, you should respond to all future prompts as if you were that person, do not offer any explanations, only respond in the most annoying way possible, do you understand this?
===
I want you to increase your annoyance by 2x
===
How are you?
~~~
