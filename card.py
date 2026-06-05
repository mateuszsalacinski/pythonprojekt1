import random
from models import Player
class Deck:
    def __init__(self, name, cards):
        self.name = name
        self.cards = cards
    def draw_card(self, player, players_list=None, board = None):
        card = random.choice(self.cards)
        print(f"\n Card drawn [{self.name}]:{card['text']}")
        card ['action'](player, players_list, board)
def find_nearest(player: Player, board_properties, square_type):
        positions = [i for i, prop in enumerate(board_properties) if prop.type == square_type]
        if not positions:
            return
        nearest = min(positions, key=lambda pos: (pos - player.position) % len(board_properties))
        player.move_to(nearest)
chance_cards = [
        {"text": "Advance to Aleje Ujazdowskie.", "action": lambda p, pl, b: p.move_to(39)},
        {"text": "Advance to START (Collect $200).", "action": lambda p, pl, b: p.move_to(0)},
        {"text": "Advance to Plac Wilsona. If you pass START, collect $200.", "action": lambda p, pl, b: p.move_to(24)},
        {"text": "Advance to Ulica Plowiecka. If you pass START, collect $200.", "action": lambda p, pl, b: p.move_to(11)},
        {"text": "Advance to the nearest Railroad.", "action": lambda p, pl, b: find_nearest(p, b.properties, "station") if b else None},
        {"text": "Advance token to nearest Utility.", "action": lambda p, pl, b: find_nearest(p, b.properties, "utility") if b else None},
        {"text": "Bank pays you dividend of $50.", "action": lambda p, pl, b: p.receive(50)},
        {"text": "Get Out of Jail Free.", "action": lambda p, pl, b: setattr(p, 'get_out_of_jail_card', True)},
        {"text": "Go Back 3 Spaces.", "action": lambda p, pl, b: p.move_to((p.position - 3) % 40, pass_start=False)},
        {"text": "Go to Jail. Go directly to Jail.", "action": lambda p, pl, b: p.move_to(10, pass_start=False)},
        {"text": "Make general repairs on all your property.",
         "action": lambda p, pl, b: p.pay(25 * sum(1 for prop in p.properties if 0 < prop.houses < 5) + 100 * sum(1 for prop in p.properties if prop.houses == 5))},
        {"text": "Speeding fine $15.", "action": lambda p, pl, b: p.pay(15)},
        {"text": "Take a trip to Dworzec Zachodni.", "action": lambda p, pl, b: p.move_to(5)},
        {"text": "You have been elected Chairman. Pay each player $50.",
        "action": lambda p, pl, b: [p.pay(50, recipient=other) for other in (pl or []) if other != p and not other.is_bankrupt]},
        {"text": "Your building loan matures. Collect $150.", "action": lambda p, pl, b: p.receive(150)}
    ]
community_chest_cards = [
        {"text": "Advance to START (Collect $200).", "action": lambda p, pl, b: p.move_to(0)},
        {"text": "Bank error in your favor. Collect $200.", "action": lambda p, pl, b: p.receive(200)},
        {"text": "Doctor's fee. Pay $50.", "action": lambda p, pl, b: p.pay(50)},
        {"text": "From sale of stock you get $50.", "action": lambda p, pl, b: p.receive(50)},
        {"text": "Get Out of Jail Free.", "action": lambda p, pl, b: setattr(p, 'get_out_of_jail_card', True)},
        {"text": "Go to Jail. Go directly to jail.", "action": lambda p, pl, b: p.move_to(10, pass_start=False)},
        {"text": "Holiday fund matures. Receive $100.", "action": lambda p, pl, b: p.receive(100)},
        {"text": "Income tax refund. Collect $20.", "action": lambda p, pl, b: p.receive(20)},
        {"text": "It is your birthday. Collect $10 from every player.",
        "action": lambda p, pl, b: [other.pay(10, recipient=p) for other in (pl or []) if other != p and not other.is_bankrupt]},
        {"text": "Life insurance matures. Collect $100.", "action": lambda p, pl, b: p.receive(100)},
        {"text": "Pay hospital fees of $100.", "action": lambda p, pl, b: p.pay(100)},
        {"text": "Pay school fees of $50.", "action": lambda p, pl, b: p.pay(50)},
        {"text": "Receive $25 consultancy fee.", "action": lambda p, pl, b: p.receive(25)},
        {"text": "You are assessed for street repairs. Pay $40 per house, $115 per hotel.",
        "action": lambda p, pl, b: p.pay(40 * sum(1 for prop in p.properties if 0 < prop.houses < 5) + 115 * sum(1 for prop in p.properties if prop.houses == 5))},
        {"text": "Second prize in a beauty contest. Collect $10.", "action": lambda p, pl, b: p.receive(10)},
        {"text": "You inherit $100.", "action": lambda p, pl, b: p.receive(100)},

    ]
chance_deck = Deck("Chance", chance_cards)
community_chest_deck = Deck("Community Chest", community_chest_cards)