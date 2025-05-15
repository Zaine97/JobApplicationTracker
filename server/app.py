from flask import Flask, request, jsonify
from flask_cors import CORS
from database import init_db
import sqlite3
from collections import Counter
from datetime import datetime

app = Flask(__name__)
CORS(app)
init_db()

def get_db_connection():
    conn = sqlite3.connect('job_applications.db')
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/applications', methods=['GET'])
def get_applications():
    status_filter = request.args.get('status')
    company_filter = request.args.get('company')
    sort_by = request.args.get('sort_by', 'application_date')

    conn = get_db_connection()
    cursor = conn.cursor()

    query = "SELECT * FROM applications WHERE 1=1"
    params = []

    if status_filter:
        query += " AND status = ?"
        params.append(status_filter)
    if company_filter:
        query += " AND company_name LIKE ?"
        params.append(f"%{company_filter}%")
    if sort_by in ['application_date', 'company_name', 'job_title']:
        query += f" ORDER BY {sort_by} ASC"

    cursor.execute(query, params)
    rows = cursor.fetchall()
    conn.close()

    applications = [
        {
            "id": row["id"],
            "job_title": row["job_title"],
            "company_name": row["company_name"],
            "application_date": row["application_date"],
            "status": row["status"]
        }
        for row in rows
    ]
    return jsonify(applications)

@app.route('/applications', methods=['POST'])
def add_application():
    data = request.get_json()
    job_title = data['job_title']
    company_name = data['company_name']
    application_date = data['application_date']
    status = data['status']

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        '''INSERT INTO applications (job_title, company_name, application_date, status)
           VALUES (?, ?, ?, ?)''',
        (job_title, company_name, application_date, status)
    )
    conn.commit()
    conn.close()
    return jsonify({"message": "Application added!"}), 201

@app.route('/applications/<int:id>', methods=['DELETE'])
def delete_application(id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM applications WHERE id = ?', (id,))
    conn.commit()
    conn.close()
    return jsonify({"message": f"Application with id {id} deleted!"})

@app.route('/analytics', methods=['GET'])
def get_analytics():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT application_date FROM applications')
    rows = cursor.fetchall()
    conn.close()

    weekly_count = Counter()
    monthly_count = Counter()

    for row in rows:
        date = datetime.strptime(row['application_date'], "%Y-%m-%d")
        weekly_count[date.strftime('%Y-W%U')] += 1
        monthly_count[date.strftime('%Y-%m')] += 1

    return jsonify({
        "weekly": dict(weekly_count),
        "monthly": dict(monthly_count)
    })

if __name__ == '__main__':
    app.run(debug=True)
