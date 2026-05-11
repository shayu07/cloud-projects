"""
Hospital Patient Registration System — Data Redundancy Removal
Prevents duplicate patient records in a cloud-connected hospital database.
Real-world use case: Hospitals waste millions annually on duplicate patient records,
leading to wrong treatments, billing errors, and wasted resources.
"""

from flask import Flask, render_template, request, jsonify
import os
from dotenv import load_dotenv
from db_utils import init_db, check_duplicates, add_record, log_duplicate, get_all_records, get_stats, mark_cloud_synced, delete_record, search_records
from cloud_storage import CloudStorage

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('FLASK_SECRET_KEY', 'dev-secret-key')

init_db()
cloud = CloudStorage()


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/api/check', methods=['POST'])
def api_check_data():
    """Check if patient data is a duplicate before registering."""
    data = request.get_json()
    name = data.get('name', '').strip()
    email = data.get('email', '').strip()
    phone = data.get('phone', '').strip()

    if not name or not email or not phone:
        return jsonify({'error': 'Patient name, email, and phone are required.'}), 400

    result = check_duplicates(name, email, phone)
    return jsonify(result)


@app.route('/api/add', methods=['POST'])
def api_add_record():
    """Register a new patient after verification."""
    data = request.get_json()
    name = data.get('name', '').strip()
    email = data.get('email', '').strip()
    phone = data.get('phone', '').strip()
    age = data.get('age', '').strip()
    gender = data.get('gender', '').strip()
    blood_group = data.get('blood_group', '').strip()
    address = data.get('address', '').strip()

    if not name or not email or not phone:
        return jsonify({'error': 'Required fields missing.'}), 400

    # Final duplicate check
    dup = check_duplicates(name, email, phone)
    if dup['is_duplicate'] and dup['match_type'] == 'EXACT':
        log_duplicate(
            {'name': name, 'email': email, 'phone': phone},
            dup['matched_record']['id'], dup['confidence'], 'EXACT', 'blocked'
        )
        return jsonify({
            'status': 'blocked',
            'message': 'Duplicate patient record detected and blocked.',
            'duplicate_info': dup
        }), 409

    record_id = add_record(name, email, phone, age, gender, blood_group, address)

    cloud_result = cloud.upload_record({
        'id': record_id, 'name': name, 'email': email,
        'phone': phone, 'age': age, 'gender': gender,
        'blood_group': blood_group, 'address': address
    }, record_id)

    if cloud_result['status'] == 'uploaded':
        mark_cloud_synced(record_id)

    return jsonify({
        'status': 'success',
        'message': f'Patient #{record_id} registered successfully.',
        'record_id': record_id,
        'cloud_sync': cloud_result
    }), 201


@app.route('/api/force-add', methods=['POST'])
def api_force_add():
    """Override fuzzy duplicate and register patient anyway."""
    data = request.get_json()
    name = data.get('name', '').strip()
    email = data.get('email', '').strip()
    phone = data.get('phone', '').strip()
    age = data.get('age', '').strip()
    gender = data.get('gender', '').strip()
    blood_group = data.get('blood_group', '').strip()
    address = data.get('address', '').strip()

    record_id = add_record(name, email, phone, age, gender, blood_group, address)
    log_duplicate({'name': name, 'email': email, 'phone': phone}, None, 0, 'FUZZY', 'user_accepted')

    cloud_result = cloud.upload_record({
        'id': record_id, 'name': name, 'email': email,
        'phone': phone, 'age': age, 'gender': gender,
        'blood_group': blood_group, 'address': address
    }, record_id)
    if cloud_result['status'] == 'uploaded':
        mark_cloud_synced(record_id)

    return jsonify({
        'status': 'success', 'message': f'Patient #{record_id} registered (override).',
        'record_id': record_id, 'cloud_sync': cloud_result
    }), 201


@app.route('/api/records')
def api_get_records():
    q = request.args.get('q', '').strip()
    if q:
        records = search_records(q)
    else:
        records = get_all_records()
    return jsonify({'records': records, 'total': len(records)})


@app.route('/api/records/<int:record_id>', methods=['PUT'])
def api_update_record(record_id):
    data = request.get_json()
    name = data.get('name', '').strip()
    email = data.get('email', '').strip()
    phone = data.get('phone', '').strip()
    age = data.get('age', '').strip()
    gender = data.get('gender', '').strip()
    blood_group = data.get('blood_group', '').strip()
    address = data.get('address', '').strip()

    if not name or not email or not phone:
        return jsonify({'error': 'Required fields missing.'}), 400

    from db_utils import update_record
    update_record(record_id, name, email, phone, age, gender, blood_group, address)
    
    cloud_result = cloud.upload_record({
        'id': record_id, 'name': name, 'email': email,
        'phone': phone, 'age': age, 'gender': gender,
        'blood_group': blood_group, 'address': address
    }, record_id)

    if cloud_result['status'] == 'uploaded':
        mark_cloud_synced(record_id)

    return jsonify({'status': 'success', 'message': f'Patient #{record_id} updated successfully.'})


@app.route('/api/records/<int:record_id>', methods=['DELETE'])
def api_delete_record(record_id):
    delete_record(record_id)
    return jsonify({'status': 'deleted', 'message': f'Patient #{record_id} removed.'})


@app.route('/api/stats')
def api_get_stats():
    stats = get_stats()
    stats['cloud'] = cloud.get_cloud_status()
    return jsonify(stats)


@app.route('/api/cloud/backup', methods=['POST'])
def api_cloud_backup():
    records = get_all_records()
    return jsonify(cloud.upload_backup(records))


@app.route('/api/cloud/status')
def api_cloud_status():
    return jsonify(cloud.get_cloud_status())


if __name__ == '__main__':
    port = int(os.getenv('PORT', 5001))
    print(f"\n{'='*55}")
    print(f"  MedGuard - Hospital Patient Registration System")
    print(f"  Running on http://localhost:{port}")
    print(f"  Cloud: {'AWS S3' if cloud.is_connected() else 'LOCAL'}")
    print(f"{'='*55}\n")
    app.run(host='0.0.0.0', port=port, debug=True)
