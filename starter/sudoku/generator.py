"""Utilities for generating Sudoku boards and puzzles."""

from __future__ import annotations

import copy
import random
from typing import List, Tuple

SIZE = 9
EMPTY = 0


Board = List[List[int]]


def create_empty_board() -> Board:
    """Create an empty Sudoku board."""
    return [[EMPTY for _ in range(SIZE)] for _ in range(SIZE)]


def deep_copy_board(board: Board) -> Board:
    """Return a deep copy of the supplied board."""
    return copy.deepcopy(board)


def is_safe(board: Board, row: int, col: int, num: int) -> bool:
    """Return whether a value can be placed in the given cell."""
    for x in range(SIZE):
        if board[row][x] == num or board[x][col] == num:
            return False

    start_row = row - row % 3
    start_col = col - col % 3
    for i in range(3):
        for j in range(3):
            if board[start_row + i][start_col + j] == num:
                return False

    return True


def fill_board(board: Board) -> bool:
    """Fill a board recursively with a valid Sudoku solution."""
    for row in range(SIZE):
        for col in range(SIZE):
            if board[row][col] == EMPTY:
                possible_values = list(range(1, SIZE + 1))
                random.shuffle(possible_values)
                for candidate in possible_values:
                    if is_safe(board, row, col, candidate):
                        board[row][col] = candidate
                        if fill_board(board):
                            return True
                        board[row][col] = EMPTY
                return False
    return True


def remove_cells(board: Board, clues: int) -> None:
    """Remove cells from a solved board while preserving a unique solution.

    Cells are considered in random order. When a removal would lead to
    multiple solutions, the removed value is restored.
    """
    target_removals = SIZE * SIZE - clues
    coords = [(r, c) for r in range(SIZE) for c in range(SIZE)]
    random.shuffle(coords)

    removed = 0

    def _count_solutions_local(bd: Board, limit: int = 2) -> int:
        import copy

        work = copy.deepcopy(bd)
        solutions = 0

        def backtrack() -> None:
            nonlocal solutions
            if solutions >= limit:
                return
            for rr in range(SIZE):
                for cc in range(SIZE):
                    if work[rr][cc] == EMPTY:
                        for candidate in range(1, SIZE + 1):
                            if is_safe(work, rr, cc, candidate):
                                work[rr][cc] = candidate
                                backtrack()
                                work[rr][cc] = EMPTY
                                if solutions >= limit:
                                    return
                        return
            solutions += 1

        backtrack()
        return solutions

    for row, col in coords:
        if removed >= target_removals:
            break
        if board[row][col] == EMPTY:
            continue

        backup = board[row][col]
        board[row][col] = EMPTY

        sols = _count_solutions_local(board, limit=2)
        if sols != 1:
            board[row][col] = backup
        else:
            removed += 1


def create_puzzle(clues: int = 35) -> Tuple[Board, Board]:
    """Create a Sudoku puzzle and its full solution."""
    board = create_empty_board()
    fill_board(board)
    solution = deep_copy_board(board)
    remove_cells(board, clues)
    puzzle = deep_copy_board(board)
    return puzzle, solution


def generate_puzzle(clues: int = 35) -> Tuple[Board, Board]:
    """Backward-compatible wrapper for puzzle generation."""
    return create_puzzle(clues)
