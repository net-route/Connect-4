
import logging
import random
import os
import json
import rich
from rich.panel import Panel
from rich.table import Table
from rich.console import Console
from colorama import Fore, Style


def main():
    logging.basicConfig(
        filename='cnct4.log',
        format='%(asctime)s %(message)s',
        datefmt='%m/%d/%Y %H:%M:%S',
        level=logging.INFO,
    )

    logging.info("App started...")

    rich.print(Panel(
        "Before starting, please be sure to notify me of anything that can be improved! You can contact me on"
        "[REDACTED] with any errors or suggestions. Have fun!",
        title="Welcome",
        padding=1
    ))

    header()
    print()

    show_leaderboard()
    print()

    logging.info("Entering game loop...")

    game_loop()


def header():
    console = Console()

    style = "bold white on #284ca9"
    style2 = "#fdca70"

    console.print("--------------------------------------------", style=style, justify="center")
    console.print("--------------------------------------------", style=style, justify="center")
    console.print("CONNECT [white]4[/white]", style=style, justify="center")
    console.print("The Classic Vertical Four-in-a-row Game!", style=style, justify="center")
    console.print("--------------------------------------------\n", style=style, justify="center")
    console.print("--------------------------------------------\n", style=style, justify="center")
    console.print("Console Edition - Powered by Python!\n", style=style2, justify="center")


def player_setup():
    console = Console()
    error_style = "bold white on #C70017"
    interrupt_style = "bold white on #730e1d"
    try:
        player_1 = input("Please input the name for" + Fore.LIGHTGREEN_EX + " player 1: " + Style.RESET_ALL)
        if player_1 == "":
            player_1 = "Player 1"
        player_2 = input("Please input the name for" + Fore.LIGHTGREEN_EX + " player 2: " + Style.RESET_ALL)
        if player_2 == "":
            player_2 = "Player 2"
        return player_1, player_2
    except EOFError:
        console.print("EOF ERROR: Invalid formatting. Assigning default names...", style=error_style)
        logging.error(f"ERROR: EOF. Unexpected character entered. Assigning default names...")
        player_1 = "Player 1"
        player_2 = "Player 2"
        return player_1, player_2
    except KeyboardInterrupt:
        console.print("All right, see you later.", style=interrupt_style)
        logging.warning("WARNING: User input CTRL + C to end program unexpectedly.")
        exit()
    except Exception as x:
        console.print("Whoa, that's not right...", style=error_style)
        console.print(f"Unexpected error: {x}. Assigning default names as a precaution...", style=error_style)
        logging.error(f"ERROR: {x}. Assigning default names...")
        player_1 = "Player 1"
        player_2 = "Player 2"
        return player_1, player_2


def game_loop():
    # NAME PLAYERS
    player_1, player_2 = player_setup()
    players = [player_1, player_2]
    logging.info("Game starting with %s and %s", player_1, player_2)

    # SETUP BOARD
    # The board is presented an empty set of lists that we fill in.
    board = [
        [None, None, None, None, None, None, None],
        [None, None, None, None, None, None, None],
        [None, None, None, None, None, None, None],
        [None, None, None, None, None, None, None],
        [None, None, None, None, None, None, None],
        [None, None, None, None, None, None, None],
    ]

    # CHOOSE WHO GOES FIRST
    print(f"\nLet's flip for who goes first:" + Fore.LIGHTGREEN_EX + f" {player_1} " + Fore.WHITE +
          "or" + Fore.LIGHTGREEN_EX + f" {player_2}" + Style.RESET_ALL + "...")
    coin_flip = random.randint(0, 1)
    if coin_flip == 0:
        active_player_index = 0  # Starts with player 1 taking a turn
        print(Fore.LIGHTGREEN_EX + f"{player_1}" + Style.RESET_ALL + " goes first!")
        logging.info("Player 1: %s, is going first", player_1)
    else:
        active_player_index = 1  # Starts with player 2 taking a turn
        print(f"{player_2} goes first!")
        logging.info("Player 2: %s, is going first", player_2)

    # Game Pieces
    symbols = [Fore.LIGHTRED_EX + "X" + Style.RESET_ALL, Fore.LIGHTCYAN_EX + "O" + Style.RESET_ALL]

    # GAME PLAY
    player = players[active_player_index]  # Safety assignment to avoid issues with 'player' later
    while not find_winner(board):
        game_piece = symbols[active_player_index]
        player = players[active_player_index]

        announce_turn(player)
        show_board(board)

        choose_location(board, game_piece)
        check_winning_sequence(board)
        active_player_index = (active_player_index + 1) % len(players)
        logging.info("Changing over to %s's turn...", player)
    logging.info("%s has won the game.", player)
    console = Console()
    console.print(f"\nGAME OVER! [#f7b23c]{player}[/#f7b23c] has won with this board!", style="white on #284ca9")
    show_board(board)
    record_win(player)

    new_game_request(player)


def show_board(board):
    console = Console()
    print("  ", end='')
    for n in range(1, 8, 1):
        console.print(n, end='   ')
    print()
    for row in board:
        print("| ", end='')
        for cell in row:
            game_piece = cell if cell is not None else "_"
            print(game_piece, end=" | ")
        print()


def choose_location(board, symbol):
    console = Console()
    error_style = "bold white on #C70017"
    interrupt_style = "bold white on #730e1d"
    try:
        while True:
            column = int(input("Which column will you place your piece?: "))

            column -= 1
            logging.info("Column %s has been selected", column)
            if column < 0 or column >= len(board[0]):
                logging.info("Player has selected an invalid location.")
                return False

            cell = board[0][column]
            if cell is not None:
                print("Whoops, looks like there's no space there. Try another.")
                logging.info("Player has tried placing a symbol in a full column")
                continue

            break

        current_row = 0

        # Starts for loop; checks all entries in the board list
        # IF condition 1: subtracts 1 from total list number to check if current row is same as last row: empty
        # IF condition 2: checks if column in the row directly underneath has something in it.
        # if either are met, assigns current_row to row value
        # This allows the check to keep moving down the column list until it finds something or hits the bottom
        for row in range(0, len(board)):
            if row == (len(board) - 1) or board[row+1][column] is not None:
                current_row = row
                break

        board[current_row][column] = symbol
        return True
    except EOFError:
        console.print("EOF ERROR: Invalid formatting. Skipping turn to avoid disaster...", style=error_style)
        logging.error(f"ERROR: EOF. Unexpected character entered. Skipping turn.")
    except KeyboardInterrupt:
        console.print("All right, see you later.", style=interrupt_style)
        logging.warning("WARNING: User input CTRL + C to end program unexpectedly.")
        exit()
    except Exception as x:
        console.print("Whoa, that's not right...", style=error_style)
        console.print(f"Unexpected error: {x}", style=error_style)
        console.print("Skipping turn to avoid disaster...", style=error_style)
        logging.error(f"Unexpected ERROR: {x}. Skipping turn.")


def announce_turn(player):
    print()
    print("It's" + Fore.LIGHTGREEN_EX + f" {player}'s " + Style.RESET_ALL + "turn. Make your move.")
    print()
    logging.info("%s is making their turn", player)


def find_winner(board):
    logging.info("Checking for possible win sequences...")
    sequences = check_winning_sequence(board)

    for cells in sequences:
        symbol1 = cells[0]
        if symbol1 and all(symbol1 == cell for cell in cells):
            return True

    return False


def check_winning_sequence(board):
    sequences = []

    # Win by rows.
    rows = board
    for row in rows:
        # Go through each row and get any consecutive sequence of 4 cells
        fours_across = find_sequences_of_four_cells_in_a_row(row)
        sequences.extend(fours_across)

    # Win by columns
    for col_idx in range(0, 7):
        col = [
            board[0][col_idx],
            board[1][col_idx],
            board[2][col_idx],
            board[3][col_idx],
            board[4][col_idx],
            board[5][col_idx],
        ]
        # Go through each column and get any consecutive sequence of 4 cells
        fours_down = find_sequences_of_four_cells_in_a_row(col)
        sequences.extend(fours_down)

    diagonals = [
        # Down to the right diagonals
        [board[2][0], board[3][1], board[4][2], board[5][3]],
        [board[1][0], board[2][1], board[3][2], board[4][3], board[5][4]],
        [board[0][0], board[1][1], board[2][2], board[3][3], board[4][4], board[5][5]],
        [board[0][1], board[1][2], board[2][3], board[3][4], board[4][5], board[5][6]],
        [board[0][2], board[1][3], board[2][4], board[3][5], board[4][6]],
        [board[0][3], board[1][4], board[2][5], board[3][6]],

        # Down to the left diagonals
        [board[0][3], board[1][2], board[2][1], board[3][0]],
        [board[0][4], board[1][3], board[2][2], board[3][1], board[4][0]],
        [board[0][5], board[1][4], board[2][3], board[3][2], board[4][1], board[5][0]],
        [board[0][6], board[1][5], board[2][4], board[3][3], board[4][2], board[5][1]],
        [board[1][6], board[2][5], board[3][4], board[4][3], board[5][2]],
        [board[2][6], board[3][5], board[4][4], board[5][3]],
    ]

    for diag in diagonals:
        fours_diagonals = find_sequences_of_four_cells_in_a_row(diag)
        sequences.extend(fours_diagonals)

    return sequences


def find_sequences_of_four_cells_in_a_row(cells):
    sequences = []
    for n in range(0, len(cells) - 3):
        candidate = cells[n:n + 4]
        if len(candidate) == 4:
            sequences.append(candidate)

    return sequences


def new_game_request(player):
    console = Console()
    style = "bold white on #284ca9"
    style2 = "bold white on #730e1d"
    error_style = "bold white on #C70017"
    interrupt_style = "bold white on #730e1d"

    logging.info("Requesting user for a new game...")
    valid_responses = ["y", "yes"]
    negative_responses = ["n", "no"]
    rich.print(Panel(f"\nCongratulations, [#15B20c]{player}[/]!"
                     " The game is over and there is not much else to show, but... "
                     "Would you like to play again?", title="Game over!",))
    try:
        response = input("\n[Y]es or [N]o: ")
        if response.lower() in valid_responses:
            console.print("\nOkay, starting a new game...\n\n", style=style)
            logging.info("Game restarting...")
            game_loop()
        elif response.lower() in negative_responses:
            console.print("\nAll right, thanks for playing.", style=style2)
            logging.info("Session terminated.")
            exit()
    except EOFError:
        console.print("EOF ERROR: Invalid character string entered. Quitting game anyway...", style=error_style)
        logging.error("ERROR: EOF. Unexpected character entered. Terminating...")
        exit()
    except KeyboardInterrupt:
        console.print("All right, see you later.", style=interrupt_style)
        logging.warning("WARNING: User input CTRL + C to end program unexpectedly.")
        exit()
    except Exception as x:
        console.print("Whoa, that's not right...", style=error_style)
        console.print(f"Unexpected error: {x}", style=error_style)
        console.print("Proceeding to terminate program anyway...", style=error_style)
        logging.error(f"Unexpected ERROR: {x}. Terminating...")
        exit()


def show_leaderboard():
    leaders = load_leaderboard()

    table = Table(box=rich.table.box.ROUNDED)
    table.add_column("[#f7b23c]LEADERBOARD[/#f7b23c]",
                     justify="left",
                     style="bold",
                     )

    sorted_leaders = list(leaders.items())  # asking for 'items' returns the key and item
    sorted_leaders.sort(key=lambda l: l[1], reverse=True)
    # ^ sorts leaderboard in descending order based on win count (second item, aka [1])
    for name, wins in sorted_leaders[0:5]:  # [0:5] expression will only list the first five results
        table.add_row(f"{wins:,} -- {name}")
        # using , in wins lets us use commas when printing the number "3,000"

    console = Console()
    console.print(table)


def load_leaderboard():
    directory = os.path.dirname(__file__)
    filename = os.path.join(directory, 'cnct4_leaderboard.json')

    if not os.path.exists(filename):
        logging.warning("Missing 'cnct4_leaderboard.json'. Creating new instance.")
        return {"Mario": 3, "Gamer_Guy": 1}

    with open(filename, 'r', encoding='utf-8') as fin:
        return json.load(fin)


def record_win(player):
    leaders = load_leaderboard()

    if player in leaders:
        leaders[player] += 1
    else:
        leaders[player] = 1

    directory = os.path.dirname(__file__)
    filename = os.path.join(directory, 'cnct4_leaderboard.json')

    with open(filename, 'w', encoding='utf-8') as fout:
        json.dump(leaders, fout)


if __name__ == '__main__':
    main()
