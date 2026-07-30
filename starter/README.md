# Sudoku Game with GitHub Copilot

## Project Overview

This project is a Flask-based Sudoku web application that was refactored and enhanced using GitHub Copilot. The application was modularized, tested with pytest, and extended with several new gameplay and user experience features.

## Features

- Modular Flask project structure
- Multiple difficulty levels (Easy, Medium, Hard)
- Unique-solution Sudoku puzzle generation
- Puzzle validation
- Check Puzzle functionality
- Hint system
- Automatic win detection
- Game timer
- Top 10 leaderboard using browser localStorage
- Dark mode with saved user preference
- Responsive user interface
- Alternating 3×3 Sudoku block styling

## Technologies Used

- Python
- Flask
- HTML
- CSS
- JavaScript
- Pytest
- GitHub Copilot

## Installation

1. Clone the repository.

2. Create and activate a virtual environment.

Windows:

```bash
python -m venv .venv
.venv\Scripts\activate
```

3. Install the required packages.

```bash
pip install -r requirements.txt
```

## Running the Application

```bash
python app.py
```

Open your browser and navigate to:

```
http://127.0.0.1:5000
```

## Running Tests

```bash
python -m pytest
```

## GitHub Copilot Usage

GitHub Copilot was used throughout the project to assist with:

- Refactoring the application into multiple modules
- Setting up pytest
- Implementing difficulty levels
- Adding unique puzzle validation
- Implementing the game timer
- Creating the Check Puzzle feature
- Developing the Hint system
- Implementing automatic win detection
- Creating the Top 10 leaderboard
- Adding Dark Mode
- Improving the responsive user interface

All Copilot-generated code was reviewed, tested, and integrated before use.

## Copilot Evaluation

During development, I evaluated a GitHub Copilot suggestion for changing the Sudoku button color.

Instead of automatically accepting the generated change, I reviewed the proposed edit using the Copilot Edit workflow (Keep/Undo). I decided not to keep the suggestion because it did not match the final UI design and styling of the application.

The screenshot `Screenshots/copilot_evaluation.png` demonstrates this evaluation process.

## Project Structure

```
starter/
│
├── app.py
├── routes.py
├── instruction.md
├── README.md
├── requirements.txt
├── sudoku/
├── static/
├── templates/
└── tests/
```

## Author

Developed as part of the GitHub Copilot Sudoku Refactoring Project.