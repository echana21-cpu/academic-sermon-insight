# Academic Sermon Insight Pipeline (`sermon-insight`)

성경 본문(예: 히브리서 8장, 로마서 8장)에 대해 **영미권·독일어권 학술 문헌 탐색 및 실존 검증**, **1차 정량 포렌식 서지 감사**, **5대 마크다운 헌법 린트**, **2차 정성 신학 검수**, 그리고 **3대 대지 8개 소지 4분법 강해 설교 개요** 산출물 세트를 표준화하여 반복 생산할 수 있는 Python CLI & 템플릿 파이프라인입니다.

`examples/hebrews8_sermon_insight/` 디렉터리에 실제 히브리서 8장 레퍼런스 샘플이 포함되어 있습니다.

## 주요 기능

1. **프로젝트 스캐폴딩 (`init`)**: 성경 66권(한글/영문/약어)을 인식해 `{book}{chapter}_sermon_insight/` 폴더와 `DASHBOARD.md` + 4대 보고서 템플릿을 즉시 생성합니다.
2. **국제 학술 저수지 검색 (`search`)**: CrossRef REST API 및 OpenAlex API를 조회하여 실재 논문·단행본 메타데이터와 시카고(Chicago) 양식 서지를 반환합니다.
3. **DOI / ISBN 실증 검증 (`verify-doi`, `verify-isbn`)**: CrossRef API로 DOI 실존 여부를 확인하고, ISBN-10/13 체크섬 및 OpenLibrary 메타데이터를 검증하여 **가상 서지(환각) 0건**을 보장합니다.
4. **5대 마크다운 헌법 린터 (`lint`)**:
   - 이탤릭체(`*...*`, `_..._`) 배제
   - 볼드 괄호 분리(`**단어**(설명)`)
   - 볼드 내부 공백 금지(`** 단어 **` 차단)
   - 엠대시(`—`) 금지 -> 하이픈(`-`) 통일 (`--fix` 자동 수정 지원)
   - 문서별 필수 목차 구조 검증
5. **1차 정량 포렌식 감사 (`audit`)**:
   - `*_ACADEMIC_ANALYSIS_REPORT.md`의 2.1절 서지 총괄표를 파싱하여 영·독 문헌 쿼터, 사료 3등급제, `.txt` 합성 스텁 부재, DOI/ISBN 유효성, 마크다운 린트 오류 0건을 검증하고 `*_QUANTITATIVE_AUDIT_REPORT.md`를 자동 생성합니다.

## 설치 방법

Python 3.9 이상에서 별도 외부 런타임 의존성 없이 바로 설치·실행할 수 있습니다.

```bash
git clone https://github.com/echana21-cpu/academic-sermon-insight.git
cd academic-sermon-insight
pip install -e ".[dev]"
```

## 빠른 시작 (Quick Start)

```bash
# 1. 새 성경 본문 프로젝트 생성 (예: 로마서 8장)
sermon-insight init "로마서 8장" --out ~/Desktop

# 2. 영미권/독일어권 학술 문헌 검색
sermon-insight search "Romans 8 Spirit adoption" --rows 10
sermon-insight search "Römer 8 Geist" --source openalex --rows 10

# 3. DOI 및 ISBN 검증
sermon-insight verify-doi 10.1163/ej.9789004206519.i-338
sermon-insight verify-isbn 978-3-16-133502-0

# 4. 히브리서 8장 샘플 프로젝트 검증 (오프라인 모드)
sermon-insight lint examples/hebrews8_sermon_insight
sermon-insight audit examples/hebrews8_sermon_insight --offline

# 5. 실제 네트워크 API로 DOI 전수 검증 및 감사 보고서 생성
sermon-insight audit ~/Desktop/romans8_sermon_insight --write-report
```

## 테스트 실행

```bash
pytest -v
```
