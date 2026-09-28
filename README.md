# NHTSA 신고 텍스트 정제 및 리콜 후보 연결 데이터

차량 결함 신고 텍스트를 정제하고, 차량 조건·부품·설명문을 비교해 관련 리콜 후보를 연결한 데이터셋입니다.

## 데이터 다운로드

**[전체 데이터 받기 — Releases](https://github.com/Minha-Kang/nhtsa-text-mining/releases/tag/dataset-2026-09-28)**

전체 ZIP은 약 3.69 GB로, GitHub 첨부 크기 제한에 맞춰 두 조각으로 나누었습니다. 아래 세 파일을 같은 폴더에 받은 뒤 실행하세요.

- `nhtsa_text_mining_complete.zip.001`
- `nhtsa_text_mining_complete.zip.002`
- `restore_zip.py`

```bash
python restore_zip.py
```

Python 표준 라이브러리만 사용합니다. 원래의 `nhtsa_text_mining_complete.zip`을 복원하고 SHA-256으로 무결성을 확인합니다. 분할 조각은 각각 독립적으로 압축 해제할 수 없습니다. GitHub의 자동 생성 `Source code (zip)`에는 대용량 데이터가 포함되지 않습니다.

## 포함 자료

| 경로 | 내용 |
|---|---|
| `raw/` | 공식 NHTSA 신고·리콜 원본과 데이터 사전 |
| `processed/` | 정제한 신고 텍스트, 차량 신고, 리콜 데이터와 검증 결과 |
| `linked/` | 신고–리콜 통합표, 전체 후보 연결표, 연결 근거와 검증 결과 |
| Python 코드·설명서 | 정제·연결·읽기 코드, 재현에 필요한 패키지, 작업 인계 문서 |

- 정제 차량 신고: **1,603,647건**, 통합표에서도 전체 보존
- 차량 조건에 맞는 리콜 후보가 있는 신고: **1,449,513건**
- 부품 일치 근거가 있는 신고: **623,285건**
- 전체 신고–리콜 후보 쌍: **8,164,815쌍**
- 원본 ZIP 내부 파일: **46개**

주요 파일은 `processed/vehicle_complaints.parquet`, `linked/complaints_with_recall.parquet`, `linked/complaint_recall_candidates.parquet`입니다.

## 반드시 확인할 해석 범위

**연결된 리콜은 관련 후보이며, 해당 신고 차량이 실제 리콜 대상이었다는 확정 정답이 아닙니다. 연결을 1, 미연결을 0으로 바로 사용하면 안 됩니다.**

신고 번호 `odi_number`와 리콜 번호 `CAMPNO` 사이에 공통 신고 키가 없어 제조사·모델·연식, 부품 일치와 설명문 유사도를 비교했습니다. 차량 생산 범위·개별 VIN의 리콜 해당 여부는 확인하지 않았습니다. 후보 개수나 연결률은 매칭 정확도가 아닙니다.

예측 모델의 학습용 정답은 예측 단위·기간·관찰 범위를 먼저 정하고 공식 리콜 기록으로 별도 구성해야 합니다. 리콜 후보 정보를 담은 `_link_` 열은 예측 입력에서 제외해야 합니다. 상세 설명은 ZIP 내부 `HANDOFF.md`, `linked/JOINED_DATA_GUIDE.md`에 있습니다.

## 출처

[NHTSA Datasets and APIs](https://www.nhtsa.gov/nhtsa-datasets-and-apis)의 공개 신고·리콜 자료를 사용했습니다. 작업본 날짜는 2026-09-28입니다.
