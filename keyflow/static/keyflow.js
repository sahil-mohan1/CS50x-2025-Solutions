const paragraphs = [
  "Walking through a dense forest offers a unique sensory experience that is difficult to replicate in a city environment. The way the sunlight filters through the canopy of leaves creates a shifting mosaic of light and shadow on the forest floor. You might hear the rustling of small animals in the underbrush or the distant call of a bird high above. The air usually feels cooler and fresher, filled with the earthy scent of damp soil and pine needles. Taking the time to observe the intricate details of nature, like the pattern of bark on a tree or the delicate structure of a fern, can be incredibly grounding. It reminds us of the slow, steady rhythm of life that exists outside of our busy schedules and digital distractions.",

  "Gazing up at the night sky has fascinated humanity for thousands of years. When you look at the stars, you are effectively looking back in time, as the light from those distant suns has traveled for years, centuries, or even millennia to reach your eyes. It is a humbling perspective that makes our daily worries seem insignificant in the grand scheme of the universe. Modern telescopes have revealed that our galaxy is just one of billions, each containing billions of stars of their own. The sheer scale of the cosmos is almost impossible for the human mind to fully comprehend. Yet, the drive to explore and understand the unknown continues to push science and technology forward toward new horizons and discoveries.",

  "Learning to play a musical instrument is a journey that requires patience, dedication, and a significant amount of practice. At the beginning, your fingers might feel clumsy and the sounds you produce may not be very pleasant to the ear. However, with consistent effort, muscle memory begins to take over, and notes start to flow together into recognizable melodies. The process of mastering a difficult piece of music is incredibly rewarding. It is not just about the technical skill, but also about expression and emotion. Music has the power to convey feelings that words sometimes cannot, bridging gaps between different cultures and languages. Whether you play for yourself or for an audience, the joy of creating music is a universal feeling.",

  "For many people, the morning ritual of brewing a fresh cup of coffee is the true start of the day. The aroma of ground beans filling the kitchen signals that it is time to wake up and face the world. There is a certain comfort in the routine, whether you prefer a simple black coffee or a complex latte with foam art. It is a quiet moment of preparation before the chaos of work or school begins. Beyond the caffeine kick, this daily habit often serves as a small meditation, a few minutes to gather your thoughts and plan your schedule. In cafes around the world, this shared love for a warm beverage creates a buzzing social atmosphere where ideas are exchanged and friendships are formed.",

  "Wandering through the streets of an ancient city is like stepping into a living history book. The architecture tells the story of the generations that came before, with every stone and brick holding a secret from the past. You might see a modern glass building standing right next to a centuries-old cathedral, showcasing the sharp contrast between the old and the new. Cobblestone streets often lead to hidden courtyards or bustling market squares that have been the center of community life for hundreds of years. Preserving these historical sites is crucial because they provide a tangible link to our heritage. They remind us of the craftsmanship and artistic vision of our ancestors, inspiring us to build things that will also stand the test of time."
];

// DOM Elements
const textDisplay = document.getElementById("text-to-type-display");
const userInput = document.getElementById("user-input");
const wpmDisplay = document.getElementById("wpm-display");
const accuracyDisplay = document.getElementById("accuracy-display");
const timerDisplay = document.getElementById("timer-display");
const resetButton = document.getElementById('reset-button');
const timeSelector = document.getElementById('time-selector');
const typingArea = document.getElementById('typing-area');
const resultsContainer = document.getElementById('results-container');
const ctx = document.getElementById('wpmChart');

// State
let TIME_LIMIT = 30; // Default time limit
let timeLeft = TIME_LIMIT;
let timerId = null;
let isTyping = false;
let wpmHistory = [];
let labelHistory = [];
let chartInstance = null;

// Function to reset the test
function resetTest() {
    clearInterval(timerId);
    timeLeft = TIME_LIMIT;
    isTyping = false;
    timerId = null;
    wpmHistory = [];
    labelHistory = [];

    if (typingArea && resultsContainer) {
        typingArea.classList.remove('hidden');
        resultsContainer.classList.add('hidden');
    }
    if (chartInstance) {
        chartInstance.destroy();
        chartInstance = null;
    }

    if (textDisplay) textDisplay.innerHTML = "";
    if (userInput) {
        userInput.value = "";
        userInput.disabled = false;
        userInput.focus();
    }
    if (timerDisplay) timerDisplay.textContent = TIME_LIMIT;
    if (wpmDisplay) wpmDisplay.textContent = 0;
    if (accuracyDisplay) accuracyDisplay.textContent = "100%";

    loadNewParagraph();
}

// Function to load a new paragraph into the display
function loadNewParagraph() {
    if (!textDisplay) return;
    const randomParagraph = paragraphs[Math.floor(Math.random() * paragraphs.length)];
    
    textDisplay.innerHTML = '';
    
    const words = randomParagraph.split(' ');
    words.forEach((word, wordIndex) => {
        const wordSpan = document.createElement('span');
        wordSpan.className = 'word';
        
        word.split('').forEach(char => {
            const charSpan = document.createElement('span');
            charSpan.className = 'char';
            charSpan.textContent = char;
            wordSpan.appendChild(charSpan);
        });

        if (wordIndex < words.length - 1) {
            const spaceSpan = document.createElement('span');
            spaceSpan.className = 'char space';
            spaceSpan.textContent = ' ';
            wordSpan.appendChild(spaceSpan);
        }
        
        textDisplay.appendChild(wordSpan);
    });

    const firstChar = textDisplay.querySelector('.char');
    if (firstChar) firstChar.classList.add('cursor');
    
    const firstWord = textDisplay.querySelector('.word');
    if (firstWord) firstWord.classList.add('active');
}

// Function to save the score to the backend
async function saveScore() {
    // Only try to save if the user is logged in
    if (typeof IS_LOGGED_IN === 'undefined' || !IS_LOGGED_IN) {
        console.log("Guest mode: score not saved.");
        return; // Exit the function for guests
    }

    const wpm = parseInt(wpmDisplay.textContent, 10);
    const accuracy = parseInt(accuracyDisplay.textContent, 10);
    
    // Only save if the user actually typed something
    if (wpm === 0) return;

    try {
        const response = await fetch('/save-score', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                wpm: wpm,
                accuracy: accuracy,
                test_time: TIME_LIMIT
            }),
        });
        if (!response.ok) {
            console.error('Failed to save score');
        }
    } catch (error) {
        console.error('Error saving score:', error);
    }
}

// Function to start the timer
function startTimer() {
    isTyping = true;
    timerId = setInterval(() => {
        timeLeft--;
        if (timerDisplay) timerDisplay.textContent = timeLeft;
        
        updateWPM();

        if (wpmDisplay) {
            const currentWPM = parseInt(wpmDisplay.textContent, 10);
            wpmHistory.push(currentWPM);
            labelHistory.push(TIME_LIMIT - timeLeft);
        }

        if (timeLeft === 0) {
            clearInterval(timerId);
            if (userInput) userInput.disabled = true;
            saveScore(); // <-- ADD THIS LINE
            showResults();
        }
    }, 1000);
}

// Function to show chart results
function showResults() {
    if (typingArea) typingArea.classList.add('hidden');
    if (resultsContainer) resultsContainer.classList.remove('hidden');
    
    if (ctx) {
        // Read CSS variables dynamically based on current theme
        const rootStyles = getComputedStyle(document.documentElement);
        const colorPrimary = rootStyles.getPropertyValue('--sky-400').trim() || '#38bdf8';
        const colorPrimaryAlpha = rootStyles.getPropertyValue('--sky-500-alpha').trim() || 'rgba(56, 189, 248, 0.1)';
        const colorMuted = rootStyles.getPropertyValue('--slate-400').trim() || '#94a3b8';

        chartInstance = new Chart(ctx, {
            type: 'line',
            data: {
                labels: labelHistory,
                datasets: [{
                    label: 'Words Per Minute',
                    data: wpmHistory,
                    borderColor: colorPrimary, 
                    backgroundColor: colorPrimaryAlpha,
                    borderWidth: 2,
                    fill: true,
                    tension: 0.3,
                    pointBackgroundColor: colorPrimary,
                    pointRadius: 3
                }]
            },
            options: {
                responsive: true,
                scales: {
                    y: {
                        beginAtZero: true,
                        grid: { color: 'rgba(255,255,255,0.1)' },
                        ticks: { color: colorMuted }
                    },
                    x: {
                        grid: { color: 'rgba(255,255,255,0.1)' },
                        title: { display: true, text: 'Seconds', color: colorMuted },
                        ticks: { color: colorMuted }
                    }
                },
                plugins: {
                    legend: { labels: { color: colorMuted } }
                }
            }
        });
    }
}

// Function to update WPM
function updateWPM() {
    if (!wpmDisplay) return;
    const correctChars = document.querySelectorAll('.correct').length;
    const timeElapsed = TIME_LIMIT - timeLeft;
    const wpm = timeElapsed > 0 ? Math.round((correctChars / 5) / (timeElapsed / 60)) : 0;
    wpmDisplay.textContent = wpm;
}

// Function to update accuracy
function updateAccuracy() {
    if (!accuracyDisplay) return;
    const correctChars = document.querySelectorAll('.correct').length;
    const typedCharsCount = userInput.value.length;
    const accuracy = typedCharsCount > 0 ? Math.round((correctChars / typedCharsCount) * 100) : 100;
    accuracyDisplay.textContent = `${accuracy}%`;
}

// Function to handle user typing
function handleInput() {
    if (!isTyping) {
        startTimer();
    }

    const textSpans = textDisplay.querySelectorAll('.char');
    const typedChars = userInput.value.split('');

    let newlyIncorrect = false;

    textSpans.forEach((charSpan, index) => {
        const typedChar = typedChars[index];
        charSpan.classList.remove('cursor');
        
        if (typedChar == null) {
            charSpan.classList.remove('correct', 'incorrect');
        } else if (typedChar === charSpan.textContent) {
            charSpan.classList.add('correct');
            charSpan.classList.remove('incorrect');
        } else {
            if (!charSpan.classList.contains('incorrect') && typedChars.length - 1 === index) {
                newlyIncorrect = true;
            }
            charSpan.classList.add('incorrect');
            charSpan.classList.remove('correct');
        }
    });

    const cursorIndex = typedChars.length;
    if (cursorIndex < textSpans.length) {
        const targetSpan = textSpans[cursorIndex];
        targetSpan.classList.add('cursor');
        
        // Active word tracking
        const activeWordSpan = targetSpan.closest('.word');
        const allWords = textDisplay.querySelectorAll('.word');
        allWords.forEach(w => w.classList.remove('active', 'error'));
        if (activeWordSpan) {
            activeWordSpan.classList.add('active');
            
            const charsInActiveWord = activeWordSpan.querySelectorAll('.char');
            const hasError = Array.from(charsInActiveWord).some(c => c.classList.contains('incorrect'));
            if (hasError) {
                activeWordSpan.classList.add('error');
            }
        }
    } else {
        // Typing finished/at the end
        const allWords = textDisplay.querySelectorAll('.word');
        allWords.forEach(w => w.classList.remove('active'));
    }

    if (newlyIncorrect) {
        textDisplay.classList.remove('animate-shake');
        void textDisplay.offsetWidth; // Trigger reflow
        textDisplay.classList.add('animate-shake');
    }

    updateAccuracy();
}


// Event Listeners
document.addEventListener("DOMContentLoaded", () => {
    resetTest(); // Initialize the test on page load

    if (userInput) {
        userInput.addEventListener('input', handleInput);

        // Prevent pasting into the input field
        userInput.addEventListener('paste', (e) => {
            e.preventDefault();
        });

        // Prevent selecting text in the input field
        userInput.addEventListener('select', (e) => {
            e.preventDefault();
        });
    }
    if (resetButton) {
        resetButton.addEventListener('click', resetTest);
    }
    if (timeSelector) {
        timeSelector.addEventListener('click', (e) => {
            if (e.target.classList.contains('time-btn')) {
                // Update time limit
                TIME_LIMIT = parseInt(e.target.dataset.time, 10);
                
                // Update active button style
                timeSelector.querySelectorAll('.time-btn').forEach(btn => btn.classList.remove('active'));
                e.target.classList.add('active');

                // Reset the test with the new time
                resetTest();
            }
        });
    }

    // Theme Switcher Logic
    const themeSelector = document.getElementById('theme-selector');
    if (themeSelector) {
        // Load saved theme
        const savedTheme = localStorage.getItem('keyflow-theme') || 'default';
        themeSelector.value = savedTheme;
        if (savedTheme !== 'default') {
            document.documentElement.setAttribute('data-theme', savedTheme);
        }

        // Handle Change
        themeSelector.addEventListener('change', (e) => {
            const selectedTheme = e.target.value;
            if (selectedTheme === 'default') {
                document.documentElement.removeAttribute('data-theme');
            } else {
                document.documentElement.setAttribute('data-theme', selectedTheme);
            }
            localStorage.setItem('keyflow-theme', selectedTheme);
            
            // Fix input focus if they switched themes during test
            if (userInput && !userInput.disabled) userInput.focus();
        });
    }
});

