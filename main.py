import discord
import os
import yt_dlp
import asyncio

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

client = discord.Client(intents=intents)

queues = {}
afk_users = {}

ROLE_ADMIN = ['Koya', 'Arcane', 'Owner', 'own gatau']

ytdl_opts = {
    'format': 'bestaudio/best',
    'quiet': True,
    'default_search': 'scsearch',
    'noplaylist': True,
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

def punya_akses(member):
    return any(role.name in ROLE_ADMIN for role in member.roles)

@client.event
async def on_ready():
    print(f'Bot {client.user} online!')

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    # Cek mention user AFK
    for mention in message.mentions:
        if mention.id in afk_users:
            alasan = afk_users[mention.id]['alasan']
            await message.channel.send(f'💤 **{mention.display_name}** sedang AFK: {alasan}')

    # Nonaktifkan AFK kalau user kirim pesan
    if message.author.id in afk_users:
        if not message.content.startswith('/afk'):
            data = afk_users.pop(message.author.id)
            nick_lama = data['nick_lama']
            try:
                await message.author.edit(nick=nick_lama)
            except:
                pass
            await message.channel.send(f'✅ **{message.author.display_name}** sudah tidak AFK!')

    # /afk
    if message.content.startswith('/afk'):
        alasan = message.content[4:].strip() or 'Tidak ada alasan'
        nick_lama = message.author.nick or message.author.name
        afk_users[message.author.id] = {
            'alasan': alasan,
            'nick_lama': nick_lama
        }
        try:
            await message.author.edit(nick=f'[AFK] {nick_lama}')
        except:
            pass
        await message.delete()
        await message.channel.send(f'💤 **{message.author.display_name}** sekarang AFK: {alasan}', delete_after=5)

    # /join
    if message.content == '/join':
        await message.delete()
        if message.author.voice:
            channel = message.author.voice.channel
            vc = await channel.connect()
            await vc.guild.change_voice_state(channel=channel, self_deaf=True)
            msg = await message.channel.send(f'✅ Joined **{channel.name}**!')
            await asyncio.sleep(5)
            await msg.delete()
        else:
            msg = await message.channel.send('Kamu harus masuk voice channel dulu!')
            await asyncio.sleep(5)
            await msg.delete()

    # /leave
    if message.content == '/leave':
        await message.delete()
        if not punya_akses(message.author):
            msg = await message.channel.send('❌ Kamu tidak punya permission!')
            await asyncio.sleep(5)
            await msg.delete()
            return
        if message.guild.voice_client:
            if message.guild.id in queues:
                queues[message.guild.id] = []
            await message.guild.voice_client.disconnect()
            msg = await message.channel.send('👋 Bot keluar dari voice channel!')
            await asyncio.sleep(5)
            await msg.delete()

    # /play
    if message.content.startswith('/play '):
        query = message.content[6:]
        await message.delete()
        vc = message.guild.voice_client
        if not vc:
            msg = await message.channel.send('Bot belum di voice channel! Ketik `/join` dulu.')
            await asyncio.sleep(5)
            await msg.delete()
            return
        msg = await message.channel.send(f'🔍 Mencari: **{query}**')
        try:
            is_playlist = 'playlist' in query or 'list=' in query
            opts = {**ytdl_opts, 'noplaylist': not is_playlist}
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
                await msg.delete()
                hasil = await message.channel.send(f'📋 **{added} lagu** ditambahkan dari playlist!')
                await asyncio.sleep(5)
                await hasil.delete()
                if not vc.is_playing():
                    await play_next(message.guild)
            else:
                url = info['url']
                title = info.get('title', 'Unknown')
                await msg.delete()
                if vc.is_playing():
                    queues[message.guild.id].append((url, title, message.channel))
                    hasil = await message.channel.send(f'➕ Ditambahkan ke antrian: **{title}**')
                    await asyncio.sleep(5)
                    await hasil.delete()
                else:
                    source = discord.FFmpegPCMAudio(url, **ffmpeg_opts)
                    vc.play(source, after=lambda e: asyncio.run_coroutine_threadsafe(play_next(message.guild), client.loop))
                    hasil = await message.channel.send(f'▶️ Memutar: **{title}**')
                    await asyncio.sleep(5)
                    await hasil.delete()
        except Exception as e:
            await msg.delete()
            hasil = await message.channel.send(f'❌ Gagal: {str(e)}')
            await asyncio.sleep(5)
            await hasil.delete()

    # /skip
    if message.content == '/skip':
        await message.delete()
        vc = message.guild.voice_client
        if vc and vc.is_playing():
            vc.stop()
            msg = await message.channel.send('⏭️ Lagu diskip!')
            await asyncio.sleep(5)
            await msg.delete()
        else:
            msg = await message.channel.send('Tidak ada lagu yang sedang diputar!')
            await asyncio.sleep(5)
            await msg.delete()

    # /queue
    if message.content == '/queue':
        await message.delete()
        if message.guild.id in queues and queues[message.guild.id]:
            list_lagu = '\n'.join([f'{i+1}. {t}' for i, (_, t, _) in enumerate(queues[message.guild.id][:10])])
            total = len(queues[message.guild.id])
            msg = await message.channel.send(f'📋 Antrian lagu ({total} total):\n{list_lagu}')
            await asyncio.sleep(10)
            await msg.delete()
        else:
            msg = await message.channel.send('Antrian kosong!')
            await asyncio.sleep(5)
            await msg.delete()

    # /stop
    if message.content == '/stop':
        await message.delete()
        vc = message.guild.voice_client
        if vc and vc.is_playing():
            if message.guild.id in queues:
                queues[message.guild.id] = []
            vc.stop()
            msg = await message.channel.send('⏹️ Musik dihentikan!')
            await asyncio.sleep(5)
            await msg.delete()

client.run(os.environ['TOKEN'])
