import copy
import re
from abc import ABC, abstractmethod
import random
from colorama import Fore, Back, Style
from enum import Enum


# import sys
# f1=open("testcase.txt","rt")
# sys.stdin=f1
# f2=open("out.txt","wt")
# sys.stdout=f2

class ChessSituation(Enum):
    NOTHING: int = 0
    MOVED: int = 1
    SELECTED: int = 2


class UserSituation(Enum):
    NOTHING: int = 0
    LOGGEDIN: int = 1
    PLAYING: int = 2


class User:
    users = []

    def __init__(self, username: str = "", password: str = "", wins: int = 0, draws: int = 0, losses: int = 0,
                 scores: int = 0, undos: int = 0):
        self.username = username
        self.password = password
        self.wins = wins
        self.draws = draws
        self.losses = losses
        self.scores = scores
        self.undos = undos

    @staticmethod
    def register(username: str, password: str):
        if not re.search("^[a-zA-Z0-9_]+$", username):
            print("username format is invalid")
            return None
        if not re.search("^[a-zA-Z0-9_]+$", password):
            print("password format is invalid")
            return None

        if username in User.users:
            print("a user exists with this username")
            return None

        User.users.append(User(username, password))
        print("register successful")

    @staticmethod
    def login(username: str, password: str):
        if not re.search("^[a-zA-Z0-9_]+$", username):
            print("username format is invalid")
            return None

        user = next((u for u in User.users if u.username == username), None)
        if not user:
            print("no user exists with this username")
            return None

        if not re.search("^[a-zA-Z0-9_]+$", password):
            print("password format is invalid")
            return None
        if user.password != password:
            print("incorrect password")
            return None
        print("login successful")
        chess.white_user = user  # Assuming chess is defined elsewhere
        return user

    @staticmethod
    def remove(username: str, password: str):
        if not re.search("^[a-zA-Z0-9_]+$", username):
            print("username format is invalid")
            return None

        user = next((u for u in User.users if u.username == username), None)
        if not user:
            print("no user exists with this username")
            return None

        if not re.search("^[a-zA-Z0-9_]+$", password):
            print("password format is invalid")
            return None
        if user.password != password:
            print("incorrect password")
            return None

        User.users = [u for u in User.users if u.username != username]
        print(f"removed {username} successfully")

    @staticmethod
    def show_scoreboard():
        sorted_users = sorted(User.users, key=lambda u: (-u.scores, -u.wins, -u.draws, u.losses, u.username))
        print(f"{'Username'} {'Score'} {'Wins'} {'Draws'} {'Losses'}")
        for user in sorted_users:
            print(f"{user.username} {user.scores} {user.wins} {user.draws} {user.losses}")

    def __str__(self):
        return f"{self.username}"

    def __eq__(self, other):
        if isinstance(other, str):
            return other == self.username or other == self.password
        elif isinstance(other, User):
            return other.username == self.username or other.password == self.password

    # def start_game(self, username: str):
    #     if not re.search("^[a-zA-Z0-9_]+$", username):
    #         print("username format is invalid")
    #         return None
    #     if self.limit < 0:
    #         print("number should be positive to have a limit or 0 for no limit")

    def log_out(self, username: str, password: str):
        pass


class Piece(ABC):
    def __init__(self, name: str = "", x: int = 0, y: int = 0, color: str = "", prev_x: int = 0, prev_y: int = 0,
                 dest_x: int = 0, dest_y: int = 0, if_undo: bool = False):
        self.name = name
        self.x = x
        self.y = y
        self.color = color
        self.prev_x = prev_x
        self.prev_y = prev_y
        self.dest_x = dest_x
        self.dest_y = dest_y
        self.if_undo = if_undo

    def __str__(self):
        return f"{self.name}{self.color}"

    def __eq__(self, other):
        if other is None:
            return False
        return self.y == other.y and self.x == other.x

    @abstractmethod
    def move(self, x, y, board):
        pass


class King(Piece):
    def __init__(self, color, x, y):
        super().__init__('K', x, y, color)

    def move(self, x, y, board):
        self.prev_x, self.prev_y = self.x, self.y
        result = MoveResult()  # Create a new MoveResult instance
        s_r, s_c = CoordinatesHelper.cartesian_to_index(self.x, self.y)
        d_r, d_c = CoordinatesHelper.cartesian_to_index(x, y)

        # Check if move is within valid range for the King
        if ((s_c - d_c) ** 2) + ((s_r - d_r) ** 2) <= 0 or ((s_c - d_c) ** 2) + ((s_r - d_r) ** 2) > 2:
            result.valid = False
            result.message = "Invalid move for King."
            return result  # Return a MoveResult with valid=False and a message

        dest_piece = board[d_r][d_c]
        if dest_piece is not None:
            if dest_piece.color == self.color:
                result.valid = False
                result.message = "Invalid move. Cannot capture your own piece."
                return result  # Return a MoveResult indicating an invalid capture attempt
            else:
                print(f"{dest_piece} captured!")
                result.captured_piece = dest_piece
                result.message = f"{dest_piece} captured!"
                board[d_r][d_c] = None  # Remove captured piece from board

        # Move the King and update the MoveResult
        board[d_r][d_c] = self
        board[s_r][s_c] = None
        result.valid = True
        result.new_position = (x, y)  # Store the new position as a tuple
        result.message = "Valid move for King."
        self.x, self.y = x, y
        return result


class Queen(Piece):
    def __init__(self, color, x, y):
        super().__init__('Q', x, y, color)

    def move(self, x, y, board):
        self.prev_x, self.prev_y = self.x, self.y
        result = MoveResult()  # Create a new MoveResult instance
        s_r, s_c = CoordinatesHelper.cartesian_to_index(self.x, self.y)
        d_r, d_c = CoordinatesHelper.cartesian_to_index(x, y)

        # Validate Queen's movement (straight lines or diagonals)
        if s_r == d_r or s_c == d_c:  # Straight-line movement
            if s_r == d_r:  # Horizontal move
                step = 1 if d_c > s_c else -1
                for c in range(s_c + step, d_c, step):
                    if board[s_r][c] is not None:  # Path is blocked
                        result.valid = False
                        result.message = "Invalid move. Piece in the way."
                        return result
            elif s_c == d_c:  # Vertical move
                step = 1 if d_r > s_r else -1
                for r in range(s_r + step, d_r, step):
                    if board[r][s_c] is not None:  # Path is blocked
                        result.valid = False
                        result.message = "Invalid move. Piece in the way."
                        return result
        elif abs(s_r - d_r) == abs(s_c - d_c):  # Diagonal movement
            row_step = 1 if d_r > s_r else -1
            col_step = 1 if d_c > s_c else -1
            r, c = s_r + row_step, s_c + col_step
            while r != d_r and c != d_c:
                if board[r][c] is not None:  # Path is blocked
                    result.valid = False
                    result.message = "Invalid move. Piece in the way."
                    return result
                r += row_step
                c += col_step
        else:  # Invalid move for Queen
            result.valid = False
            result.message = "Invalid move for Queen. Queen can only move in straight lines or diagonally."
            return result

        # Check destination square
        dest_piece = board[d_r][d_c]
        if dest_piece is not None:
            if dest_piece.color == self.color:  # Cannot capture own piece
                result.valid = False
                result.message = "Invalid move. Cannot capture your own piece."
                return result
            else:  # Capture opponent's piece
                result.captured_piece = dest_piece
                result.message = f"{dest_piece} captured!"
                board[d_r][d_c] = None  # Remove captured piece

        # Update board and move Queen
        board[d_r][d_c] = self
        board[s_r][s_c] = None
        result.valid = True
        result.new_position = (x, y)
        result.message = "Valid move for Queen."
        self.x, self.y = x, y
        return result


class Knight(Piece):
    def __init__(self, color, x, y):
        super().__init__('N', x, y, color)

    def move(self, x, y, board):
        self.prev_x, self.prev_y = self.x, self.y
        result = MoveResult()  # Create a new MoveResult instance
        s_r, s_c = CoordinatesHelper.cartesian_to_index(self.x, self.y)
        d_r, d_c = CoordinatesHelper.cartesian_to_index(x, y)

        # Validate Knight's unique "L" shaped movement
        if ((d_c - s_c) ** 2) + ((d_r - s_r) ** 2) != 5:
            result.valid = False
            result.message = "Invalid move for Knight. Knight moves in an L-shape."
            return result

        # Check destination square
        dest_piece = board[d_r][d_c]
        if dest_piece is not None:
            if dest_piece.color == self.color:  # Cannot capture own piece
                result.valid = False
                result.message = "Invalid move. Cannot capture your own piece."
                return result
            else:  # Capture opponent's piece
                result.captured_piece = dest_piece
                result.message = f"{dest_piece} captured!"
                board[d_r][d_c] = None  # Remove captured piece

        # Update board and move Knight
        board[d_r][d_c] = self
        board[s_r][s_c] = None
        result.valid = True
        result.new_position = (x, y)
        result.message = "Valid move for Knight."
        self.x, self.y = x, y
        return result


class Bishop(Piece):
    def __init__(self, color, x, y):
        super().__init__('B', x, y, color)

    def move(self, x, y, board):
        self.prev_x, self.prev_y = self.x, self.y
        result = MoveResult()  # Create a new MoveResult instance
        s_r, s_c = CoordinatesHelper.cartesian_to_index(self.x, self.y)
        d_r, d_c = CoordinatesHelper.cartesian_to_index(x, y)

        # Validate diagonal movement (Bishop's movement rule)
        if abs(s_r - d_r) != abs(s_c - d_c):
            result.valid = False
            result.message = "Invalid move for Bishop. Bishop can only move diagonally."
            return result

        # Check if the diagonal path is clear
        row_step = 1 if d_r > s_r else -1
        col_step = 1 if d_c > s_c else -1
        r, c = s_r + row_step, s_c + col_step
        while r != d_r and c != d_c:
            if board[r][c] is not None:  # Path is blocked
                result.valid = False
                result.message = "Invalid move. Piece in the way."
                return result
            r += row_step
            c += col_step

        # Check destination square
        dest_piece = board[d_r][d_c]
        if dest_piece is not None:
            if dest_piece.color == self.color:  # Cannot capture own piece
                result.valid = False
                result.message = "Invalid move. Cannot capture your own piece."
                return result
            else:  # Capture opponent's piece
                result.captured_piece = dest_piece
                result.message = f"{dest_piece} captured!"
                board[d_r][d_c] = None  # Remove captured piece

        # Update board and move Bishop
        board[d_r][d_c] = self
        board[s_r][s_c] = None
        result.valid = True
        result.new_position = (x, y)
        result.message = "Valid move for Bishop."
        self.x, self.y = x, y
        return result


class Rook(Piece):
    def __init__(self, color, x, y):
        super().__init__('R', x, y, color)

    def move(self, x, y, board):
        self.prev_x, self.prev_y = self.x, self.y
        result = MoveResult()  # Create a new MoveResult instance
        s_r, s_c = CoordinatesHelper.cartesian_to_index(self.x, self.y)
        d_r, d_c = CoordinatesHelper.cartesian_to_index(x, y)

        # Check if move is in a straight line (Rook's movement rule)
        if s_r != d_r and s_c != d_c:
            result.valid = False
            result.message = "Invalid move for Rook. Rook can only move in straight lines."
            return result

        # Check if path is clear for horizontal or vertical movement
        if s_r == d_r:  # Horizontal move
            if any(board[s_r][min(s_c, d_c) + 1:max(s_c, d_c)]):
                result.valid = False
                result.message = "Invalid move. Piece in the way."
                return result
        if s_c == d_c:  # Vertical move
            if any(board[i][s_c] for i in range(min(s_r, d_r) + 1, max(s_r, d_r))):
                result.valid = False
                result.message = "Invalid move. Piece in the way."
                return result

        # Check if destination has a piece
        dest_piece = board[d_r][d_c]
        if dest_piece is not None:
            if dest_piece.color == self.color:  # Cannot capture own piece
                result.valid = False
                result.message = "Invalid move. Cannot capture your own piece."
                return result
            else:  # Capture opponent's piece
                result.captured_piece = dest_piece
                result.message = f"{dest_piece} captured!"
                board[d_r][d_c] = None  # Remove captured piece

        # Update board and move Rook
        board[d_r][d_c] = self
        board[s_r][s_c] = None
        result.valid = True
        result.new_position = (x, y)
        result.message = "Valid move for Rook."
        self.x, self.y = x, y
        return result


class Pawn(Piece):
    def __init__(self, color, x, y):
        super().__init__('P', x, y, color)

    def move(self, x, y, board):
        self.prev_x, self.prev_y = self.x, self.y
        result = MoveResult()  # Create a new MoveResult instance
        s_r, s_c = CoordinatesHelper.cartesian_to_index(self.x, self.y)
        d_r, d_c = CoordinatesHelper.cartesian_to_index(x, y)

        # Determine direction based on color
        direction = -1 if self.color == "w" else 1
        starting_row = 6 if self.color == "w" else 1
        promotion_row = 0 if self.color == "w" else 7

        # Forward move
        if s_c == d_c:  # Same column
            if d_r == s_r + direction:  # Move one square forward
                if board[d_r][d_c] is None:  # Square must be empty
                    board[d_r][d_c] = self  # Update the board
                    board[s_r][s_c] = None  # Clear the source square
                    self.x, self.y = x, y  # Update the pawn's position
                    result.valid = True
                    result.new_position = (x, y)
                    result.message = "Valid move for Pawn."
                    if d_r == promotion_row:
                        result.message = "Pawn promoted!"
                        # Handle promotion logic if needed
                    return result
            elif s_r == starting_row and d_r == s_r + 2 * direction:  # Move two squares forward
                if board[d_r][d_c] is None and board[s_r + direction][d_c] is None:  # Path must be clear
                    board[d_r][d_c] = self  # Update the board
                    board[s_r][s_c] = None  # Clear the source square
                    self.x, self.y = x, y  # Update the pawn's position
                    result.valid = True
                    result.new_position = (x, y)
                    result.message = "Valid move for Pawn."
                    return result

        # Diagonal capture
        elif abs(d_c - s_c) == 1 and d_r == s_r + direction:  # Diagonal capture
            dest_piece = board[d_r][d_c]
            if dest_piece is not None and dest_piece.color != self.color:  # Opponent's piece
                board[d_r][d_c] = self  # Update the board
                board[s_r][s_c] = None  # Clear the source square
                self.x, self.y = x, y  # Update the pawn's position
                result.valid = True
                result.captured_piece = dest_piece
                result.new_position = (x, y)
                result.message = f"{dest_piece} captured!"
                if d_r == promotion_row:
                    result.message = "Pawn promoted after capture!"
                    # Handle promotion logic if needed
                return result

        # Invalid move
        result.valid = False
        result.message = "Invalid move for Pawn."
        return result

class CoordinatesHelper:
    @staticmethod
    def cartesian_to_index(x, y):
        c = x - 1
        r = 8 - y
        return r, c

    @staticmethod
    def index_to_cartesian(r, c):
        x = c + 1
        y = 8 - r
        return x, y


class MoveResult:
    def __init__(self, valid=False, new_position=None, captured_piece=None, message=""):
        """
        Represents the result of a move.
        :param valid: Whether the move is valid.
        :param new_position: The new position of the piece after the move, as a tuple (x, y).
        :param captured_piece: The captured piece, if any.
        :param message: A message describing the result of the move.
        """
        self.valid = valid
        self.new_position = new_position
        self.captured_piece = captured_piece
        self.message = message

    def __str__(self):
        """
        Returns a string representation of the MoveResult object.
        """
        return (f"MoveResult(valid={self.valid}, "
                f"new_position={self.new_position}, "
                f"captured_piece={self.captured_piece}, "
                f"message='{self.message}')")


class Chess:
    def __init__(self, white_user: 'User' = None, black_user: 'User' = None, board: list = None,
                 limit: int = 0, moves: list = None, kills: list = None, turn: 'User' = None,
                 selected_piece : 'Piece' = None, moves_count: int = 0, undo_count: int = 0, undid: bool = False,
                 last_move: list = None, last_kill=None,move_res:'MoveResult'=None):
        self.white_user = white_user
        self.black_user = black_user
        self.board = board if board is not None else []  # Initialize as an empty list if None
        self.limit = limit
        self.moves = moves if moves is not None else []  # Initialize as an empty list if None
        self.kills = kills if kills is not None else []  # Initialize as an empty list if None
        self.turn = turn
        self.selected_piece = selected_piece
        self.moves_count = moves_count
        self.undo_count = undo_count
        self.undid = undid
        self.Chess_situ: ChessSituation = ChessSituation.NOTHING
        self.User_situ: UserSituation = UserSituation.NOTHING
        self.last_move = last_move if last_move is not None else []  # Initialize as an empty list if None
        self.last_kill = last_kill
        self.move_res=move_res


    def move(self, x: int, y: int) -> bool:
        """
        Centralized method to handle moves on the chessboard.
        :param x: Destination x-coordinate.
        :param y: Destination y-coordinate.
        :return: True if the move was successful, False otherwise.
        """
        if self.Chess_situ != ChessSituation.SELECTED:
            print("No piece selected. You must select a piece before moving.")
            return False

        if self.selected_piece is None:
            print("No piece is selected.")
            return False

        # Call the move method of the selected piece
        move_result = self.selected_piece.move(x, y, self.board)

        # Process the result of the move
        return self.process_move_result(move_result)

    def process_move_result(self, move_result: MoveResult) -> bool:
        if self.Chess_situ != ChessSituation.SELECTED:
            print("No piece selected. You must select a piece before moving.")
            return False

        if not move_result.valid:
            print(move_result.message)
            return False

        new_x, new_y = move_result.new_position
        if move_result.captured_piece:
            captured = move_result.captured_piece
            self.last_kill=captured
            self.kills.append(f"{captured} captured!")
            if str(captured) == "kb":
                self.white_user.scores += 3
                print(f"{self.white_user} won by capturing the black king!")
                self.end_game()
            elif str(captured) == "kw":  # If the white king is captured
                self.black_user.scores += 3
                print(f"{self.black_user} won by capturing the white king!")
                self.end_game()

        # Update the game situation and print success message
        self.Chess_situ = ChessSituation.MOVED
        self.moves_count+=1
        print(move_result.message)
        if self.moves_count==self.limit:
            print("Game Limit has Reached. Game drawn")
            self.white_user.scores+=1
            self.black_user.scores+=1
            self.end_game()
        return True

    # def move(self, x, y):
    #     if self.Chess_situ == ChessSituation.SELECTED:
    #         ret = self.selected_piece.move(x, y, self.board)
    #         if ret["game_ended"]:
    #             self.end_game()
    #             self.white_user.scores += ret["white_user"]["score"]
    #             self.black_user.scores += ret["black_user"]["score"]
    #             self.kills.append(ret["kill"])

    def initialize(self):
        self.board = [[None for i in range(8)] for j in range(8)]
        self.board[0] = [Rook("b", 1, 8), Knight("b", 2, 8), Bishop("b", 3, 8), Queen("b", 4, 8), King("b", 5, 8),
                         Bishop("b", 6, 8), Knight("b", 7, 8), Rook("b", 8, 8)]
        self.board[7] = [Rook("w", 1, 1), Knight("w", 2, 1), Bishop("w", 3, 1), Queen("w", 4, 1), King("w", 5, 1),
                         Bishop("w", 6, 1), Knight("w", 7, 1), Rook("w", 8, 1)]
        self.board[1] = [Pawn("b", i, 7) for i in range(1, 9)]
        self.board[6] = [Pawn("w", i, 2) for i in range(1, 9)]

    def print(self):
        if chess.User_situ != UserSituation.PLAYING:
            print("You should start a game")
        else:
            for row in self.board:
                print("|".join([Fore.RED + str(
                    self.selected_piece) + Style.RESET_ALL if self.selected_piece == piece else str(
                    piece) if piece is not None else "  " for piece in row]) + "|")

    def random_board(self, count, selected_class):
        a = 0
        self.board = [[None for i in range(8)] for j in range(8)]
        arr = []
        while a < count:
            r = random.randint(0, 7)
            c = random.randint(0, 7)
            if self.board[r][c] is None:
                x, y = CoordinatesHelper.index_to_cartesian(r, c)
                piece_type = random.randint(0, 1)
                color = random.choice(['b', 'w'])
                if piece_type == 0:
                    piece = selected_class(color, x, y)
                    arr.append(piece)
                else:
                    piece = Pawn(color, x, y)
                self.board[r][c] = piece
                a += 1

        self.selected_piece = arr[-1]
        self.print()

    def select(self, x, y, board):
        if chess.User_situ == UserSituation.PLAYING:
            r, c = CoordinatesHelper.cartesian_to_index(x, y)
            if self.Chess_situ == ChessSituation.NOTHING:
                if board[r][c] is None:
                    print("no piece on this spot")
                    return False
                if self.turn != board[r][c].color:
                    print("You can only select one of your pieces")
                    return False
                self.selected_piece = board[r][c]
                self.Chess_situ = ChessSituation.SELECTED
                print(f"{self.selected_piece} selected")
                return True
            else:
                print("already selected")
                return False
        print("you should start a game first")

    def new_game(self, username: str, limit: int):
        steps = 0
        self.limit = limit
        if not re.search("^[a-zA-Z0-9_]+$", username):
            print("username format is invalid")
            return False
        if limit < 0:
            print("number should be positive to have a limit or 0 for no limit")
            return False
        if username == self.white_user:
            print("you must choose another player to start a game")
            return False
        if username not in User.users:
            print("no user exists with this username")
            return False
        self.User_situ = UserSituation.PLAYING
        print("game started")
        self.black_user = User.users[User.users.index(username)]
        self.initialize()
        self.print()
        self.turn = "w"
        print(f"first : {self.white_user},second : {self.black_user}, limit : {limit}, turn : {self.turn}")
        return True

    def end_game(self):
        if chess.User_situ == UserSituation.PLAYING:
            self.white_user = None
            self.black_user = None
            self.User_situ = UserSituation.NOTHING
            print("game ended")

    def next_turn(self):
        # print(self.limit)
        if self.User_situ != UserSituation.PLAYING:
            print("You should start a game")
            return
        if self.Chess_situ!=ChessSituation.MOVED:
            print("You should move a piece first")
            return
        self.selected_piece = None
        if self.moves_count < self.limit:
            self.turn = 'b' if self.turn == 'w' else 'w'
            print(f"Now it's {self.turn}'s turn.")
            self.moves_count += 1
            # print(self.limit-self.moves_count)
            self.Chess_situ = ChessSituation.NOTHING
            self.undid = False
            return True
        elif self.limit == 0:
            self.turn = 'b' if self.turn == 'w' else 'w'
            print(f"Now it's {self.turn}'s turn.")
            self.Chess_situ = ChessSituation.NOTHING
            self.undid = False
            return True
        else:
            print("match exceeded the limit. Game has ended")
            return False

    def undo(self):
        if self.User_situ != UserSituation.PLAYING:
            print("You should start a game.")
            return False

        current_player = self.white_user if self.turn == "w" else self.black_user
        if current_player.undos >= 2:
            print("Undo limit reached.")
            return False

        if self.Chess_situ != ChessSituation.MOVED or self.undid:
            print("Select and move first, then undo.")
            return False

        self.undid = True

        current_r, current_c = CoordinatesHelper.cartesian_to_index(self.selected_piece.x, self.selected_piece.y)
        prev_r, prev_c = CoordinatesHelper.cartesian_to_index(self.selected_piece.prev_x, self.selected_piece.prev_y)

        self.board[prev_r][prev_c] = self.selected_piece
        self.board[current_r][current_c] = None
        self.selected_piece.x, self.selected_piece.y = self.selected_piece.prev_x, self.selected_piece.prev_y

        if self.moves:
            self.moves.pop()
        self.Chess_situ = ChessSituation.NOTHING
        current_player.undos += 1

        if self.last_kill:
            last_kill_r, last_kill_c = CoordinatesHelper.cartesian_to_index(self.last_kill.x, self.last_kill.y)
            self.board[last_kill_r][last_kill_c] = self.last_kill
            print("Undo successful.")
        print("Undo successful.")
        return True
    def show_turn(self):
        if self.User_situ != UserSituation.PLAYING:
            print("You should start a game")
            return
        if self.turn == "w":
            print(f"Its {self.white_user}'s turn with White pieces")
            return self.turn
        else:
            print(f"Its {self.black_user}'s turn with Black pieces")
            return self.turn

    def show_moves(self, aarg=False):
        if self.User_situ != UserSituation.PLAYING:
            print("You should start a game")
            return
        if aarg:
            for move in self.moves:
                print(move)
                # print(move[1])
        else:
            for move in self.moves:
                if move[1] == self.turn:
                    print(move)

    def show_last_move(self):
        if self.User_situ != UserSituation.PLAYING:
            print("You should start a game")
            return
        else:
            print(self.last_move[-1])

    def show_kills(self, aarg2=False):
        if self.User_situ != UserSituation.PLAYING:
            print("You should start a game")
            return
        if aarg2:
            for kill in self.kills:
                print(kill)
                # print(move[1])
        else:
            for kill in self.kills:
                if kill[1] != self.turn:
                    print(kill)

    def forfeit(self):
        if self.User_situ != UserSituation.PLAYING:
            print("You should start a game")
            return
        if self.turn == "w":
            self.white_user.scores -= 1
            self.white_user.losses += 1
            self.black_user.scores += 2
            self.black_user.wins += 1
            print("you have forfeited")
            print(f"player {self.black_user} with color Black won")
        elif self.turn == "b":
            self.black_user.scores -= 1
            self.black_user.losses += 1
            self.white_user.scores += 2
            self.white_user.wins += 1
            print("you have forfeited")
            print(f"player {self.white_user} with color white won")
        self.white_user = None
        self.black_user = None
        self.User_situ = UserSituation.NOTHING


player1 = User("alireza", "12345", 10, 5, 5, 15)
player2 = User("amir", "09876", 3, 1, 4, 2)
player3 = User("zahra", "54321", 10, 6, 3, 8)
player4 = User("ahmad", "67890", 10, 5, 5, 10)
player5 = User("paria", "11111", 8, 4, 5, 12)
player6 = User("nazi", "22222", 10, 5, 5, 15)
player7 = User("amirali", "09876", 3, 1, 3, 2)
User.users.append(player1)
User.users.append(player2)
User.users.append(player3)
User.users.append(player4)
User.users.append(player5)
User.users.append(player6)
User.users.append(player7)
chess = Chess()
while True:
    parts = input(">> ").strip().split()
    if len(parts) == 0:
        continue

    command = parts[0]

    if command == "register" and len(parts) == 3:
        User.register(parts[1], parts[2])
    elif command == "login" and len(parts) == 3:
        User.login(parts[1], parts[2])
        chess.User_situ = UserSituation.LOGGEDIN
    elif command == "remove" and len(parts) == 3:
        User.remove(parts[1], parts[2])
    elif command == "new_game" and len(parts) == 3:
        if chess.User_situ == UserSituation.LOGGEDIN:
            chess.new_game(parts[1], int(parts[2]))
    elif command == "list_users":
        sorted_usernames = sorted(user.username for user in User.users)
        for username in sorted_usernames:
            print(username)
    elif command == "help":
        if chess.User_situ == UserSituation.NOTHING:
            print(f"register[username][password]")
            print(f"login[username][password]")
            print(f"remove[username][password]")
            print("list_users")
            print("exit")
        elif chess.User_situ == UserSituation.LOGGEDIN:
            print("new_game[username][limit]")
            print("scoreboard")
            print("list_users")
            print("logout")
        elif chess.User_situ == UserSituation.PLAYING:
            print("select[x], [y]")
            print("deselect")
            print("move[x], [y]")
            print("next_turn")
            print("show_turn")
            print("undo")
            print("undo_number")
            print("show_moves[-all]")
            print("show_killed[-all]")
            print("show_board")
            print("forfeit")

    elif command == "exit":
        print("Program ended.")
        break
    elif command == "forfeit":
        chess.forfeit()
        chess.end_game()
        # User.users.forfeit()
    elif command == "scoreboard":
        User.show_scoreboard()
        # player2.show_scoreboard()
    elif command == "show_board":
        # chess.initialize()
        chess.print()
    elif command == "random" and len(parts) == 2:
        try:
            count = int(parts[1])
            chess.random_board(count, Pawn)
        except ValueError:
            print("Invalid count. Please enter a valid number.")
    elif command == "move" and len(parts) == 2:
        try:
            # Parse and validate the input coordinates
            dest_x, dest_y = map(int, parts[1].split(","))
            if not (1 <= dest_x <= 8 and 1 <= dest_y <= 8):
                print("Invalid coordinates. Please enter values between 1 and 8.")
                continue

            # Perform the move
            success = chess.move(dest_x, dest_y)
            if success:
                # If the move was successful, update the move history and print the board
                selected_piece = chess.selected_piece
                if selected_piece:
                    chess.print()
                    chess.moves.append(
                        f"{selected_piece} from (x:{selected_piece.prev_x} , y:{selected_piece.prev_y}) "
                        f"to (x: {dest_x}, y: {dest_y})"
                    )
                    chess.last_move.append(f"{dest_x},{dest_y}")
            else:
                print("Move failed.")
        except ValueError:
            print("Invalid input format. Use 'move x,y' where x and y are integers between 1 and 8.")



    elif command == "place":
        if chess.User_situ != UserSituation.PLAYING:
            print("You should start a game")
        else:
            selected_piece = chess.selected_piece
            r, c = CoordinatesHelper.cartesian_to_index(selected_piece.x, selected_piece.y)
            print(f"{r},{c}")
    elif command == "xplace":
        if chess.User_situ != UserSituation.PLAYING:
            print("You should start a game")
        else:
            selected_piece = chess.selected_piece
            print(f"{selected_piece.x},{selected_piece.y}")
    elif command == "select" and len(parts) == 2:
        if int(parts[1].split(",")[0]) >= 1 and int(parts[1].split(",")[0]) <= 8:
            x, y = int(parts[1].split(",")[0]), int(parts[1].split(",")[1])
            chess.select(x, y, chess.board)
        else:
            print("wrong coordination")
    elif command == "next_turn":
        chess.next_turn()
    elif command == "show_turn":
        chess.show_turn()
    elif command == "show_moves":
        if len(parts) == 2 and parts[1] == "-all":
            chess.show_moves(True)
        elif len(parts) == 1:
            chess.show_moves()
        else:
            print("invalid command")
    elif command == "last_move":
        chess.show_last_move()
    elif command == "undo":
        chess.undo()
    elif command == "deselect":
        if chess.Chess_situ == ChessSituation.SELECTED:
            chess.Chess_situ = ChessSituation.NOTHING
            print("deselected")
        else:
            print("you should select a piece")
    elif command == "show_kills":
        if len(parts) == 2 and parts[1] == "-all":
            chess.show_kills(True)
        elif len(parts) == 1:
            chess.show_kills()
        else:
            print("invalid command")
    else:
        print("Invalid command.")