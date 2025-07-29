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
intents.members = True
intents.reactions = True

client = discord.Client(intents=intents)

@client.event
async def on_ready():
    
    print(f'Sikeresen bejelentkezve mint: {client.user}')
    print('------')

@client.event
async def on_member_join(member):
    """
    Eseménykezelő, amikor egy új felhasználó csatlakozik a szerverhez.
    Üdvözlő üzenetet küld és felszólítja a szabályzat elolvasására.
    """
    global rules_message_id # Hozzáférés a globális változóhoz

    # Keresd meg a csatornát, ahová az üdvözlő üzenetet küldeni szeretnéd.
    # Használhatsz egy konkrét csatorna ID-t, vagy megpróbálhatod megtalálni a "welcome" vagy "rules" nevű csatornát.
    # Ha nincs ilyen, akkor a szerver alapértelmezett rendszerüzenet csatornáját használja.
    welcome_channel = discord.utils.get(member.guild.channels, name="welcome") or \
                      discord.utils.get(member.guild.channels, name="szabalyzat") or \
                      member.guild.system_channel

    if welcome_channel:
        welcome_message = (
            f"Üdvözlünk, {member.mention}, a(z) **{member.guild.name}** szerveren!\n"
            f"Kérlek, olvasd el a <#YOUR_RULES_CHANNEL_ID> csatornán található szabályzatunkat, és fogadd el a reakcióval, "
            f"hogy hozzáférj a többi csatornához."
        )
        # Cseréld le a <#YOUR_RULES_CHANNEL_ID> helyére a szabályzat csatornád tényleges ID-jét.
        # Például: f"Kérlek, olvasd el a <#123456789012345678> csatornán található szabályzatunkat..."
        sent_message = await welcome_channel.send(welcome_message)
        rules_message_id = sent_message.id # Tároljuk az elküldött üzenet ID-jét
        print(f"Üdvözlő üzenet elküldve {member.name} felhasználónak a(z) {welcome_channel.name} csatornára. Üzenet ID: {rules_message_id}")
    else:
        print(f"[HIBA] Nem található üdvözlő csatorna a(z) {member.guild.name} szerveren.")

@client.event
async def on_raw_reaction_add(payload):
    """
    Eseménykezelő, amikor egy felhasználó reakciót ad egy üzenethez.
    Ez akkor is működik, ha az üzenet nincs a bot gyorsítótárában.
    """
    if payload.guild_id is None: # Csak szervereken belüli reakciókat kezelünk
        return

    # Ellenőrizzük, hogy a reakció a szabályzat üzenetre történt-e
    if payload.message_id == rules_message_id:
        guild = client.get_guild(payload.guild_id)
        if guild is None:
            return

        member = guild.get_member(payload.user_id)
        if member is None or member.bot: # Ne adjunk rangot a botoknak
            return

       
        if str(payload.emoji) == '👍':
            # Keresd meg a "Tag" nevű rangot
            role = discord.utils.get(guild.roles, name="Tag")
            if role:
                if role not in member.roles: # Csak akkor adjuk hozzá, ha még nincs meg neki
                    await member.add_roles(role)
                    print(f"'{member.name}' felhasználó megkapta a '{role.name}' rangot a szabályzat elfogadásáért.")
                else:
                    print(f"'{member.name}' felhasználó már rendelkezik a '{role.name}' ranggal.")
            else:
                print(f"[HIBA] Nem található 'Tag' nevű rang a(z) {guild.name} szerveren. Kérlek, hozd létre!")
        else:
            print(f"Nem a várt emoji ({payload.emoji}) a szabályzat üzenetre.")
    # else:
    #     print(f"Reakció egy másik üzenetre: {payload.message_id}")

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

    if command == 'tagok':
        guild = message.guild
        if guild is None:
            await message.channel.send("Ez a parancs csak szerveren belül használható.")
            return

        tag_role = discord.utils.get(guild.roles, name="Tag")
        if tag_role is None:
            await message.channel.send("Nem található 'Tag' nevű rang a szerveren.")
            return

        members_with_tag_role = []
        for member in guild.members:
            if tag_role in member.roles:
                members_with_tag_role.append(member.display_name)

        if members_with_tag_role:
            response = "**Tag ranggal rendelkező felhasználók:**\n"
            response += "\n".join(members_with_tag_role)
            await message.channel.send(response)
        else:
            await message.channel.send("Jelenleg nincs 'Tag' ranggal rendelkező felhasználó.")

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
            f"`{COMMAND_PREFIX}tagok` - Kilistázza az összes 'Tag' rangú felhasználót.\n"
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
