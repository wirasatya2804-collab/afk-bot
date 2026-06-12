import discord
import os
import yt_dlp
import asyncio

intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)

queues = {}

ytdl_opts_search = {
    'format': 'bestaudio/best',
    'quiet': True,
    'default_search': 'scsearch',
    'noplaylist': True,
}

ytdl_opts_playlist = {
    'format': 'bestaudio/best',
    'quiet': True,
    'extract_flat': False,
    'noplaylist': False,
}

ffmpeg_opts = {
    'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
    'options': '-vn'
}

async def play_next(guild):
    if guild.id in queues and queues[guild.id]:
        url, title, channel = queues[guild.id].pop(0)
        vc = guild.voice_client
        if vc:
            source = discord.FFmpegPCMAudio(url, **ffmpeg_opts)
            vc.play(source, after=lambda e: asyncio.run_coroutine_threadsafe(play_next(guild), client.loop))
            asyncio.run_coroutine_threadsafe(channel.send(f'▶️ Memutar: **{title}**'), client.loop)

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
            vc = await channel.connect()
            await vc.guild.change_voice_state(channel=channel, self_deaf=True)
            await message.channel.send(f'✅ Joined **{channel.name}**!')
        else:
            await message.channel.send('Kamu harus masuk voice channel dulu!')

    if message.content.startswith('!play '):
        query = message.content[6:]
        vc = message.guild.voice_client
        if not vc:
            await message.channel.send('Bot belum di voice channel! Ketik `!join` dulu.')
            return

        await message.channel.send(f'🔍 Mencari: **{query}**')

        try:
            is_playlist = 'playlist' in query or 'list=' in query
            opts = ytdl_opts_playlist if is_playlist else ytdl_opts_search

            with yt_dlp.YoutubeDL(opts) as ydl:
                if query.startswith('http'):
                    info = ydl.extract_info(query, download=False)
                else:
                    info = ydl.extract_info(query, download=False)['entries'][0]

            if message.guild.id not in queues:
                queues[message.guild.id] = []

            if 'entries' in info:
                entries = info['entries']
                added = 0
                for entry in entries:
                    try:
                        url = entry['url']
                        title = entry.get('title', 'Unknown')
                        queues[message.guild.id].append((url, title, message.channel))
                        added += 1
                    except:
                        continue

                await message.channel.send(f'📋 **{added} lagu** ditambahkan dari playlist!')

                if not vc.is_playing():
                    await play_next(message.guild)
            else:
                url = info['url']
                title = info.get('title', 'Unknown')

                if vc.is_playing():
                    queues[message.guild.id].append((url, title, message.channel))
                    await message.channel.send(f'➕ Ditambahkan ke antrian: **{title}**')
                else:
                    source = discord.FFmpegPCMAudio(url, **ffmpeg_opts)
                    vc.play(source, after=lambda e: asyncio.run_coroutine_threadsafe(play_next(message.guild), client.loop))
                    await message.channel.send(f'▶️ Memutar: **{title}**')

        except Exception as e:
            await message.channel.send(f'❌ Gagal: {str(e)}')

    if message.content == '!skip':
        vc = message.guild.voice_client
        if vc and vc.is_playing():
            vc.stop()
            await message.channel.send('⏭️ Lagu diskip!')
        else:
            await message.channel.send('Tidak ada lagu yang sedang diputar!')

    if message.content == '!queue':
        if message.guild.id in queues and queues[message.guild.id]:
            list_lagu = '\n'.join([f'{i+1}. {t}' for i, (_, t, _) in enumerate(queues[message.guild.id][:10])])
            total = len(queues[message.guild.id])
            await message.channel.send(f'📋 Antrian lagu ({total} total):\n{list_lagu}')
        else:
            await message.channel.send('Antrian kosong!')

    if message.content == '!stop':
        vc = message.guild.voice_client
        if vc and vc.is_playing():
            queues[message.guild.id] = []
            vc.stop()
            await message.channel.send('⏹️ Musik dihentikan dan antrian dikosongkan!')

    if message.content == '!leave':
        if message.guild.voice_client:
            if message.guild.id in queues:
                queues[message.guild.id] = []
            await message.guild.voice_client.disconnect()
            await message.channel.send('👋 Bot keluar dari voice channel!')

client.run(os.environ['TOKEN'])
