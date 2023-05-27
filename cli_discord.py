"""cli_discord - See discord messages from the comfort of your terminal"""
import asyncio
import argparse
import os
import sys
import discord
import colorama
from colorama import Fore, Back
from aioconsole import ainput

parser = argparse.ArgumentParser(description="CliDiscord")
parser.add_argument('token', type=str, help="The token of the discord bot")
parser.add_argument('channelid', type=str, help="The Channel ID")
args = parser.parse_args()

TOKEN = args.token
CHANNEL_ID = args.channelid

intents = discord.Intents.default()
intents.messages = True
client = discord.Client(intents=intents)

# fuck offn't pylint
MESSAGE_HISTORY = []
SHOULD_CLEAR_SCREEN = True


def clear_screen():
    """Clear the terminal screen"""
    if os.name == 'nt':
        os.system('cls')
    else:
        os.system('clear')


@client.event
async def on_ready():
    """Bot startup"""
    global MESSAGE_HISTORY, SHOULD_CLEAR_SCREEN
    if SHOULD_CLEAR_SCREEN:
        clear_screen()
        SHOULD_CLEAR_SCREEN = False
    print(f'{Back.YELLOW}{Fore.BLUE}Logged in as {client.user.name} '
          f'({client.user.id}){Back.RESET}{Fore.RESET}')
    channel = client.get_channel(int(CHANNEL_ID))
    if channel is not None:
        messages = []
        # Gather last 50 messages
        async for message in channel.history(limit=50, oldest_first=False):
            messages.append(message)
        MESSAGE_HISTORY = messages
        for message in reversed(MESSAGE_HISTORY):
            if message.content:
                colorama.init()
                try:
                    print(
                        f'{Fore.RESET}{Fore.BLUE}{message.author}: {message.content}{Fore.RESET}')
                finally:
                    colorama.deinit()
    else:
        print(f'Failed to fetch channel with ID {CHANNEL_ID}')

    await update_messages(channel)


@client.event
async def on_message(message):
    """When a message is sent"""
    if message.channel.id == int(CHANNEL_ID):
        global SHOULD_CLEAR_SCREEN
        if SHOULD_CLEAR_SCREEN:
            clear_screen()
            SHOULD_CLEAR_SCREEN = False
        print(f'{Fore.RESET}{Fore.BLUE}{message.author}: {message.content}{Fore.RESET}')
        MESSAGE_HISTORY.append(message)


@client.event
async def on_message_edit(before, after):
    """When a message is edited"""
    if before.channel.id == int(CHANNEL_ID):
        if before.content != after.content:
            global SHOULD_CLEAR_SCREEN
            if SHOULD_CLEAR_SCREEN:
                clear_screen()
                SHOULD_CLEAR_SCREEN = False
            print(f'{Fore.RESET}{Fore.BLUE}'
                  f'{before.author}: {after.content}'
                  f'{Fore.RESET}')
            # Update message in history
            for i, message in enumerate(MESSAGE_HISTORY):
                if message.id == before.id:
                    MESSAGE_HISTORY[i] = after
                    break


@client.event
async def on_message_delete(message):
    """When a message is deleted"""
    if message.channel.id == int(CHANNEL_ID):
        if message in MESSAGE_HISTORY:
            MESSAGE_HISTORY.remove(message)


async def send_discord_message(channel, message):
    """Send a message"""
    await channel.send(message)
    await update_messages(channel)


async def update_messages(channel):
    """Update and display messages"""
    global MESSAGE_HISTORY, SHOULD_CLEAR_SCREEN
    messages = []
    async for message in channel.history(limit=50, oldest_first=False):
        messages.append(message)

    new_messages = [
        message for message in messages if message not in MESSAGE_HISTORY]
    MESSAGE_HISTORY += new_messages

    if new_messages:
        SHOULD_CLEAR_SCREEN = True

    for message in reversed(new_messages):
        if message.content:
            colorama.init()
            try:
                print(
                    f'{Fore.RESET}{Fore.BLUE}{message.author}: {message.content}{Fore.RESET}')
            finally:
                colorama.deinit()


async def user_input():
    """Check for user input"""
    await client.wait_until_ready()
    channel = client.get_channel(int(CHANNEL_ID))

    if channel is not None:
        colorama.init()
        try:
            while not client.is_closed():
                sys.stdout.write(f"{Fore.RESET}{Back.GREEN}{Fore.WHITE}"
                                 f"{client.user.name}#{client.user.discriminator}:"
                                 f"{Back.RESET}{Fore.RESET} ")

                sys.stdout.flush()
                sys.stdout.write(f"{Fore.YELLOW}")
                msg = await ainput()  # Asynchronously read user input
                sys.stdout.write(f"{Fore.RESET}")

                sys.stdout.write("\033[F\033[K")  # Move up 1 line, Clear line
                sys.stdout.flush()
                if msg:
                    # if msg == "[[.refresh":
                    #     await update_messages(channel)
                    # else:
                    # Deprectated since it now updates in real-time
                    await send_discord_message(channel, msg)
        finally:
            colorama.deinit()


async def main():
    """Start bot and start gathering user input"""
    await asyncio.gather(
        client.start(TOKEN),
        user_input()
    )

loop = asyncio.get_event_loop()
loop.run_until_complete(main())
