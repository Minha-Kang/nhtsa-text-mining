# 신고 글에서 어떤 증상을 찾았나요?

신고 글에 ‘시동이 꺼졌다’, ‘브레이크가 작동하지 않았다’ 같은 표현이 있으면 해당 증상을 표시합니다. 영어 원문을 23가지 문장 규칙으로 확인했습니다.

예를 들어 ‘The engine stalled’에는 시동 꺼짐을 표시하지만, ‘The engine did not stall’에는 표시하지 않습니다. ‘에어백이 터지지 않았다’처럼 부정 표현 자체가 문제 증상인 경우도 따로 구분합니다. 이 문장들은 원리 설명용 예시입니다.

한 글에 여러 증상이 붙을 수 있습니다. 무엇을 보고 분류했는지 근거 문구도 남깁니다. 규칙이 증상을 찾지 못하면 미분류로 둡니다. **미분류는 정상이라는 뜻이 아닙니다.**

전체 1,603,647건 중 572,867건에서 하나 이상의 규칙 근거를 찾았습니다. 사용 가능한 본문이 있지만 매칭되지 않은 것은 1,030,766건, 사용 가능한 본문이 없는 것은 14건입니다.

**사람이 전체 문장을 검토한 전문가 진단은 아닙니다.** 복잡한 부정 표현·가정·다른 차량 이야기 등을 잘못 읽을 수 있습니다. 이 결과는 월별로 세어 X에 넣는 정보이며, 리콜 y와 별개입니다. [라벨링 전체 설명](../LABELING_GUIDE.md)

## 23개 증상 유형

아래 건수는 각 유형의 규칙 근거가 발견된 **민원 ID 수**입니다. 한 민원에 여러 유형이 함께 붙을 수 있으므로 행별 건수를 합산해 전체 민원 수로 해석하면 안 됩니다. 영어 예시는 실제 민원에서 채택된 짧은 규칙 근거이며, 전체 문맥과 민원 ID는 [감사 예시](audit_examples.json)에 있습니다.

| 모드 ID | 한국어 증상명 | 실제 규칙 근거 예시 | 민원 수 |
|---|---|---|---:|
| `engine_stall` | 주행·작동 중 시동 꺼짐 | `STALL` | 122,581 |
| `failure_to_start` | 시동·재시동 불가 | `CAR WOULD NOT START` | 30,559 |
| `reduced_engine_power` | 엔진·추진 출력 저하 또는 상실 | `VEHICLE COMPLETELY LOSES POWER` | 22,721 |
| `unintended_acceleration` | 의도하지 않은 가속·급격한 전진 | `VEHICLE SURGES` | 20,918 |
| `loss_of_braking` | 제동 기능 저하·상실 | `ABS BRAKING SYSTEM FAILED` | 56,329 |
| `unintended_braking` | 의도하지 않은 제동·브레이크 잠김 | `ABS BRAKE SYSTEM LOCKED UP` | 12,456 |
| `steering_loss` | 조향·조향 보조 상실 또는 조작 곤란 | `DIFFICULT TO STEER` | 65,107 |
| `transmission_shift_failure` | 변속 불량·미끄러짐·충격 | `TRANSMISSION JERKS` | 50,589 |
| `fluid_leak` | 연료·오일·냉각수 등 차량 유체 누출 | `OIL LEAK` | 47,080 |
| `overheating` | 엔진·배터리·차량 부품 과열 | `OVERHEAT` | 18,301 |
| `fire_smoke` | 화재·불꽃·연기 발생 | `CAUSING FIRE` | 44,771 |
| `airbag_non_deployment` | 에어백 미전개 | `AIRBAGS DID NOT DEPLOY` | 26,397 |
| `unintended_airbag_deployment` | 의도하지 않은 에어백 전개 | `AIR BAG UNEXPECTEDLY DEPLOYED` | 1,597 |
| `electrical_power_loss` | 전기 공급 상실·배터리 방전 | `BATTERY GOES DEAD` | 6,861 |
| `tire_failure` | 타이어 파열·트레드 분리·공기압 상실 | `TIRE SIDEWALL BLEW` | 18,216 |
| `wheel_detachment` | 주행 바퀴·휠 이탈 | `WHEEL TO DETACH` | 2,959 |
| `suspension_failure` | 현가·관련 연결 부품 파손 또는 기능 실패 | `STRUT FAILED` | 16,153 |
| `restraint_failure` | 안전벨트·버클·구속장치 기능 실패 | `SEAT BELTS FAILED` | 12,424 |
| `visibility_failure` | 와이퍼·유리·김서림 관련 시야 문제 | `WINDOW SHATTERED` | 20,803 |
| `lighting_failure` | 전조등·후미등·방향지시등 등 작동 불량 | `HEADLIGHTS FLICKER` | 17,811 |
| `door_latch_failure` | 문·후드·트렁크 잠금 불량 또는 비의도 개방 | `DOOR WILL NOT CLOSE AT ALL AND IT WILL NOT LATCH` | 4,877 |
| `rough_running` | 엔진 부조·실화·주저 반응 | `VEHICLE BEGAN HESITATING` | 18,707 |
| `abnormal_vibration` | 차량·조향계의 비정상 진동·떨림 | `VEHICLE VIBRATES` | 39,784 |

## 필드와 미분류 해석

- `failure_modes`: 해당 민원에서 규칙 근거가 발견된 모든 유형입니다. 복수 유형을 허용합니다.
- `fm_<모드 ID>`: 해당 유형의 근거가 있으면 `1`, 채택된 근거가 없으면 `0`입니다. **`0`은 증상이 없다는 확인이 아닙니다.**
- `mode_count`: 유형 수입니다. 본문은 있으나 일치 규칙이 없으면 `classification_status = no_forced_class`, 사용 가능한 본문이 없으면 `no_usable_text`입니다. 두 경우 모두 유형을 억지로 부여하지 않습니다.
- `primary_failure_mode`: 유형이 정확히 하나일 때만 그 값을 넣습니다. 0개 또는 2개 이상이면 `null`입니다. 심각도 순위나 대표 원인을 추정한 필드가 아닙니다.
- `evidence`: 채택한 규칙 ID, 근거 구절, 본문 변형 번호를 기록합니다. 같은 유형이라도 상충하는 본문 변형별 근거를 보존합니다.

## 본문 충돌과 분석용 제외 기준

`has_text_conflict = true`인 **13,144개 민원**에서는 서로 다른 사용 가능한 본문 **43,322개**를 각각 분류한 뒤 유형의 합집합을 저장했습니다. 이 중 **6,794개 민원**은 본문 변형마다 얻은 유형 집합이 달랐습니다. 합집합은 상충하는 주장 중 무엇이 사실인지 결정한 결과가 아닙니다. 충돌 자료는 `text_conflict_classified` 또는 `text_conflict_no_forced_class` 상태로 구별됩니다.

충돌의 영향을 확인하려면 전체 자료 결과와 함께 **`has_text_conflict = false`인 민원만 남기는 분석용 마스크**를 적용한 결과를 비교할 수 있습니다. 이때 분자와 분모에 같은 제외 기준을 적용해야 합니다. 충돌 자료의 `primary_failure_mode`가 채워져 있더라도 확정 진단으로 해석하면 안 됩니다. 본문 충돌을 해소하지 않은 상태에서 임의의 대표 유형을 새로 선택하지 않습니다.

## 부정 표현과 검증 범위

`no fire`처럼 발생을 부정하는 표현은 제외하고, `airbag did not deploy`처럼 필요한 작동의 부재를 말하는 표현은 에어백 미전개 근거로 인정합니다. `no warning`은 고장 자체를 부정하지 않습니다. `airbag did not deploy unexpectedly`처럼 의도하지 않은 전개만 부정하는 모호한 문장은 미전개로 강제 분류하지 않습니다.

**54개 합성 문장 검사**와 전체 출력의 ID 중복·0/1 값·유형 수·단일 유형 필드 검사를 통과했습니다. 이는 규칙 동작과 파일 무결성 검사이며, **실제 민원에 대한 측정 정확도·정밀도·재현율이 아닙니다.** 복잡한 부정·가정·과거 수리·타 차량 언급은 여전히 오분류를 일으킬 수 있습니다. 실제 데이터 예시도 독립적인 전문가 정답 집합이 아닙니다.

정확한 규칙은 [taxonomy.json](taxonomy.json), 집계와 한계는 [report.json](report.json), 재실행 코드는 [classify_failure_modes.py](classify_failure_modes.py)를 참고하세요.
