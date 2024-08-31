import io
import os
import discord
import logging
from PIL import Image
from dotenv import load_dotenv
from utils import *

# main = False | dev = True
DEV_MODE = True

load_dotenv()
patterns_folder_path = os.getenv("PATTERNS_FOLDER_PATH")

if DEV_MODE:
    token = os.getenv('TOKEN_DEV')
else:
    token = os.getenv('TOKEN_MAIN')

intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)

logging.basicConfig(level=logging.INFO)


@client.event
async def on_ready():
    print(f'Loggeado como {client.user}')


@client.event
async def on_message(message):
    if message.author == client.user:
        return

    msg = message.content

    if msg.startswith("pinga"):
        try:
            texto = msg.replace("pinga ", "")

            # List of image file paths
            patterns = get_patterns_from_text(texto)

            image_paths = [f"{patterns_folder_path}/{pattern}.png" for pattern in patterns]

            # Split images into chunks of 16
            chunk_size = 16
            for i in range(0, len(image_paths), chunk_size):
                chunk = image_paths[i:i + chunk_size]
                montage = create_beatmap_image(chunk)

                # Save the image to a BytesIO object (in-memory file)
                with io.BytesIO() as image_binary:
                    montage.save(image_binary, 'PNG')
                    image_binary.seek(0)

                    # Send the image using discord.File
                    await message.channel.send(
                        file=discord.File(fp=image_binary, filename=f'combined_image_{i // chunk_size + 1}.png'))
        except Exception as e:
            print(f"Error generando imagen: {e}")
            await message.channel.send("Error generando imagen.")

    elif msg.startswith("tt "):
        texto = msg.replace("tt ", "")
        mensaje = ""
        try:
            patterns = get_patterns_from_text(texto)
            for emote in patterns:
                emoji = discord.utils.get(client.emojis, name=emote)
                if emoji:
                    mensaje += str(emoji)
                else:
                    mensaje += f":{emote}:"  # Fallback if emoji not found
            mensaje += "​"  # Invisible character to ensure formatting
            await message.channel.send(mensaje)
        except Exception as e:
            print(f"Error procesando patrón: {e}")
            await message.channel.send(
                "Patrón mal formulado o muy largo. Ejemplo correcto: (kkkdddk)kdd(kkkd)d[kkd]d k"
            )


try:
    client.run(token)
except Exception as e:
    logging.error(f"Error iniciando el bot: {e}")
