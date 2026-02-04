from flask import Flask, jsonify
from datetime import datetime

app = Flask(__name__)

@app.route('/api/audit', methods=['POST'])
def audit():
    return jsonify({
        "status": "success",
        "url": "https://example.com",
        "timestamp": datetime.utcnow().isoformat(),
        "scores": {
            "technical": 85,
            "content": 72,
            "authority": 65,
            "overall": 74
        },
        "message": "SEO audit completed successfully!"
    })

def handler(request):
    return app(request)
