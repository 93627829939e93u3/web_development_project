from ast import Return
from flask import Flask, request, render_template, redirect,make_response
import sqlite3
import uuid


app = Flask(__name__)

# Create table if it doesn't exist
def init_db():
    with sqlite3.connect('names.db') as conn:
        conn.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                description TEXT,
                device_id TEXT
            )
        ''')


@app.route('/', methods=['GET', 'POST'])
def index():
    # Step 1: Get or create device ID
    device_id = request.cookies.get('device_id')
    if not device_id:
        device_id = str(uuid.uuid4())

    # Step 2: Handle POST request
    if request.method == 'POST':
        name = request.form.get('name')
        description = request.form.get('description')
        if name:
            with sqlite3.connect('names.db') as conn:
                conn.execute('INSERT INTO users (name, description, device_id) VALUES (?, ?, ?)', (name, description, device_id))
        return redirect('/')

    # Step 3: Fetch only tasks for this device
    with sqlite3.connect('names.db') as conn:
        cursor = conn.execute('SELECT id, name, description FROM users WHERE device_id = ?', (device_id,))
        users = cursor.fetchall()

    # Step 4: Set cookie and return response
    response = make_response(render_template('index.html', users=users))
    response.set_cookie('device_id', device_id, max_age=60*60*24*365*2)  # 2 years
    return response

@app.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit(id):
    device_id = request.cookies.get('device_id')
    if not device_id:
        return redirect('/')

    if request.method == 'POST':
        new_name = request.form.get('name')
        new_description = request.form.get('description')
        if new_name:
            with sqlite3.connect('names.db') as conn:
                conn.execute('UPDATE users SET name = ?, description = ? WHERE id = ? AND device_id = ?', (new_name, new_description, id, device_id))
            return redirect('/')

    with sqlite3.connect('names.db') as conn:
        cursor = conn.execute('SELECT id, name, description FROM users WHERE id = ? AND device_id = ?', (id, device_id))
        user = cursor.fetchone()

    if not user:
        return redirect('/')

    return render_template('edit.html', user=user)

@app.route('/delete/<int:id>')
def delete(id):
    device_id = request.cookies.get('device_id')
    if not device_id:
        return redirect('/')
    with sqlite3.connect('names.db') as conn:
        conn.execute('DELETE FROM users WHERE id = ? AND device_id = ?', (id, device_id))
    return redirect('/')

if __name__ == '__main__':
    init_db()
    app.run(debug=True)
