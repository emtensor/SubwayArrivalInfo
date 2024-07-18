from flask import Flask, render_template, request, jsonify
import pandas as pd
import requests
import threading

app = Flask(__name__)

# API 엔드포인트
API_ENDPOINT = "http://swopenapi.seoul.go.kr/api/subway/{api_key}/json/realtimeStationArrival/0/20/{station_name}"
API_KEY = "API 키를 입력"
INFO_FILE = 'info.xlsx' # 엑셀 파일 경로

station_info = {} # 역 정보를 저장할 딕셔너리
all_stations = [] # 전체 역 이름(호선)을 저장한 리스트
stations = []  # 역 이름과 호선을 튜플로 저장할 리스트

# 호선을 지하철 ID로 변환하는 함수
def line_name_to_subway_id(line_name):
    subway_id_mapping = {
        '1호선': 1001,
        '2호선': 1002,
        '3호선': 1003,
        '4호선': 1004,
        '5호선': 1005,
        '6호선': 1006,
        '7호선': 1007,
        '8호선': 1008,
        '9호선': 1009,
        '중앙선': 1061,
        '경의중앙선': 1063,
        '공항철도': 1065,
        '경춘선': 1067,
        '수인분당선': 1075,
        '신분당선': 1077,
        '우이신설선': 1092,
        '서해선': 1093,
        '경강선': 1081,
        'GTX-A': 1032
    }
    return subway_id_mapping.get(line_name, None)

# 엑셀 파일의 데이터를 불러오는 함수
def load_station_info():
    try:
        xl = pd.ExcelFile(INFO_FILE)
        for sheet_name in xl.sheet_names:
            df = xl.parse(sheet_name)
            df = df[['SUBWAY_ID', 'STATN_ID', 'STATN_NM', '호선이름']]
            for index, row in df.iterrows():
                station_name = row['STATN_NM']
                subway_id = row['SUBWAY_ID']
                station_id = row['STATN_ID']
                line_name = row['호선이름']
                station_info[station_name] = {
                    'SUBWAY_ID': subway_id,
                    'STATN_ID': station_id,
                    '호선이름': line_name
                }
                all_stations.append(f"{station_name}[{line_name}]")
        return True
    except Exception as e:
        print(f"역 정보를 로드하는 중 오류 발생: {e}")
        return False

# 도착정보를 조회하는 함수
def fetch_arrival_info(station_name, line_name):
    try:
        subway_id = line_name_to_subway_id(line_name)
        if subway_id is None:
            return {'error': f'{line_name}에 대한 지하철 ID를 찾을 수 없습니다.'}

        url = API_ENDPOINT.format(api_key=API_KEY, station_name=station_name)
        response = requests.get(url)
        data = response.json()
        if 'realtimeArrivalList' in data:
            arrivals = data['realtimeArrivalList']
            arrivals = [arrival for arrival in arrivals if int(arrival['subwayId']) == subway_id]
            arrivals.sort(key=lambda x: int(x['barvlDt']))

            def filter_arrivals(arrivals, direction):
                filtered = []
                train_lines = set()
                count = 0
                for arrival in arrivals:
                    arrival_time = int(arrival['barvlDt'])
                    train_line_nm = arrival['trainLineNm']
                    if arrival_time <= 600 and train_line_nm not in train_lines:
                        if (direction == 'up' and arrival['updnLine'] in ['상행', '내선']) or \
                           (direction == 'down' and arrival['updnLine'] in ['하행', '외선']):
                            filtered.append({
                                'trainLineNm': train_line_nm,
                                'arvlMsg2': '도착' if arrival_time <= 60 else f'{arrival_time // 60}분 {arrival_time % 60}초 후 도착',
                                'barvlDt': arrival_time
                            })
                            train_lines.add(train_line_nm)
                            count += 1
                            if count >= 3:
                                break
                return filtered

            up_direction = filter_arrivals(arrivals, 'up')
            down_direction = filter_arrivals(arrivals, 'down')
            return {'up_direction': up_direction, 'down_direction': down_direction}
        return {'error': '데이터를 가져올 수 없습니다'}
    except Exception as e:
        print(f"도착 정보를 조회하는 중 오류 발생: {e}")
        return {'error': '데이터를 가져오지 못했습니다'}


# 렌더링
@app.route('/')
def index():
    return render_template('index.html', stations=[], all_stations=all_stations)

# 추가한 지하철역을 저장
@app.route('/add', methods=['POST'])
def add_station():
    try:
        station_name = request.form['station']
        line_name = request.form['subway_line']
        if station_name in station_info:
            if (station_name, line_name) not in stations:
                stations.append((station_name, line_name))
            arrival_info = {f'{station[0]}({station[1]})': fetch_arrival_info(station[0], station[1]) for station in stations}
            return jsonify({'stations': stations, 'arrival_info': arrival_info})
        else:
            return jsonify({'error': '유효하지 않은 역입니다'})
    except Exception as e:
        return jsonify({'error': str(e)})

# 제거한 지하철역을 삭제
@app.route('/delete/<station_name>/<line_name>', methods=['DELETE'])
def delete_station(station_name, line_name):
    station_name = station_name.lstrip()
    global stations
    stations = [(s, l) for s, l in stations if s != station_name or l != line_name]
    arrival_info = {f'{station[0]}({station[1]})': fetch_arrival_info(station[0], station[1]) for station in stations}
    return jsonify({'stations': stations, 'arrival_info': arrival_info})

# 도착정보를 반환
@app.route('/get_arrivals/<station>')
def get_arrivals(station):
    station_tuple = next((s for s in stations if s[0] == station), None)
    if station_tuple:
        return jsonify(fetch_arrival_info(station_tuple[0], station_tuple[1]))
    else:
        return jsonify({'error': '역을 찾을 수 없습니다'})

# 자동완성
@app.route('/search_stations', methods=['GET'])
def search_stations():
    query = request.args.get('query', '')
    matches = [station for station in all_stations if query in station][:3]
    return jsonify({'stations': matches})

# 업데이트(60초)
# 1초마다 업데이트를 계획했지만 API 제한으로 60초로 설정
def update_arrival_times():
    while True:
        threading.Event().wait(60)
        updated_info = {}
        for station_tuple in stations:
            updated_info[f'{station_tuple[0]}({station_tuple[1]})'] = fetch_arrival_info(station_tuple[0], station_tuple[1])

if __name__ == '__main__':
    load_station_info()

    updater = threading.Thread(target=update_arrival_times)
    updater.daemon = True
    updater.start()

    app.run(debug=True)
