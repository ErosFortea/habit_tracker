from datetime import date, datetime, timedelta
import sqlite3
import pandas as pd

class Habit:
    def __init__(self, name='', description='', date_today=None, frequency='', status='',time_goal=''):
        self.name = name
        self.description = description
        self.date = date_today if date_today else date.today().strftime('%Y-%m-%d')
        self.frequency = frequency
        self.status = status
        self.time_goal = time_goal

    def create_new_habit(self):
        print('Welcome to the habit creation portal')
        print('------------------------------------')
        self.name = input('What is the new habit about? ')
        self.description = input('Insert a small description about the habit: ')
        self.frequency = int(input('What is the frequency of the new habit? insert 1 for daily 2 for weekly 3 for monthly: '))
        self.status = int(input('Please insert 1 if active or 2 if it is in standby or 3 to complete it: '))

        if self.status == 1:
            self.status = 'Active'
        elif self.status == 2:
            self.status = 'Standby'
        elif self.status == 3:
            self.status = 'Completed'
        else:
            print('Invalid status input. Setting status to "Unknown"')
            self.status = 'Unknown'

        if self.frequency == 1:
            self.frequency = 'Daily'
        elif self.frequency == 2:
            self.frequency = 'Weekly'
        elif self.frequency ==3:
            self.frequency = 'Monthly'
        else:
            print('Invalid frequency input. Setting status to "Unknown"')
            self.status = 'Unknown'

        # Insert the new habit into the database
        conn = sqlite3.connect('habits.db')
        cur = conn.cursor()

        cur.execute('''
            INSERT INTO habits (name, description, date, frequency, status)
            VALUES (?, ?, ?, ?, ?)
        ''', (self.name, self.description, self.date, self.frequency, self.status))

        conn.commit()
        conn.close()
        print(f'New habit "{self.name}" successfully created!')

    def view_all(self):

        conn = sqlite3.connect('habits.db')
        query = 'SELECT * FROM habits'
        df = pd.read_sql(query, conn)
        conn.close()

        print("All Habits:")
        print(df.to_string(index=False))





    def upgrade_habits(self):

        self.view_all()
        print('--------------------------------')
        habit_id = int(input('Please, introduce the id of the habit you want to upgrade: '))
        self.name = input('Enter the new name: ')
        self.description = input('Enter the new description: ')
        self.frequency = int(input('What is the frequency of the new habit? insert 1 for daily 2 for weekly 3 for monthly: '))
        self.status = int(input('Please insert 1 if active or 2 if it is in standby or 3 to complete it: '))

        if self.status == 1:
            self.status = 'Active'
        elif self.status == 2:
            self.status = 'Standby'
        elif self.status == 3:
            self.status = 'Completed'
        else:
            print('Invalid status input. Setting status to "Unknown"')
            self.status = 'Unknown'

        if self.frequency == 1:
            self.frequency = 'Daily'
        elif self.frequency == 2:
            self.frequency = 'Weekly'
        elif self.frequency == 3:
            self.frequency = 'Monthly'
        else:
            print('Invalid frequency input. Setting status to "Unknown"')
            self.status = 'Unknown'

        # Update the habit in the database
        conn = sqlite3.connect('habits.db')
        cur = conn.cursor()
        cur.execute('''
            UPDATE habits
            SET name = ?, description = ?, date = ?, frequency = ?, status = ?
            WHERE id = ?
        ''', (self.name, self.description, self.date, self.frequency, self.status, habit_id))

        conn.commit()
        conn.close()
        print(f'Habit "{self.name}" successfully upgraded!')

    def deleting_habit(self):
        print('Here you have a list of your habits')
        print('------------------------------------')
        self.view_all()
        print('------------------------------------')
        habit_to_delete = int(input('Choose the id of the habit you want to delete: '))

        # Delete the habit from the database
        conn = sqlite3.connect('habits.db')
        cur = conn.cursor()
        cur.execute('DELETE FROM habits WHERE id = ?', (habit_to_delete,))
        conn.commit()
        conn.close()
        print(f'Habit with id "{habit_to_delete}" successfully deleted!')

    def longer_streak(self):

        conn = sqlite3.connect('habits.db')
        cur = conn.cursor()
        cur.execute('SELECT id, name, date FROM habits ORDER BY id, date')
        rows = cur.fetchall()
        conn.close()

        if not rows:
            print("No habits found.")
            return

        # Process data into a dictionary of habit dates
        habit_dates = {}
        for row in rows:
            habit_id, habit_name, habit_date = row
            if habit_id not in habit_dates:
                habit_dates[habit_id] = {'name': habit_name, 'dates': []}
            habit_dates[habit_id]['dates'].append(datetime.strptime(habit_date, '%Y-%m-%d'))

        # Calculate the longest streak for each habit
        longest_streaks = {}
        for habit_id, habit_data in habit_dates.items():
            dates = sorted(habit_data['dates'])
            current_streak = longest_streak = 1
            for i in range(1, len(dates)):
                if dates[i] == dates[i - 1] + timedelta(days=1):
                    current_streak += 1
                else:
                    longest_streak = max(longest_streak, current_streak)
                    current_streak = 1
            longest_streak = max(longest_streak, current_streak)
            longest_streaks[habit_id] = {'name': habit_data['name'], 'streak': longest_streak}

        # Display the longest streaks for each habit
        for habit_id, streak_data in longest_streaks.items():
            print(f'Habit: {streak_data["name"]} - Longest Streak: {streak_data["streak"]} days')

    def habits_goals(self):
        print('''
        Here you are able to set goals towards your habits and keep them updated.
        You can set a timeline for them.
        -----------------------------------------------------------------------------
        ''')

        self.view_all()

        habit_to_select = input(
            'Please select the id of the habit you want to set the goal for or check it for today: ')
        # Solve possible errors
        try:
            habit_to_select = int(habit_to_select)
        except ValueError:
            print("Please enter a valid habit id.")
            return

        conn = sqlite3.connect('habits.db')
        cur = conn.cursor()
        cur.execute('SELECT id FROM habits')
        rows = cur.fetchall()

        habit_ids = [row[0] for row in rows]
        if habit_to_select not in habit_ids:
            print("Habit id not found.")
            conn.close()
            return

        try:
            options = int(input('Press 1 to set a time-goal, 2 to check it for today: '))
        except ValueError:
            print("Please enter a valid option (1 or 2).")
            conn.close()
            return

        if options == 1:
            try:
                goal = int(input('For how long do you want to keep the habit? (in days): '))
                self.time_goal = goal

                # Update the time_goal in the database
                cur.execute('UPDATE habits SET goal = ? WHERE id = ?', (self.time_goal, habit_to_select))
                conn.commit()
                print('Goal set.')
            except ValueError:
                print('Please introduce a correct value.')
        elif options == 2:
            check = input('Have you completed the habit today? (y/n): ').strip().lower()
            if check == 'y':
                cur.execute('SELECT goal FROM habits WHERE id = ?', (habit_to_select,))
                current_goal = cur.fetchone()[0]
                if current_goal is not None and current_goal > 0:
                    self.time_goal = current_goal - 1
                    cur.execute('UPDATE habits SET goal = ? WHERE id = ?', (self.time_goal, habit_to_select))
                    conn.commit()
                    print('Congrats!! Keep it up.')
                else:
                    print('No goal set for this habit.')
            elif check == 'n':
                print("Never surrender, don't let this happen again!!")
            else:
                print("Invalid input. Please enter 'y' or 'n'.")
        else:
            print("Invalid option selected.")

        conn.close()







    def menu(self):
        while True:
            prompt = int(input(
                '''
                Welcome to the menu:
                Press 1 if you want to create a new habit,
                press 2 if you want to view all,
                press 3 if you want to upgrade an habit,
                press 4 if you want to delete an habit,
                press 5 if you want to check your longer streak
                press 6 to set goals towards your habits
                '''
            ))

            if prompt == 1:
                self.create_new_habit()
            elif prompt == 2:
                self.view_all()
            elif prompt == 3:
                self.upgrade_habits()
            elif prompt == 4:
                self.deleting_habit()
            elif prompt == 5:
                self.longer_streak()
            elif prompt == 6:
                self.habits_goals()
            else:
                print('Value not valid')
                continue





if __name__ == "__main__":

    habit_menu = Habit()
    habit_menu.menu()





