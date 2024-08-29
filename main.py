import io
import os
import discord
import logging
from PIL import Image
from dotenv import load_dotenv
from funciones import get_patterns_from_text

# main = False | dev = True
DEV_MODE = False

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
            patterns = get_patterns_from_text(texto)

            # List of image file paths
            patterns = get_patterns_from_text(texto)

            image_paths = [f"{patterns_folder_path}/{pattern}.png" for pattern in patterns]

            # Load all images
            images = [Image.open(img) for img in image_paths]

            # Assuming all images have the same height
            widths, heights = zip(*(i.size for i in images))

            # Total width will be fixed to 1984 pixels
            total_width = 1984

            # Height will be the height of the tallest image
            max_height = max(heights)

            # Create a new blank image with the appropriate size in RGBA mode (to support transparency)
            new_image = Image.new('RGBA', (total_width, max_height))

            # Paste each image into the new image
            x_offset = 0
            for img in images:
                new_image.paste(img, (x_offset, 0), img)
                x_offset += img.size[0]

            # Save the final montage to a BytesIO object (in-memory file)
            with io.BytesIO() as image_binary:
                new_image.save(image_binary, 'PNG')  # Save image to the in-memory file
                image_binary.seek(0)  # Seek to the start of the file

                # Send the image using discord.File
                await message.channel.send(
                    file=discord.File(fp=image_binary, filename='combined_image.png'))
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
