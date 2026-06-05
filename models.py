import csv
import re
import random
class MonopolyError(Exception):
    pass
def require_active(func):
    def wrapper(self, *args, **kwargs):
        if getattr(self, 'is_bankrupt', False):
            print(f"{self.name} is bankrupt and cannot perform this action!")
            return None
        return func(self, *args, **kwargs)
    return wrapper
class Player:
    def __init__(self, name, starting_budget = 1500 ):
        if not isinstance(name, str) or name.strip().isdigit() or name.strip() == "":
            raise MonopolyError("[ERROR] Invalid player name.")
        if not isinstance(starting_budget, int) or starting_budget < 0:
            raise MonopolyError("[ERROR] Starting budget must be a positivr integer")
        self.name = name
        self.money = starting_budget
        self.position = 0
        self.properties = []
        self.is_bankrupt = False
        self.in_jail = False
        self.jail_turns = 0
        self.get_out_of_jail_card = False
        print(f"Player {self.name} has started playing. \nMoney left: ${self.money}")
    def roll_dice(self):
        die1 = random.randint(1, 6)
        die2 = random.randint(1, 6)
        total_dice=die1+die2
        is_double=(die1==die2)
        print(f"\n🎲 {self.name} rolls the dice: {die1} and {die2} (Total moves: {total_dice})")
        if is_double:
            print("   [!] Double! You will get an extra turn.")
        return total_dice, is_double
    def move(self, count, size=40):
        self.position += count
        if self.position >= size:
            self.position = self.position % size
            self.receive(200)
            print(f"{self.name} crossed the START. $200 has been added.")
    @require_active
    def move_to(self, target_position, pass_start = True):
        if pass_start and target_position < self.position:
            self.receive(200)
            print(f"{self.name} passed the START. $200 has been added.")
        self.position = target_position
    @require_active
    def go_to_jail(self):
        print("Go directly to the jail! You lose your turn.")
        self.in_jail = True
        self.jail_turns = 0
        self.position = 10
    @require_active
    def pay(self,amount, recipient = None):
        if self.money >= amount:
            self.money -= amount
            if recipient:
                recipient.receive(amount)
                print(f"{self.name} paid ${amount} to ${recipient.name}.")
            else:
                print(f"{self.name} paid ${amount} to the Bank.")
            return True
        else:
            print(f"{self.name} failed to pay ${amount}. Current balance: ${self.money}")
            self.declare_bankruptcy(recipient)
            return False
    def receive(self, amount):
        self.money += amount
    @require_active
    def buy_property(self, property_obj):
        if self.money >= property_obj.price:
            self.money -= property_obj.price
            self.properties.append(property_obj)
            property_obj.owner = self
            print(f" {self.name} bought {property_obj.name}!")
            return True
        else:
            print(f"{self.name} cannot afford {property_obj.name}! Price:{property_obj.price}, Balance: ${self.money}")
            return False
    def declare_bankruptcy(self, creditor = None):
        self.is_bankrupt = True
        self.money = 0
        print(f"{self.name} has gone bankrupt!")
        for prop in self.properties:
            if creditor:
                prop.owner = creditor
                creditor.properties.append(prop)
            else:
                prop.owner = None
        self.properties.clear()
    def has_monopoly(self, color, board_properties):
        if color == 'none':
            return False
        all_of_color = [p for p in board_properties if p.color == color]
        owned_of_color = [p for p in self.properties if p.color == color]
        return len(all_of_color) == len(owned_of_color)

    @require_active
    def build_house(self, property_obj, board_properties):
        if property_obj.owner != self:
            print("You don't own this property.")
            return False
        if not self.has_monopoly(property_obj.color, board_properties):
            print("You need a full color monopoly to build.")
            return False
        if property_obj.houses >= 5:
            print(f"{property_obj.name} already has a hotel (max level).")
            return False
        same_color = [p for p in board_properties if p.color == property_obj.color]
        if any(p.houses < property_obj.houses for p in same_color):
            print("You must build evenly — upgrade your other properties first.")
            return False
        price = property_obj.get_house_price()
        if self.money < price:
            print(f"Not enough money. Build cost: ${price}, your balance: ${self.money}")
            return False
        self.money -= price
        property_obj.houses += 1
        label = "hotel" if property_obj.houses == 5 else f"house #{property_obj.houses}"
        print(f" Built {label} on {property_obj.name}. Cost: ${price} | Balance: ${self.money}")
        return True

    @require_active
    def sell_house(self, property_obj):
        if property_obj.owner != self:
            print("You don't own this property.")
            return False
        if property_obj.houses == 0:
            print(f"{property_obj.name} has no houses to sell.")
            return False
        refund = property_obj.get_house_price() // 2
        property_obj.houses -= 1
        self.money += refund
        label = "hotel" if property_obj.houses + 1 == 5 else f"house #{property_obj.houses + 1}"
        print(f"Sold {label} on {property_obj.name}. Refund: ${refund} | Balance: ${self.money}")
        return True

    @require_active
    def mortgage_property(self, property_obj):
        if property_obj.owner != self:
            print("You don't own this property.")
            return False
        if property_obj.is_mortgaged:
            print(f"{property_obj.name} is already mortgaged.")
            return False
        if property_obj.houses > 0:
            print("Sell all houses first before mortgaging.")
            return False
        value = property_obj.price // 2
        self.money += value
        property_obj.is_mortgaged = True
        print(f"Mortgaged {property_obj.name} for ${value} | Balance: ${self.money}")
        return True

    @require_active
    def unmortgage_property(self, property_obj):
        if property_obj.owner != self:
            print("You don't own this property.")
            return False
        if not property_obj.is_mortgaged:
            print(f"{property_obj.name} is not mortgaged.")
            return False
        cost = int(property_obj.price // 2 * 1.1)
        if self.money < cost:
            print(f"Not enough money. Cost: ${cost} | Balance: ${self.money}")
            return False
        self.money -= cost
        property_obj.is_mortgaged = False
        print(f"Unmortgaged {property_obj.name} for ${cost} | Balance: ${self.money}")
        return True



class Property:
    def __init__(self, name, price, tax, square_type, color):
        self.price = price
        self.name = name
        self.tax = tax
        self.type = square_type.strip().lower()
        self.color = color.strip().lower() if color else "none"
        self.owner = None
        self.houses = 0
        self.is_mortgaged = False
    def get_house_price(self):
        if self.color in ["brown", "lightblue"]: return 50
        if self.color in ["pink", "orange"]: return 100
        if self.color in ["red", "yellow"]: return 150
        if self.color in ["green", "darkblue"]: return 200
        return 0
    def get_current_rent(self, owner_has_monopoly = False, dice_roll = None):
        if self.is_mortgaged:
            return 0
        if self.type == "station":
            count = sum(1 for p in self.owner.properties if p.type == "station")
            return 25 * (2 ** (count - 1))
        if self.type == "utility":
            multiplier = 10 if owner_has_monopoly else 4
            return multiplier * (dice_roll or 7)
        if self.type != "street":
            return self.tax
        multipliers = [1, 5, 15, 40, 50, 60]
        if self.houses == 0 and owner_has_monopoly:
            return self.tax * 2
        return self.tax * multipliers[self.houses]
class Board:
    def __init__(self):
        self.properties = []
    def receive_board(self, file_name):
        self.properties.clear()
        with open(file_name, mode='r', encoding='utf-8') as file:
            reader = csv.reader(file, delimiter=';')
            for row in reader:
                if row:
                    color = row[4].strip() if len(row) > 4 else "none"
                    new_square = Property(
                        name=row[0].strip(),
                        price=int(row[1].strip()),
                        tax=int(row[2].strip()),
                        square_type=row[3].strip(),
                        color=color
                    )
                    self.properties.append(new_square)
    def default_game(self):
        print("The default version of the game has been chosen.")
        try:
            self.receive_board('BOARD_PL.csv')
            print(f"Success! The board contains {len(self.properties)} squares.")
        except FileNotFoundError:
            print("[ERROR] Did not find the PLANSZA.csv file in the game folder!")

    def current_square(self, position):
        return self.properties[position]

    def custom_game(self):
        print("\n======================================")
        print("         CUSTOM GAME CREATOR")
        print("======================================")
        print("Enter the squares one by one. To finish and save, type 'DONE' as the square name.\n")
        self.properties.clear()
        number_pattern = re.compile(r"^\d+$")
        while True:
            name = input("1. Enter the square NAME (or 'DONE'): ").strip()
            if name.upper() == "DONE":
                if len(self.properties) == 0:
                    print("[ERROR] The board cannot be empty! Add at least one square.")
                    continue
                break
            print("2. Enter the square TYPE. Choose from:")
            print("   -> street (standard purchasable property)")
            print("   -> tax (e.g., Income Tax, Luxury Tax)")
            print("   -> station / utility (e.g., Railway, Water Works)")
            print("   -> start / chance / community_chest / visit / parking / go_to_jail")
            square_type = input("   Your choice: ").strip().lower()
            price = 0
            tax = 0
            color = "none"
            if square_type == "street":
                while True:
                    price_in = input("3. Enter the purchase PRICE: ").strip()
                    if number_pattern.match(price_in):
                        price = int(price_in)
                        break
                    print("[ERROR] The price must consist only of digits! Try again.")
                while True:
                    tax_in = input("4. Enter the base RENT/TAX: ").strip()
                    if number_pattern.match(tax_in):
                        tax = int(tax_in)
                        break
                    print("[ERROR] The rent must consist only of digits! Try again.")
                color = input("5. Enter the group COLOR (e.g., red): ").strip().lower()
            elif square_type == "tax":
                while True:
                    amount_in = input("3. Enter the TAX AMOUNT to be paid by the player: ").strip()
                    if number_pattern.match(amount_in):
                        tax = int(amount_in)
                        break
                    print("[ERROR] The tax amount must be a number!")
            elif square_type in ["station", "utility"]:
                while True:
                    price_in = input("3. Enter the purchase PRICE: ").strip()
                    if number_pattern.match(price_in):
                        price = int(price_in)
                        break
                    print("[ERROR] The price must be a number!")
            else:
                print("-> Passive special square selected. Prices and taxes automatically set to $0.")
            new_square = Property(name=name, price=price, tax=tax, square_type=square_type, color=color)
            self.properties.append(new_square)
            print(f" Successfully added: {name} (Type: {square_type})\n" + "-" * 40)
        print("\n=== SAVING THE BOARD ===")
        file_name = input("Enter a name for the CSV file (e.g., my_board.csv): ").strip()
        if not file_name.lower().endswith(".csv"):
            file_name += ".csv"

        with open(file_name, mode='w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file, delimiter=';')
            for square in self.properties:
                writer.writerow([square.name, square.price, square.tax, square.type, square.color])

        print(f" Success! The board has been saved as '{file_name}' and loaded into the current game!")




