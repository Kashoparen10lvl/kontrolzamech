from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from database import get_db, init_db
from datetime import datetime
import os

app = Flask(__name__)
CORS(app)

# Инициализация БД
init_db()

# === Аутентификация ===
@app.route('/api/login', methods=['POST'])
def login():
    data = request.json
    username = data.get('username')
    password = data.get('password')
    
    conn = get_db()
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE username = ? AND password = ?", (username, password))
    user = c.fetchone()
    conn.close()
    
    if user:
        return jsonify({
            'success': True,
            'user': {
                'id': user['id'],
                'username': user['username'],
                'role': user['role']
            }
        })
    else:
        return jsonify({'success': False, 'error': 'Неверный логин или пароль'}), 401

@app.route('/api/register', methods=['POST'])
def register():
    data = request.json
    username = data.get('username')
    password = data.get('password')
    role = data.get('role', 'Сотрудник')
    
    conn = get_db()
    c = conn.cursor()
    try:
        c.execute("INSERT INTO users (username, password, role) VALUES (?, ?, ?)", (username, password, role))
        conn.commit()
        return jsonify({'success': True})
    except:
        return jsonify({'success': False, 'error': 'Пользователь уже существует'}), 400
    finally:
        conn.close()

@app.route('/api/recover', methods=['POST'])
def recover_password():
    data = request.json
    username = data.get('username')
    
    conn = get_db()
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE username = ?", (username,))
    user = c.fetchone()
    conn.close()
    
    if user:
        return jsonify({'success': True, 'password': user['password']})
    else:
        return jsonify({'success': False, 'error': 'Пользователь не найден'}), 404

# === Объекты ===
@app.route('/api/objects', methods=['GET'])
def get_objects():
    conn = get_db()
    c = conn.cursor()
    c.execute("SELECT * FROM objects")
    objects = [dict(row) for row in c.fetchall()]
    conn.close()
    return jsonify(objects)

@app.route('/api/objects', methods=['POST'])
def create_object():
    data = request.json
    conn = get_db()
    c = conn.cursor()
    c.execute("INSERT INTO objects (name, address) VALUES (?, ?)", (data['name'], data['address']))
    conn.commit()
    obj_id = c.lastrowid
    conn.close()
    return jsonify({'success': True, 'id': obj_id})

# === Замечания ===
@app.route('/api/objects/<int:obj_id>/remarks', methods=['GET'])
def get_remarks(obj_id):
    conn = get_db()
    c = conn.cursor()
    c.execute("SELECT * FROM remarks WHERE object_id = ?", (obj_id,))
    remarks = [dict(row) for row in c.fetchall()]
    conn.close()
    return jsonify(remarks)

@app.route('/api/remarks', methods=['POST'])
def create_remark():
    data = request.json
    conn = get_db()
    c = conn.cursor()
    c.execute("""
        INSERT INTO remarks (object_id, title, place, status, photo_path)
        VALUES (?, ?, ?, ?, ?)
    """, (data['object_id'], data['title'], data['place'], data.get('status', 'Новое'), data.get('photo_path')))
    conn.commit()
    remark_id = c.lastrowid
    conn.close()
    return jsonify({'success': True, 'id': remark_id})

@app.route('/api/remarks/<int:remark_id>', methods=['PUT'])
def update_remark(remark_id):
    data = request.json
    conn = get_db()
    c = conn.cursor()
    c.execute("""
        UPDATE remarks SET title = ?, place = ?, status = ?, photo_path = ?, updated_at = ?
        WHERE id = ?
    """, (data.get('title'), data.get('place'), data.get('status'), data.get('photo_path'), datetime.now(), remark_id))
    conn.commit()
    conn.close()
    return jsonify({'success': True})

@app.route('/api/remarks/<int:remark_id>', methods=['DELETE'])
def delete_remark(remark_id):
    conn = get_db()
    c = conn.cursor()
    c.execute("DELETE FROM remarks WHERE id = ?", (remark_id,))
    conn.commit()
    conn.close()
    return jsonify({'success': True})

# === Загрузка фото ===
@app.route('/api/upload', methods=['POST'])
def upload_photo():
    if 'photo' not in request.files:
        return jsonify({'success': False, 'error': 'Нет файла'}), 400
    
    file = request.files['photo']
    if file.filename == '':
        return jsonify({'success': False, 'error': 'Файл не выбран'}), 400
    
    upload_dir = os.path.join(os.path.dirname(__file__), 'uploads')
    os.makedirs(upload_dir, exist_ok=True)
    
    filename = f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_{file.filename}"
    filepath = os.path.join(upload_dir, filename)
    file.save(filepath)
    
    return jsonify({'success': True, 'path': f'/uploads/{filename}'})

@app.route('/uploads/<path:filename>')
def serve_upload(filename):
    return send_from_directory(os.path.join(os.path.dirname(__file__), 'uploads'), filename)

if __name__ == '__main__':
    # Получаем IP адрес ноутбука
    import socket
    hostname = socket.gethostname()
    ip_address = socket.gethostbyname(hostname)
    
    print(f"\n🚀 Сервер запущен!")
    print(f"📍 IP адрес: {ip_address}")
    print(f"🌐 URL: http://{ip_address}:5000")
    print(f"📱 В мобильном приложении укажите: http://{ip_address}:5000\n")
    
    app.run(host='0.0.0.0', port=5000, debug=True)
