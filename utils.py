from PIL import Image


def create_beatmap_image(image_paths):
    # Load all images
    images = [Image.open(img) for img in image_paths]

    widths, heights = zip(*(i.size for i in images))

    # Total width should be 1984px but discord crop makes 2016px prettier, which is a horizontal margin of 16px
    total_width = 2016
    max_height = 124

    # Create a new blank image with the appropriate size in RGBA mode
    map_image = Image.new('RGBA', (total_width, max_height))

    # Paste each image into the new image
    x_offset = 16
    for img in images:
        map_image.paste(img, (x_offset, 0), img)
        x_offset += img.size[0]

    return map_image


def do_open_and_closing_symbols_match(input_string, opening_symbol,
                                      closing_symbol):
    s = []
    balanced = True
    index = 0
    while index < len(input_string) and balanced:
        token = input_string[index]
        if token == opening_symbol:
            s.append(token)
        elif token == closing_symbol:
            if len(s) == 0:
                balanced = False
            else:
                s.pop()

        index += 1

    return balanced and len(s) == 0


def text_is_correct(text):
    return (do_open_and_closing_symbols_match(text, "(", ")")
            and do_open_and_closing_symbols_match(
                text, "[", "]")) and do_open_and_closing_symbols_match(
        text, "{", "}")


def get_patterns_from_text(texto):
    message = texto
    acum = []
    separators = ["(", ")", "[", "]"]
    message_normalized = ""
    es_un_tercio = False
    i = 0
    j = 0

    # escudo anti boludos
    for letter in message:
        message_normalized += letter.lower()
        if letter.lower() not in {"(", ")", "[", "]", "k", "d", " "}:
            i = len(message)
            acum.append("pepiga")

    message = message_normalized

    # detector de duplicado de ()[]
    for count, letter in enumerate(message):
        if count < len(message) - 1 and message[count] == message[
            count + 1] and message[count] in separators:
            i = len(message)
            acum.append("pepiga")

    # detector de closings y openings sin match
    pare_a, pare_c, corc_a, corc_c = 0, 0, 0, 0
    pare = ""
    corc = ""
    for letter in message:
        if letter == "(":
            pare_a += 1
            pare += letter
        elif letter == ")":
            pare_c += 1
            pare += letter
        elif letter == "[":
            corc_a += 1
            corc += letter
        elif letter == "]":
            corc_c += 1
            corc += letter
    if (pare_a != pare_c or corc_a
        != corc_c) or (not do_open_and_closing_symbols_match(pare, "(", ")")
                       or not do_open_and_closing_symbols_match(corc, "[", "]")):
        i = len(message)
        acum.append("pepiga")

    while i < len(message):
        if message[i] not in separators:
            # modo 1/4
            if message[i] == " ":
                acum.append("bk")
            else:
                acum.append("1" + message[i])
            i += 1

        elif message[i] == "(":
            # modo 1/6

            # obtengo cantidad de x dentro de ()
            while message[i + j + 1] != ")":
                if message[i + j + 1] == " ":
                    es_un_tercio = True
                j += 1

            # 1/3 experimental
            if es_un_tercio:
                while message[i + j + 1] != ")" and message[i + j + 1] != " ":
                    j += 1

            # un (xx) doble
            if j == 2:
                # 1x6x
                acum.append("1" + message[i + 1] + "6" + message[i + 2])

                # 6x2
                acum.append("6" + message[i + 2] + "2")

            # un (xxx) raro pato por que
            if j == 3:
                # 1x6x
                acum.append("1" + message[i + 1] + "6" + message[i + 2])

                # 6x6x
                acum.append("6" + message[i + 2] + "6" + message[i + 3])

                # 6x1
                acum.append("6" + message[i + 3] + "1")

            # un simple (xxxx)
            if j == 4:
                # 1x6x
                acum.append("1" + message[i + 1] + "6" + message[i + 2])

                # 6x6x
                acum.append("6" + message[i + 2] + "6" + message[i + 3])

                # 6x1x
                acum.append("6" + message[i + 3] + "1" + message[i + 4])

            # un (xxx|xxx|x) o más cantidad de xxx|
            elif j % 3 == 1:
                # 1x6x
                acum.append("1" + message[i + 1] + "6" + message[i + 2])

                # 6x6x
                acum.append("6" + message[i + 2] + "6" + message[i + 3])

                # # # parte loopeada
                y = 3
                while y < j - 1:
                    # # 6x1x6x
                    acum.append("6" + message[i + y] + "1" + message[i + y + 1] + "6" +
                                message[i + y + 2])

                    # # 6x6x
                    acum.append("6" + message[i + y + 2] + "6" + message[i + y + 3])

                    # # pasos de a 3 por (xxx|)
                    y += 3

                # 6x1x
                acum.append("6" + message[i + j - 1] + "1" + message[i + j])
            i += j + 2

        elif message[i] == "[":
            # modo 1/8
            print("[")

            # obtengo cantidad de x dentro de []
            while message[i + j + 1] != "]":
                j += 1

            # [x] re troll
            if j == 1:
                acum.append("1" + message[i + 1])

            # [xx] dobles
            if j == 2:
                es_doble = True
                # 1x8x
                acum.append("1" + message[i + 1] + "8" + message[i + 2])

                # 8x
                acum.append("8" + message[i + 2])

            # [xxx]
            if j == 3:
                # 1x8x
                acum.append("1" + message[i + 1] + "8" + message[i + 2])

                # 8x1x
                acum.append("8" + message[i + 2] + "1" + message[i + 3])

            # [xxxx]
            # interpretación [abcd] = [1a8b+1b8c1d+8d]
            elif j == 4:
                # 1x8x
                acum.append("1" + message[i + 1] + "8" + message[i + 2])

                # 8x1x8x
                acum.append("8" + message[i + 2] + "1" + message[i + 3] + "8" +
                            message[i + 4])

                # 8x
                acum.append("8" + message[i + 4])

            # [xxxxx]
            # interpretación [abcde] = [1a8b + 1b8c1d + 1d8e]
            #                           [1a8b + loopear j/2-2 veces + 1d8e]
            elif j >= 5 and j % 2 == 1:
                y = 1
                # 1x8x
                acum.append("1" + message[i + y] + "8" + message[i + y + 1])

                # 8x1x8x
                while y < j - 2:
                    acum.append("8" + message[i + y + 1] + "1" + message[i + y + 2] +
                                "8" + message[i + y + 3])
                    y += 2

                # 8x1x
                acum.append("8" + message[i + y + 1] + "1" + message[i + y + 2])

            # [xxxxxx]
            # interpretación [abcdef] = [1a8b + 1b8c1d + 1d8e1f + 8f]
            #                           [1a8b + loopear j/2-2 veces + 8y+j/2]
            elif j >= 6 and j % 2 == 0:
                y = 1
                # 1x8x
                acum.append("1" + message[i + y] + "8" + message[i + y + 1])

                # 8x1x8x
                while y < j - 1:
                    acum.append("8" + message[i + y + 1] + "1" + message[i + y + 2] +
                                "8" + message[i + y + 3])
                    y += 2

                # 8x
                acum.append("8" + message[i + y + 1])

            i += j + 2
            print(f"este [] tuvo {j} notas")
            print("]")
    return acum
