from colorama import init, Fore, Style

def print_colored_message(message, color):
    if color == "Green":
        colored = Fore.GREEN
    elif color == "Red":
        colored = Fore.RED
    elif color == "Yellow":
        colored = Fore.YELLOW

    print(colored + message + Style.RESET_ALL)