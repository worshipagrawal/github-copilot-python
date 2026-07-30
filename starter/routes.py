from __future__ import annotations

from typing import Dict, Optional

from flask import Blueprint, jsonify, render_template, request

from sudoku.game import create_sudoku_puzzle, get_clue_count, get_hint, get_incorrect_cells, is_board_solved
from sudoku.generator import Board

routes = Blueprint("routes", __name__)

CURRENT: Dict[str, object] = {
    "puzzle": None,
    "solution": None,
    "board": None,
    "hints_used": 0,
}


@routes.route("/")
def index() -> str:
    return render_template("index.html")


@routes.route("/new")
def new_game() -> dict[str, Board]:
    difficulty = request.args.get("difficulty", "medium")
    clues = get_clue_count(difficulty)
    puzzle, solution = create_sudoku_puzzle(clues)
    CURRENT["puzzle"] = puzzle
    CURRENT["solution"] = solution
    CURRENT["board"] = [row[:] for row in puzzle]
    CURRENT["hints_used"] = 0
    return jsonify({"puzzle": puzzle, "difficulty": difficulty, "hints_used": 0})


@routes.route("/hint", methods=["POST"])
def get_hint_for_board():
    data = request.get_json() or {}
    board: Board = data.get("board", [])
    solution = CURRENT.get("solution")
    if solution is None:
        return jsonify({"error": "No game in progress"}), 400

    if not board:
        board = CURRENT.get("board") or CURRENT.get("puzzle")

    try:
        row, col, value = get_hint(board, solution)
    except ValueError:
        return jsonify({"error": "No empty cells left"}), 400

    updated_board = [row_vals[:] for row_vals in board]
    updated_board[row][col] = value
    CURRENT["board"] = updated_board
    CURRENT["hints_used"] = int(CURRENT.get("hints_used", 0)) + 1
    return jsonify({
        "board": updated_board,
        "hint": [row, col, value],
        "hints_used": CURRENT["hints_used"],
    })


@routes.route("/check", methods=["POST"])
def check_solution():
    data = request.get_json() or {}
    board: Board = data.get("board", [])
    solution = CURRENT.get("solution")
    if solution is None:
        return jsonify({"error": "No game in progress"}), 400

    incorrect = get_incorrect_cells(board, solution)
    solved = is_board_solved(board, solution)
    return jsonify({"incorrect": incorrect, "solved": solved})
