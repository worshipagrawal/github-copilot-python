"""Sudoku solving helpers."""

from __future__ import annotations

from typing import List

from .generator import EMPTY, SIZE, Board, is_safe


def is_board_complete(board: Board) -> bool:
    """Return whether the board has no empty cells."""
    return all(cell != EMPTY for row in board for cell in row)


def is_valid_board(board: Board) -> bool:
    """Return whether the provided board is a valid Sudoku state."""
    for row in range(SIZE):
        for col in range(SIZE):
            value = board[row][col]
            if value == EMPTY:
                continue
            if not is_safe(board, row, col, value):
                return False
    return True


def solve_board(board: Board) -> bool:
    """Solve the given board in place using backtracking."""
    for row in range(SIZE):
        for col in range(SIZE):
            if board[row][col] == EMPTY:
                for candidate in range(1, SIZE + 1):
                    if is_safe(board, row, col, candidate):
                        board[row][col] = candidate
                        if solve_board(board):
                            return True
                        board[row][col] = EMPTY
                return False
    return True


def count_solutions(board: Board, limit: int = 2) -> int:
    """Count solutions for the given board up to `limit`.

    Stops early once the number of found solutions reaches `limit`.
    """
    import copy

    work = copy.deepcopy(board)
    solutions = 0

    def backtrack() -> None:
        nonlocal solutions
        if solutions >= limit:
            return
        for r in range(SIZE):
            for c in range(SIZE):
                if work[r][c] == EMPTY:
                    for candidate in range(1, SIZE + 1):
                        if is_safe(work, r, c, candidate):
                            work[r][c] = candidate
                            backtrack()
                            work[r][c] = EMPTY
                            if solutions >= limit:
                                return
                    return
        solutions += 1

    backtrack()
    return solutions
