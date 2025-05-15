from flask import Flask, request, jsonify, redirect, url_for
from flask_cors import CORS
import sqlite3

app = Flask(__name__)
CORS(app)
//
DATABASE = 'applications.db'

# 🔄 Connect to SQLite database
def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

# ✅ Root route - redirects to the main applications page
@app.route('/')
def index():
    return redirect(url_for('get_applications'))

# 📥 Create a new job application
@app.route('/applications', methods=['POST'])
def add_application():
    data = request.get_json()
    company = data.get('company')
    position = data.get('position')
    date_applied = data.get('date_applied')
    status = data.get('status')

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO applications (company, position, date_applied, status)
        VALUES (?, ?, ?, ?)
    ''', (company, position, date_applied, status))
    conn.commit()
    conn.close()

    return jsonify({'message': 'Application added successfully'}), 201

# 📋 Get all job applications
@app.route('/applications', methods=['GET'])
def get_applications():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM applications')
    rows = cursor.fetchall()
    conn.close()

    applications = [dict(row) for row in rows]
    return jsonify(applications)

# 🛠️ Update a specific application
@app.route('/applications/<int:id>', methods=['PUT'])
def update_application(id):
    data = request.get_json()
    company = data.get('company')
    position = data.get('position')
    date_applied = data.get('date_applied')
    status = data.get('status')

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        UPDATE applications
        SET company = ?, position = ?, date_applied = ?, status = ?
        WHERE id = ?
    ''', (company, position, date_applied, status, id))
    conn.commit()
    conn.close()

    return jsonify({'message': 'Application updated successfully'})

# ❌ Delete a specific application
@app.route('/applications/<int:id>', methods=['DELETE'])
def delete_application(id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM applications WHERE id = ?', (id,))
    conn.commit()
    conn.close()

    return jsonify({'message': 'Application deleted successfully'})

# 🔄 Restart point (optional health check)
@app.route('/health', methods=['GET'])
def health():
    return jsonify({'status': 'ok'}), 200

# ✅ Run the app (for local testing only, not needed on Render)
# if __name__ == '__main__':
#     app.run(debug=True)
