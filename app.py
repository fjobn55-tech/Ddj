import os, sqlite3, uuid, datetime, requests
from flask import Flask, g, render_template, request, redirect, url_for, send_from_directory, flash, session
import config as cfg

app = Flask(__name__)
app.secret_key = cfg.SECRET_KEY
DB = cfg.DATABASE

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        need_init = not os.path.exists(DB)
        db = g._database = sqlite3.connect(DB)
        db.row_factory = sqlite3.Row
        if need_init:
            init_db(db)
    return db

def init_db(db):
    cur = db.cursor()
    cur.execute('''
        CREATE TABLE orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            game TEXT,
            uid TEXT,
            pack_label TEXT,
            price INTEGER,
            lang TEXT,
            status TEXT,
            slip_path TEXT,
            created_at TEXT
        );
    ''')
    cur.execute('''
        CREATE TABLE settings (
            key TEXT PRIMARY KEY,
            value TEXT
        );
    ''')
    # set initial shop credit
    cur.execute("INSERT OR REPLACE INTO settings(key, value) VALUES(?, ?)", ('shop_credit', str(cfg.SHOP_CREDIT)))
    db.commit()

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

def get_shop_credit():
    db = get_db()
    cur = db.execute("SELECT value FROM settings WHERE key='shop_credit'")
    row = cur.fetchone()
    return int(row['value'])

def set_shop_credit(amount):
    db = get_db()
    db.execute("UPDATE settings SET value=? WHERE key='shop_credit'", (str(amount),))
    db.commit()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/create_order', methods=['POST'])
def create_order():
    game = request.form.get('game')
    uid = request.form.get('uid')
    pack = request.form.get('pack')  # format like "100_3000"
    lang = request.form.get('lang','th')
    try:
        diamonds, price = pack.split('_')
        price = int(price)
        pack_label = f"{diamonds} 💎"
    except:
        diamonds = '100'
        price = 3000
        pack_label = '100 💎'
    db = get_db()
    cur = db.cursor()
    cur.execute('INSERT INTO orders(game, uid, pack_label, price, lang, status, slip_path, created_at) VALUES(?,?,?,?,?,?,?,?)',
                (game, uid, pack_label, price, lang, 'pending', '', datetime.datetime.utcnow().isoformat()))
    db.commit()
    order_id = cur.lastrowid
    return render_template('order_created.html', order_id=order_id, game=game, pack_label=pack_label, price=price, currency=cfg.CURRENCY, bank_name=cfg.BANK_ACCOUNT_NAME, bank_number=cfg.BANK_ACCOUNT_NUMBER)

@app.route('/upload_slip/<int:order_id>', methods=['POST'])
def upload_slip(order_id):
    file = request.files.get('slip')
    if not file:
        return "no file", 400
    filename = f"slip_{order_id}_{uuid.uuid4().hex}.png"
    save_path = os.path.join('static', filename)
    file.save(save_path)
    db = get_db()
    db.execute('UPDATE orders SET slip_path=? WHERE id=?', (save_path, order_id))
    db.commit()
    return redirect(url_for('index'))

@app.route('/admin', methods=['GET'])
def admin_index():
    if not session.get('admin'):
        return render_template('admin_login.html')
    db = get_db()
    cur = db.execute('SELECT * FROM orders ORDER BY id DESC')
    orders = cur.fetchall()
    orders_list = []
    for r in orders:
        orders_list.append({'id': r['id'], 'game': r['game'], 'uid': r['uid'], 'pack_label': r['pack_label'], 'price': r['price'], 'status': r['status']})
    credit = get_shop_credit()
    return render_template('admin_dashboard.html', orders=orders_list, credit=credit, currency=cfg.CURRENCY)

@app.route('/admin/login', methods=['POST'])
def admin_login():
    username = request.form.get('username')
    password = request.form.get('password')
    if username == cfg.ADMIN_USERNAME and password == cfg.ADMIN_PASSWORD:
        session['admin'] = True
        return redirect(url_for('admin_index'))
    return 'invalid credentials', 403

@app.route('/admin/logout')
def admin_logout():
    session.pop('admin', None)
    return redirect(url_for('index'))

@app.route('/admin/order/<int:order_id>')
def admin_order(order_id):
    if not session.get('admin'):
        return redirect(url_for('admin_index'))
    db = get_db()
    cur = db.execute('SELECT * FROM orders WHERE id=?', (order_id,))
    order = cur.fetchone()
    if not order:
        return 'not found', 404
    order_d = dict(order)
    return render_template('admin_order.html', order=order_d)

@app.route('/admin/order/<int:order_id>/confirm', methods=['POST'])
def admin_order_confirm(order_id):
    if not session.get('admin'):
        return redirect(url_for('admin_index'))
    action = request.form.get('action')
    db = get_db()
    cur = db.execute('SELECT * FROM orders WHERE id=?', (order_id,))
    order = cur.fetchone()
    if not order:
        return 'not found', 404
    if action == 'mark_paid':
        db.execute('UPDATE orders SET status=? WHERE id=?', ('paid', order_id))
        db.commit()
        return redirect(url_for('admin_index'))
    elif action == 'fill':
        # Simulate calling real API (requires cfg.GAME_API_ENDPOINT and cfg.GAME_API_KEY)
        if not cfg.GAME_API_ENDPOINT or not cfg.GAME_API_KEY:
            return 'API not configured. Put GAME_API_ENDPOINT and GAME_API_KEY in config.py', 400
        # Check shop credit
        credit = get_shop_credit()
        price = order['price']
        if credit < price:
            return 'credit not enough', 400
        # Simulate API success
        set_shop_credit(credit - price)
        db.execute('UPDATE orders SET status=? WHERE id=?', ('filled', order_id))
        db.commit()
        return redirect(url_for('admin_index'))
    return redirect(url_for('admin_index'))

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
