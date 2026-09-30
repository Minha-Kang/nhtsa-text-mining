# 신고 글에서 찾은 16개 주제는 무엇인가요?

비슷한 단어들이 함께 반복되는 패턴을 찾은 것입니다. 예를 들어 steering·wheel 같은 표현이 묶이면 조향 관련 주제로 해석합니다.

글을 TF-IDF라는 숫자 표현으로 바꾼 뒤, 과거 훈련 기간의 글 15만 건에 NMF를 적용해 16개 주제를 찾았습니다. 각 주제의 비중이 큰 단어를 읽고 아래처럼 설명용 이름을 붙였습니다. 완성된 변환기는 전체 신고에 적용했습니다.

**16개는 탐색용으로 정한 수이며 여러 개수를 비교해 최적이라고 검증한 값은 아닙니다.** 실제 고장 종류가 정확히 16개라는 뜻도 아닙니다. 문의나 행정 내용, 여러 증상이 섞인 주제도 있습니다.

한 글에 여러 주제의 비중이 함께 나올 수 있습니다. 이 비중을 월별로 평균 내 X의 일부로 사용합니다. 리콜 여부 y나 전문가 고장 진단으로 사용하지 않습니다.

표의 mixed는 여러 내용이 섞였다는 뜻, administrative_mixed는 문의·행정 내용도 포함한다는 뜻, component_symptom은 부품·증상 관련 단어가 중심이라는 뜻입니다.

| 토픽 | 검토용 이름 | 대표 단어 | 성격 |
|---|---|---|---|
| 0 | 일반적인 문제·불만 서술 | problem, not, would, no, could, issue, time, said | mixed |
| 1 | 에어백 관련 문의·문제 인지 | air bags, bags, issue not, aware issue, time, air, issue, aware | administrative_mixed |
| 2 | 에어백·경고등 | bag, air bag, air, light, bag light, passenger, bag warning, illuminated | component_symptom |
| 3 | 조향·파워 스티어링 | steering, power steering, power, wheel, steering wheel, turn, column, steering column | component_symptom |
| 4 | 브레이크·제동 | brake, brakes, pedal, brake pedal, abs, stop, floor, rotors | component_symptom |
| 5 | 주행 중 이상·정비 서술 | taken, driving mph, mph, driving, warning, not, needed, needed replaced | mixed |
| 6 | 좌석·안전벨트 | seat, belt, seat belt, driver, driver seat, passenger, passenger seat, buckle | component_symptom |
| 7 | 연료 탱크·펌프·누유 | fuel, tank, gas, fuel tank, pump, fuel pump, gas tank, gauge | component_symptom |
| 8 | 충돌 시 에어백 미전개 | did not, deploy, did, not deploy, bags, air bags, bags did, air | component_symptom |
| 9 | 변속기·기어 변환 | transmission, gear, shift, transmission failed, automatic, automatic transmission, shifting, gears | component_symptom |
| 10 | 타이어·트레드 | tire, tires, rear, tread, dot, size, firestone, right | component_symptom |
| 11 | 여러 부품의 고장 서술 | failed, brakes failed, transmission failed, failed causing, causing, brakes, failed times, failed deploy | mixed |
| 12 | 도어·창문·잠금 | door, open, driver, doors, passenger, driver door, lock, rear | component_symptom |
| 13 | 엔진·오일·경고등 | engine, light, engine light, check, oil, check engine, came, light came | component_symptom |
| 14 | 다카타 에어백 관련 신고 | takata, airbag, tool confirms, confirms, confirms not, tool, not tool, ford | administrative_mixed |
| 15 | 점화장치·와이퍼·전기 계통 | ignition, switch, windshield, ignition switch, wipers, key, windshield wipers, turn | mixed |

고장 증상 분류는 별도의 23개 설명 가능한 규칙으로 수행합니다. 토픽 최대 가중치를 고장 유형 정답이나 확률로 해석하지 않습니다.

학습: TF-IDF는 2018-12-31까지의 유효 신고 전체에 적합하고, NMF/SVD는 그중 고정 난수로 뽑은 150,000건에 적합했습니다. 전체 1,603,647건을 변환했으며 충돌·빈 문장·내용 없는 서식 문구는 표시하고 벡터를 비워 두었습니다.

32차원 SVD는 전체 단어 공간의 일부만 압축한 선택지입니다. 원래 30,000차원 TF-IDF 희소 행렬도 `tfidf/`에 제공하므로 차원 축소에 따른 정보 손실 없이 다른 표현을 선택할 수 있습니다.
