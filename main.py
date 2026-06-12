import discord
import os

intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)

@client.event
async def on_ready():
    print(f'Bot {client.user} online!')

@client.event
async def on_message(message):
    if message.author == client.user:
        return
    
    if message.content == '!join':
        if message.author.voice:
            channel = message.author.voice.channel
            await channel.connect()
            await message.channel.send(f'Joined **{channel.name}**!')
        else:
            await message.channel.send('Kamu harus masuk voice channel dulu!')
    
    if message.content == '!leave':
        if message.guild.voice_client:
            await message.guild.voice_client.disconnect()
            await message.channel.send('Bot keluar dari voice channel!')

client.run(os.environ['TOKEN'])
