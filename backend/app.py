from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app) # 프론트엔드(React)의 접근을 허용합니다.

# app.py 코드 윗부분에 추가
@app.route('/')
def home():
    return "백엔드 서버가 아주 잘 돌아가고 있습니다! (포트: 5000)"

@app.route('/api/route', methods=['POST'])
def get_route():
    data = request.get_json()
    print(f"검색 요청 도착: {data}")

    # 테스트용 가짜 경로 데이터 (수원역 부근)
    mock_path = [
        [37.2664, 127.0002],
        [37.2675, 127.0015],
        [37.2685, 127.0025]
    ]

    return jsonify({
        "status": "success",
        "path": mock_path
    })

if __name__ == '__main__':
    app.run(debug=True, port=5000)
