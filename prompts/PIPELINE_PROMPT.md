# Academic Sermon Insight AI Agent Pipeline Prompt

다음 성경 본문에 대해 `examples/hebrews8_sermon_insight/`와 동일한 품질의 학술 주해 및 강해 설교 개요 패키지를 생성하십시오.

## 1. 사전 스캐폴딩
```bash
sermon-insight init "{성경본문}" --out .
```

## 2. 영미권·독일어권 학술 문헌 수집 및 실증
- 영미권 최소 5편 + 독일어권 최소 5편(권장 각 10편) 수집
- 모든 문헌은 `sermon-insight search` 또는 CrossRef/IxTheo/DNB를 통해 실재 DOI/ISBN을 확인
- 사료 진위 3등급제(`[1등급: 원문 전문 확보]`, `[2등급: 초록·서지 확인]`) 엄격 구분

## 3. 5대 마크다운 헌법 준수
- 이탤릭(`*...*`, `_..._`) 금지
- 볼드 괄호 분리: `**단어**(설명)`
- 볼드 내부 공백 금지
- 엠대시(`—`) 금지 -> 하이픈(`-`) 사용
- 학술 보고서(평어체 `-다/-함`)와 설교 개요서(구어체 `-합니다/-하십시오`) 문체 분리

## 4. 자동 정량 감사 및 린트
```bash
sermon-insight lint {폴더} --fix
sermon-insight audit {폴더} --write-report
```
모든 항목이 `CLEAN` 판정을 받을 때까지 보완한 뒤, 2차 정성 검수 보고서(`*_QUALITATIVE_REVIEW_REPORT.md`)와 독립 강해 설교 개요서(`*_SERMON_OUTLINE.md`, 3대지 8소지 4분법 + 1:1 교차 매핑표)를 완결하십시오.
