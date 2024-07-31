import socket
import threading
from collections import defaultdict
import select

# GM sends "table;cozmo;[count]" before each player turn
# NOTE: GM always sends response to message, so you must wait for a response before you can send your next card

# Whole game flow (as I understood it)
# 1) All players and dealer connect to Game Master with a "table;cozmoName;position" message
# Once we get all the players we start round
# 2) Dealer somehow signals the GM to start round. Message for this is "table;START;".
# 3) GM sends out a hand start message ("table;START;same/new;num_decks;num_players")
# 4) Dealer sends first hidden card value with a card value message ("table;cozmoName;cardNumber;cardValue") with cozmoName equal to "dealer" (not necessary)
# 5) All players receive their initial two cards and send out a card value message for each card
# 6) Dealer sends shown card value, which updates the count. GM sends "table;BLACKJACK" if dealer got blackjack
# 6) GM sends out current card count
# 7) Player sends out card value of their card if they hit or "table;name;-1;-1" if they stay.
# 8) Repeat (6) and (7) until it is dealer's turn
# 9) Dealer plays their turn.
# 10) Once GM receives a stay action from dealer, GM sends out message with final dealer total ("table;dealer;final;value")
# Keep same shoe until it runs out.
# GM waits for dealer to start next round 'table;dealer;newhand;

# All messages (in roughly the order they are sent):
# Players connect: "table;cozmoName:position"
# GM acknowledges player connection: "table;cozmoName;CONNECTED"
# Dealer sends start signal to GM: "table;START;num_decks"
# GM sends out round start signal to cozmos: "table;START;same/new;num_decks;num_players"
# Before each player action, GM sends out message with card count and the cozmo whose turn it is: "table;cozmoName;[count]"
# Players send card value message to GM when they draw a card and when they hit: "table;cozmoName;cardNumber;cardValue"
# Player send stay message when they stay or go bust: "table;name;-1;-1"
# GM send bj message if dealer gets blackjack: "table;BLACKJACK"
# Dealer sends card value messages if they have to until they go bust: "table;dealer;cardNumber;cardValue"
# Dealer sends stay message: "table;dealer;-1;-1"
# Message with final dealer total: "table;dealer;final;value"

# This is mostly done, but I still need to iron out a few kinks before it works. I also need to test.


class Game:
    def __init__(self, table_id: str) -> None:
        self.cards_played = [0] * 13
        self.num_decks = 0
        self.player_hands = defaultdict(list)
        self.order = {}
        self.current_position = 1
        self.table_id = table_id
        self.message = ""

    def __calculate_hand_total__(self, player_name: str) -> int:
        cards = self.player_hands[player_name]
        total = 0
        count_aces = 0

        for card in cards:
            match card:
                case "Ace":
                    count_aces += 1
                case "Two":
                    total += 2
                case "Three":
                    total += 3
                case "Four":
                    total += 4
                case "Five":
                    total += 5
                case "Six":
                    total += 6
                case "Seven":
                    total += 7
                case "Eight":
                    total += 8
                case "Nine":
                    total += 9
                case "Ten":
                    total += 10
                case "Jack":
                    total += 10
                case "Queen":
                    total += 10
                case "King":
                    total += 10

        if total > 21 or total + count_aces > 21:
            return -1

        # TODO: Deal with aces

    def add_player(self, name: str, position: int):
        if position not in self.order:
            self.order[position] = name
            self.message = f"{self.table_id};{name};CONNECTED"

    def update_count(self, cozmo_name: str, card_value: str, card_number: int):
        # Update count
        match card_value:
            case "Ace":
                self.cards_played[0] += 1
            case "Two":
                self.cards_played[1] += 1
            case "Three":
                self.cards_played[2] += 1
            case "Four":
                self.cards_played[3] += 1
            case "Five":
                self.cards_played[4] += 1
            case "Six":
                self.cards_played[5] += 1
            case "Seven":
                self.cards_played[6] += 1
            case "Eight":
                self.cards_played[7] += 1
            case "Nine":
                self.cards_played[8] += 1
            case "Ten":
                self.cards_played[9] += 1
            case "Jack":
                self.cards_played[10] += 1
            case "Queen":
                self.cards_played[11] += 1
            case "King":
                self.cards_played[12] += 1

        # Add card to player's hand
        self.player_hands[cozmo_name].append(card_value)

        if (
            cozmo_name == "dealer"
            and len(self.player_hands[cozmo_name]) == 2
            and self.__calculate_hand_total__(cozmo_name) == 21
        ):
            self.message = f"{self.table_id};BLACKJACK"
        elif card_number > 2:
            self.message = f"{self.table_id};{cozmo_name};{self.cards_played}"
        else:
            self.message = f"{self.table_id};{cozmo_name};RECEIVED"

    def stay(self, cozmo_name: str):
        self.current_position = (
            (self.current_position + 1) % (len(self.order) + 1)
            if (self.current_position + 1) != (len(self.order) + 1)
            else 1
        )

        if cozmo_name == "dealer":
            self.message = f"{self.table_id};dealer;final;{self.__calculate_hand_total__(cozmo_name)}"
        else:
            self.message = f"{self.table_id};{self.order[self.current_position]};{self.cards_played}"

    def hand_start(self, num_decks) -> None:
        self.num_decks = num_decks
        self.player_hands = []

        # TODO: Check if 20 cards is a good number to stop at
        if sum(self.cards_played) + 20 > self.num_decks * 52:
            game_status = "new"
            self.cards_played = []
        else:
            game_status = "same"

        self.message = (
            f"{self.table_id};START;{game_status};{self.num_decks};{len(self.order)}"
        )

    def dealer_blackjack(self) -> None:
        self.message = f"{self.table_id};BLACKJACK"


class GameMaster:
    CONNECTION_BACKLOG = 40

    def __init__(self, port: int) -> None:
        self.port = port
        self.games = {}
        self.clients = []
        self.lock = threading.Lock()

    def __initialize_server__(self) -> None:
        """Sets up server socket and binds it to the specified port"""
        # Create a socket object
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        # Bind the socket to a specific address and port
        self.server_socket.bind(("localhost", self.port))

        # Set the server socket to non-blocking mode
        self.server_socket.setblocking(False)

    def __broadcast__(self, game):
        with self.lock:
            for client in self.clients:
                try:
                    client.sendall(self.games[game].message.encode())
                except socket.error as e:
                    # Handle errors, e.g., if the client disconnected
                    print(f"Error sending response to a client: {e}")
                    self.clients.remove(client)
                    client.close()

    def __handle_message__(self, message: str) -> None:
        args = message.split(";")

        #  Add player message
        if len(args) == 3:
            table, cozmo, position = message.split(";")

            if table not in self.games:
                new_game = Game(table)
                self.games[table] = new_game

            self.games[table].add_player(cozmo, position)

        # Start message
        elif len(args) == 3 and args[1] == "START":
            table, _, num_decks = args

            if table in self.games:
                self.games[table].hand_start(num_decks)

        # Card value message
        elif len(args) == 4:
            table, cozmo_name, card_number, card_value = args

            if table in self.games:
                if card_number == "-1" and card_number == "-1":
                    self.games[table].stay(cozmo_name)
                else:
                    self.games[table].update_count(
                        cozmo_name, card_value, int(card_number)
                    )

        # Send game's message
        if table in self.games and self.games[table].message != "":
            self.__broadcast__(table)

    def __listen_for_connections__(self) -> None:
        while True:
            # Use select to check for readable sockets
            readable, _, _ = select.select([self.server_socket] + self.clients, [], [])

            for sock in readable:
                if sock is self.server_socket:
                    # Accept new connection
                    client_socket, addr = self.server_socket.accept()
                    print(f"Accepted connection from {addr}")
                    client_socket.setblocking(False)
                    with self.lock:
                        self.clients.append(client_socket)
                else:
                    # Check if the socket is ready for reading
                    if sock in select.select([sock], [], [])[0]:
                        # Receive messages and handle them
                        try:
                            message = sock.recv(4096).decode()
                            if message:
                                self.__handle_message__(message)
                        except socket.error as e:
                            # Handle disconnections or errors
                            print(f"Error reading from {sock.getpeername()}: {e}")
                            with self.lock:
                                self.clients.remove(sock)
                            sock.close()

    def listen(self) -> None:
        """Starts threads to listen for connections and messages"""
        # Initialize server
        self.__initialize_server__()

        # Start listening for connections
        self.server_socket.listen(GameMaster.CONNECTION_BACKLOG)

        self.accepting_thread = threading.Thread(target=self.__listen_for_connections__)
        self.message_handling_thread = None

        print(f"GM listening on {self.server_socket.getsockname()}")
        self.accepting_thread.start()


if __name__ == "__main__":
    gm = GameMaster(3306)
    gm.listen()
