from flask import Flask, request, jsonify, redirect, url_for
from flask_cors import CORS
import sqlite3
from collections import Counter
from datetime import datetime

app = Flask(__name__)
CORS(app)

DATABASE = 'job_applications.db'

def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS applications (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            job_title TEXT NOT NULL,
            company_name TEXT NOT NULL,
            application_date TEXT NOT NULL,
            status TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

init_db()

@app.route('/')
def index():
    return redirect(url_for('get_applications'))

@app.route('/applications', methods=['POST'])
def add_application():
    data = request.get_json()
    job_title = data.get('job_title')
    company_name = data.get('company_name')
    application_date = data.get('application_date')
    status = data.get('status')

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO applications (job_title, company_name, application_date, status)
        VALUES (?, ?, ?, ?)
    ''', (job_title, company_name, application_date, status))
    conn.commit()
    conn.close()

    return jsonify({'message': 'Application added successfully'}), 201

@app.route('/applications', methods=['GET'])
def get_applications():
    sort_by = request.args.get('sort_by', 'application_date')
    status_filter = request.args.get('status')
    company_filter = request.args.get('company')

    query = 'SELECT * FROM applications'
    filters = []
    params = []

    if status_filter:
        filters.append('status = ?')
        params.append(status_filter)
    if company_filter:
        filters.append('company_name LIKE ?')
        params.append(f'%{company_filter}%')

    if filters:
        query += ' WHERE ' + ' AND '.join(filters)

    if sort_by in ['application_date', 'company_name', 'job_title']:
        query += f' ORDER BY {sort_by}'

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(query, params)
    rows = cursor.fetchall()
    conn.close()

    applications = [dict(row) for row in rows]
    return jsonify(applications)

@app.route('/applications/<int:id>', methods=['PUT'])
def update_application(id):
    data = request.get_json()
    job_title = data.get('job_title')
    company_name = data.get('company_name')
    application_date = data.get('application_date')
    status = data.get('status')

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        UPDATE applications
        SET job_title = ?, company_name = ?, application_date = ?, status = ?
        WHERE id = ?
    ''', (job_title, company_name, application_date, status, id))
    conn.commit()
    conn.close()

    return jsonify({'message': 'Application updated successfully'})

@app.route('/applications/<int:id>', methods=['DELETE'])
def delete_application(id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM applications WHERE id = ?', (id,))
    conn.commit()
    conn.close()

    return jsonify({'message': 'Application deleted successfully'})

@app.route('/analytics', methods=['GET'])
def analytics():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT application_date FROM applications')
    rows = cursor.fetchall()
    conn.close()

    dates = [row['application_date'] for row in rows]
    weekly = Counter()
    monthly = Counter()

    for date_str in dates:
        try:
            date_obj = datetime.strptime(date_str, '%Y-%m-%d')
            week = date_obj.strftime('%Y-W%U')
            month = date_obj.strftime('%Y-%m')
            weekly[week] += 1
            monthly[month] += 1
        except ValueError:
            continue

    return jsonify({
        'weekly': dict(weekly),
        'monthly': dict(monthly)
    })

@app.route('/health', methods=['GET'])
def health():
    return jsonify({'status': 'ok'}), 200

if __name__ == '__main__':
    app.run(debug=True)
