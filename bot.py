import discord
import sys
import random
import datetime
import asyncio
import imap_handler 

COMMAND_PREFIX = "!"
TOKEN_FILE = "token.txt"

def load_token():

    try:
        with open(TOKEN_FILE, "r") as f:
            token = f.read().strip() 
            if not token:
                print(f"[HIBA] A '{TOKEN_FILE}' fájl üres. Kérlek, írd bele a botod tokenjét.")
                sys.exit(1) 
            return token
    except FileNotFoundError:
        print(f"[HIBA] Nem található a '{TOKEN_FILE}' fájl.")
        print(f"Kérlek, hozd létre a '{TOKEN_FILE}' nevű fájlt ugyanabban a mappában, ahol a bot fut,")
        print("és illeszd bele a Discord botod tokenjét.")
        sys.exit(1) 

DISCORD_TOKEN = load_token()


intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)

@client.event
async def on_ready():
    
    print(f'Sikeresen bejelentkezve mint: {client.user}')
    print('------')

@client.event
async def on_message(message):
    """
    Figyeli az üzeneteket és reagál a parancsokra.
    """
   
    if message.author == client.user:
        return

    if not message.content.startswith(COMMAND_PREFIX):
        return

    command = message.content[len(COMMAND_PREFIX):]

    if command == 'hello':
        await message.channel.send(f'Szia, {message.author.mention}!')

    if command == 'kocka':
        dobas = random.randint(1, 6)
        await message.channel.send(f'{message.author.mention} a te dobásod: **{dobas}**!')

    if command == 'ping':
        time_taken = datetime.datetime.now(datetime.timezone.utc) - message.created_at
        message_latency = round(time_taken.total_seconds() * 1000)
        websocket_latency = round(client.latency * 1000)

        await message.channel.send(
            f"Pong! 🏓\n"
            f"Teljes késleltetés: **{message_latency}ms**\n"
            f"Websocket válaszidő: **{websocket_latency}ms**"
        )

      if command == 'segitseg':
        response = (
            f"**Elérhető parancsok:**\n"
            f"`{COMMAND_PREFIX}hello` - A bot köszön neked.\n"
            f"`{COMMAND_PREFIX}kocka` - Dob egy hatoldalú kockával.\n"
            f"`{COMMAND_PREFIX}ping` - Megméri a bot válaszidejét.\n"
            f"`{COMMAND_PREFIX}segitseg` - Megjeleníti ezt az üzenetet."
        )
        await message.channel.send(response)

async def periodic_email_check():
   
    NOTIFICATION_CHANNEL_ID = 847443762967216128 
    await client.wait_until_ready()
    notification_channel = client.get_channel(NOTIFICATION_CHANNEL_ID)

    if not notification_channel:
        print(f"[HIBA] Az értesítési csatorna ID-vel {NOTIFICATION_CHANNEL_ID} nem található.")
        return

    while not client.is_closed():
        try:
            print("Új e-mailek ellenőrzése...")
           
            new_email_subjects = await imap_handler.check_for_new_emails()

            if new_email_subjects:
                for subject in new_email_subjects:
                    message_content = f"Új email érkezett: **{subject}**"
                    await notification_channel.send(message_content)
                    print(f"Értesítés elküldve a tárgyról: {subject}")
            else:
                print("Nincs új e-mail.")

        except Exception as e:
            print(f"[HIBA] Hiba történt a periodikus e-mail ellenőrzés során: {e}")
        await asyncio.sleep(60)  #sec

client.loop.create_task(periodic_email_check())

try:
    client.run(DISCORD_TOKEN)
except discord.errors.LoginFailure:
    print("[HIBA] Érvénytelen Discord Token. Kérlek, ellenőrizd a token.txt fájl tartalmát.")
except Exception as e:
    print(f"[HIBA] Hiba történt a bot futtatása során: {e}")
