# Gra Monopoly CLI 
Tekstowa gra bezpośrednio w interfejsie napisana w języku Python.

## Pliki
- `game.py` - główna pętla gry
- `card.py` - talie kart Szansa i Kasa społeczna
- `models.py` - klasy Player, Property, Board
- `setup_game.py` - konfiguracja graczy
- `BOARD_PL.csv` - dane planszy 

## Uruchomienie
1. Upewnij się, że masz zainstalowanego Pythona w jak najnowszej wersji. 
2. Umieść wszystkie pliki w jednym folderze.
3. Uruchom grę wpis: ``` python game.py ```

## Jak grać?
- 2-4 graczy
- możliwość wyboru własnej bądź dołączonej planszy ładowanej bezpośrednio z pliku CSV.
- Każdy gracz zaczyna z $1500
- Komendy w trakcie tury:
  - `R` — rzut kośćmi
  - `B` — buduj domek/hotel
  - `S` — sprzedaj domek/hotel
  - `M` — zastaw nieruchomość
  - `U` — wykup nieruchomość
  - `I` — statystyki gracza
  - `Q` — wyjście z gry
