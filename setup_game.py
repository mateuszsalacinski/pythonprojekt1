import re
from models import Player, MonopolyError


def setup_players():
    players_list = []
    number_pattern= re.compile(r"^\d+$")

    print("\n=== PLAYER SETUP ===")
    while True:
        num_players = input("Enter the number of players(2-4): ").strip()
        if number_pattern.match(num_players) and 2 <= int(num_players) <= 4:
            num_players = int(num_players)
            break
        print("[ERROR] Please enter a valid number between 2 and 4.")
    for i in range(1, num_players + 1):
        while True:
            name = input(f"Enter a name for Player {i}: ").strip()
            if name == "" or name.isdigit():
                print("[ERROR] The name cannot be empty or consist only of digits!")
                continue
            try:
                new_player = Player(name=name)
                players_list.append(new_player)
                break
            except MonopolyError as e:
                print(e)

    return players_list
def turn_generator(players):
    while True:
        for player in players:
            if player.is_bankrupt:
                continue
            yield player

