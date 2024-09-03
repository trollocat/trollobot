import io
import os
import math
import asyncio
import discord
import logging
from utils import *
from dotenv import load_dotenv
from discord.ext import commands

# main = False | dev = True
DEV_MODE = True

load_dotenv()
patterns_folder_path = os.getenv("PATTERNS_FOLDER_PATH")
trollocat_id = os.getenv("TROLLOCAT_ID")

if DEV_MODE:
    token = os.getenv('TOKEN_DEV')
else:
    token = os.getenv('TOKEN_MAIN')

intents = discord.Intents.default()
intents.message_content = True
client = commands.Bot(command_prefix='/', intents=intents)

logging.basicConfig(level=logging.INFO)


@client.event
async def on_ready():
    print(f'Loggeado como {client.user}')


@client.tree.command(name="sync", description="Sincroniza slash commands")
async def sync(interaction: discord.Interaction):
    if interaction.user.id == int(trollocat_id):
        await client.tree.sync()
        await interaction.response.send_message("Slash commands sincronizados")
    else:
        await interaction.response.send_message("Solo el todopoderoso trollocat puede usar este comando")


@client.tree.command(name="pinga", description="Genera una imagen a partir de un patrón")
async def pinga(interaction: discord.Interaction, texto: str):
    try:
        patterns = get_patterns_from_text(texto)

        if "pepiga" in patterns:
            raise ValueError("patrón mal formulado. Ejemplo correcto: (kkkdddk)kdd(kkkd)d[kkd]d k")

        image_paths = [f"{patterns_folder_path}/{pattern}.png" for pattern in patterns]

        chunk_size = 16
        image_limit = 8

        if len(image_paths) > chunk_size * image_limit:
            raise ValueError(
                f"El resultado daría {math.ceil(len(image_paths) / chunk_size)} imágenes, lo cual es una banda")

        for i in range(0, len(image_paths), chunk_size):
            chunk = image_paths[i:i + chunk_size]
            montage = create_beatmap_image(chunk)

            with io.BytesIO() as image_binary:
                montage.save(image_binary, 'PNG')
                image_binary.seek(0)

                # First interaction
                if i == 0:
                    await interaction.response.send_message(
                        file=discord.File(fp=image_binary,
                                          filename=f'trollobot_taiko_pattern{i // chunk_size + 1}.png'))
                else:
                    await interaction.channel.send(
                        file=discord.File(fp=image_binary,
                                          filename=f'trollobot_taiko_pattern{i // chunk_size + 1}.png'))



    except ValueError as ve:

        await interaction.response.send_message(f"Error, {ve}", ephemeral=True)


    except Exception as e:

        await interaction.response.send_message(f"Error inesperado, {e}", ephemeral=True)


@client.tree.command(name="tt", description="Genera un mensaje con emojis a partir de un patrón")
async def tt(interaction: discord.Interaction, texto: str):
    mensaje = ""
    try:
        patterns = get_patterns_from_text(texto)
        for emote in patterns:
            if emote == "pepiga":
                raise ValueError("patrón mal formulado. Ejemplo correcto: (kkkdddk)kdd(kkkd)d[kkd]d k")
            emoji = discord.utils.get(client.emojis, name=emote)
            if emoji:
                mensaje += str(emoji)
            else:
                mensaje += f":{emote}:"
        mensaje += "​"  # Invisible zero width character

        if len(mensaje) > 1500:
            raise ValueError("mensaje muy largo")

        await interaction.response.send_message(mensaje)

    except ValueError as ve:
        await interaction.response.send_message(f"Error, {ve}", ephemeral=True)

    except Exception as e:
        await interaction.response.send_message(f"Error inesperado, {e}", ephemeral=True)


client.run(token)
