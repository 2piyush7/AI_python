
from __future__ import annotations

from math import inf


HUMAN = "X"
AI = "O"
EMPTY = " "

WINNING_LINES = (
    (0, 1, 2),
    (3, 4, 5),
    (6, 7, 8),
    (0, 3, 6),
    (1, 4, 7),
    (2, 5, 8),
    (0, 4, 8),
    (2, 4, 6),
)


def print_board(board: list[str]) -> None:
    """Show the board using move numbers for empty cells."""
    cells = [str(index + 1) if value == EMPTY else value for index, value in enumerate(board)]
    print()
    print(f" {cells[0]} | {cells[1]} | {cells[2]} ")
    print("---+---+---")
    print(f" {cells[3]} | {cells[4]} | {cells[5]} ")
    print("---+---+---")
    print(f" {cells[6]} | {cells[7]} | {cells[8]} ")
    print()


def winner(board: list[str]) -> str | None:
    """Return the winning marker, or None if nobody has won yet."""
    for a, b, c in WINNING_LINES:
        if board[a] != EMPTY and board[a] == board[b] == board[c]:
            return board[a]
    return None


def is_full(board: list[str]) -> bool:
    return EMPTY not in board


def available_moves(board: list[str]) -> list[int]:
    return [index for index, value in enumerate(board) if value == EMPTY]


def minimax(
    board: list[str],
    is_ai_turn: bool,
    alpha: float = -inf,
    beta: float = inf,
) -> int:
    """Score the board from the AI's point of view."""
    current_winner = winner(board)
    if current_winner == AI:
        return 1
    if current_winner == HUMAN:
        return -1
    if is_full(board):
        return 0

    if is_ai_turn:
        best_score = -inf
        for move in available_moves(board):
            board[move] = AI
            best_score = max(best_score, minimax(board, False, alpha, beta))
            board[move] = EMPTY
            alpha = max(alpha, best_score)
            if beta <= alpha:
                break
        return int(best_score)

    best_score = inf
    for move in available_moves(board):
        board[move] = HUMAN
        best_score = min(best_score, minimax(board, True, alpha, beta))
        board[move] = EMPTY
        beta = min(beta, best_score)
        if beta <= alpha:
            break
    return int(best_score)


def best_ai_move(board: list[str]) -> int:
    """Choose a move that guarantees at least a draw with perfect play."""
    best_score = -inf
    best_move = -1

    for move in available_moves(board):
        board[move] = AI
        score = minimax(board, False)
        board[move] = EMPTY

        if score > best_score:
            best_score = score
            best_move = move

    return best_move


def ask_yes_no(prompt: str) -> bool:
    while True:
        answer = input(prompt).strip().lower()
        if answer in {"y", "yes"}:
            return True
        if answer in {"n", "no"}:
            return False
        print("Please enter y or n.")


def ask_human_move(board: list[str]) -> int:
    while True:
        raw_move = input("Choose a square (1-9): ").strip()

        if not raw_move.isdigit():
            print("Please enter a number from 1 to 9.")
            continue

        move = int(raw_move) - 1
        if move not in range(9):
            print("That square is outside the board.")
            continue
        if board[move] != EMPTY:
            print("That square is already taken.")
            continue

        return move


def play_game() -> None:
    board = [EMPTY] * 9
    human_turn = ask_yes_no("Would you like to go first? (y/n): ")

    print("\nYou are X. The unbeatable AI is O.")
    print_board(board)

    while True:
        if human_turn:
            move = ask_human_move(board)
            board[move] = HUMAN
        else:
            move = best_ai_move(board)
            board[move] = AI
            print(f"AI chooses square {move + 1}.")

        print_board(board)

        current_winner = winner(board)
        if current_winner or is_full(board):
            if current_winner == HUMAN:
                print("You win! That should be impossible, so check the AI code.")
            elif current_winner == AI:
                print("AI wins!")
            else:
                print("It's a draw. Perfect play on both sides.")
            return

        human_turn = not human_turn


def main() -> None:
    print("Tic-Tac-Toe")
    print("Positions are numbered 1 through 9.")

    while True:
        play_game()
        if not ask_yes_no("\nPlay again? (y/n): "):
            print("Thanks for playing!")
            break


if __name__ == "__main__":
    main()
