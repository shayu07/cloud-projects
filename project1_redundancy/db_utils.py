"""
Database Utilities — Hospital Patient Registration
Handles SQLite operations, hashing, and duplicate patient detection.
"""

import sqlite3
import hashlib
import os
from difflib import SequenceMatcher

DB_PATH = os.path.join(os.path.dirname(__file__), 'hospital.db')


def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db()
    conn.execute('''
        CREATE TABLE IF NOT EXISTS patients (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT NOT NULL,
            phone TEXT NOT NULL,
            age TEXT,
            gender TEXT,
            blood_group TEXT,
            address TEXT,
            data_hash TEXT NOT NULL,
            status TEXT DEFAULT 'active',
            cloud_synced INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.execute('''
        CREATE TABLE IF NOT EXISTS duplicates_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            incoming_data TEXT NOT NULL,
            matched_record_id INTEGER,
            similarity_score REAL,
            match_type TEXT,
            action_taken TEXT DEFAULT 'pending',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()
    print("[DB] Hospital database initialized.")


def compute_hash(name, email, phone):
    normalized = f"{name.strip().lower()}|{email.strip().lower()}|{phone.strip()}"
    return hashlib.md5(normalized.encode()).hexdigest()


def similarity_score(str1, str2):
    return SequenceMatcher(None, str1.lower().strip(), str2.lower().strip()).ratio()


def check_duplicates(name, email, phone):
    conn = get_db()
    incoming_hash = compute_hash(name, email, phone)

    exact = conn.execute('SELECT * FROM patients WHERE data_hash = ?', (incoming_hash,)).fetchone()
    if exact:
        conn.close()
        return {
            'is_duplicate': True, 'match_type': 'EXACT', 'confidence': 100.0,
            'matched_record': dict(exact),
            'matched_fields': ['Name', 'Email', 'Phone'],
            'message': f'Exact duplicate — matches Patient #{exact["id"]} ({exact["name"]})'
        }

    all_records = conn.execute('SELECT * FROM patients').fetchall()
    best_match, best_score = None, 0.0

    for r in all_records:
        s = (similarity_score(name, r['name']) * 0.4 +
             similarity_score(email, r['email']) * 0.4 +
             similarity_score(phone, r['phone']) * 0.2) * 100
        if s > best_score:
            best_score = s
            best_match = dict(r)

    conn.close()

    if best_score >= 75.0:
        matched_fields = []
        if similarity_score(name, best_match['name']) > 0.8: matched_fields.append("Name")
        if similarity_score(email, best_match['email']) > 0.8: matched_fields.append("Email")
        if similarity_score(phone, best_match['phone']) > 0.8: matched_fields.append("Phone")
        
        return {
            'is_duplicate': True, 'match_type': 'FUZZY',
            'confidence': round(best_score, 1), 'matched_record': best_match,
            'matched_fields': matched_fields,
            'message': f'Potential duplicate ({round(best_score, 1)}% match) — similar to Patient #{best_match["id"]} ({best_match["name"]})'
        }

    return {
        'is_duplicate': False, 'match_type': None,
        'confidence': round(best_score, 1) if best_match else 0,
        'matched_record': None, 'matched_fields': [], 'message': 'No duplicates found — patient is unique.'
    }


def add_record(name, email, phone, age, gender, blood_group, address):
    conn = get_db()
    h = compute_hash(name, email, phone)
    cur = conn.execute(
        'INSERT INTO patients (name, email, phone, age, gender, blood_group, address, data_hash) VALUES (?,?,?,?,?,?,?,?)',
        (name, email, phone, age, gender, blood_group, address, h)
    )
    rid = cur.lastrowid
    conn.commit()
    conn.close()
    return rid

def update_record(rid, name, email, phone, age, gender, blood_group, address):
    conn = get_db()
    h = compute_hash(name, email, phone)
    conn.execute(
        'UPDATE patients SET name=?, email=?, phone=?, age=?, gender=?, blood_group=?, address=?, data_hash=?, cloud_synced=0 WHERE id=?',
        (name, email, phone, age, gender, blood_group, address, h, rid)
    )
    conn.commit()
    conn.close()


def log_duplicate(incoming, matched_id, score, match_type, action):
    conn = get_db()
    conn.execute(
        'INSERT INTO duplicates_log (incoming_data, matched_record_id, similarity_score, match_type, action_taken) VALUES (?,?,?,?,?)',
        (str(incoming), matched_id, score, match_type, action)
    )
    conn.commit()
    conn.close()


def get_all_records():
    conn = get_db()
    records = [dict(r) for r in conn.execute('SELECT * FROM patients ORDER BY created_at DESC').fetchall()]
    conn.close()
    return records


def search_records(query):
    conn = get_db()
    q = f'%{query}%'
    records = [dict(r) for r in conn.execute(
        'SELECT * FROM patients WHERE name LIKE ? OR email LIKE ? OR phone LIKE ? OR blood_group LIKE ? ORDER BY created_at DESC',
        (q, q, q, q)
    ).fetchall()]
    conn.close()
    return records


def get_stats():
    conn = get_db()
    total = conn.execute('SELECT COUNT(*) FROM patients').fetchone()[0]
    dups = conn.execute('SELECT COUNT(*) FROM duplicates_log').fetchone()[0]
    exact = conn.execute("SELECT COUNT(*) FROM duplicates_log WHERE match_type='EXACT'").fetchone()[0]
    fuzzy = conn.execute("SELECT COUNT(*) FROM duplicates_log WHERE match_type='FUZZY'").fetchone()[0]
    synced = conn.execute('SELECT COUNT(*) FROM patients WHERE cloud_synced=1').fetchone()[0]
    conn.close()
    return {
        'total_records': total, 'duplicates_caught': dups,
        'exact_matches': exact, 'fuzzy_matches': fuzzy, 'cloud_synced': synced,
        'accuracy': round((total / (total + dups) * 100), 1) if (total + dups) > 0 else 100
    }


def mark_cloud_synced(rid):
    conn = get_db()
    conn.execute('UPDATE patients SET cloud_synced=1 WHERE id=?', (rid,))
    conn.commit()
    conn.close()


def delete_record(rid):
    conn = get_db()
    conn.execute('DELETE FROM patients WHERE id=?', (rid,))
    conn.commit()
    conn.close()
