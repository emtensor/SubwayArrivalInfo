# 서울시 실시간 지하철 도착정보

## 목차
- [개요](#개요)
- [목적](#목적)
- [진행](#진행)
- [환경](#환경)
- [설명](#설명)

## 개요
서울시 실시간 지하철 도착정보를 제공하는 웹을 구현했습니다.</br>
서울시 열린데이터 광장의 서울시 지하철 실시간 도착정보를 조회합니다.</br>
http://data.seoul.go.kr/dataList/OA-12764/F/1/datasetView.do</br>

## 목적
- 원하는 지하철역만 추가하여 도착정보를 확인합니다.
- 추가한 지하철역의 도착정보를 통해 단기적 지하철 탑승 계획을 설립합니다.

## 진행
- 기간: 3주
- 개인 프로젝트

## 환경
- 언어: Python, HTML
- 프레임워크: Flask

## 설명
### 파일
- app.py: 메인 파일
- index.html: UI를 정의한 파일
- info.xlsx: 지하철역의 호선 ID, 역 ID, 역 이름, 호선 정보를 포함한 파일

### 역 추가
검색창에 역을 입력할 때 자동완성 기능이 제공됩니다.</br>
![image](https://github.com/user-attachments/assets/bb282b56-4bb9-4303-a3e8-f3e391f8e7f6)</br>
역 이름을 입력하고 '+'버튼을 누르면 역이 추가되며, 도착정보를 확인할 수 있습니다.</br>
![image](https://github.com/user-attachments/assets/cc4c0016-0b80-4c62-a292-6df72fadbd4c)</br>
같은 역의 다른 호선 도착정보도 확인할 수 있습니다.</br>
![image](https://github.com/user-attachments/assets/ca79230e-b4cc-42c2-9175-56fd3c012c03)</br>

### 역 제거
'-'버튼을 눌러 역을 제거할 수 있습니다.

### 도착정보 갱신
60초 주기로 도착정보가 갱신됩니다.


