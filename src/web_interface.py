"""
Simple web interface for IAM automation tool
"""

from flask import Flask, render_template, request, jsonify, flash
import json
import os
from iam_manager import IAMManager
from utils.logger import setup_logger

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'dev-secret-key')

# Setup logging
setup_logger()

@app.route('/')
def index():
    """Main dashboard"""
    return render_template('index.html')

@app.route('/api/create-user', methods=['POST'])
def api_create_user():
    """API endpoint to create user"""
    try:
        data = request.get_json()
        
        iam_manager = IAMManager(
            region=data.get('region', 'us-east-1'),
            dry_run=data.get('dry_run', False)
        )
        
        result = iam_manager.create_user(
            username=data['username'],
            groups=data.get('groups', []),
            policies=data.get('policies', [])
        )
        
        return jsonify(result)
    
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/create-role', methods=['POST'])
def api_create_role():
    """API endpoint to create role"""
    try:
        data = request.get_json()
        
        iam_manager = IAMManager(
            region=data.get('region', 'us-east-1'),
            dry_run=data.get('dry_run', False)
        )
        
        # Create temporary trust policy file
        import tempfile
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(data['trust_policy'], f)
            trust_policy_file = f.name
        
        try:
            result = iam_manager.create_role(
                role_name=data['role_name'],
                trust_policy_file=trust_policy_file,
                policies=data.get('policies', [])
            )
        finally:
            os.unlink(trust_policy_file)
        
        return jsonify(result)
    
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/audit', methods=['POST'])
def api_audit():
    """API endpoint to run audit"""
    try:
        data = request.get_json()
        
        iam_manager = IAMManager(
            region=data.get('region', 'us-east-1')
        )
        
        # Use temporary file for audit results
        import tempfile
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            temp_file = f.name
        
        try:
            result = iam_manager.audit_permissions(temp_file)
            
            # Read audit results
            with open(temp_file, 'r') as f:
                audit_data = json.load(f)
            
            result['audit_data'] = audit_data
        finally:
            os.unlink(temp_file)
        
        return jsonify(result)
    
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

# Simple HTML template (you can create proper templates later)
@app.route('/templates/index.html')
def serve_template():
    return '''
<!DOCTYPE html>
<html>
<head>
    <title>IAM Automation Tool</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 40px; }
        .container { max-width: 800px; margin: 0 auto; }
        .form-group { margin: 20px 0; }
        label { display: block; margin-bottom: 5px; font-weight: bold; }
        input, select, textarea { width: 100%; padding: 8px; margin-bottom: 10px; }
        button { background: #007cba; color: white; padding: 10px 20px; border: none; cursor: pointer; }
        button:hover { background: #005a87; }
        .result { margin: 20px 0; padding: 15px; background: #f0f0f0; border-radius: 5px; }
        .error { background: #ffebee; color: #c62828; }
        .success { background: #e8f5e8; color: #2e7d32; }
    </style>
</head>
<body>
    <div class="container">
        <h1>IAM Automation Tool</h1>
        
        <div class="form-group">
            <h2>Create User</h2>
            <form id="createUserForm">
                <label>Username:</label>
                <input type="text" id="username" required>
                
                <label>Groups (comma-separated):</label>
                <input type="text" id="groups" placeholder="developers,admins">
                
                <label>Policies (comma-separated ARNs):</label>
                <textarea id="policies" placeholder="arn:aws:iam::aws:policy/ReadOnlyAccess"></textarea>
                
                <label>
                    <input type="checkbox" id="dryRun"> Dry Run
                </label>
                
                <button type="submit">Create User</button>
            </form>
        </div>
        
        <div class="form-group">
            <h2>Run Audit</h2>
            <button onclick="runAudit()">Run IAM Audit</button>
        </div>
        
        <div id="result" class="result" style="display: none;"></div>
    </div>
    
    <script>
        document.getElementById('createUserForm').addEventListener('submit', function(e) {
            e.preventDefault();
            
            const data = {
                username: document.getElementById('username').value,
                groups: document.getElementById('groups').value.split(',').filter(g => g.trim()),
                policies: document.getElementById('policies').value.split(',').filter(p => p.trim()),
                dry_run: document.getElementById('dryRun').checked
            };
            
            fetch('/api/create-user', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify(data)
            })
            .then(response => response.json())
            .then(result => {
                showResult(result);
            })
            .catch(error => {
                showResult({status: 'error', message: error.message});
            });
        });
        
        function runAudit() {
            fetch('/api/audit', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({})
            })
            .then(response => response.json())
            .then(result => {
                showResult(result);
            })
            .catch(error => {
                showResult({status: 'error', message: error.message});
            });
        }
        
        function showResult(result) {
            const resultDiv = document.getElementById('result');
            resultDiv.style.display = 'block';
            resultDiv.className = 'result ' + (result.status === 'error' ? 'error' : 'success');
            resultDiv.innerHTML = '<pre>' + JSON.stringify(result, null, 2) + '</pre>';
        }
    </script>
</body>
</html>
    '''

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8000))
    app.run(host='0.0.0.0', port=port, debug=True)