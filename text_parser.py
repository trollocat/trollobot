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


def validate_symbol_balance(text):
    stack = []
    for char in text:
        if char == "(" or char == "[":
            if stack:  # Check if there is already an open symbol
                raise ValueError("No se pueden poner paréntesis o corchetes dentro de sí mismos.")
            stack.append(char)
        elif char == ")" or char == "]":
            if not stack:
                raise ValueError("Símbolo de cierre sin su símbolo de apertura correspondiente.")
            if (char == ")" and stack[-1] != "(") or (char == "]" and stack[-1] != "["):
                raise ValueError("No concuerda el símbolo de clausura con el de apertura.")
            stack.pop()

    if stack:
        raise ValueError("Paréntesis o corchetes desbalanceados.")


def validate_characters(text, separators):
    for char in text:
        if char not in separators and char not in {"k", "d", " "}:
            raise ValueError(f"El caracter '{char}' no es válido.")


def validate_duplicate_symbols(text, separators):
    for count, char in enumerate(text[:-1]):
        if char == text[count + 1] and char in separators:
            raise ValueError(f"Símbolo '{char}' duplicado encontrado.")


def validate_symbol_counts(text):
    open_paren_count = text.count("(")
    close_paren_count = text.count(")")
    open_brack_count = text.count("[")
    close_brack_count = text.count("]")

    if open_paren_count != close_paren_count or open_brack_count != close_brack_count:
        raise ValueError("No coinciden los símbolos de apertura con los de clausura.")


def process_1_6_patterns(normalized_text, i):
    result = []
    j = 0
    while normalized_text[i + j + 1] != ")":
        j += 1

    if j == 1:
        result.append((f"1{normalized_text[i + 1]}", 0))

    elif j == 2:
        result.append((f"1{normalized_text[i + 1]}6{normalized_text[i + 2]}", 0))
        result.append((f"6{normalized_text[i + 2]}2", 1 / 3))

    elif j == 3:
        result.append((f"1{normalized_text[i + 1]}6{normalized_text[i + 2]}", 0))
        result.append((f"6{normalized_text[i + 2]}6{normalized_text[i + 3]}", 0))
        result.append((f"6{normalized_text[i + 3]}1", 2 / 3))

    elif j == 4:
        result.append((f"1{normalized_text[i + 1]}6{normalized_text[i + 2]}", 0))
        result.append((f"6{normalized_text[i + 2]}6{normalized_text[i + 3]}", 0))
        result.append((f"6{normalized_text[i + 3]}1{normalized_text[i + 4]}", 0))

    elif j >= 5 and j % 3 == 2:
        result.append((f"1{normalized_text[i + 1]}6{normalized_text[i + 2]}", 0))
        y = 2
        while y < j - 1:
            result.append((f"6{normalized_text[i + y]}6{normalized_text[i + y + 1]}", 0))
            result.append((f"6{normalized_text[i + y + 1]}1{normalized_text[i + y + 2]}6{normalized_text[i + y + 3]}", 0))
            y += 3
        result.append((f"6{normalized_text[i + j]}2", 1 / 3))

    elif j >= 6 and j % 3 == 0:
        result.append((f"1{normalized_text[i + 1]}6{normalized_text[i + 2]}", 0))
        result.append((f"6{normalized_text[i + 2]}6{normalized_text[i + 3]}", 0))
        y = 3
        while y < j - 1:
            result.append((f"6{normalized_text[i + y]}1{normalized_text[i + y + 1]}6{normalized_text[i + y + 2]}", 0))
            result.append((f"6{normalized_text[i + y + 2]}6{normalized_text[i + y + 3]}", 0))
            y += 3
        result.append((f"6{normalized_text[i + j]}1", 2 / 3))

    elif j >= 7 and j % 3 == 1:
        result.append((f"1{normalized_text[i + 1]}6{normalized_text[i + 2]}", 0))
        result.append((f"6{normalized_text[i + 2]}6{normalized_text[i + 3]}", 0))
        y = 3
        while y < j - 1:
            result.append((f"6{normalized_text[i + y]}1{normalized_text[i + y + 1]}6{normalized_text[i + y + 2]}", 0))
            result.append((f"6{normalized_text[i + y + 2]}6{normalized_text[i + y + 3]}", 0))
            y += 3
        result.append((f"6{normalized_text[i + j - 1]}1{normalized_text[i + j]}", 0))

    return result, j + 2


def process_1_8_patterns(normalized_text, i):
    result = []
    j = 0
    while normalized_text[i + j + 1] != "]":
        j += 1

    if j == 1:
        result.append((f"1{normalized_text[i + 1]}", 0))

    elif j == 2:
        result.append((f"1{normalized_text[i + 1]}8{normalized_text[i + 2]}", 0))
        result.append((f"8{normalized_text[i + 2]}", 1 / 2))

    elif j == 3:
        result.append((f"1{normalized_text[i + 1]}8{normalized_text[i + 2]}", 0))
        result.append((f"8{normalized_text[i + 2]}1{normalized_text[i + 3]}", 0))

    elif j == 4:
        result.append((f"1{normalized_text[i + 1]}8{normalized_text[i + 2]}", 0))
        result.append((f"8{normalized_text[i + 2]}1{normalized_text[i + 3]}8{normalized_text[i + 4]}", 0))
        result.append((f"8{normalized_text[i + 4]}", 1 / 2))

    elif j >= 5 and j % 2 == 1:
        y = 1
        result.append((f"1{normalized_text[i + y]}8{normalized_text[i + y + 1]}", 0))
        while y < j - 2:
            result.append((f"8{normalized_text[i + y + 1]}1{normalized_text[i + y + 2]}8{normalized_text[i + y + 3]}", 0))
            y += 2
        result.append((f"8{normalized_text[i + y + 1]}1{normalized_text[i + y + 2]}", 0))

    elif j >= 6 and j % 2 == 0:
        y = 1
        result.append((f"1{normalized_text[i + y]}8{normalized_text[i + y + 1]}", 0))
        while y < j - 1:
            result.append((f"8{normalized_text[i + y + 1]}1{normalized_text[i + y + 2]}8{normalized_text[i + y + 3]}", 0))
            y += 2
        result.append((f"8{normalized_text[i + y + 1]}", 1 / 2))

    return result, j + 2


def get_patterns_from_text(text):
    separators = {"(", ")", "[", "]"}
    normalized_text = text.lower()
    result = []
    i = 0

    validate_characters(normalized_text, separators)
    validate_duplicate_symbols(normalized_text, separators)
    validate_symbol_counts(normalized_text)
    validate_symbol_balance(normalized_text)

    while i < len(normalized_text):
        if normalized_text[i] not in separators:
            if normalized_text[i] == " ":
                result.append(("bk", 0))
            else:
                result.append(("1" + normalized_text[i], 0))
            i += 1

        elif normalized_text[i] == "(":
            # Process 1/6 patterns
            pattern_result, skip_count = process_1_6_patterns(normalized_text, i)
            result.extend(pattern_result)
            i += skip_count

        elif normalized_text[i] == "[":
            # Process 1/8 patterns
            pattern_result, skip_count = process_1_8_patterns(normalized_text, i)
            result.extend(pattern_result)
            i += skip_count

    return result


if __name__ == "__main__":
    example = "(dkdkd)(kdkdk)(dkdkdk)(kdkdkd)(dkdkdkd)(kdkdkdk)"
    emoji_message = ""
    patterns = get_patterns_from_text(example)
    for emoji in patterns:
        emoji_message = f"{emoji_message}:{emoji[0]}:"
    print(emoji_message)
