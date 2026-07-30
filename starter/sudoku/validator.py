"""Utilities for validating Sudoku submissions."""

from __future__ import annotations

from typing import List, Tuple

from .generator import EMPTY, SIZE, Board


def find_incorrect_cells(board: Board, solution: Board) -> List[List[int]]:
    """Return the coordinates of non-empty cells that do not match the solution."""
    incorrect: List[List[int]] = []
    for row in range(SIZE):
        for col in range(SIZE):
            if board[row][col] == 0:
                continue
            if board[row][col] != solution[row][col]:
                incorrect.append([row, col])
    return incorrect
