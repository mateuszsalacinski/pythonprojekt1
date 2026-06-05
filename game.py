from models import *
from setup_game import *
from card import *
board = Board()
print("Choose game mode:")
print(" [1] - Default board (BOARD_PL.csv)")
print(" [2] - Custom board")
choice = input("Your choice: ").strip()
if choice == "2":
    board.custom_game()
else:
    board.default_game()

players_list = setup_players()
turn_manager = turn_generator(players_list)
print("\n=== LET THE GAME BEGIN! ===")
while True:
    active_players = [p for p in players_list if not p.is_bankrupt]
    if len(active_players) <=1:
        print(f"\n GAME OVER! {active_players[0].name} wins!")
        break

    current_player = next(turn_manager)
    print(f"\n====================================")
    print(f"           {current_player.name}'s TURN")
    print(f"====================================")
    consecutive_doubles = 0
    extra_turn = True
    while extra_turn:
        current_square_name = board.current_square(current_player.position).name
        print(f"\n[Balance: ${current_player.money} | Position: {current_player.position} ({current_square_name})]")
        print("\nAvailable actions:")
        print(" [R] - Roll the dice")
        print(" [I] - View my stats")
        print(" [Q] - Quit game")
        print(" [B] - Build house/hotel")
        print(" [S] - Sell house/hotel")
        print(" [M] - Mortgage property")
        print(" [U] - Unmortgage property")
        command = input(f"{current_player.name}'s move: ").strip().upper()

        if command == "Q":
            print("Ending the game. Thanks for playing!")
            exit()
        elif command == "B":
            buildable = [p for p in current_player.properties if p.type == "street" and p.houses < 5]
            if not buildable:
                print("No properties available to build on (need a full color set).")
            else:
                print("\nChoose a property to build on:")
                for i, p in enumerate(buildable):
                    label = "hotel" if p.houses == 4 else f"{p.houses} house(s)"
                    print(f"  [{i}] {p.name} ({p.color}) — currently: {label} — build cost: ${p.get_house_price()}")
                choice = input("Enter number (or ENTER to cancel): ").strip()
                if choice.isdigit() and int(choice) < len(buildable):
                    current_player.build_house(buildable[int(choice)], board.properties)
        elif command == "S":
            sellable = [p for p in current_player.properties if p.type == "street" and p.houses > 0]
            if not sellable:
                print("No houses or hotels to sell.")
            else:
                print("\nChoose a property to sell a house from:")
                for i, p in enumerate(sellable):
                    label = "hotel" if p.houses == 5 else f"{p.houses} house(s)"
                    print(f"  [{i}] {p.name} ({p.color}) — currently: {label} — refund: ${p.get_house_price() // 2}")
                choice = input("Enter number (or ENTER to cancel): ").strip()
                if choice.isdigit() and int(choice) < len(sellable):
                    current_player.sell_house(sellable[int(choice)])
        elif command == "M":
            mortgageable = [p for p in current_player.properties if not p.is_mortgaged and p.houses == 0]
            if not mortgageable:
                print("No properties available to mortgage.")
            else:
                print("\nChoose a property to mortgage:")
                for i, p in enumerate(mortgageable):
                    print(f"  [{i}] {p.name} — value: ${p.price // 2}")
                choice = input("Enter number (or ENTER to cancel): ").strip()
                if choice.isdigit() and int(choice) < len(mortgageable):
                    current_player.mortgage_property(mortgageable[int(choice)])
        elif command == "U":
            unmortgageable = [p for p in current_player.properties if p.is_mortgaged]
            if not unmortgageable:
                print("No mortgaged properties to unmortgage.")
            else:
                print("\nChoose a property to unmortgage:")
                for i, p in enumerate(unmortgageable):
                    cost = int(p.price // 2 * 1.1)
                    print(f"  [{i}] {p.name} — cost: ${cost}")
                choice = input("Enter number (or ENTER to cancel): ").strip()
                if choice.isdigit() and int(choice) < len(unmortgageable):
                    current_player.unmortgage_property(unmortgageable[int(choice)])
        elif command == "I":
            print(f"\n--- {current_player.name}'s INFO ---")
            print(f"Balance: ${current_player.money}")
            print(f"Get Out of Jail Free card: {'Yes' if current_player.get_out_of_jail_card else 'No'}")
            print(f"Properties owned: {len(current_player.properties)}")
            for p in current_player.properties:
                if p.houses == 0:
                    status = "mortgaged" if p.is_mortgaged else "no houses"
                elif p.houses == 5:
                    status = "hotel"
                else:
                    status = f"{p.houses} house(s)"
                print(f"  - {p.name} ({p.color}) - {status}")
            if not current_player.properties:
                print("  None")
            print("-" * 25)
        elif command == "R" or command == "":
            if current_player.in_jail:
                print("\nYou are in jail!")
                if current_player.get_out_of_jail_card:
                    ans = input("Use your Get Out of Jail Free card? (Y/N): ").strip().upper()
                    if ans == "Y":
                        current_player.get_out_of_jail_card = False
                        current_player.in_jail = False
                        current_player.jail_turns = 0
                        print("You used your Get Out of Jail Free card!")
                if current_player.money >= 50:
                    ans = input("Pay $50 bail to get out now? (Y/N): ").strip().upper()
                    if ans == "Y":
                        current_player.pay(50)
                        current_player.in_jail = False
                        current_player.jail_turns = 0
                        print("You paid $50 bail! You are now free.")
            steps, is_double = current_player.roll_dice()
            if current_player.in_jail:
                if is_double:
                    print("DOUBLE! You broke out of jail!")
                    current_player.in_jail = False
                    current_player.jail_turns = 0
                    extra_turn = False
                else:
                    current_player.jail_turns += 1
                    print(f"No double. Turn {current_player.jail_turns}/3 in jail.")
                    if current_player.jail_turns >= 3:
                        print("3 turns passed. You MUST pay $50.")
                        current_player.pay(50)
                        current_player.in_jail = False
                        current_player.jail_turns = 0
                        extra_turn = False
                    else:
                        extra_turn = False
                        input("\nPress ENTER to end your turn...")
                        continue

            else:
                if is_double:
                    consecutive_doubles += 1
                    if consecutive_doubles == 3:
                        print(f"3 doubles in a row. You lose your turn (and should go to jail)!")
                        current_player.go_to_jail()
                        extra_turn = False
                        input("\nPress ENTER to end your turn...")
                        continue
                else:
                    consecutive_doubles = 0
            current_player.move(steps, size=len(board.properties))
            current_square = board.current_square(current_player.position)
            square_resolved = False
            while not square_resolved:
                current_square = board.current_square(current_player.position)
                print(f" {current_player.name} landed on: {current_square.name} (Type: {current_square.type})")
                square_resolved = True
                if current_square.type in ["street", "station", "utility"]:
                    if current_square.owner is None:
                        decision = input(f"Buy {current_square.name} for ${current_square.price}? (Y/N): ").strip().upper()
                        if decision == "Y" or decision == "":
                            current_player.buy_property(current_square)
                    elif current_square.owner == current_player:
                        print("You own this property.")
                    else:
                        has_monopoly = False
                        if current_square.type == "street":
                            has_monopoly = current_square.owner.has_monopoly(current_square.color, board.properties)
                        elif current_square.type == "utility":
                            all_utilities = [p for p in board.properties if p.type == "utility"]
                            has_monopoly = all(p.owner == current_square.owner for p in all_utilities)
                        rent = current_square.get_current_rent(owner_has_monopoly=has_monopoly, dice_roll=steps)
                        print(f"💰 This property belongs to {current_square.owner.name}. Rent due: ${rent}")
                        current_player.pay(rent, recipient=current_square.owner)
                elif current_square.type == "tax":
                    print(f"️ TAX SQUARE! You must pay ${current_square.tax} to the Bank.")
                    current_player.pay(current_square.tax)
                    print(f"Current balance: ${current_player.money}")

                elif current_square.type == "chance":
                    old_position = current_player.position
                    chance_deck.draw_card(current_player, players_list, board)
                    if current_player.position != old_position:
                        square_resolved = False


                elif current_square.type == "community_chest":
                    old_position = current_player.position
                    community_chest_deck.draw_card(current_player, players_list, board)
                    if current_player.position != old_position:
                        square_resolved = False


                elif current_square.type == "go_to_jail":
                    current_player.go_to_jail()
                    extra_turn = False

                elif current_square.type in ["start", "visit", "parking"]:
                     print("Neutral space.")

                else:
                    print(f"Unrecognised type: {current_square.type}")


            if current_player.is_bankrupt:
                extra_turn = False
                input("\nPress ENTER to end your turn...")
            elif is_double:
                print(f" DOUBLE! {current_player.name} gets another roll!")
                extra_turn = True
            else:
                extra_turn = False
                print(f"\n[Balance: ${current_player.money} | Position: {current_player.position} ({current_square.name})]")
                input("\nPress ENTER to end your turn...")

        else:
            print("[ERROR] Invalid command. Try again.")