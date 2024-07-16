import sqlite3


# Ensure the table exists
conn = sqlite3.connect('/Users/erosfortea/Desktop/Habit_tracker_app/habits.db')
cur = conn.cursor()
cur.execute('''
CREATE TABLE IF NOT EXISTS habits (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    description TEXT,
    date TEXT NOT NULL,
    frequency TEXT,
    status TEXT NOT NULL,
    goal INTEGER
);
''')
conn.commit()
conn.close()
