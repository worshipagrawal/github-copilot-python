from pathlib import Path

from routes import CURRENT
from sudoku.game import get_clue_count, get_hint


def test_app_loads_successfully(client):
    response = client.get('/')

    assert response.status_code == 200
    assert b'<!doctype html>' in response.data.lower()


def test_difficulty_clue_counts_are_configured():
    assert get_clue_count('easy') == 42
    assert get_clue_count('medium') == 34
    assert get_clue_count('hard') == 26


def test_timer_display_is_rendered(client):
    response = client.get('/')

    assert response.status_code == 200
    assert b'id="game-timer"' in response.data


def test_new_game_uses_selected_difficulty(client):
    response = client.get('/new?difficulty=hard')

    assert response.status_code == 200
    puzzle = response.get_json()['puzzle']
    clues = sum(cell != 0 for row in puzzle for cell in row)
    assert 24 <= clues <= 28


def test_check_endpoint_ignores_empty_cells(client):
    client.get('/new?difficulty=easy')

    response = client.post('/check', json={'board': [[0] * 9 for _ in range(9)]})

    assert response.status_code == 200
    assert response.get_json()['incorrect'] == []


def test_check_endpoint_detects_a_completed_board(client):
    client.get('/new?difficulty=easy')

    response = client.post('/check', json={'board': CURRENT['solution']})

    assert response.status_code == 200
    assert response.get_json()['solved'] is True
    assert response.get_json()['incorrect'] == []


def test_get_hint_returns_the_solution_value_for_the_first_empty_cell():
    board = [
        [5, 3, 0, 0, 7, 0, 0, 0, 0],
        [6, 0, 0, 1, 9, 5, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0],
    ]
    solution = [
        [5, 3, 4, 6, 7, 8, 9, 1, 2],
        [6, 7, 8, 1, 9, 5, 3, 4, 0],
        [1, 9, 2, 3, 4, 6, 5, 7, 8],
    ]

    assert get_hint(board, solution) == (0, 2, 4)


def test_hint_endpoint_applies_a_single_safe_hint(client):
    new_game_response = client.get('/new?difficulty=easy')
    puzzle = new_game_response.get_json()['puzzle']

    board_with_user_value = [row[:] for row in puzzle]
    board_with_user_value[0][0] = 8

    response = client.post('/hint', json={'board': board_with_user_value})

    assert response.status_code == 200
    payload = response.get_json()
    assert payload['hints_used'] == 1
    assert payload['hint'][2] == payload['board'][payload['hint'][0]][payload['hint'][1]]
    assert board_with_user_value[0][0] == 8
    assert sum(cell == 0 for row in payload['board'] for cell in row) == sum(cell == 0 for row in board_with_user_value for cell in row) - 1


def test_leaderboard_section_is_rendered(client):
    response = client.get('/')

    assert response.status_code == 200
    assert b'id="leaderboard"' in response.data
    assert b'Leaderboard' in response.data


def test_client_script_contains_leaderboard_storage_logic():
    main_js_path = Path(__file__).resolve().parents[1] / 'static' / 'main.js'
    content = main_js_path.read_text(encoding='utf-8')

    assert 'localStorage' in content
    assert 'leaderboard' in content.lower()


def test_client_script_auto_checks_completed_board_on_edit_events():
    main_js_path = Path(__file__).resolve().parents[1] / 'static' / 'main.js'
    content = main_js_path.read_text(encoding='utf-8')

    assert "queueAutoCheck()" in content
    assert "addEventListener('change'" in content
    assert "checkBoardStatus({auto: true})" in content


def test_template_includes_responsive_accessibility_markup(client):
    response = client.get('/')

    assert response.status_code == 200
    assert b'<meta name="viewport"' in response.data
    assert b'aria-label="Sudoku game controls"' in response.data
    assert b'aria-label="Leaderboard"' in response.data


def test_template_includes_theme_toggle_button(client):
    response = client.get('/')

    assert response.status_code == 200
    assert b'id="theme-toggle"' in response.data
    assert b'Dark Mode' in response.data


def test_styles_include_responsive_and_dark_mode_rules():
    styles_path = Path(__file__).resolve().parents[1] / 'static' / 'styles.css'
    content = styles_path.read_text(encoding='utf-8')

    assert '@media (max-width: 768px)' in content
    assert 'prefers-color-scheme: dark' in content
    assert 'block-even' in content


def test_client_script_applies_block_based_cell_classes():
    main_js_path = Path(__file__).resolve().parents[1] / 'static' / 'main.js'
    content = main_js_path.read_text(encoding='utf-8')

    assert 'block-' in content


def test_client_script_supports_persisted_theme_toggle():
    main_js_path = Path(__file__).resolve().parents[1] / 'static' / 'main.js'
    content = main_js_path.read_text(encoding='utf-8')

    assert 'theme-toggle' in content
    assert 'data-theme' in content
    assert 'localStorage' in content
