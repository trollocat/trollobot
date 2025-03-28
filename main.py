import io
import os
import math
import json
import discord
import logging
import asyncpg
import threading
from utils import *
from database import *
from dotenv import load_dotenv
from discord import app_commands
from discord.ext import commands

# main = False | dev = True
DEV_MODE = True

load_dotenv()
trollocat_id = os.getenv("TROLLOCAT_ID")
patterns_folder_path = os.getenv("PATTERNS_FOLDER_PATH")

if DEV_MODE:
    token = os.getenv('TOKEN_DEV')
else:
    token = os.getenv('TOKEN_MAIN')

DB = None

admins = {trollocat_id}
tp_emoji = "<:tp:1354982310277157024>"

intents = discord.Intents.default()
intents.message_content = True
client = commands.Bot(command_prefix='!', intents=intents)

logging.basicConfig(level=logging.INFO)


@client.event
async def on_ready():
    print(f'Loggeado como {client.user}')
    global DB
    DB = await init_db()
    print(f"{client.user} está listo y conectado a la base de datos!")


@client.hybrid_command()
async def sync(ctx: commands.Context):
    await ctx.send("Slash commands sincronizados")
    await client.tree.sync()


@client.tree.command(name="pinga", description="Genera una imagen o GIF a partir de un patrón.")
@app_commands.describe(texto="Patrón en texto.", gif="¿Visualizar animado en GIF? por defecto: False.",
                       bpm="Velocidad del GIF, por defecto: 120.")
async def pinga(interaction: discord.Interaction, texto: str, gif: bool = False, bpm: float = 120.0):
    try:
        patterns = get_patterns_from_text(texto)
    except ValueError as ve:
        await interaction.response.send_message(f"Error. {ve}", ephemeral=True)
    else:
        try:
            await interaction.response.defer()  # Defer the response to avoid timeout

            image_paths = [f"{patterns_folder_path}/{pattern[0]}.png" for pattern in patterns]

            chunk_size = 16
            image_limit = 8

            # GIF
            if gif:
                images = [Image.open(path) for path in image_paths]

                frame_duration_ms = 22
                precision_factor = 100
                # total_width = 2016
                total_width = 1512
                max_height = 124

                total_scroll_width = total_width * 2 + sum(img.size[0] for img in images)

                frames = []
                for offset in range(0, (total_scroll_width - total_width + 1) * precision_factor,
                                    int(frame_duration_ms * precision_factor * (bpm / 120.0) * 0.895)):
                    frame = Image.new("RGBA", (total_width, max_height), (255, 255, 255, 0))
                    x_offset = total_width * precision_factor - offset
                    for index, img in enumerate(images):
                        if x_offset + img.size[0] * precision_factor > 0 and x_offset < total_width * precision_factor:
                            frame.paste(img, (int(x_offset / precision_factor), 0), img)
                        x_offset += img.size[0] * precision_factor
                        x_offset = int(x_offset - max_height * patterns[index][1] * precision_factor)

                    frames.append(frame)

                    if len(frames) > 1200:
                        raise ValueError(
                            f"El gif duraría más de {int(round(len(frames) * frame_duration_ms / 1000, 0))} segundos, lo cual es una banda.")

                if frames:
                    with io.BytesIO() as image_binary:
                        frames[0].save(image_binary, format='GIF', save_all=True, disposal=2, append_images=frames[1:],
                                       duration=frame_duration_ms, loop=0)
                        image_binary.seek(0)

                        await interaction.followup.send(
                            file=discord.File(fp=image_binary, filename='trollobot_taiko_patterns.gif'))
                else:
                    await interaction.followup.send("No hay frames para crear el GIF.")

            # PNG
            else:
                if len(image_paths) > chunk_size * image_limit:
                    raise ValueError(
                        f"El resultado daría {math.ceil(len(image_paths) / chunk_size)} imágenes, lo cual es una banda.")

                for i in range(0, len(image_paths), chunk_size):
                    chunk = image_paths[i:i + chunk_size]
                    montage = create_beatmap_image(chunk)

                    with io.BytesIO() as image_binary:
                        montage.save(image_binary, 'PNG')
                        image_binary.seek(0)

                        # First interaction
                        if i == 0:
                            await interaction.followup.send(
                                file=discord.File(fp=image_binary,
                                                  filename=f'trollobot_taiko_pattern{i // chunk_size + 1}.png'))
                        else:
                            await interaction.channel.send(
                                file=discord.File(fp=image_binary,
                                                  filename=f'trollobot_taiko_pattern{i // chunk_size + 1}.png'))


        except ValueError as ve:

            await interaction.followup.send(f"Error. {ve}")


        except Exception as e:

            await interaction.followup.send(f"Error inesperado. {e}")


@client.tree.command(name="tt", description="Genera un mensaje con emojis a partir de un patrón.")
async def tt(interaction: discord.Interaction, texto: str):
    try:
        patterns = get_patterns_from_text(texto)
    except ValueError as ve:
        await interaction.response.send_message(f"Error. {ve}", ephemeral=True)
    else:
        try:
            result = ""
            for emote in patterns:
                emoji = discord.utils.get(client.emojis, name=emote[0])
                if emoji:
                    result += str(emoji)
                else:
                    result += f":{emote}:"
            result += "​"  # Invisible zero width character

            if len(result) > 1500:
                raise ValueError("El mensaje se pasa del límite de 1500 caracteres de Discord.")

            await interaction.response.send_message(result)

        except ValueError as ve:
            await interaction.response.send_message(f"Error. {ve}", ephemeral=True)

        except Exception as e:
            await interaction.response.send_message(f"Error inesperado. {e}", ephemeral=True)


@client.tree.command(name="saldo", description="para consultar tu saldo de trollopesos")
async def saldo(interaction: discord.Interaction):
    user = await get_user(DB, interaction.user.id, interaction.user.name)
    await interaction.response.send_message(f"💰 hola {interaction.user.name}, tenés {user['balance']} {tp_emoji}.")


@client.tree.command(name="comprar", description="para comprar un trollocat")
async def comprar(interaction: discord.Interaction, card_name: str):
    user = await get_user(DB, interaction.user.id, interaction.user.name)
    card = await DB.fetchrow("SELECT * FROM cards WHERE name = $1", card_name)

    if not card:
        await interaction.response.send_message(f"🚫 {interaction.user.name}, ese trollocat no existe")
        return

    if user["balance"] < card["price"]:
        await interaction.response.send_message(f"💸 {interaction.user.name}, no te alcanza la guita")
        return

    await update_balance(DB, interaction.user.id, -card["price"])
    await DB.execute("INSERT INTO transactions (user_id, card_id, transaction_type, amount) VALUES ($1, $2, 'buy', $3)",
                     interaction.user.id, card["id"], card["price"])

    await interaction.response.send_message(f"✅ felitaciones {interaction.user.name}, compraste {card_name} por {card['price']} {tp_emoji}!")


@client.tree.command(name="mis_trollocats", description="muestra tus trollocat")
async def mis_trollocats(interaction: discord.Interaction):
    user_id = interaction.user.id
    cards = await DB.fetch("SELECT name FROM cards WHERE id IN (SELECT card_id FROM transactions WHERE user_id = $1)", user_id)

    if not cards:
        await interaction.response.send_message(f"📭 {interaction.user.name}, no tenés trollocats")
    else:
        card_names = ", ".join([card["name"] for card in cards])
        await interaction.response.send_message(f"📜 {interaction.user.name}, tenés los siguientes trollocats: {card_names}")


@client.tree.command(name="trollocat", description="muestra la información de un trollocat")
async def trollocat(interaction: discord.Interaction, nombre: str):
    user = interaction.user
    card = await get_card(DB, nombre)

    if not card:
        await interaction.response.send_message(f"❌ no se encontró el trollocat **{nombre}**.", ephemeral=True)
        return

    nombre, card_price, image_path = card["name"], card["price"], card["image_path"]

    embed = discord.Embed(
        title=f"📜 {nombre}",
        description=f"💰 **precio:** {card_price} {tp_emoji}",
        color=discord.Color.gold()
    )
    embed.set_footer(text=f"comando de {user.name}")

    if os.path.exists(image_path):
        file = discord.File(image_path, filename="card.png")
        embed.set_image(url=f"attachment://card.png")
        await interaction.response.send_message(embed=embed, file=file)
    else:
        embed.set_image(url="https://via.placeholder.com/300?text=Imagen+no+disponible")  # Placeholder
        await interaction.response.send_message(embed=embed)


@client.tree.command(name="laburar", description="agarrá la pala y ganá 5 trollopesos.")
async def laburar(interaction: discord.Interaction):
    await update_balance(DB, interaction.user.id, 5)
    await interaction.response.send_message(f"🔨 {interaction.user.name}, trabajaste (por fin) y ganaste 5 {tp_emoji}!")


@client.tree.command(name="admin_agregar_trollocat", description="(admin) agrega una nueva trollocat.")
async def admin_agregar_trollocat(interaction: discord.Interaction, card_name: str, price: int, image: discord.Attachment):
    if interaction.user.id not in admins:  # Replace with real admin IDs
        await interaction.response.send_message("🚫 solo admins", ephemeral=True)
        return

    file_path = f"storage/{card_name}.png"
    await image.save(file_path)

    await add_card(DB, card_name, price, file_path)
    await interaction.response.send_message(f"✅ se agregó el trollocat {card_name} con un precio de lista de {price} {tp_emoji}.")


client.run(token)
