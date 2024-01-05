# import sqlite3
# from flask import Flask, render_template #, request, url_for, flash, redirect
# from werkzeug.exceptions import abort


# app = Flask(__name__)
# app.config['SECRET_KEY'] = 'your secret key'

# def get_db_connection():
#     conn = sqlite3.connect('database.db')
#     conn.row_factory = sqlite3.Row
#     return conn

# @app.route('/')
# def index():
#     conn = get_db_connection()
#     events = conn.execute('SELECT * FROM events ORDER BY dateEvent').fetchall()
#     conn.close()
#     return render_template('index.html', events=events)
# # 

# # # hc = calendar.HTMLCalendar(calendar.SUNDAY)
# # # str = hc.formatmonth(2023,12)
# # # print(str)
# app.py

import calendar
from flask import Flask, render_template, request, redirect, url_for, flash, g
from datetime import datetime
from werkzeug.exceptions import abort
import sqlite3

app = Flask(__name__, template_folder='templates')
app.config['SECRET_KEY'] = 'your secret key'

def get_db_connection():
    if 'db' not in g:
        conn = sqlite3.connect('database.db')
        conn.row_factory = sqlite3.Row
        g.db = conn
    return g.db

@app.teardown_appcontext
def close_db(error):
    if hasattr(g, 'db'):
        g.db.close()

@app.route('/')
def index():
    today = datetime.today()
    year = today.year
    month = today.month

    query_params = request.args.to_dict()
    if 'year' in query_params and query_params['year'].isdigit():
        year = int(query_params['year'])
    if 'month' in query_params and query_params['month'].isdigit():
        month = int(query_params['month'])

    if 'prev' in query_params:
        month -= 1
        if month == 0:
            month = 12
            year -= 1
    elif 'next' in query_params:
        month += 1
        if month == 13:
            month = 1
            year += 1

    calendar.setfirstweekday(calendar.SUNDAY)
    cal = calendar.monthcalendar(year, month)
    display_date = datetime(year, month, 1).strftime('%B %Y')

    prev_month = month - 1 if month > 1 else 12
    prev_year = year - 1 if month == 1 else year
    next_month = month + 1 if month < 12 else 1
    next_year = year + 1 if month == 12 else year

    return render_template('index.html', display_date=display_date, calendar=cal, year=year, month=month, today=today,
                           prev_year=prev_year, prev_month=prev_month, next_year=next_year, next_month=next_month)

def get_events_for_day(year, month, day):
    conn = get_db_connection()
    
    # Format the input date components into a string for comparison
    target_date = f'{year:04d}-{month:02d}-{day:02d}'

    # Execute the query to get events for the specified day
    events = conn.execute('SELECT * FROM events WHERE dateEvent = ?',
                          (target_date,)).fetchall()
    conn.close()
    return events


@app.route('/events/<int:year>/<int:month>/<int:day>', methods=['GET'])
def events_for_day(year, month, day):
    events = get_events_for_day(year, month, day)
    display_date = f"{month}/{day}/{year}"
    return render_template('events.html', display_date=display_date, events=events)

@app.route('/create', methods=['GET', 'POST'])
def create_event():
    if request.method == 'POST':
        # Retrieve event details from the form
        event_name = request.form['eventName']
        event_date = request.form['dateEvent']
        event_description = request.form['eventDescription']

        # Insert the new event into the database
        conn = get_db_connection()
        conn.execute('INSERT INTO events (eventName, dateEvent, eventDescription) VALUES (?, ?, ?)',
                     (event_name, event_date, event_description))
        conn.commit()
        conn.close()

        # Redirect to the events page for the new event's date
        return redirect(url_for('events_for_day', year=int(event_date.split('-')[0]),
                                month=int(event_date.split('-')[1]),
                                day=int(event_date.split('-')[2])))
    
    return render_template('create.html')

# Modify the edit_event route
# @app.route('/edit/<int:event_id>', methods=['GET', 'POST'])
# def edit_event(event_id):
#     conn = get_db_connection()
#     event = conn.execute('SELECT * FROM events WHERE eventID = ?', (event_id,)).fetchone()
#     if request.method == 'POST':
#         event_name = request.form['event_name']
#         event_date = request.form['event_date']
#         event_description = request.form['event_description']

#         if not event_name or not event_date or not event_description:
#             flash('All form fields are required!')
#         else:
#             conn.execute('UPDATE events SET eventName = ?, dateEvent = ?, eventDescription = ? WHERE eventID = ?',
#                          (event_name, event_date, event_description, event_id))
#             conn.commit()
#             conn.close()

#             flash('Event updated successfully!', 'success')
#             return redirect(url_for('index'))  # Redirect to the homepage after successful edit

#     conn.close()
#     return render_template('edit.html', event=event)

@app.route('/edit/<int:event_id>', methods=['GET', 'POST'])
def edit_event(event_id):
    conn = get_db_connection()
    event = conn.execute('SELECT * FROM events WHERE eventID = ?', (event_id,)).fetchone()
    if request.method == 'POST':
        event_name = request.form['eventName']  # Use the correct form field name
        event_date = request.form['dateEvent']  # Use the correct form field name
        event_description = request.form['eventDescription']  # Use the correct form field name

        if not event_name or not event_date or not event_description:
            flash('All form fields are required!')
        else:
            conn.execute('UPDATE events SET eventName = ?, dateEvent = ?, eventDescription = ? WHERE eventID = ?',
                         (event_name, event_date, event_description, event_id))
            conn.commit()
            conn.close()

            flash('Event updated successfully!', 'success')
            return redirect(url_for('index'))  # Redirect to the homepage after successful edit

    conn.close()
    return render_template('edit.html', event=event)

# Add this route for event deletion
@app.route('/delete/<int:event_id>', methods=['POST'])
def delete_event(event_id):
    conn = get_db_connection()
    event = conn.execute('SELECT * FROM events WHERE eventID = ?', (event_id,)).fetchone()

    if event:
        conn.execute('DELETE FROM events WHERE eventID = ?', (event_id,))
        conn.commit()
        conn.close()

        flash('Event deleted successfully!', 'success')
    else:
        flash('Event not found!', 'error')

    return redirect(url_for('index'))  # Redirect to the homepage after successful deletion

if __name__ == '__main__':
    app.run(debug=True)
