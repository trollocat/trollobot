import io
import os
import math
import asyncio
import discord
import logging
from utils import *
from dotenv import load_dotenv
from discord import app_commands
from discord.ext import commands

# main = False | dev = True
DEV_MODE = False

load_dotenv()
patterns_folder_path = os.getenv("PATTERNS_FOLDER_PATH")
trollocat_id = os.getenv("TROLLOCAT_ID")

if DEV_MODE:
    token = os.getenv('TOKEN_DEV')
else:
    token = os.getenv('TOKEN_MAIN')

intents = discord.Intents.default()
intents.message_content = True
client = commands.Bot(command_prefix='!', intents=intents)

logging.basicConfig(level=logging.INFO)


@client.event
async def on_ready():
    print(f'Loggeado como {client.user}')


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


client.run(token)
