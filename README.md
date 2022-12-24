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
