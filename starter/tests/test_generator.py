from sudoku import generate_puzzle
from sudoku.solver import count_solutions
from sudoku.game import DIFFICULTY_CLUE_COUNTS, get_clue_count


def test_generated_puzzles_have_unique_solution():
    # For each difficulty, generate a puzzle and assert it has exactly one solution
    for difficulty in DIFFICULTY_CLUE_COUNTS:
        clues = get_clue_count(difficulty)
        puzzle, solution = generate_puzzle(clues)
        sols = count_solutions(puzzle, limit=2)
        assert sols == 1, f"Puzzle for {difficulty} has {sols} solutions"
