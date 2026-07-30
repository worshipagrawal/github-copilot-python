// Client-side rendering and interaction for the Flask-backed Sudoku
const SIZE = 9;
const LEADERBOARD_STORAGE_KEY = 'sudokuLeaderboard';
const THEME_STORAGE_KEY = 'sudokuTheme';
let puzzle = [];
let timerIntervalId = null;
let elapsedSeconds = 0;
let hintsUsed = 0;
let lockedCells = new Set();
let currentDifficulty = 'medium';
let hasCompletedCurrentGame = false;
let autoCheckTimerId = null;

function formatTime(totalSeconds) {
  const minutes = Math.floor(totalSeconds / 60);
  const seconds = totalSeconds % 60;
  return `${String(minutes).padStart(2, '0')}:${String(seconds).padStart(2, '0')}`;
}

function updateTimerDisplay() {
  const timerElement = document.getElementById('game-timer');
  if (timerElement) {
    timerElement.textContent = formatTime(elapsedSeconds);
  }
}

function resetTimer() {
  if (timerIntervalId !== null) {
    clearInterval(timerIntervalId);
  }
  elapsedSeconds = 0;
  timerIntervalId = null;
  updateTimerDisplay();
}

function startTimer() {
  if (timerIntervalId !== null) {
    return;
  }
  timerIntervalId = setInterval(() => {
    elapsedSeconds += 1;
    updateTimerDisplay();
  }, 1000);
}

function stopTimer() {
  if (timerIntervalId !== null) {
    clearInterval(timerIntervalId);
    timerIntervalId = null;
  }
}

function updateHintCount() {
  const hintCountElement = document.getElementById('hint-count');
  if (hintCountElement) {
    hintCountElement.textContent = hintsUsed;
  }
}

function updateDifficultyDisplay() {
  const difficultyElement = document.getElementById('difficulty-level');
  if (difficultyElement) {
    difficultyElement.textContent = currentDifficulty.charAt(0).toUpperCase() + currentDifficulty.slice(1);
  }
}

function queueAutoCheck() {
  if (autoCheckTimerId !== null) {
    window.clearTimeout(autoCheckTimerId);
  }

  autoCheckTimerId = window.setTimeout(() => {
    autoCheckTimerId = null;
    void checkBoardStatus({auto: true});
  }, 50);
}

function loadLeaderboardEntries() {
  try {
    const rawEntries = window.localStorage.getItem(LEADERBOARD_STORAGE_KEY);
    if (!rawEntries) {
      return [];
    }
    const parsedEntries = JSON.parse(rawEntries);
    if (!Array.isArray(parsedEntries)) {
      return [];
    }
    return parsedEntries.filter((entry) => entry && typeof entry.timeSeconds === 'number');
  } catch (error) {
    console.warn('Unable to read leaderboard entries:', error);
    return [];
  }
}

function saveLeaderboardEntries(entries) {
  const topEntries = entries
    .slice()
    .sort((left, right) => left.timeSeconds - right.timeSeconds)
    .slice(0, 10);

  try {
    window.localStorage.setItem(LEADERBOARD_STORAGE_KEY, JSON.stringify(topEntries));
  } catch (error) {
    console.warn('Unable to save leaderboard entries:', error);
  }

  return topEntries;
}

function renderLeaderboard(entries = loadLeaderboardEntries()) {
  const leaderboardList = document.getElementById('leaderboard-list');
  if (!leaderboardList) {
    return;
  }

  leaderboardList.innerHTML = '';
  if (!entries.length) {
    const emptyMessage = document.createElement('p');
    emptyMessage.className = 'leaderboard-empty';
    emptyMessage.textContent = 'No completed games yet.';
    leaderboardList.appendChild(emptyMessage);
    return;
  }

  const orderedList = document.createElement('ol');
  entries.forEach((entry, index) => {
    const item = document.createElement('li');
    item.className = 'leaderboard-item';

    const name = document.createElement('span');
    name.textContent = `${index + 1}. ${entry.playerName}`;

    const details = document.createElement('span');
    details.textContent = `${formatTime(entry.timeSeconds)} • ${entry.difficulty.charAt(0).toUpperCase() + entry.difficulty.slice(1)} • Hints: ${entry.hintsUsed}`;

    item.appendChild(name);
    item.appendChild(details);
    orderedList.appendChild(item);
  });

  leaderboardList.appendChild(orderedList);
}

function saveCompletionToLeaderboard() {
  const playerName = window.prompt('Enter your name for the leaderboard:', '');
  const trimmedName = (playerName || '').trim() || 'Anonymous';
  const entries = loadLeaderboardEntries();
  entries.push({
    playerName: trimmedName,
    timeSeconds: elapsedSeconds,
    difficulty: currentDifficulty,
    hintsUsed,
  });
  saveLeaderboardEntries(entries);
  renderLeaderboard(loadLeaderboardEntries());
}

function getPreferredTheme() {
  if (window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches) {
    return 'dark';
  }
  return 'light';
}

function getStoredTheme() {
  try {
    const storedTheme = window.localStorage.getItem(THEME_STORAGE_KEY);
    if (storedTheme === 'dark' || storedTheme === 'light') {
      return storedTheme;
    }
  } catch (error) {
    console.warn('Unable to read saved theme:', error);
  }
  return null;
}

function applyTheme(theme) {
  const normalizedTheme = theme === 'dark' ? 'dark' : 'light';
  document.documentElement.setAttribute('data-theme', normalizedTheme);
  document.documentElement.style.colorScheme = normalizedTheme;

  const toggleButton = document.getElementById('theme-toggle');
  if (toggleButton) {
    toggleButton.setAttribute('aria-pressed', normalizedTheme === 'dark' ? 'true' : 'false');
    toggleButton.textContent = normalizedTheme === 'dark' ? '☀️ Light Mode' : '🌙 Dark Mode';
  }

  try {
    window.localStorage.setItem(THEME_STORAGE_KEY, normalizedTheme);
  } catch (error) {
    console.warn('Unable to save theme preference:', error);
  }
}

function initializeTheme() {
  const savedTheme = getStoredTheme();
  applyTheme(savedTheme || getPreferredTheme());
}

function toggleTheme() {
  const currentTheme = document.documentElement.getAttribute('data-theme') === 'dark' ? 'dark' : 'light';
  applyTheme(currentTheme === 'dark' ? 'light' : 'dark');
}

function applyCellStyling(input, { isLocked, isHinted, isIncorrect }) {
  const classes = ['sudoku-cell'];
  if (isLocked) {
    classes.push('prefilled');
  }
  if (isHinted) {
    classes.push('hinted');
  }
  if (isIncorrect) {
    classes.push('incorrect');
  }
  input.className = classes.join(' ');
}

function createBoardElement() {
  const boardDiv = document.getElementById('sudoku-board');
  boardDiv.innerHTML = '';
  for (let i = 0; i < SIZE; i++) {
    const rowDiv = document.createElement('div');
    rowDiv.className = 'sudoku-row';
    for (let j = 0; j < SIZE; j++) {
      const input = document.createElement('input');
      input.type = 'text';
      input.maxLength = 1;
      const blockRow = Math.floor(i / 3);
      const blockCol = Math.floor(j / 3);
      const blockIndex = blockRow * 3 + blockCol;
      input.className = `sudoku-cell block-${blockIndex % 2 === 0 ? 'even' : 'odd'}`;
      input.dataset.row = i;
      input.dataset.col = j;
      input.addEventListener('input', (e) => {
        const val = e.target.value.replace(/[^1-9]/g, '');
        e.target.value = val;
        queueAutoCheck();
      });
      input.addEventListener('change', () => {
        queueAutoCheck();
      });
      rowDiv.appendChild(input);
    }
    boardDiv.appendChild(rowDiv);
  }
}

function renderPuzzle(puz) {
  puzzle = puz;
  createBoardElement();
  const boardDiv = document.getElementById('sudoku-board');
  const inputs = boardDiv.getElementsByTagName('input');
  for (let i = 0; i < SIZE; i++) {
    for (let j = 0; j < SIZE; j++) {
      const idx = i * SIZE + j;
      const val = puzzle[i][j];
      const inp = inputs[idx];
      const isLocked = val !== 0 || lockedCells.has(idx);
      const isHinted = lockedCells.has(idx);
      inp.dataset.locked = isLocked ? 'true' : 'false';
      inp.dataset.hinted = isHinted ? 'true' : 'false';
      inp.disabled = isLocked;
      if (val !== 0) {
        inp.value = val;
      } else {
        inp.value = '';
      }
      applyCellStyling(inp, {isLocked, isHinted, isIncorrect: false});
    }
  }
}

function getBoardFromInputs() {
  const boardDiv = document.getElementById('sudoku-board');
  const inputs = boardDiv.getElementsByTagName('input');
  const board = [];
  for (let i = 0; i < SIZE; i++) {
    board[i] = [];
    for (let j = 0; j < SIZE; j++) {
      const idx = i * SIZE + j;
      const val = inputs[idx].value;
      board[i][j] = val ? parseInt(val, 10) : 0;
    }
  }
  return board;
}

async function newGame() {
  const difficulty = document.getElementById('difficulty-select').value;
  currentDifficulty = difficulty;
  const res = await fetch(`/new?difficulty=${encodeURIComponent(difficulty)}`);
  const data = await res.json();
  puzzle = data.puzzle;
  lockedCells = new Set();
  hintsUsed = 0;
  hasCompletedCurrentGame = false;
  updateHintCount();
  updateDifficultyDisplay();
  renderPuzzle(puzzle);
  resetTimer();
  startTimer();
  document.getElementById('message').innerText = '';
}

async function applyHint() {
  const board = getBoardFromInputs();
  const res = await fetch('/hint', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({board})
  });
  const data = await res.json();
  const msg = document.getElementById('message');
  if (data.error) {
    msg.style.color = 'var(--message-error)';
    msg.innerText = data.error;
    return;
  }
  puzzle = data.board;
  const [row, col] = data.hint;
  lockedCells.add(row * SIZE + col);
  hintsUsed = data.hints_used;
  updateHintCount();
  renderPuzzle(puzzle);
  msg.style.color = 'var(--message-info)';
  msg.innerText = `Hint used (${hintsUsed}).`;
  checkBoardStatus({auto: true});
}

async function checkBoardStatus({auto = false} = {}) {
  const board = getBoardFromInputs();
  const res = await fetch('/check', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({board})
  });
  const data = await res.json();
  const msg = document.getElementById('message');
  const boardDiv = document.getElementById('sudoku-board');
  const inputs = boardDiv.getElementsByTagName('input');
  if (data.error) {
    msg.style.color = 'var(--message-error)';
    msg.innerText = data.error;
    return;
  }
  const incorrect = new Set(data.incorrect.map(x => x[0]*SIZE + x[1]));
  for (let idx = 0; idx < inputs.length; idx++) {
    const inp = inputs[idx];
    if (inp.disabled) continue;
    const isLocked = inp.dataset.locked === 'true';
    const isHinted = inp.dataset.hinted === 'true';
    applyCellStyling(inp, {isLocked, isHinted, isIncorrect: incorrect.has(idx)});
  }
  if (data.solved) {
    stopTimer();
    if (!hasCompletedCurrentGame) {
      hasCompletedCurrentGame = true;
      saveCompletionToLeaderboard();
    }
    msg.style.color = 'var(--message-success)';
    msg.innerText = `Congratulations! You solved it in ${formatTime(elapsedSeconds)}. Difficulty: ${currentDifficulty.charAt(0).toUpperCase() + currentDifficulty.slice(1)}. Hints used: ${hintsUsed}.`;
    return;
  }
  if (auto) {
    msg.innerText = '';
    return;
  }
  msg.style.color = 'var(--message-error)';
  msg.innerText = 'Some cells are incorrect.';
}

async function checkSolution() {
  await checkBoardStatus({auto: false});
}

// Wire buttons
window.addEventListener('load', () => {
  initializeTheme();
  const themeToggleButton = document.getElementById('theme-toggle');
  if (themeToggleButton) {
    themeToggleButton.addEventListener('click', toggleTheme);
  }
  document.getElementById('new-game').addEventListener('click', newGame);
  document.getElementById('check-solution').addEventListener('click', checkSolution);
  document.getElementById('get-hint').addEventListener('click', applyHint);
  renderLeaderboard();
  // initialize
  newGame();
});