import platform, os, re


def clear_terminal():
    if platform.system() == "Windows":
        os.system('cls')
    else:
        os.system('clear')


def break_text_lines(text, size=15):
    words = text.split()
    lines = []
    current_line = ""

    for word in words:
        # Quebra a palavra se ela for muito longa
        while len(word) > size:
            # Adiciona a parte da palavra que cabe na linha atual
            lines.append(word[:size])
            word = word[size:]  # Remove a parte já adicionada

        # Se a adição da próxima palavra exceder o tamanho, adicionar a linha atual à lista
        if len(current_line) + len(word) + (1 if current_line else 0) > size:
            lines.append(current_line)
            current_line = word  # Começar uma nova linha com a palavra atual
        else:
            if current_line:  # Adiciona espaço se não for a primeira palavra
                current_line += " "
            current_line += word

    # Adicionar a última linha se não estiver vazia
    if current_line:
        lines.append(current_line)

    return '\n'.join(lines)