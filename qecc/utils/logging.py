from colorama import Fore


def print_blue(val: str) -> None:
    print(Fore.BLUE + val + Fore.RESET)  # ty:ignore[unsupported-operator]
