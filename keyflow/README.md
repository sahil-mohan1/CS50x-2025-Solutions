# KeyFlow

#### Description:
KeyFlow is a web-based productivity application designed to help users master their typing speed and accuracy through a minimalist and responsive interface.

## 🚀 Key Features
*   **Real-time WPM Tracking:** Calculates words per minute dynamically as the user types, providing instant feedback on performance.
*   **Accuracy Analytics:** Tracks keystroke errors and provides a percentage-based accuracy score.
*   **Enhanced Data Visualization (Chart.js):** After each session, view a detailed line graph of your typing speed (WPM) over time to identify consistency and peaks.
*   **Dynamic Theme Engine:** Switch between multiple high-fidelity themes including **Slate (Default)**, **Cyberpunk**, and **Forest** to suit your aesthetic preference.
*   **Advanced UI/UX:** Features a custom blinking cursor, active word highlighting, smooth fade-in animations, and a "shake" effect for typing errors.
*   **Leaderboard:** Benchmark your speed against the community's best performers across distinct time categories (15s, 30s, 45s, and 60s).
*   **Guest & Authenticated Modes:** Practice instantly as a guest or register to save your performance history and compete on the leaderboard.

## File Structure and Functionality
To keep the project organized and scalable, KeyFlow is divided into several key files, each with a distinct responsibility:

* **`app.py`:** This serves as the heart of the application. Built using the Flask framework, it manages the backend server logic and session handling. I implemented several specific routes to handle the app's functionality: @app.route("/") renders the main typing interface, while @app.route("/login") and @app.route("/register") handle user authentication using POST requests. One of the most critical parts of this file is the /save-score route. It listens for JSON data sent from the JavaScript frontend via a fetch request, validates the user’s session, and then executes SQL commands to insert the WPM and accuracy data into the database. This file also ensures that the Flask-Session is configured correctly so users stay logged in while they navigate between the leaderboard and the home page.
* **`index.html`:** The primary interface for the application. It contains the structure for the typing arena, the statistics dashboard, and the navigation elements.
* **`keyflow.js`:** The keyflow.js file is basically the brain of the whole frontend and it is where I put most of the logic for the app. I used it to set up event listeners that watch the input box for every single keystroke. Whenever someone types, the script compares their input to the current paragraph and updates the text color to green or red immediately by toggling CSS classes on individual span elements. It also handles all the real-time math for the stats shown on the dashboard. For example, the WPM is calculated by taking the number of correct characters and dividing by five to get a standard word length, then checking that against the time elapsed. It also tracks accuracy by comparing correct characters against the total number of keys pressed. When the timer hits zero, the script uses an asynchronous fetch request to send the final stats over to the Flask backend so they can be saved in the database. I also made sure to include some extra functionality like a reset function to refresh the text and some simple code to prevent users from cheating by pasting text into the box.
* **`helpers.py`:**  Contains modular functions  to keep the main application logic clean and modular. It features the login_required decorator, which serves as a security layer to ensure that specific routes like the leaderboard are only accessible to authenticated users. It also contains the apology function, which provides a standardized way to render error messages to the user, ensuring that feedback is consistent and professional whenever a request cannot be fulfilled.
* **`requirements.txt`:** Lists all the Python dependencies required to run the project, ensuring easy installation for other developers.

## Database Schema
The structure of the SQLite database (keyflow.db) was a major part of the development process. I designed two main tables to handle the application's needs:

users table: This table stores essential user information. It includes an id as a primary key (integer), a username (text) which is set to be unique to prevent duplicate accounts, and a hash (text) to store the secured, hashed version of the user's password.

scores table: This table tracks every completed typing test. It uses a user_id as a foreign key to link scores back to the specific person who achieved them. It also stores the wpm (integer), the accuracy (integer), the test_time (integer) to differentiate between 15s or 60s tests, and a timestamp which is automatically generated whenever a new score is inserted.

Using these two tables allows me to run complex SQL queries such as selecting the top five highest WPM scores for the 60-second category while joining the users table to display the actual names on the leaderboard.

## Design Choices and Challenges
During the development of KeyFlow, I encountered several design dilemmas that shaped the final product.

### Frontend vs. Backend Logic
One of the primary debates was whether to calculate WPM on the server-side or the client-side. I ultimately decided to handle all live calculations in **JavaScript** on the client-side. This choice was made to ensure zero latency; waiting for a server response every time a user presses a key would have disrupted the "flow" that the project is named after.

### Database Selection
I chose to use SQLite because of its lightweight nature and ease of integration with Flask. While a heavier database like PostgreSQL was considered, the current scope of KeyFlow benefits more from the speed and simplicity of a local file-based system.

### UI/UX Minimalism
I debated adding more "gamified" elements like leveling systems or sound effects. However, I decided against this to maintain a "Zen" aesthetic. The goal of KeyFlow is to promote focus, and I felt that excessive visual or auditory noise would detract from the user’s concentration.

## Installation and Usage
To run KeyFlow locally:
1.  Clone the repository.
2.  Install dependencies: `pip install -r requirements.txt`.
3.  Execute `flask run`.
4.  Navigate to `localhost:5000` in your web browser.

## Conclusion
KeyFlow represents the culmination of my learning in CS50 2025, combining frontend interactivity with backend stability. It has taught me the importance of state management in JavaScript and the complexities of designing a user interface that is both simple and powerful.
