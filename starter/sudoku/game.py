from __future__ import annotations

from typing import Tuple

from .generator import Board, generate_puzzle
from .validator import find_incorrect_cells

DIFFICULTY_CLUE_COUNTS = {
    "easy": 42,
    "medium": 34,
    "hard": 26,
}


def get_clue_count(difficulty: str | None = "medium") -> int:
    """Return the clue count for the given difficulty level."""
    normalized = (difficulty or "medium").strip().lower()
    return DIFFICULTY_CLUE_COUNTS.get(normalized, DIFFICULTY_CLUE_COUNTS["medium"])


def create_sudoku_puzzle(clues: int = 35) -> Tuple[Board, Board]:
    """Create a new Sudoku puzzle and its full solution."""
    return generate_puzzle(clues)


def get_incorrect_cells(board: Board, solution: Board) -> list[list[int]]:
    """Return coordinates of incorrect cells compared to the provided solution."""
    return find_incorrect_cells(board, solution)


def get_hint(board: Board, solution: Board) -> tuple[int, int, int]:
    """Return the first empty cell and its solution value for a hint."""
    for row in range(len(board)):
        for col in range(len(board[row])):
            if board[row][col] == 0:
                return row, col, solution[row][col]
    raise ValueError("No empty cells available for a hint")


def is_board_solved(board: Board, solution: Board) -> bool:
    """Return True when every cell is filled and matches the solution."""
    if not board or not solution:
        return False
    if len(board) != len(solution):
        return False

    for row in range(len(board)):
        if len(board[row]) != len(solution[row]):
            return False
        for col in range(len(board[row])):
            value = board[row][col]
            if value == 0 or value != solution[row][col]:
                return False
    return True
