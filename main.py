import discord
import os
import yt_dlp
import asyncio
import datetime
import random

intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.voice_states = True

client = discord.Client(intents=intents)

queues = {}
afk_users = {}
last_voice_channel = {}
intentional_leave = {}
user_data = {}

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

# ===== DATA FUN =====
JAWABAN_8BALL = [
    "Ya, pasti!", "Tidak mungkin.", "Mungkin saja.", "Sepertinya iya.",
    "Sepertinya tidak.", "Tanya lagi nanti.", "Aku yakin itu benar.",
    "Jangan berharap terlalu tinggi.", "100% YA!", "Big NO.",
    "Coba tanya orang lain.", "Aku tidak yakin."
]

JOKES = [
    "Kenapa programmer suka alam? Karena banyak 'tree' nya. \U0001F333",
    "Kamu tahu kenapa laptop selalu sedih? Karena banyak 'window' nya. \U0001FA9F",
    "Apa bedanya kamu sama wifi? Wifi bisa connect, kamu nggak. \U0001F4F6",
    "Kenapa hantu nggak bisa bohong? Karena ketahuan transparant. \U0001F47B",
    "Kerja itu seperti puzzle, semakin lama semakin banyak yang ilang... niat. \U0001F9E9",
    "Kenapa ikan nggak suka main basket? Takut kena net. \U0001F41F"
]

TRUTH = [
    "Siapa crush kamu sekarang?",
    "Apa hal paling memalukan yang pernah kamu lakukan?",
    "Pernah nggak kamu nyontek waktu ujian?",
    "Apa rahasia yang belum pernah kamu ceritakan ke siapa pun?",
    "Siapa orang yang paling kamu kagumi di server ini?",
    "Pernah nggak kamu suka sama teman sendiri?"
]

DARE = [
    "Kirim voice note nyanyi lagu apapun!",
    "Ganti nickname kamu jadi 'Aku Imut' selama 10 menit.",
    "Kirim emoji yang menggambarkan mood kamu sekarang tanpa kata-kata.",
    "Tulis pesan tanpa huruf 'a' selama 3 kalimat.",
    "Sebutkan 3 hal yang kamu suka tentang orang di atas kamu.",
    "Kirim foto random dari galeri kamu (yang aman ya!)."
]

ADVENTURE_EVENTS = [
    # Gold events
    ("🏆 Kamu menemukan harta karun kuno yang tersembunyi!", 'gold', 50),
    ("🕳️ Kamu terjebak jebakan, kehilangan koin!", 'gold', -30),
    ("💰 Kamu menemukan koin emas di dalam gua!", 'gold', 75),
    ("🎁 Kamu menemukan kotak misterius berisi koin!", 'gold', 40),
    ("💸 Kamu dirampok bandit di persimpangan jalan!", 'gold', -40),
    ("🪙 Kamu menemukan dompet berisi emas di tepi sungai!", 'gold', 60),
    ("🛒 Kamu menemukan pedagang barang bawaan dan dapat diskon gold!", 'gold', 35),
    ("💎 Kamu menemukan berlian kecil di gua bawah tanah!", 'gold', 100),
    ("🏚️ Kamu menggeledah rumah tua dan menemukan harta tersembunyi!", 'gold', 45),
    # HP events
    ("⚔️ Kamu diserang monster dan kalah, HP berkurang!", 'hp', -20),
    ("🧪 Kamu menemukan ramuan penyembuh ajaib!", 'hp', 25),
    ("🌿 Kamu menemukan tanaman obat langka di hutan!", 'hp', 15),
    ("🐍 Kamu digigit ular berbisa, HP berkurang drastis!", 'hp', -35),
    ("⛰️ Kamu jatuh dari tebing, tapi selamat dengan luka!", 'hp', -15),
    ("🏊 Kamu berenang menyeberangi sungai deras, kelelahan!", 'hp', -10),
    ("🍄 Kamu memakan jamur ajaib, HP bertambah!", 'hp', 30),
    ("🛡️ Kamu menemukan tameng yang melindungimu dari serangan!", 'hp', 20),
    # XP events
    ("🗡️ Kamu berhasil mengalahkan monster! Dapat EXP!", 'xp', 30),
    ("🐉 Kamu bertarung dengan naga kecil dan menang!", 'xp', 50),
    ("🧙 Kamu belajar dari penyihir tua di menara, dapat ilmu baru!", 'xp', 40),
    ("🏹 Kamu latihan memanah dan skill meningkat!", 'xp', 25),
    ("📜 Kamu menemukan gulungan mantra kuno dan mempelajarinya!", 'xp', 35),
    ("🐺 Kamu bertarung dengan serigala liar dan menang!", 'xp', 20),
    ("🧟 Kamu mengalahkan zombie yang berkeliaran di pemakaman!", 'xp', 45),
    ("🦅 Kamu diselamatkan elang raksasa dan diajarkan cara terbang!", 'xp', 60),
    ("🗺️ Kamu menjelajah wilayah baru yang belum pernah ditemukan!", 'xp', 55),
    ("🏰 Kamu berhasil melewati kastil berhantu tanpa cedera!", 'xp', 70),
]

# ===== ITEM & SHOP =====
SHOP_ITEMS = {
    'sword': {'nama': '⚔️ Pedang Besi', 'harga': 150, 'efek': 'atk+10', 'deskripsi': 'Pedang biasa, menambah ATK saat duel'},
    'shield': {'nama': '🛡️ Perisai Kayu', 'harga': 120, 'efek': 'def+10', 'deskripsi': 'Perisai sederhana, mengurangi damage duel'},
    'potion': {'nama': '🧪 Ramuan HP', 'harga': 50, 'efek': 'hp+50', 'deskripsi': 'Memulihkan 50 HP seketika'},
    'elixir': {'nama': '✨ Elixir Ajaib', 'harga': 200, 'efek': 'hp+100', 'deskripsi': 'Memulihkan HP penuh dan tambah XP 20'},
    'lucky_charm': {'nama': '🍀 Jimat Keberuntungan', 'harga': 100, 'efek': 'luck', 'deskripsi': 'Meningkatkan peluang event bagus saat adventure'},
    'axe': {'nama': '🪓 Kapak Perang', 'harga': 250, 'efek': 'atk+20', 'deskripsi': 'Senjata kuat untuk duel'},
    'armor': {'nama': '🥋 Zirah Rantai', 'harga': 300, 'efek': 'def+20', 'deskripsi': 'Perlindungan tinggi untuk duel'},
    'bomb': {'nama': '💣 Bom Asap', 'harga': 80, 'efek': 'special', 'deskripsi': 'Digunakan saat duel untuk skip 1 ronde'},
}

# ===== DUNGEON =====
DUNGEONS = {
    'hutan': {
        'nama': '🌲 Hutan Terlarang',
        'min_level': 1, 'harga': 30,
        'boss': '🐺 Serigala Raksasa',
        'boss_hp': 80,
        'reward_xp': 80, 'reward_gold': 60,
        'event': [
            "Kamu masuk ke hutan gelap... pepohonan menutup langit.",
            "Seekor goblin menghadang! Kamu berhasil mengalahkannya.",
            "Kamu menemukan jalan tersembunyi menuju inti hutan.",
        ]
    },
    'gua': {
        'nama': '🕳️ Gua Kristal',
        'min_level': 3, 'harga': 60,
        'boss': '🕷️ Laba-laba Raksasa',
        'boss_hp': 120,
        'reward_xp': 150, 'reward_gold': 100,
        'event': [
            "Kamu menerangi gua dengan obor...",
            "Kristal-kristal indah berkilauan di dinding.",
            "Kamu melewati jembatan rapuh di atas jurang dalam!",
        ]
    },
    'kastil': {
        'nama': '🏰 Kastil Kegelapan',
        'min_level': 5, 'harga': 100,
        'boss': '💀 Lich Raja Kegelapan',
        'boss_hp': 200,
        'reward_xp': 300, 'reward_gold': 200,
        'event': [
            "Kamu memasuki gerbang kastil yang reot...",
            "Zombie dan hantu berkeliaran di lorong.",
            "Kamu menemukan ruang tahta... ada sesuatu di sana!",
        ]
    },
    'gunung': {
        'nama': '🌋 Gunung Api',
        'min_level': 8, 'harga': 150,
        'boss': '🔥 Naga Api Kuno',
        'boss_hp': 350,
        'reward_xp': 500, 'reward_gold': 350,
        'event': [
            "Panas menyengat saat kamu mendaki gunung...",
            "Lahar mengalir di kiri kananmu, berbahaya!",
            "Kamu mencapai puncak... dan melihat sarang naga!",
        ]
    }
}

# ===== BOSS HUNT (event langka) =====
WORLD_BOSSES = [
    {'nama': '👹 Ogre Penjaga Hutan', 'hp': 500, 'reward_xp': 200, 'reward_gold': 300},
    {'nama': '🦂 Kalajengking Raksasa', 'hp': 400, 'reward_xp': 150, 'reward_gold': 250},
    {'nama': '🧟 Raja Zombie', 'hp': 600, 'reward_xp': 250, 'reward_gold': 400},
]
world_boss_active = None
world_boss_participants = {}

# ===== PET SYSTEM =====
PETS = {
    'wolf': {
        'nama': '🐺 Serigala', 'harga': 300,
        'atk_bonus': 15, 'def_bonus': 5, 'hp_bonus': 20,
        'skill': 'Terkam', 'skill_dmg': 25,
        'deskripsi': 'Lincah dan agresif, bonus ATK tinggi'
    },
    'dragon': {
        'nama': '🐉 Naga Kecil', 'harga': 800,
        'atk_bonus': 30, 'def_bonus': 10, 'hp_bonus': 30,
        'skill': 'Semburan Api', 'skill_dmg': 50,
        'deskripsi': 'Pet paling kuat, bonus ATK & HP besar'
    },
    'fox': {
        'nama': '🦊 Rubah Sakti', 'harga': 250,
        'atk_bonus': 10, 'def_bonus': 15, 'hp_bonus': 15,
        'skill': 'Tipu Daya', 'skill_dmg': 20,
        'deskripsi': 'Licik, bonus DEF dan dodge tinggi'
    },
    'eagle': {
        'nama': '🦅 Elang Emas', 'harga': 400,
        'atk_bonus': 20, 'def_bonus': 8, 'hp_bonus': 10,
        'skill': 'Cakar Kilat', 'skill_dmg': 35,
        'deskripsi': 'Cepat dan mematikan, skill damage tinggi'
    },
    'bear': {
        'nama': '🐻 Beruang Kutub', 'harga': 500,
        'atk_bonus': 10, 'def_bonus': 25, 'hp_bonus': 50,
        'skill': 'Hantam Bumi', 'skill_dmg': 30,
        'deskripsi': 'Tanky banget, bonus HP & DEF besar'
    },
    'cat': {
        'nama': '🐱 Kucing Mistik', 'harga': 150,
        'atk_bonus': 8, 'def_bonus': 8, 'hp_bonus': 10,
        'skill': 'Cakar Mistik', 'skill_dmg': 15,
        'deskripsi': 'Pet murah untuk pemula, seimbang'
    },
    'phoenix': {
        'nama': '🔥 Phoenix', 'harga': 1200,
        'atk_bonus': 25, 'def_bonus': 20, 'hp_bonus': 40,
        'skill': 'Kebangkitan Api', 'skill_dmg': 60,
        'deskripsi': 'Pet legendaris, bisa revive 1x saat hp 0'
    },
}

PET_EXP_PER_LEVEL = 50  # exp yang dibutuhkan per level pet

# ===== GEMS SYSTEM =====
GEMS = {
    'fire_gem':    {'nama': '🔴 Fire Gem',    'rarity': 'Common',    'efek': 'atk+5',     'deskripsi': 'Menambah ATK +5 saat hunting'},
    'ice_gem':     {'nama': '🔵 Ice Gem',     'rarity': 'Common',    'efek': 'def+5',     'deskripsi': 'Menambah DEF +5 saat hunting'},
    'wind_gem':    {'nama': '🟢 Wind Gem',    'rarity': 'Uncommon',  'efek': 'spd+10',    'deskripsi': 'Meningkatkan peluang dapat loot rare'},
    'earth_gem':   {'nama': '🟤 Earth Gem',   'rarity': 'Uncommon',  'efek': 'hp+20',     'deskripsi': 'HP tidak berkurang saat hunting gagal'},
    'thunder_gem': {'nama': '🟡 Thunder Gem', 'rarity': 'Rare',      'efek': 'atk+15',    'deskripsi': 'ATK +15 dan peluang critical hit'},
    'dark_gem':    {'nama': '⚫ Dark Gem',    'rarity': 'Rare',      'efek': 'lifesteal',  'deskripsi': 'Steal HP dari monster saat hunting'},
    'light_gem':   {'nama': '⚪ Light Gem',   'rarity': 'Epic',      'efek': 'allstats+10','deskripsi': 'Semua stat +10 saat hunting'},
    'chaos_gem':   {'nama': '🌈 Chaos Gem',   'rarity': 'Legendary', 'efek': 'x2_loot',   'deskripsi': 'DOUBLE semua loot saat hunting!'},
}

GEM_DROP_RATE = {
    'Common': 40, 'Uncommon': 25, 'Rare': 15, 'Epic': 8, 'Legendary': 2
}
GEM_POOL_BY_RARITY = {
    'Common':    ['fire_gem', 'ice_gem'],
    'Uncommon':  ['wind_gem', 'earth_gem'],
    'Rare':      ['thunder_gem', 'dark_gem'],
    'Epic':      ['light_gem'],
    'Legendary': ['chaos_gem'],
}

# ===== HUNTING SYSTEM =====
HUNT_MONSTERS = [
    {'nama': '🐀 Tikus Raksasa',    'level': 1,  'hp': 30,  'reward_xp': 15, 'reward_gold': 10, 'loot_table': ['fire_gem', 'ice_gem']},
    {'nama': '🐍 Ular Beracun',     'level': 1,  'hp': 45,  'reward_xp': 20, 'reward_gold': 15, 'loot_table': ['fire_gem', 'wind_gem']},
    {'nama': '🐺 Serigala Hutan',   'level': 3,  'hp': 80,  'reward_xp': 40, 'reward_gold': 30, 'loot_table': ['ice_gem', 'wind_gem', 'earth_gem']},
    {'nama': '🕷️ Laba-laba Hitam', 'level': 3,  'hp': 70,  'reward_xp': 35, 'reward_gold': 25, 'loot_table': ['dark_gem', 'ice_gem']},
    {'nama': '🐊 Buaya Purba',      'level': 5,  'hp': 120, 'reward_xp': 60, 'reward_gold': 50, 'loot_table': ['earth_gem', 'thunder_gem']},
    {'nama': '🦁 Singa Gurun',      'level': 5,  'hp': 110, 'reward_xp': 55, 'reward_gold': 45, 'loot_table': ['thunder_gem', 'wind_gem']},
    {'nama': '🐉 Wyrm Tanah',       'level': 8,  'hp': 200, 'reward_xp': 100,'reward_gold': 90, 'loot_table': ['dark_gem', 'light_gem', 'thunder_gem']},
    {'nama': '👻 Hantu Banshee',    'level': 8,  'hp': 180, 'reward_xp': 90, 'reward_gold': 80, 'loot_table': ['light_gem', 'dark_gem']},
    {'nama': '🔥 Elemental Api',    'level': 10, 'hp': 300, 'reward_xp': 150,'reward_gold': 120,'loot_table': ['chaos_gem', 'light_gem', 'thunder_gem']},
    {'nama': '🧊 Golem Es',         'level': 10, 'hp': 350, 'reward_xp': 160,'reward_gold': 130,'loot_table': ['chaos_gem', 'light_gem', 'earth_gem']},
]

RARE_LOOT = [
    {'nama': '💍 Cincin Keberanian', 'efek': 'atk_perm+3',  'deskripsi': 'Permanen ATK +3'},
    {'nama': '📿 Kalung Pelindung',  'efek': 'def_perm+3',  'deskripsi': 'Permanen DEF +3'},
    {'nama': '🪬 Amulet Kehidupan',  'efek': 'hp_perm+20',  'deskripsi': 'Permanen max HP +20'},
    {'nama': '🗡️ Shard Pedang Kuno','efek': 'atk_perm+5',  'deskripsi': 'Permanen ATK +5 (langka!)'},
    {'nama': '🛡️ Fragmen Tameng',   'efek': 'def_perm+5',  'deskripsi': 'Permanen DEF +5 (langka!)'},
]

# ===== PVP DUEL =====
duel_requests = {}  # {challenger_id: {target_id, channel}}

# ===== QUEST SYSTEM =====
# Daily quest: reset tiap hari, bisa dikerjakan ulang
DAILY_QUESTS = [
    {'id': 'dq1', 'nama': '🗺️ Penjelajah Harian', 'deskripsi': 'Lakukan adventure sebanyak 3x', 'tipe': 'adventure', 'target': 3, 'reward_xp': 50, 'reward_gold': 40},
    {'id': 'dq2', 'nama': '💰 Kolektor Koin', 'deskripsi': 'Kumpulkan 100 Gold dari adventure/explore', 'tipe': 'earn_gold', 'target': 100, 'reward_xp': 30, 'reward_gold': 60},
    {'id': 'dq3', 'nama': '⚔️ Pemburu Monster', 'deskripsi': 'Lakukan explore sebanyak 2x', 'tipe': 'explore', 'target': 2, 'reward_xp': 40, 'reward_gold': 30},
    {'id': 'dq4', 'nama': '🏥 Perawatan Diri', 'deskripsi': 'Gunakan heal 1x', 'tipe': 'heal', 'target': 1, 'reward_xp': 20, 'reward_gold': 25},
    {'id': 'dq5', 'nama': '🎰 Penjudi Beruntung', 'deskripsi': 'Gambling sebanyak 2x', 'tipe': 'gamble', 'target': 2, 'reward_xp': 25, 'reward_gold': 35},
]

# Main quest: permanen, hanya bisa diselesaikan sekali
MAIN_QUESTS = [
    {'id': 'mq1', 'nama': '🌱 Petualang Pemula', 'deskripsi': 'Lakukan adventure pertamamu', 'tipe': 'adventure', 'target': 1, 'reward_xp': 80, 'reward_gold': 50},
    {'id': 'mq2', 'nama': '🏰 Penakluk Dungeon', 'deskripsi': 'Selesaikan dungeon pertamamu', 'tipe': 'dungeon_clear', 'target': 1, 'reward_xp': 150, 'reward_gold': 100},
    {'id': 'mq3', 'nama': '⚔️ Petarung Sejati', 'deskripsi': 'Menangkan 3x duel PvP', 'tipe': 'duel_win', 'target': 3, 'reward_xp': 200, 'reward_gold': 150},
    {'id': 'mq4', 'nama': '💎 Hartawan', 'deskripsi': 'Kumpulkan total 500 Gold', 'tipe': 'gold_total', 'target': 500, 'reward_xp': 100, 'reward_gold': 200},
    {'id': 'mq5', 'nama': '🧙 Penyihir Level 5', 'deskripsi': 'Capai Level 5', 'tipe': 'level', 'target': 5, 'reward_xp': 300, 'reward_gold': 250},
    {'id': 'mq6', 'nama': '🐉 Pembunuh Naga', 'deskripsi': 'Selesaikan dungeon gunung', 'tipe': 'dungeon_clear_gunung', 'target': 1, 'reward_xp': 500, 'reward_gold': 400},
    {'id': 'mq7', 'nama': '🏪 Kolektor Item', 'deskripsi': 'Miliki 3 item berbeda di inventory', 'tipe': 'inventory_count', 'target': 3, 'reward_xp': 120, 'reward_gold': 80},
    {'id': 'mq8', 'nama': '🌍 Pahlawan Server', 'deskripsi': 'Serang World Boss sebanyak 5x', 'tipe': 'boss_attack', 'target': 5, 'reward_xp': 400, 'reward_gold': 350},
    {'id': 'mq9', 'nama': '🗺️ Legenda Penjelajah', 'deskripsi': 'Lakukan adventure total 50x', 'tipe': 'adventure', 'target': 50, 'reward_xp': 600, 'reward_gold': 500},
    {'id': 'mq10', 'nama': '👑 Raja Duel', 'deskripsi': 'Menangkan 10x duel PvP', 'tipe': 'duel_win', 'target': 10, 'reward_xp': 800, 'reward_gold': 700},
]

def get_quest_data(data):
    """Inisialisasi quest data jika belum ada"""
    if 'quest' not in data:
        data['quest'] = {
            'daily': {},        # {quest_id: progress}
            'daily_date': None, # tanggal terakhir reset
            'main': {},         # {quest_id: progress}
            'main_done': [],    # list quest_id yang sudah selesai
            'daily_done': [],   # list quest_id yang sudah selesai hari ini
        }
    q = data['quest']
    # backward compat
    for key, default in [('daily', {}), ('daily_date', None), ('main', {}),
                          ('main_done', []), ('daily_done', [])]:
        if key not in q:
            q[key] = default
    return q

def reset_daily_quest_if_needed(data):
    """Reset daily quest jika hari sudah berganti"""
    q = get_quest_data(data)
    today = datetime.date.today().isoformat()
    if q['daily_date'] != today:
        q['daily'] = {}
        q['daily_done'] = []
        q['daily_date'] = today

async def update_quest_progress(message, data, tipe, jumlah=1, extra=None):
    """Update progress quest dan kirim notif jika selesai"""
    reset_daily_quest_if_needed(data)
    q = get_quest_data(data)
    notif = []

    # Cek daily quests
    for quest in DAILY_QUESTS:
        if quest['id'] in q['daily_done']:
            continue
        if quest['tipe'] != tipe:
            continue
        q['daily'][quest['id']] = q['daily'].get(quest['id'], 0) + jumlah
        if q['daily'][quest['id']] >= quest['target']:
            q['daily_done'].append(quest['id'])
            data['xp'] += quest['reward_xp']
            data['gold'] += quest['reward_gold']
            cek_level_up(data)
            notif.append(f'📋 **Quest Harian Selesai!** {quest["nama"]}\n🎁 Reward: +{quest["reward_xp"]} XP, +{quest["reward_gold"]} Gold')

    # Cek main quests
    for quest in MAIN_QUESTS:
        if quest['id'] in q['main_done']:
            continue
        # Cek tipe khusus
        if quest['tipe'] == 'gold_total':
            q['main'][quest['id']] = data['gold']
        elif quest['tipe'] == 'level':
            q['main'][quest['id']] = data['level']
        elif quest['tipe'] == 'inventory_count':
            q['main'][quest['id']] = len(data.get('inventory', {}))
        elif quest['tipe'] == tipe:
            q['main'][quest['id']] = q['main'].get(quest['id'], 0) + jumlah
        elif quest['tipe'] == 'dungeon_clear_gunung' and tipe == 'dungeon_clear' and extra == 'gunung':
            q['main'][quest['id']] = q['main'].get(quest['id'], 0) + 1
        else:
            continue

        if q['main'].get(quest['id'], 0) >= quest['target']:
            q['main_done'].append(quest['id'])
            data['xp'] += quest['reward_xp']
            data['gold'] += quest['reward_gold']
            cek_level_up(data)
            notif.append(f'🏅 **Main Quest Selesai!** {quest["nama"]}\n🎁 Reward: +{quest["reward_xp"]} XP, +{quest["reward_gold"]} Gold')

    for n in notif:
        await message.channel.send(f'{message.author.mention} {n}')

def get_user(user_id):
    if user_id not in user_data:
        user_data[user_id] = {
            'gold': 100, 'hp': 100, 'xp': 0, 'level': 1,
            'last_daily': None, 'last_adventure': None,
            'last_dungeon': None, 'last_boss': None, 'last_hunt': None,
            'inventory': {}, 'wins': 0, 'losses': 0,
            'max_hp': 100, 'atk': 10, 'def': 5,
            'pet': None, 'pet_exp': 0, 'pet_level': 1,
            'gems': {}, 'loot': [], 'atk_bonus': 0, 'def_bonus': 0, 'hp_bonus': 0,
        }
    data = user_data[user_id]
    for key, default in [
        ('inventory', {}), ('wins', 0), ('losses', 0),
        ('max_hp', 100), ('atk', 10), ('def', 5),
        ('last_dungeon', None), ('last_boss', None), ('last_hunt', None),
        ('pet', None), ('pet_exp', 0), ('pet_level', 1),
        ('gems', {}), ('loot', []), ('atk_bonus', 0), ('def_bonus', 0), ('hp_bonus', 0),
    ]:
        if key not in data:
            data[key] = default
    return data

def get_pet_bonus(data, stat):
    pet_key = data.get('pet')
    if not pet_key or pet_key not in PETS:
        return 0
    pet = PETS[pet_key]
    pet_lv = data.get('pet_level', 1)
    multiplier = 1 + (pet_lv - 1) * 0.1  # +10% per level
    return int(pet.get(f'{stat}_bonus', 0) * multiplier)

def get_atk(data):
    base = data['atk'] + data.get('atk_bonus', 0)
    inv = data.get('inventory', {})
    if 'sword' in inv: base += 10
    if 'axe' in inv: base += 20
    base += get_pet_bonus(data, 'atk')
    return base

def get_def(data):
    base = data['def'] + data.get('def_bonus', 0)
    inv = data.get('inventory', {})
    if 'shield' in inv: base += 10
    if 'armor' in inv: base += 20
    base += get_pet_bonus(data, 'def')
    return base

def get_max_hp(data):
    base = data.get('max_hp', 100) + data.get('hp_bonus', 0)
    base += get_pet_bonus(data, 'hp')
    return base

def get_active_gems(data):
    """Return list gem keys yang sedang dipasang (max 3)"""
    return list(data.get('gems', {}).keys())

def apply_gem_effects(data, base_atk, base_def, base_loot_mult=1.0):
    """Apply gem effects ke hunting stats, return (atk, def, loot_mult, has_lifesteal, no_hp_loss)"""
    gems_active = get_active_gems(data)
    atk, def_ = base_atk, base_def
    loot_mult = base_loot_mult
    has_lifesteal = False
    no_hp_loss = False
    for g in gems_active:
        if g not in GEMS: continue
        efek = GEMS[g]['efek']
        if efek == 'atk+5': atk += 5
        elif efek == 'def+5': def_ += 5
        elif efek == 'atk+15': atk += 15
        elif efek == 'spd+10': loot_mult *= 1.3
        elif efek == 'hp+20': no_hp_loss = True
        elif efek == 'lifesteal': has_lifesteal = True
        elif efek == 'allstats+10': atk += 10; def_ += 10
        elif efek == 'x2_loot': loot_mult *= 2.0
    return atk, def_, loot_mult, has_lifesteal, no_hp_loss

def cek_pet_levelup(data):
    naik = False
    while data['pet_exp'] >= data['pet_level'] * PET_EXP_PER_LEVEL:
        data['pet_exp'] -= data['pet_level'] * PET_EXP_PER_LEVEL
        data['pet_level'] += 1
        naik = True
    return naik

def cek_level_up(data):
    naik = False
    while data['xp'] >= data['level'] * 100:
        data['xp'] -= data['level'] * 100
        data['level'] += 1
        data['max_hp'] = 100 + (data['level'] - 1) * 10
        data['atk'] = 10 + (data['level'] - 1) * 2
        data['def'] = 5 + (data['level'] - 1) * 1
        data['hp'] = data['max_hp']
        naik = True
    return naik

# ===== UTIL AFK =====
def format_durasi(delta):
    detik = int(delta.total_seconds())
    hari, sisa = divmod(detik, 86400)
    jam, sisa = divmod(sisa, 3600)
    menit, detik = divmod(sisa, 60)

    bagian = []
    if hari > 0:
        bagian.append(f'{hari} hari')
    if jam > 0:
        bagian.append(f'{jam} jam')
    if menit > 0:
        bagian.append(f'{menit} menit')
    if detik > 0 and not bagian:
        bagian.append(f'{detik} detik')

    return ' '.join(bagian) if bagian else 'beberapa saat'

async def play_next(guild):
    if guild.id in queues and queues[guild.id]:
        url, title, channel = queues[guild.id].pop(0)
        vc = guild.voice_client
        if vc:
            source = discord.FFmpegPCMAudio(url, **ffmpeg_opts)
            vc.play(source, after=lambda e: asyncio.run_coroutine_threadsafe(play_next(guild), client.loop))
            asyncio.run_coroutine_threadsafe(channel.send(f'\u25B6\uFE0F Memutar: **{title}**'), client.loop)

def punya_akses(member):
    return any(role.name in ROLE_ADMIN for role in member.roles)

@client.event
async def on_ready():
    print(f'Bot {client.user} online!')

@client.event
async def on_voice_state_update(member, before, after):
    if member.id != client.user.id:
        return

    if before.channel is not None and after.channel is None:
        guild_id = member.guild.id

        if intentional_leave.get(guild_id):
            intentional_leave[guild_id] = False
            return

        channel = last_voice_channel.get(guild_id)
        if channel:
            await asyncio.sleep(2)
            try:
                vc = await channel.connect()
                await vc.guild.change_voice_state(channel=channel, self_deaf=True)
                print(f'Auto-rejoin ke {channel.name}')
            except Exception as e:
                print(f'Gagal auto-rejoin: {e}')

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    content = message.content.strip()

    # ===== AFK SYSTEM =====
    for mention in message.mentions:
        if mention.id in afk_users:
            data = afk_users[mention.id]
            durasi = format_durasi(datetime.datetime.now() - data['waktu'])
            await message.channel.send(f'\U0001F4A4 **{mention.display_name}** sedang AFK sejak {durasi} yang lalu: {data["alasan"]}')

    if message.author.id in afk_users:
        if not content.startswith('?afk'):
            data = afk_users.pop(message.author.id)
            nick_lama = data['nick_lama']
            durasi = format_durasi(datetime.datetime.now() - data['waktu'])
            try:
                await message.author.edit(nick=nick_lama)
            except:
                pass
            await message.channel.send(f'\u2705 **{message.author.display_name}** sudah tidak AFK! (AFK selama {durasi})')

    if content.startswith('?afk'):
        alasan = content[4:].strip() or 'Tidak ada alasan'
        nick_lama = message.author.nick or message.author.name
        afk_users[message.author.id] = {
            'alasan': alasan,
            'nick_lama': nick_lama,
            'waktu': datetime.datetime.now()
        }
        try:
            await message.author.edit(nick=f'[AFK] {nick_lama}')
        except:
            pass
        await message.channel.send(f'\U0001F4A4 **{message.author.display_name}** sekarang AFK: {alasan}')

    # ===== VOICE =====
    if content == '?join':
        if message.author.voice:
            channel = message.author.voice.channel
            vc = await channel.connect()
            await vc.guild.change_voice_state(channel=channel, self_deaf=True)
            last_voice_channel[message.guild.id] = channel
            await message.channel.send(f'\u2705 Joined **{channel.name}**!')
        else:
            await message.channel.send('Kamu harus masuk voice channel dulu!')

    if content == '?leave':
        if not punya_akses(message.author):
            await message.channel.send('\u274C Kamu tidak punya permission!')
            return
        if message.guild.voice_client:
            if message.guild.id in queues:
                queues[message.guild.id] = []
            intentional_leave[message.guild.id] = True
            last_voice_channel.pop(message.guild.id, None)
            await message.guild.voice_client.disconnect()
            await message.channel.send('\U0001F44B Bot keluar dari voice channel!')

    # ===== MUSIK =====
    if content.startswith('?play '):
        query = content[6:]
        vc = message.guild.voice_client
        if not vc:
            await message.channel.send('Bot belum di voice channel! Ketik `?join` dulu.')
            return
        await message.channel.send(f'\U0001F50D Mencari: **{query}**')
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
                await message.channel.send(f'\U0001F4CB **{added} lagu** ditambahkan dari playlist!')
                if not vc.is_playing():
                    await play_next(message.guild)
            else:
                url = info['url']
                title = info.get('title', 'Unknown')
                if vc.is_playing():
                    queues[message.guild.id].append((url, title, message.channel))
                    await message.channel.send(f'\u2795 Ditambahkan ke antrian: **{title}**')
                else:
                    source = discord.FFmpegPCMAudio(url, **ffmpeg_opts)
                    vc.play(source, after=lambda e: asyncio.run_coroutine_threadsafe(play_next(message.guild), client.loop))
                    await message.channel.send(f'\u25B6\uFE0F Memutar: **{title}**')
        except Exception as e:
            await message.channel.send(f'\u274C Gagal: {str(e)}')

    if content == '?skip':
        vc = message.guild.voice_client
        if vc and vc.is_playing():
            vc.stop()
            await message.channel.send('\u23ED\uFE0F Lagu diskip!')
        else:
            await message.channel.send('Tidak ada lagu yang sedang diputar!')

    if content == '?queue':
        if message.guild.id in queues and queues[message.guild.id]:
            list_lagu = '\n'.join([f'{i+1}. {t}' for i, (_, t, _) in enumerate(queues[message.guild.id][:10])])
            total = len(queues[message.guild.id])
            await message.channel.send(f'\U0001F4CB Antrian lagu ({total} total):\n{list_lagu}')
        else:
            await message.channel.send('Antrian kosong!')

    if content == '?stop':
        vc = message.guild.voice_client
        if vc and vc.is_playing():
            if message.guild.id in queues:
                queues[message.guild.id] = []
            vc.stop()
            await message.channel.send('\u23F9\uFE0F Musik dihentikan!')

    # ===== FUN COMMANDS =====
    if content.startswith('?8ball '):
        pertanyaan = content[7:]
        jawaban = random.choice(JAWABAN_8BALL)
        await message.channel.send(f'\U0001F3B1 **Pertanyaan:** {pertanyaan}\n**Jawaban:** {jawaban}')

    if content == '?roll':
        hasil = random.randint(1, 6)
        await message.channel.send(f'\U0001F3B2 **{message.author.display_name}** melempar dadu dan mendapat: **{hasil}**')

    if content == '?coinflip':
        hasil = random.choice(['Head \U0001FA99', 'Tail \U0001FA99'])
        await message.channel.send(f'\U0001FA99 Hasilnya: **{hasil}**')

    if content.startswith('?ship'):
        if len(message.mentions) >= 2:
            user1, user2 = message.mentions[0], message.mentions[1]
        elif len(message.mentions) == 1:
            user1, user2 = message.author, message.mentions[0]
        else:
            await message.channel.send('Mention 1-2 orang ya! Contoh: `?ship @user1 @user2`')
            return
        persen = random.randint(0, 100)
        await message.channel.send(f'\U0001F495 **{user1.display_name}** + **{user2.display_name}** = **{persen}%** cocok!')

    if content.startswith('?rate '):
        target = content[6:]
        nilai = random.randint(1, 10)
        await message.channel.send(f'\u2B50 **{target}** aku kasih rating: **{nilai}/10**')

    if content == '?jokes':
        await message.channel.send(random.choice(JOKES))

    if content == '?truth':
        await message.channel.send(f'\U0001F914 **Truth:** {random.choice(TRUTH)}')

    if content == '?dare':
        await message.channel.send(f'\U0001F525 **Dare:** {random.choice(DARE)}')

    # ===== ADVENTURE / RPG =====
    if content == '?adventure':
        data = get_user(message.author.id)
        now = datetime.datetime.now()

        if data['last_adventure'] and (now - data['last_adventure']).total_seconds() < 300:
            sisa = 300 - int((now - data['last_adventure']).total_seconds())
            await message.channel.send(f'\u23F3 Tunggu **{sisa} detik** lagi sebelum adventure lagi!')
            return

        if data['hp'] <= 0:
            await message.channel.send('\U0001F480 HP kamu habis! Gunakan `?heal` untuk pulihkan HP.')
            return

        pesan, stat, jumlah = random.choice(ADVENTURE_EVENTS)
        data[stat] += jumlah
        data['last_adventure'] = now

        if data['hp'] < 0:
            data['hp'] = 0
        if data['gold'] < 0:
            data['gold'] = 0

        hasil_text = f'{pesan}\n'
        if stat == 'gold':
            hasil_text += f'{"\u2795" if jumlah > 0 else "\u2796"} {abs(jumlah)} Gold (Total: {data["gold"]})'
        elif stat == 'hp':
            hasil_text += f'{"\u2795" if jumlah > 0 else "\u2796"} {abs(jumlah)} HP (Total: {data["hp"]}/100)'
        elif stat == 'xp':
            hasil_text += f'\u2795 {jumlah} XP (Total: {data["xp"]})'

        naik = cek_level_up(data)
        if naik:
            hasil_text += f'\n\U0001F389 **LEVEL UP!** Sekarang Level **{data["level"]}**! HP dipulihkan ke 100.'

        await message.channel.send(f'\U0001F5FA\uFE0F **{message.author.display_name}** pergi berpetualang...\n\n{hasil_text}')
        await update_quest_progress(message, data, 'adventure')
        if stat == 'gold' and jumlah > 0:
            await update_quest_progress(message, data, 'earn_gold', jumlah)

    if content == '?profile':
        data = get_user(message.author.id)
        inv = data.get('inventory', {})
        inv_text = ', '.join([SHOP_ITEMS[k]['nama'] for k in inv]) if inv else 'Kosong'
        max_hp = get_max_hp(data)
        pet_key = data.get('pet')
        pet_text = f'{PETS[pet_key]["nama"]} (Lv.{data["pet_level"]}, EXP:{data["pet_exp"]}/{data["pet_level"]*PET_EXP_PER_LEVEL})' if pet_key else 'Belum punya pet'
        gems_active = get_active_gems(data)
        gems_text = ', '.join([GEMS[g]['nama'] for g in gems_active]) if gems_active else 'Kosong'
        loot_list = data.get('loot', [])
        loot_text = ', '.join([l['nama'] for l in loot_list]) if loot_list else 'Kosong'
        embed_text = (
            f'👤 **Profile {message.author.display_name}**\n'
            f'🏆 Level: **{data["level"]}** | ⚔️ W/L: {data.get("wins",0)}/{data.get("losses",0)}\n'
            f'✨ XP: {data["xp"]}/{data["level"] * 100}\n'
            f'❤️ HP: {data["hp"]}/{max_hp}\n'
            f'💰 Gold: {data["gold"]}\n'
            f'⚔️ ATK: {get_atk(data)} | 🛡️ DEF: {get_def(data)}\n'
            f'🐾 Pet: {pet_text}\n'
            f'💎 Gems Aktif: {gems_text}\n'
            f'🎁 Rare Loot: {loot_text}\n'
            f'🎒 Inventory: {inv_text}'
        )
        await message.channel.send(embed_text)

    if content == '?daily':
        data = get_user(message.author.id)
        now = datetime.datetime.now()

        if data['last_daily'] and (now - data['last_daily']).total_seconds() < 86400:
            sisa = 86400 - int((now - data['last_daily']).total_seconds())
            jam = sisa // 3600
            menit = (sisa % 3600) // 60
            await message.channel.send(f'\u23F3 Kamu sudah klaim daily! Tunggu **{jam} jam {menit} menit** lagi.')
            return

        hadiah = random.randint(50, 150)
        data['gold'] += hadiah
        data['last_daily'] = now
        await message.channel.send(f'\U0001F381 **{message.author.display_name}** klaim daily reward: **+{hadiah} Gold**! (Total: {data["gold"]})')

    if content == '?heal':
        data = get_user(message.author.id)
        max_hp = data.get('max_hp', 100)
        biaya = 30
        if data['gold'] < biaya:
            await message.channel.send(f'❌ Gold tidak cukup! Butuh {biaya} Gold untuk heal.')
            return
        if data['hp'] >= max_hp:
            await message.channel.send('❤️ HP kamu sudah penuh!')
            return
        data['gold'] -= biaya
        data['hp'] = max_hp
        await message.channel.send(f'💊 **{message.author.display_name}** heal! HP kembali penuh ({max_hp}). (-{biaya} Gold)')
        await update_quest_progress(message, data, 'heal')

    # ===== SHOP =====
    if content == '?shop':
        teks = '🏪 **TOKO PETUALANG**\n\n'
        for key, item in SHOP_ITEMS.items():
            teks += f'`{key}` — {item["nama"]} | 💰 {item["harga"]} Gold\n> {item["deskripsi"]}\n\n'
        teks += 'Beli dengan: `?buy <item>`'
        await message.channel.send(teks)

    if content.startswith('?buy '):
        item_key = content[5:].strip().lower()
        data = get_user(message.author.id)
        if item_key not in SHOP_ITEMS:
            await message.channel.send(f'❌ Item tidak ditemukan! Cek `?shop` dulu.')
            return
        item = SHOP_ITEMS[item_key]
        if data['gold'] < item['harga']:
            await message.channel.send(f'❌ Gold tidak cukup! Butuh {item["harga"]} Gold.')
            return
        # Potion & elixir langsung pakai
        if item_key == 'potion':
            data['hp'] = min(data.get('max_hp', 100), data['hp'] + 50)
            data['gold'] -= item['harga']
            await message.channel.send(f'🧪 Kamu minum ramuan! HP +50 (Sekarang: {data["hp"]}). (-{item["harga"]} Gold)')
        elif item_key == 'elixir':
            data['hp'] = data.get('max_hp', 100)
            data['xp'] += 20
            data['gold'] -= item['harga']
            await message.channel.send(f'✨ Elixir ajaib! HP penuh + XP +20. (-{item["harga"]} Gold)')
        else:
            if item_key in data.get('inventory', {}):
                await message.channel.send(f'⚠️ Kamu sudah punya {item["nama"]}!')
                return
            data['inventory'][item_key] = True
            data['gold'] -= item['harga']
            await message.channel.send(f'✅ Berhasil membeli **{item["nama"]}**! (-{item["harga"]} Gold)')
            await update_quest_progress(message, data, 'inventory_count')

    if content.startswith('?sell '):
        item_key = content[6:].strip().lower()
        data = get_user(message.author.id)
        if item_key not in data.get('inventory', {}):
            await message.channel.send(f'❌ Kamu tidak punya item itu!')
            return
        harga_jual = SHOP_ITEMS[item_key]['harga'] // 2
        del data['inventory'][item_key]
        data['gold'] += harga_jual
        await message.channel.send(f'💸 Item **{SHOP_ITEMS[item_key]["nama"]}** dijual seharga **{harga_jual} Gold**!')

    # ===== DUNGEON =====
    if content == '?dungeon':
        teks = '🗺️ **DAFTAR DUNGEON**\n\n'
        for key, d in DUNGEONS.items():
            teks += f'`{key}` — {d["nama"]}\n> Min Level: {d["min_level"]} | Biaya: {d["harga"]} Gold\n> Boss: {d["boss"]} | Reward: {d["reward_xp"]} XP + {d["reward_gold"]} Gold\n\n'
        teks += 'Masuk dengan: `?dungeon <nama>`'
        await message.channel.send(teks)

    if content.startswith('?dungeon ') and len(content) > 9:
        key = content[9:].strip().lower()
        if key not in DUNGEONS:
            await message.channel.send('❌ Dungeon tidak ditemukan! Ketik `?dungeon` untuk daftar.')
            return
        data = get_user(message.author.id)
        dungeon = DUNGEONS[key]
        now = datetime.datetime.now()
        cooldown = 600
        if data['last_dungeon'] and (now - data['last_dungeon']).total_seconds() < cooldown:
            sisa = cooldown - int((now - data['last_dungeon']).total_seconds())
            await message.channel.send(f'⏳ Kamu masih lelah! Tunggu **{sisa} detik** untuk dungeon lagi.')
            return
        if data['level'] < dungeon['min_level']:
            await message.channel.send(f'❌ Level kamu terlalu rendah! Butuh Level {dungeon["min_level"]}.')
            return
        if data['gold'] < dungeon['harga']:
            await message.channel.send(f'❌ Gold tidak cukup! Butuh {dungeon["harga"]} Gold untuk masuk.')
            return
        if data['hp'] <= 20:
            await message.channel.send('💔 HP kamu terlalu rendah untuk masuk dungeon! Heal dulu.')
            return

        data['gold'] -= dungeon['harga']
        data['last_dungeon'] = now

        # Simulasi dungeon
        cerita = f'⚔️ **{message.author.display_name}** memasuki {dungeon["nama"]}!\n\n'
        for e in dungeon['event']:
            cerita += f'▸ {e}\n'

        # Battle boss
        player_hp = data['hp']
        boss_hp = dungeon['boss_hp']
        ronde = 0
        while player_hp > 0 and boss_hp > 0 and ronde < 10:
            dmg_ke_boss = max(1, get_atk(data) + random.randint(-3, 5) - random.randint(0, 3))
            dmg_ke_player = max(1, random.randint(10, 25) - get_def(data) + random.randint(0, 5))
            boss_hp -= dmg_ke_boss
            player_hp -= dmg_ke_player
            ronde += 1

        if player_hp > 0:
            data['hp'] = max(1, player_hp)
            data['xp'] += dungeon['reward_xp']
            data['gold'] += dungeon['reward_gold']
            naik = cek_level_up(data)
            cerita += f'\n🏆 **BOSS {dungeon["boss"]} KALAH!**\n'
            cerita += f'✅ Reward: +{dungeon["reward_xp"]} XP, +{dungeon["reward_gold"]} Gold!\n'
            cerita += f'❤️ HP tersisa: {data["hp"]}'
            if naik:
                cerita += f'\n🎉 **LEVEL UP! Level {data["level"]}!**'
        else:
            data['hp'] = 1
            data['gold'] = max(0, data['gold'] - 20)
            cerita += f'\n💀 **Kamu kalah dari {dungeon["boss"]}!** HP tersisa 1, kehilangan 20 Gold.'

        await message.channel.send(cerita)
        if player_hp > 0:
            await update_quest_progress(message, data, 'dungeon_clear', extra=key)
            await update_quest_progress(message, data, 'gold_total')
    if content.startswith('?duel ') and message.mentions:
        target = message.mentions[0]
        if target.id == message.author.id:
            await message.channel.send('❌ Kamu tidak bisa duel diri sendiri!')
            return
        if target.bot:
            await message.channel.send('❌ Tidak bisa duel bot!')
            return
        duel_requests[message.author.id] = {'target': target.id, 'channel': message.channel}
        await message.channel.send(
            f'⚔️ **{message.author.display_name}** menantang **{target.display_name}** duel!\n'
            f'{target.mention} ketik `?accept` untuk menerima atau `?decline` untuk menolak.'
        )

    if content == '?accept':
        challenger_id = next((k for k, v in duel_requests.items() if v['target'] == message.author.id), None)
        if not challenger_id:
            await message.channel.send('❌ Tidak ada tantangan duel untukmu!')
            return

        ch_data = get_user(challenger_id)
        tg_data = get_user(message.author.id)
        challenger = message.guild.get_member(challenger_id)
        del duel_requests[challenger_id]

        if ch_data['hp'] <= 0 or tg_data['hp'] <= 0:
            await message.channel.send('❌ Salah satu pemain HP-nya habis! Tidak bisa duel.')
            return

        # Battle simulasi
        ch_hp = ch_data['hp']
        tg_hp = tg_data['hp']
        log = f'⚔️ **DUEL: {challenger.display_name} vs {message.author.display_name}**\n\n'
        ronde = 0
        while ch_hp > 0 and tg_hp > 0 and ronde < 15:
            dmg_ch = max(1, get_atk(ch_data) + random.randint(-2, 5) - get_def(tg_data))
            dmg_tg = max(1, get_atk(tg_data) + random.randint(-2, 5) - get_def(ch_data))
            ch_hp -= dmg_tg
            tg_hp -= dmg_ch
            ronde += 1

        taruhan = min(50, ch_data['gold'], tg_data['gold'])
        if ch_hp > tg_hp:
            winner, loser = challenger, message.author
            w_data, l_data = ch_data, tg_data
        else:
            winner, loser = message.author, challenger
            w_data, l_data = tg_data, ch_data

        w_data['gold'] += taruhan
        l_data['gold'] = max(0, l_data['gold'] - taruhan)
        w_data['wins'] = w_data.get('wins', 0) + 1
        l_data['losses'] = l_data.get('losses', 0) + 1
        w_data['xp'] += 20
        naik = cek_level_up(w_data)

        log += f'🏆 **{winner.display_name} MENANG!** setelah {ronde} ronde!\n'
        log += f'💰 {winner.display_name} mendapat {taruhan} Gold dari {loser.display_name}\n'
        log += f'✨ {winner.display_name} mendapat +20 XP!'
        if naik:
            log += f'\n🎉 {winner.display_name} LEVEL UP ke Level {w_data["level"]}!'

        await message.channel.send(log)
        # Update quest untuk pemenang
        winner_id = winner.id
        w_msg_author = message.author if winner.id == message.author.id else challenger
        await update_quest_progress(message, w_data, 'duel_win')
        challenger_id = next((k for k, v in duel_requests.items() if v['target'] == message.author.id), None)
        if challenger_id:
            del duel_requests[challenger_id]
            await message.channel.send(f'❌ **{message.author.display_name}** menolak tantangan duel!')

    # ===== GAMBLING =====
    if content.startswith('?gamble '):
        try:
            taruhan = int(content[8:].strip())
        except:
            await message.channel.send('❌ Format salah! Contoh: `?gamble 50`')
            return
        data = get_user(message.author.id)
        if taruhan <= 0:
            await message.channel.send('❌ Taruhan harus lebih dari 0!')
            return
        if taruhan > data['gold']:
            await message.channel.send(f'❌ Gold tidak cukup! Kamu punya {data["gold"]} Gold.')
            return
        hasil = random.randint(1, 100)
        if hasil <= 45:
            data['gold'] += taruhan
            await message.channel.send(f'🎰 **MENANG!** (Angka: {hasil}) Kamu mendapat **+{taruhan} Gold**! Total: {data["gold"]} Gold')
        elif hasil <= 85:
            data['gold'] -= taruhan
            data['gold'] = max(0, data['gold'])
            await message.channel.send(f'🎰 **KALAH!** (Angka: {hasil}) Kamu kehilangan **{taruhan} Gold**. Total: {data["gold"]} Gold')
        else:
            jackpot = taruhan * 3
            data['gold'] += jackpot
            await message.channel.send(f'🎰 **JACKPOT!!** 🎉 (Angka: {hasil}) Kamu mendapat **+{jackpot} Gold**! Total: {data["gold"]} Gold')
        await update_quest_progress(message, data, 'gamble')
        await update_quest_progress(message, data, 'gold_total')

    # ===== WORLD BOSS =====
    if content == '?bossspawn' and punya_akses(message.author):
        global world_boss_active, world_boss_participants
        boss = random.choice(WORLD_BOSSES)
        world_boss_active = {'nama': boss['nama'], 'hp': boss['hp'], 'max_hp': boss['hp'],
                              'reward_xp': boss['reward_xp'], 'reward_gold': boss['reward_gold']}
        world_boss_participants = {}
        await message.channel.send(
            f'🌍 **WORLD BOSS MUNCUL!** {boss["nama"]}\n'
            f'💀 HP: {boss["hp"]}\n'
            f'Gunakan `?bossattack` untuk menyerang! Boss akan hilang dalam 5 menit.'
        )

    if content == '?bossattack':
        global world_boss_active, world_boss_participants
        if not world_boss_active:
            await message.channel.send('❌ Tidak ada World Boss aktif saat ini!')
            return
        data = get_user(message.author.id)
        if data['hp'] <= 0:
            await message.channel.send('❌ HP kamu habis! Tidak bisa menyerang boss.')
            return
        dmg = get_atk(data) + random.randint(5, 20)
        world_boss_active['hp'] = max(0, world_boss_active['hp'] - dmg)
        world_boss_participants[message.author.id] = world_boss_participants.get(message.author.id, 0) + dmg

        if world_boss_active['hp'] <= 0:
            hasil = f'💥 **{world_boss_active["nama"]} DIKALAHKAN!**\n\n'
            hasil += '🏆 **Kontribusi damage:**\n'
            sorted_p = sorted(world_boss_participants.items(), key=lambda x: x[1], reverse=True)
            for uid, dmg_total in sorted_p:
                member = message.guild.get_member(uid)
                if member:
                    u_data = get_user(uid)
                    u_data['xp'] += world_boss_active['reward_xp']
                    u_data['gold'] += world_boss_active['reward_gold']
                    cek_level_up(u_data)
                    hasil += f'▸ {member.display_name}: {dmg_total} damage | +{world_boss_active["reward_xp"]} XP, +{world_boss_active["reward_gold"]} Gold\n'
            world_boss_active = None
            world_boss_participants = {}
            await message.channel.send(hasil)
        else:
            await message.channel.send(
                f'⚔️ **{message.author.display_name}** menyerang {world_boss_active["nama"]} sebesar **{dmg} damage**!\n'
                f'💀 HP Boss: {world_boss_active["hp"]}/{world_boss_active["max_hp"]}'
            )
        await update_quest_progress(message, data, 'boss_attack')
    if content == '?top':
        if not user_data:
            await message.channel.send('Belum ada data pemain!')
            return
        sorted_users = sorted(user_data.items(), key=lambda x: (x[1]['level'], x[1]['xp']), reverse=True)
        teks = '🏆 **LEADERBOARD TOP 10**\n\n'
        medals = ['🥇', '🥈', '🥉']
        for i, (uid, d) in enumerate(sorted_users[:10]):
            member = message.guild.get_member(uid)
            nama = member.display_name if member else f'User#{uid}'
            medal = medals[i] if i < 3 else f'{i+1}.'
            teks += f'{medal} **{nama}** — Lv.{d["level"]} | {d["gold"]} Gold | W:{d.get("wins",0)}\n'
        await message.channel.send(teks)

    # ===== EXPLORE (mini-game area baru) =====
    if content == '?explore':
        data = get_user(message.author.id)
        now = datetime.datetime.now()
        if data['last_adventure'] and (now - data['last_adventure']).total_seconds() < 300:
            sisa = 300 - int((now - data['last_adventure']).total_seconds())
            await message.channel.send(f'⏳ Tunggu **{sisa} detik** lagi sebelum explore lagi!')
            return
        lokasi = random.choice([
            ('🏔️ Pegunungan Utara', 'xp', random.randint(20, 60)),
            ('🌊 Pantai Misterius', 'gold', random.randint(30, 80)),
            ('🏜️ Gurun Tandus', 'hp', -random.randint(10, 25)),
            ('🌸 Padang Bunga Sakura', 'hp', random.randint(15, 35)),
            ('🌑 Gua Kegelapan', 'gold', random.randint(-40, 100)),
            ('🏛️ Reruntuhan Kuno', 'xp', random.randint(40, 80)),
        ])
        nama_lokasi, stat, jumlah = lokasi
        data[stat] = max(0, data[stat] + jumlah)
        data['last_adventure'] = now
        naik = cek_level_up(data)
        sign = '+' if jumlah >= 0 else ''
        teks = f'🗺️ **{message.author.display_name}** menjelajah ke **{nama_lokasi}**!\n'
        teks += f'{"✅" if jumlah >= 0 else "⚠️"} {sign}{jumlah} {stat.upper()} (Sekarang: {data[stat]})'
        if naik:
            teks += f'\n🎉 **LEVEL UP! Level {data["level"]}!**'
        await message.channel.send(teks)
        await update_quest_progress(message, data, 'explore')
        if stat == 'gold' and jumlah > 0:
            await update_quest_progress(message, data, 'earn_gold', jumlah)
        await update_quest_progress(message, data, 'level')

    # ===== QUEST =====
    if content == '?quest':
        data = get_user(message.author.id)
        reset_daily_quest_if_needed(data)
        q = get_quest_data(data)
        teks = '📋 **QUEST KAMU**\n\n'

        teks += '**📅 Daily Quest** (reset tiap hari)\n'
        for quest in DAILY_QUESTS:
            done = quest['id'] in q['daily_done']
            progress = q['daily'].get(quest['id'], 0)
            bar_fill = min(10, int((progress / quest['target']) * 10))
            bar = '█' * bar_fill + '░' * (10 - bar_fill)
            status = '✅' if done else f'`[{bar}]` {progress}/{quest["target"]}'
            teks += f'{"~~" if done else ""}{quest["nama"]}{"~~" if done else ""} — {status}\n'
            if not done:
                teks += f'> {quest["deskripsi"]} | 🎁 +{quest["reward_xp"]} XP, +{quest["reward_gold"]} Gold\n'
        teks += '\n'

        teks += '**🏅 Main Quest** (permanen)\n'
        for quest in MAIN_QUESTS:
            done = quest['id'] in q['main_done']
            progress = q['main'].get(quest['id'], 0)
            bar_fill = min(10, int((progress / quest['target']) * 10))
            bar = '█' * bar_fill + '░' * (10 - bar_fill)
            status = '✅ SELESAI' if done else f'`[{bar}]` {progress}/{quest["target"]}'
            teks += f'{"~~" if done else ""}{quest["nama"]}{"~~" if done else ""} — {status}\n'
            if not done:
                teks += f'> {quest["deskripsi"]} | 🎁 +{quest["reward_xp"]} XP, +{quest["reward_gold"]} Gold\n'

        await message.channel.send(teks)

    # ===== PET SYSTEM =====
    if content == '?petshop':
        teks = '🐾 **PET SHOP**\n\n'
        for key, pet in PETS.items():
            teks += (
                f'`{key}` — {pet["nama"]} | 💰 {pet["harga"]} Gold\n'
                f'> ⚔️ ATK+{pet["atk_bonus"]} | 🛡️ DEF+{pet["def_bonus"]} | ❤️ HP+{pet["hp_bonus"]}\n'
                f'> 💥 Skill: **{pet["skill"]}** ({pet["skill_dmg"]} dmg)\n'
                f'> {pet["deskripsi"]}\n\n'
            )
        teks += 'Beli dengan: `?buypet <nama>`'
        await message.channel.send(teks)

    if content.startswith('?buypet '):
        pet_key = content[8:].strip().lower()
        data = get_user(message.author.id)
        if pet_key not in PETS:
            await message.channel.send('❌ Pet tidak ditemukan! Ketik `?petshop` untuk daftar.')
            return
        if data.get('pet') == pet_key:
            await message.channel.send('⚠️ Kamu sudah punya pet ini!')
            return
        pet = PETS[pet_key]
        if data['gold'] < pet['harga']:
            await message.channel.send(f'❌ Gold tidak cukup! Butuh {pet["harga"]} Gold.')
            return
        old_pet = data.get('pet')
        data['gold'] -= pet['harga']
        data['pet'] = pet_key
        data['pet_exp'] = 0
        data['pet_level'] = 1
        pesan = f'🐾 **{message.author.display_name}** mendapatkan pet **{pet["nama"]}**! (-{pet["harga"]} Gold)\n'
        pesan += f'> ⚔️ ATK+{get_pet_bonus(data,"atk")} | 🛡️ DEF+{get_pet_bonus(data,"def")} | ❤️ HP+{get_pet_bonus(data,"hp")}'
        if old_pet:
            pesan += f'\n> (Pet lama {PETS[old_pet]["nama"]} dilepas)'
        await message.channel.send(pesan)

    if content == '?pet':
        data = get_user(message.author.id)
        pet_key = data.get('pet')
        if not pet_key:
            await message.channel.send('🐾 Kamu belum punya pet! Beli di `?petshop`.')
            return
        pet = PETS[pet_key]
        pet_lv = data['pet_level']
        pet_exp = data['pet_exp']
        exp_needed = pet_lv * PET_EXP_PER_LEVEL
        bar_fill = min(10, int((pet_exp / exp_needed) * 10))
        bar = '█' * bar_fill + '░' * (10 - bar_fill)
        teks = (
            f'🐾 **Pet Kamu: {pet["nama"]}**\n'
            f'⭐ Level: {pet_lv} | EXP: `[{bar}]` {pet_exp}/{exp_needed}\n'
            f'⚔️ ATK Bonus: +{get_pet_bonus(data,"atk")} | 🛡️ DEF Bonus: +{get_pet_bonus(data,"def")} | ❤️ HP Bonus: +{get_pet_bonus(data,"hp")}\n'
            f'💥 Skill: **{pet["skill"]}** ({int(pet["skill_dmg"] * (1 + (pet_lv-1)*0.1))} dmg)\n'
            f'> Pet exp didapat dari hunting & dungeon'
        )
        await message.channel.send(teks)

    if content.startswith('?petbattle ') and message.mentions:
        target = message.mentions[0]
        data = get_user(message.author.id)
        tg_data = get_user(target.id)
        if not data.get('pet'):
            await message.channel.send('❌ Kamu belum punya pet! Beli di `?petshop`.')
            return
        if not tg_data.get('pet'):
            await message.channel.send(f'❌ **{target.display_name}** belum punya pet!')
            return
        my_pet = PETS[data['pet']]
        tg_pet = PETS[tg_data['pet']]
        my_lv = data['pet_level']
        tg_lv = tg_data['pet_level']
        # Pet battle simulasi
        my_hp = 100 + my_pet['hp_bonus'] * my_lv
        tg_hp = 100 + tg_pet['hp_bonus'] * tg_lv
        log = f'🐾 **PET BATTLE!** {my_pet["nama"]} (Lv.{my_lv}) vs {tg_pet["nama"]} (Lv.{tg_lv})\n\n'
        ronde = 0
        skill_used_me = False
        skill_used_tg = False
        while my_hp > 0 and tg_hp > 0 and ronde < 20:
            # Skill setiap 3 ronde
            if ronde % 3 == 2 and not skill_used_me:
                dmg_me = int(my_pet['skill_dmg'] * (1 + (my_lv-1)*0.1))
                log += f'💥 {my_pet["nama"]} pakai **{my_pet["skill"]}**! ({dmg_me} dmg)\n'
            else:
                dmg_me = my_pet['atk_bonus'] * my_lv + random.randint(5, 15)
            if ronde % 3 == 2 and not skill_used_tg:
                dmg_tg = int(tg_pet['skill_dmg'] * (1 + (tg_lv-1)*0.1))
            else:
                dmg_tg = tg_pet['atk_bonus'] * tg_lv + random.randint(5, 15)
            tg_hp -= dmg_me
            my_hp -= dmg_tg
            ronde += 1

        taruhan_exp = 10
        if my_hp > tg_hp:
            winner_name, loser_name = message.author.display_name, target.display_name
            data['pet_exp'] += 20
            tg_data['pet_exp'] += taruhan_exp
            my_naik = cek_pet_levelup(data)
            tg_naik = cek_pet_levelup(tg_data)
        else:
            winner_name, loser_name = target.display_name, message.author.display_name
            tg_data['pet_exp'] += 20
            data['pet_exp'] += taruhan_exp
            my_naik = cek_pet_levelup(data)
            tg_naik = cek_pet_levelup(tg_data)

        log += f'\n🏆 **{winner_name} MENANG!** (Pet {PETS[data["pet"]]["nama"] if my_hp > tg_hp else PETS[tg_data["pet"]]["nama"]})\n'
        log += f'🐾 Pemenang: +20 Pet EXP | Pecundang: +{taruhan_exp} Pet EXP'
        if my_naik: log += f'\n⭐ {my_pet["nama"]} LEVEL UP ke Level {data["pet_level"]}!'
        if tg_naik: log += f'\n⭐ {tg_pet["nama"]} LEVEL UP ke Level {tg_data["pet_level"]}!'
        await message.channel.send(log)

    # ===== GEMS SYSTEM =====
    if content == '?gems':
        data = get_user(message.author.id)
        gems_inv = data.get('gems', {})
        teks = '💎 **GEMS KAMU**\n\n'
        if not gems_inv:
            teks += 'Belum punya gems! Dapatkan dari `?hunt` atau beli di `?gemshop`.\n'
        else:
            for g_key, jumlah in gems_inv.items():
                if g_key in GEMS:
                    g = GEMS[g_key]
                    aktif = '✅ AKTIF' if jumlah > 0 else ''
                    teks += f'{g["nama"]} x{jumlah} [{g["rarity"]}] {aktif}\n> {g["deskripsi"]}\n'
        teks += '\nPasang gem: `?equipgem <nama>` | Lepas: `?unequipgem <nama>`'
        await message.channel.send(teks)

    if content == '?gemshop':
        teks = '💎 **GEM SHOP**\n\n'
        GEM_PRICES = {
            'fire_gem': 80, 'ice_gem': 80, 'wind_gem': 150, 'earth_gem': 150,
            'thunder_gem': 300, 'dark_gem': 300, 'light_gem': 600, 'chaos_gem': 1500,
        }
        for key, gem in GEMS.items():
            teks += f'`{key}` — {gem["nama"]} [{gem["rarity"]}] | 💰 {GEM_PRICES[key]} Gold\n> {gem["deskripsi"]}\n\n'
        teks += 'Beli: `?buygem <nama>`'
        await message.channel.send(teks)

    if content.startswith('?buygem '):
        GEM_PRICES = {
            'fire_gem': 80, 'ice_gem': 80, 'wind_gem': 150, 'earth_gem': 150,
            'thunder_gem': 300, 'dark_gem': 300, 'light_gem': 600, 'chaos_gem': 1500,
        }
        gem_key = content[8:].strip().lower()
        data = get_user(message.author.id)
        if gem_key not in GEMS:
            await message.channel.send('❌ Gem tidak ditemukan! Ketik `?gemshop` untuk daftar.')
            return
        harga = GEM_PRICES[gem_key]
        if data['gold'] < harga:
            await message.channel.send(f'❌ Gold tidak cukup! Butuh {harga} Gold.')
            return
        data['gold'] -= harga
        data['gems'][gem_key] = data['gems'].get(gem_key, 0) + 1
        await message.channel.send(f'💎 Berhasil membeli **{GEMS[gem_key]["nama"]}**! (-{harga} Gold) | Stok: x{data["gems"][gem_key]}')

    if content.startswith('?equipgem '):
        gem_key = content[10:].strip().lower()
        data = get_user(message.author.id)
        gems_inv = data.get('gems', {})
        if gem_key not in gems_inv or gems_inv[gem_key] <= 0:
            await message.channel.send('❌ Kamu tidak punya gem itu!')
            return
        active = [k for k, v in gems_inv.items() if v > 0 and k in GEMS]
        # count equipped (gems dengan value > 0 tapi kita pakai semua — simplifikasi: semua yg ada di gems = equipped)
        if len(active) >= 3:
            await message.channel.send('⚠️ Slot gem penuh (max 3)! Lepas gem dulu dengan `?unequipgem <nama>`.')
            return
        await message.channel.send(f'💎 **{GEMS[gem_key]["nama"]}** dipasang! Efek: {GEMS[gem_key]["deskripsi"]}')

    if content.startswith('?unequipgem '):
        gem_key = content[12:].strip().lower()
        data = get_user(message.author.id)
        gems_inv = data.get('gems', {})
        if gem_key not in gems_inv or gems_inv[gem_key] <= 0:
            await message.channel.send('❌ Kamu tidak punya gem itu!')
            return
        gems_inv.pop(gem_key, None)
        await message.channel.send(f'💎 **{GEMS[gem_key]["nama"]}** dilepas dari slot aktif.')

    # ===== HUNTING SYSTEM =====
    if content == '?hunt':
        teks = '🏹 **DAFTAR MONSTER UNTUK HUNTING**\n\n'
        for i, m in enumerate(HUNT_MONSTERS):
            teks += f'`{i+1}` {m["nama"]} (Min Lv.{m["level"]}) | ❤️{m["hp"]} | 💰{m["reward_gold"]} | ✨{m["reward_xp"]} XP\n'
        teks += '\nHunting: `?hunt <nomor>` | Gem aktif mempengaruhi hasil!\nContoh: `?hunt 3`'
        await message.channel.send(teks)

    if content.startswith('?hunt ') and content[6:].strip().isdigit():
        idx = int(content[6:].strip()) - 1
        if idx < 0 or idx >= len(HUNT_MONSTERS):
            await message.channel.send('❌ Nomor monster tidak valid! Ketik `?hunt` untuk daftar.')
            return
        data = get_user(message.author.id)
        monster = HUNT_MONSTERS[idx]
        now = datetime.datetime.now()

        last_hunt = data.get('last_hunt')
        if last_hunt and (now - last_hunt).total_seconds() < 120:
            sisa = 120 - int((now - last_hunt).total_seconds())
            await message.channel.send(f'⏳ Cooldown hunting! Tunggu **{sisa} detik** lagi.')
            return

        if data['level'] < monster['level']:
            await message.channel.send(f'❌ Level kamu terlalu rendah! Monster ini butuh Level {monster["level"]}.')
            return
        if data['hp'] <= 15:
            await message.channel.send('💔 HP terlalu rendah untuk hunting! Heal dulu.')
            return

        data['last_hunt'] = now

        # Apply gem effects
        atk, def_, loot_mult, has_lifesteal, no_hp_loss = apply_gem_effects(
            data, get_atk(data), get_def(data)
        )

        # Battle simulasi
        m_hp = monster['hp']
        p_hp = data['hp']
        ronde = 0
        total_dmg_dealt = 0
        while m_hp > 0 and p_hp > 0 and ronde < 15:
            dmg_to_monster = max(1, atk + random.randint(-3, 8) - random.randint(0, 5))
            dmg_to_player = max(1, random.randint(8, 20) - def_ + random.randint(0, 5))
            # Thunder gem: 25% critical
            if 'thunder_gem' in data.get('gems', {}) and random.random() < 0.25:
                dmg_to_monster = int(dmg_to_monster * 1.5)
            m_hp -= dmg_to_monster
            total_dmg_dealt += dmg_to_monster
            if not no_hp_loss:
                if has_lifesteal:
                    heal = dmg_to_monster // 4
                    p_hp = min(get_max_hp(data), p_hp + heal - dmg_to_player)
                else:
                    p_hp -= dmg_to_player
            ronde += 1

        log = f'🏹 **{message.author.display_name}** berburu **{monster["nama"]}**!\n'

        # Pet ikut hunting
        pet_key = data.get('pet')
        if pet_key and pet_key in PETS:
            pet = PETS[pet_key]
            pet_contrib = int(pet['skill_dmg'] * (1 + (data['pet_level']-1)*0.1))
            m_hp -= pet_contrib
            log += f'🐾 {pet["nama"]} membantu dengan **{pet["skill"]}** ({pet_contrib} dmg)!\n'
            data['pet_exp'] += 5
            pet_naik = cek_pet_levelup(data)
            if pet_naik:
                log += f'⭐ **{pet["nama"]} LEVEL UP ke Level {data["pet_level"]}!**\n'

        log += '\n'

        if m_hp <= 0 or p_hp > 0:
            # Menang
            xp_gain = int(monster['reward_xp'] * loot_mult)
            gold_gain = int(monster['reward_gold'] * loot_mult)
            hp_lost = max(0, data['hp'] - max(1, p_hp)) if not no_hp_loss else 0
            data['hp'] = max(1, p_hp) if not no_hp_loss else data['hp']
            data['xp'] += xp_gain
            data['gold'] += gold_gain

            log += f'✅ **MENANG** dalam {ronde} ronde!\n'
            log += f'💰 +{gold_gain} Gold | ✨ +{xp_gain} XP'
            if hp_lost > 0:
                log += f' | ❤️ -{hp_lost} HP'
            if no_hp_loss:
                log += f' | 🛡️ Earth Gem: HP tidak berkurang!'
            if has_lifesteal:
                log += f' | 🩸 Lifesteal aktif!'

            # Gem: chance drop
            gem_drop_roll = random.randint(1, 100)
            cumulative = 0
            dropped_gem = None
            for rarity, chance in GEM_DROP_RATE.items():
                cumulative += chance
                if gem_drop_roll <= cumulative:
                    gem_key_drop = random.choice(GEM_POOL_BY_RARITY[rarity])
                    # Hanya drop gem yang ada di monster loot_table (atau random 30%)
                    if gem_key_drop in monster['loot_table'] or random.random() < 0.3:
                        dropped_gem = gem_key_drop
                        break

            if dropped_gem and dropped_gem in GEMS:
                if loot_mult >= 2.0:  # chaos gem: drop 2
                    data['gems'][dropped_gem] = data['gems'].get(dropped_gem, 0) + 2
                    log += f'\n💎 **LOOT x2 (Chaos Gem):** {GEMS[dropped_gem]["nama"]} x2 [{GEMS[dropped_gem]["rarity"]}]!'
                else:
                    data['gems'][dropped_gem] = data['gems'].get(dropped_gem, 0) + 1
                    log += f'\n💎 **Gem Drop:** {GEMS[dropped_gem]["nama"]} [{GEMS[dropped_gem]["rarity"]}]!'

            # Rare loot (5% chance, +5% per loot_mult bonus)
            rare_chance = 0.05 + (loot_mult - 1) * 0.05
            if random.random() < rare_chance:
                rare = random.choice(RARE_LOOT)
                loot_list = data.get('loot', [])
                if not any(l['nama'] == rare['nama'] for l in loot_list):
                    data['loot'].append(rare)
                    # Apply permanent effect
                    efek = rare['efek']
                    if 'atk_perm' in efek:
                        val = int(efek.split('+')[1])
                        data['atk_bonus'] = data.get('atk_bonus', 0) + val
                    elif 'def_perm' in efek:
                        val = int(efek.split('+')[1])
                        data['def_bonus'] = data.get('def_bonus', 0) + val
                    elif 'hp_perm' in efek:
                        val = int(efek.split('+')[1])
                        data['hp_bonus'] = data.get('hp_bonus', 0) + val
                        data['max_hp'] = data.get('max_hp', 100) + val
                    log += f'\n🌟 **RARE LOOT!!** {rare["nama"]} — {rare["deskripsi"]}!'

            naik = cek_level_up(data)
            if naik:
                log += f'\n🎉 **LEVEL UP! Level {data["level"]}!**'

        else:
            # Kalah
            data['hp'] = max(1, p_hp)
            log += f'💀 **KALAH** dari {monster["nama"]}! HP tersisa 1.\n'
            log += '> Heal dulu sebelum hunting lagi!'

        await message.channel.send(log)

    # ===== HELP =====
    if content in ('?help', ':help'):
        teks = (
            '📖 **DAFTAR COMMAND**\n\n'
            '**🎮 Adventure RPG**\n'
            '`?adventure` — Berpetualang acak (cooldown 5 menit)\n'
            '`?explore` — Jelajah area baru (cooldown 5 menit)\n'
            '`?dungeon` — Lihat daftar dungeon\n'
            '`?dungeon <nama>` — Masuk dungeon (hutan/gua/kastil/gunung)\n'
            '`?hunt` — Lihat monster untuk hunting\n'
            '`?hunt <nomor>` — Berburu monster (cooldown 2 menit)\n'
            '`?duel @user` — Tantang duel PvP\n'
            '`?bossattack` — Serang World Boss aktif\n\n'
            '**🐾 Pet**\n'
            '`?petshop` — Lihat daftar pet\n'
            '`?buypet <nama>` — Beli pet\n'
            '`?pet` — Info pet aktif\n'
            '`?petbattle @user` — Adu pet lawan pemain lain\n\n'
            '**💎 Gems**\n'
            '`?gems` — Lihat gem kamu\n'
            '`?gemshop` — Beli gem\n'
            '`?buygem <nama>` — Beli gem\n'
            '`?equipgem <nama>` — Pasang gem (max 3)\n'
            '`?unequipgem <nama>` — Lepas gem\n\n'
            '**📋 Quest**\n'
            '`?quest` — Lihat quest harian & main quest\n\n'
            '**🏪 Ekonomi**\n'
            '`?daily` — Klaim hadiah harian\n'
            '`?shop` — Lihat toko item\n'
            '`?buy <item>` — Beli item\n'
            '`?sell <item>` — Jual item\n'
            '`?gamble <gold>` — Gambling gold\n'
            '`?heal` — Pulihkan HP (30 Gold)\n\n'
            '**📊 Profil**\n'
            '`?profile` — Lihat profil lengkap\n'
            '`?top` — Leaderboard server\n\n'
            '**🎉 Fun**\n'
            '`?8ball <pertanyaan>` `?roll` `?coinflip`\n'
            '`?ship @user` `?rate <sesuatu>` `?jokes` `?truth` `?dare`\n\n'
            '**🎵 Musik**\n'
            '`?join` `?leave` `?play <lagu>` `?skip` `?stop` `?queue`'
        )
        await message.channel.send(teks)
client.run(os.environ['TOKEN'])
