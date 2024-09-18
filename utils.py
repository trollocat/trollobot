from PIL import Image


def do_open_and_closing_symbols_match(input_string, opening_symbol, closing_symbol):
    stack = []
    balanced = True
    index = 0

    while index < len(input_string) and balanced:
        token = input_string[index]

        if token == opening_symbol:
            stack.append(token)
        elif token == closing_symbol:
            if not stack:
                balanced = False
            else:
                stack.pop()

        index += 1

    return balanced and not stack


def text_is_correct(text):
    return (
            do_open_and_closing_symbols_match(text, "(", ")")
            and do_open_and_closing_symbols_match(text, "[", "]")
            and do_open_and_closing_symbols_match(text, "{", "}")
    )


def get_patterns_from_text(text):
    normalized_text = text.lower()
    result = []
    separators = {"(", ")", "[", "]"}
    i = 0

    for char in normalized_text:
        if char not in separators and char not in {"k", "d", " "}:
            result.append(("pepiga", 0))
            return result

    for count, char in enumerate(normalized_text[:-1]):
        if char == normalized_text[count + 1] and char in separators:
            result.append(("pepiga", 0))
            return result

    open_paren_count, close_paren_count = 0, 0
    open_brack_count, close_brack_count = 0, 0

    for char in normalized_text:
        if char == "(":
            open_paren_count += 1
        elif char == ")":
            close_paren_count += 1
        elif char == "[":
            open_brack_count += 1
        elif char == "]":
            close_brack_count += 1

    if (open_paren_count != close_paren_count or open_brack_count != close_brack_count) or (
            not do_open_and_closing_symbols_match(normalized_text, "(", ")") or
            not do_open_and_closing_symbols_match(normalized_text, "[", "]")
    ):
        result.append(("pepiga", 0))
        return result

    while i < len(normalized_text):
        if normalized_text[i] not in separators:
            if normalized_text[i] == " ":
                result.append(("bk", 0))
            else:
                result.append(("1" + normalized_text[i], 0))
            i += 1

        elif normalized_text[i] == "(":
            # Handle 1/6 patterns
            j = 0
            # is_one_third = False
            while normalized_text[i + j + 1] != ")":
                # if normalized_text[i + j + 1] == " ":
                #     is_one_third = True
                j += 1

            # if is_one_third:
            #     while normalized_text[i + j + 1] != ")" and normalized_text[i + j + 1] != " ":
            #         j += 1

            if j == 1:
                result.append((f"1{normalized_text[i + 1]}", 0))

            if j == 2:
                result.append((f"1{normalized_text[i + 1]}6{normalized_text[i + 2]}", 0))
                result.append((f"6{normalized_text[i + 2]}2", 0.33))

            elif j == 3:
                result.append((f"1{normalized_text[i + 1]}6{normalized_text[i + 2]}", 0))
                result.append((f"6{normalized_text[i + 2]}6{normalized_text[i + 3]}", 0))
                result.append((f"6{normalized_text[i + 3]}1", 0.66))

            elif j == 4:
                result.append((f"1{normalized_text[i + 1]}6{normalized_text[i + 2]}", 0))
                result.append((f"6{normalized_text[i + 2]}6{normalized_text[i + 3]}", 0))
                result.append((f"6{normalized_text[i + 3]}1{normalized_text[i + 4]}", 0))

            elif j % 3 == 1:
                result.append((f"1{normalized_text[i + 1]}6{normalized_text[i + 2]}", 0))
                result.append((f"6{normalized_text[i + 2]}6{normalized_text[i + 3]}", 0))
                y = 3
                while y < j - 1:
                    result.append(
                        (f"6{normalized_text[i + y]}1{normalized_text[i + y + 1]}6{normalized_text[i + y + 2]}", 0))
                    result.append((f"6{normalized_text[i + y + 2]}6{normalized_text[i + y + 3]}", 0))
                    y += 3
                result.append((f"6{normalized_text[i + j - 1]}1{normalized_text[i + j]}", 0.33))

            i += j + 2

        elif normalized_text[i] == "[":
            # Handle 1/8 patterns
            j = 0
            while normalized_text[i + j + 1] != "]":
                j += 1

            if j == 1:
                result.append((f"1{normalized_text[i + 1]}", 0))

            elif j == 2:
                result.append((f"1{normalized_text[i + 1]}8{normalized_text[i + 2]}", 0))
                result.append((f"8{normalized_text[i + 2]}", 0.5))

            elif j == 3:
                result.append((f"1{normalized_text[i + 1]}8{normalized_text[i + 2]}", 0))
                result.append((f"8{normalized_text[i + 2]}1{normalized_text[i + 3]}", 0))

            elif j == 4:
                result.append((f"1{normalized_text[i + 1]}8{normalized_text[i + 2]}", 0))
                result.append((f"8{normalized_text[i + 2]}1{normalized_text[i + 3]}8{normalized_text[i + 4]}", 0))
                result.append((f"8{normalized_text[i + 4]}", 0.5))

            elif j >= 5 and j % 2 == 1:
                y = 1
                result.append((f"1{normalized_text[i + y]}8{normalized_text[i + y + 1]}", 0))
                while y < j - 2:
                    result.append(
                        (f"8{normalized_text[i + y + 1]}1{normalized_text[i + y + 2]}8{normalized_text[i + y + 3]}", 0))
                    y += 2
                result.append((f"8{normalized_text[i + y + 1]}1{normalized_text[i + y + 2]}", 0))

            elif j >= 6 and j % 2 == 0:
                y = 1
                result.append((f"1{normalized_text[i + y]}8{normalized_text[i + y + 1]}", 0))
                while y < j - 1:
                    result.append(
                        (f"8{normalized_text[i + y + 1]}1{normalized_text[i + y + 2]}8{normalized_text[i + y + 3]}", 0))
                    y += 2
                result.append((f"8{normalized_text[i + y + 1]}", 0.5))

            i += j + 2
    return result


def create_beatmap_image(image_paths):
    images = [Image.open(img) for img in image_paths]

    # widths, heights = zip(*(i.size for i in images)) # useful but not used

    # Total width should be 1984px but discord crop makes 2016px prettier, this means a horizontal margin of 16px
    total_width = 2016
    max_height = 124

    map_image = Image.new('RGBA', (total_width, max_height))

    x_offset = 16
    for img in images:
        map_image.paste(img, (x_offset, 0), img)
        x_offset += img.size[0]

    return map_image


if __name__ == "__main__":
    example = "(kkkkkkk)"
    emoji_message = ""
    patterns = get_patterns_from_text(example)
    for emoji in patterns:
        emoji_message = f"{emoji_message}:{emoji[0]}:"
    print(emoji_message)
