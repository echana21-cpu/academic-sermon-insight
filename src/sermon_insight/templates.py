"""Project scaffolding and Markdown templates for sermon insight pipelines."""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

from sermon_insight.books import PassageRef


def render_dashboard(passage: PassageRef) -> str:
    """Render initial ``DASHBOARD.md`` milestone tracker."""
    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    prefix = passage.prefix_upper
    return f"""# {passage.title_ko} ({passage.title_en}) 연구 공정 대시보드

* **프로젝트 폴더**: `{passage.folder_name}`
* **생성 시각**: {now}
* **현재 상태**: `M0_INITIALIZED`

---

## 마일스톤 진행 현황

| 단계 | 작업 내용 | 산출물 파일 | 상태 |
| :--- | :--- | :--- | :--- |
| **M0** | 프로젝트 스캐폴딩 및 대시보드 생성 | `DASHBOARD.md` | **완료** |
| **M1** | 영미·독일 학술 문헌 탐색 및 주해 보고서 집필 | `{prefix}_ACADEMIC_ANALYSIS_REPORT.md` | 대기 |
| **M2** | 1차 정량 포렌식 서지 감사 (CrossRef/ISBN/린트) | `{prefix}_QUANTITATIVE_AUDIT_REPORT.md` | 대기 |
| **M3** | 2차 정성 신학·설교 검수 (6대 루브릭) | `{prefix}_QUALITATIVE_REVIEW_REPORT.md` | 대기 |
| **M4** | 독립 강해 설교 개요서 집필 (3대지 8소지 4분법) | `{prefix}_SERMON_OUTLINE.md` | 대기 |
| **M5** | 최종 승리 감사 (Victory Audit) 및 린트 0건 확정 | 전체 파일 | 대기 |

---

## 실행 명령어 안내

```bash
# 1. 학술 문헌 검색 (CrossRef / OpenAlex)
sermon-insight search "{passage.title_en}" --rows 10

# 2. DOI 실존 여부 단건 검증
sermon-insight verify-doi 10.1163/ej.9789004206519.i-338

# 3. 마크다운 헌법 5대 규칙 린트 (자동 수정 포함)
sermon-insight lint . --fix

# 4. 1차 정량 포렌식 감사 실행 및 보고서 자동 생성
sermon-insight audit . --write-report
```
"""


def render_academic_report_template(passage: PassageRef) -> str:
    """Render structured template for ``*_ACADEMIC_ANALYSIS_REPORT.md``."""
    return f"""# {passage.title_ko} 학술 주해 및 신학적 쟁점 종합 분석 보고서: 영미권 및 독일어권 연구 지형의 통합

## 1. 개요 및 연구 방법론

### 1.1 연구 배경 및 목적
{passage.title_ko}({passage.title_en})의 원어 구문, 구속사적 문맥, 신학적 쟁점을 영미권 및 독일어권 동료 심사(Peer-reviewed) 학술 문헌을 통해 종합 분석한다.

### 1.2 학술 저수지 및 사료 비평 규격
- **영미권 저수지**: Google Scholar, CrossRef, OpenAlex, JSTOR 등 공인 학술 데이터베이스.
- **독일어권 저수지**: IxTheo(튀빙겐), DNB(독일국립도서관), Mohr Siebeck, Vandenhoeck & Ruprecht 등.
- [**1등급: 원문 전문 확보**]: 원문 전문 PDF 및 단행본 실물 대조 완료 문헌.
- [**2등급: 초록·서지 확인**]: 공식 출판사 카탈로그 및 CrossRef/DNB 메타데이터 실증 문헌.

---

## 2. 서지 및 사료 레지스트리 (Bibliographic Registry)

### 2.1 전체 학술 문헌 종합 총괄표

| 번호 | 언어권 | 저자 | 저작/논문 제목 | 수록 학술지 및 단행본 | 권:호 (연도): 쪽수 | 공인 식별자 (DOI / ISBN / URL) | 사료 등급 |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| 1 | 영어권 | Author A | Title A | Journal A | 1:1 (2020): 1-20 | DOI: 10.0000/placeholder | [2등급: 초록·서지 확인] |

### 2.2 문헌별 상세 서지 카드 및 Chicago 인용

---

## 3. {passage.title_ko} 핵심 쟁점 심층 주해 및 신학적 분석

### 3.1 전반부 주해

### 3.2 후반부 주해

---

## 4. 영미권 및 독일어권 학술 논쟁 매트릭스 (Controversy Matrix)

### 4.1 5대 핵심 신학 쟁점 논쟁 매트릭스 총괄표

### 4.2 쟁점별 세부 학술 논쟁 심층 분석 (스틸맨 복원)

---

## 5. 신학적 종합 및 설교 가교를 위한 주해적 기초 (Theological Synthesis & Homiletical Foundations)

### 5.1 해석 층위 간 단계별 추론 보증 (Warrant Bridging across Strata)

### 5.2 현대 성도의 실존적 위기와 목회적 해답

---

## 6. 사료 검증 및 자체 학술 감사 대조표 (Verification & Audit Ledger)

### 6.1 사료 전수 실사 대조표

### 6.2 가상 사료 및 스텁 부재 인증

---

## 7. 결론
"""


def render_quantitative_audit_template(passage: PassageRef) -> str:
    """Render initial pending template for ``*_QUANTITATIVE_AUDIT_REPORT.md``."""
    return f"""# {passage.title_ko} 학술 보고서 및 설교 개요 1차 정량 검수 보고서 (Stage 1 Quantitative Forensic Audit)

* **검수 상태**: `PENDING` (`sermon-insight audit . --write-report` 실행 전)

---

## 1. 종합 판정 결과 (Formal Verdict)

**최종 판정: 대기 중**(PENDING)

---

## 2. 4대 정량 검증 영역별 실사 결과 요약

| 검증 영역 | 점검 항목 및 기준 | 실사 도구 및 방법 | 판정 결과 |
| :--- | :--- | :--- | :--- |
| **1. 서지 완전성 및 인용 진위** | 영·독 학술 문헌 전수 대조, 환각 서지 0건 | CrossRef REST API / ISBN 체크섬 | 대기 |
| **2. 사료 진위 3등급제 준수** | 1등급(전문 확보) / 2등급(초록 확인) 구분 표기 | 메타데이터 및 스텁 탐색 | 대기 |
| **3. 언어별 문헌 수 쿼터** | 영어권 5편 이상, 독일어권 5편 이상 | 언어 태그 분석 | 대기 |
| **4. 파일 실재성 및 린트** | 마크다운 5대 헌법 준수 0 에러 | `sermon-insight lint` | 대기 |

---

## 3. 서지 완전성 및 인용 진위 포렌식 전수 실사 대조표
"""


def render_qualitative_review_template(passage: PassageRef) -> str:
    """Render structured template for ``*_QUALITATIVE_REVIEW_REPORT.md``."""
    return f"""# {passage.title_ko} 학술 보고서 및 설교 개요 2차 정성 검수 보고서 (Stage 2 Qualitative Academic & Homiletical Audit)

* **검수 상태**: `PENDING`

---

## 1. 공식 판정 결과 (Formal Verdict)

**최종 판정: 검수 대기**(PENDING)

---

## 2. 6대 정성 학술·설교 감사 루브릭별 실사 평가 총괄표

| 정성 감사 축 | 핵심 감사 질문 및 기준 | 대상 문서 반영 현황 및 실사 결과 | 세부 평가 |
| :--- | :--- | :--- | :--- |
| **1. 불리한 본문 단서 검토** | 유리한 구절만 취사선택하지 않고 까다로운 반례 단서를 다루었는가? | 점검 예정 | 대기 |
| **2. 층위 간 추론 보증** | 원어 구문(1층위)에서 설교 적용(5층위)으로의 비약 없는 매개 논증이 확립되었는가? | 점검 예정 | 대기 |
| **3. 경쟁 학설의 공정한 복원** | 반대 학설을 허수아비로 만들지 않고 최상의 논거(Steel-man)로 다루었는가? | 점검 예정 | 대기 |
| **4. 인용 맥락과 양상 보존** | 원저자의 한정어와 연구 맥락을 왜곡 없이 유지하고 사료 등급을 준수하였는가? | 점검 예정 | 대기 |
| **5. 아포리아 및 긴장 보존** | 본문의 신학적 난제와 긴장을 조기 봉합하지 않고 정직하게 남겨두었는가? | 점검 예정 | 대기 |
| **6. 설교적 타당성 및 실용성** | 독립 파일 완성도, 실존적 문제 해명, 1:1 교차 매핑표 완비 여부 | 점검 예정 | 대기 |

---

## 3. 6대 정성 감사 루브릭 세부 심사 내역

---

## 4. 적대적 스트레스 테스트 및 반론 검토 (Adversarial Stress Testing)

---

## 5. 목회 강단 선포를 위한 최종 권고 및 제언
"""


def render_sermon_outline_template(passage: PassageRef) -> str:
    """Render structured template for ``*_SERMON_OUTLINE.md``."""
    return f"""# {passage.title_ko} 독립 강해 설교 개요: 제목을 입력하세요

* **설교 본문**: {passage.title_ko} ({passage.title_en})
* **설교 제목**: 제목을 입력하세요
* **문서 성격**: 학술 주해 보고서와 완전히 분리된 목회 현장 강단 선포용 독립 강해 설교 개요
* **적용 규격**: 한국어 설교 구어체 선포문 완비, 3대 대지 및 8개 소지, 1:1 교차 매핑표 완비

---

## 1. 설교 기본 정보 (Sermon Meta)

### 1.1 설교 개요 카드
* **설교 제목**: 제목을 입력하세요
* **성경 본문**: {passage.title_ko}
* **설교 형식**: 구속사적 강해 설교 (Expository Sermon)
* **예상 시간**: 35-40분
* **핵심 복음 선포**(Kerygma):
  > 핵심 복음 선포문을 작성하세요.

### 1.2 청중 프로파일 및 목회적 진단

---

## 2. 설교 서론 (Introduction)

### 2.1 주의 집중을 위한 도입 예화

### 2.2 성경 본문과의 문제 제기적 연결

### 2.3 중심 명제 (Central Proposition) 선포

---

## 3. 본론: 3대 대지(Point) 및 소지(Sub-point) 전개

### 제1대지: 첫 번째 대지 제목
> "대지 핵심 요약"

#### 소지 1: 소지 제목
* **원어 및 성경적 근거**:
* **목회적 해석 및 해설**:
* **일상적 비유**:
* **구어체 강단 선포문**:

#### 소지 2: 소지 제목
* **원어 및 성경적 근거**:
* **목회적 해석 및 해설**:
* **일상적 비유**:
* **구어체 강단 선포문**:

#### 소지 3: 소지 제목
* **원어 및 성경적 근거**:
* **목회적 해석 및 해설**:
* **일상적 비유**:
* **구어체 강단 선포문**:

### 제2대지: 두 번째 대지 제목
> "대지 핵심 요약"

#### 소지 4: 소지 제목
* **원어 및 성경적 근거**:
* **목회적 해석 및 해설**:
* **일상적 비유**:
* **구어체 강단 선포문**:

#### 소지 5: 소지 제목
* **원어 및 성경적 근거**:
* **목회적 해석 및 해설**:
* **일상적 비유**:
* **구어체 강단 선포문**:

### 제3대지: 세 번째 대지 제목
> "대지 핵심 요약"

#### 소지 6: 소지 제목
* **원어 및 성경적 근거**:
* **목회적 해석 및 해설**:
* **일상적 비유**:
* **구어체 강단 선포문**:

#### 소지 7: 소지 제목
* **원어 및 성경적 근거**:
* **목회적 해석 및 해설**:
* **일상적 비유**:
* **구어체 강단 선포문**:

#### 소지 8: 소지 제목
* **원어 및 성경적 근거**:
* **목회적 해석 및 해설**:
* **일상적 비유**:
* **구어체 강단 선포문**:

---

## 4. 설교 결론 (Conclusion) 및 결단 기도 / 축도적 파송

### 4.1 전체 설교 요약 및 마침 권면

### 4.2 성도들의 고백적 결단 기도문

### 4.3 목회적 축도 파송문 (Benediction)

---

## 5. 주해-설교 교차 매핑표 (Exegetical-to-Homiletical Cross-Reference Table)

| 본문 구절 | 핵심 원어 / 주해 요점 | 연결된 대지 및 소지 | 강단 적용 메시지 |
| :--- | :--- | :--- | :--- |
| 1절 | | 제1대지 소지 1 | |
"""


def scaffold_project(
    passage: PassageRef,
    base_dir: Path,
    overwrite: bool = False,
) -> list[Path]:
    """Create a standardized sermon insight project folder and 5 Markdown files."""
    project_dir = base_dir / passage.folder_name
    project_dir.mkdir(parents=True, exist_ok=True)
    prefix = passage.prefix_upper

    files: dict[str, str] = {
        "DASHBOARD.md": render_dashboard(passage),
        f"{prefix}_ACADEMIC_ANALYSIS_REPORT.md": render_academic_report_template(passage),
        f"{prefix}_QUANTITATIVE_AUDIT_REPORT.md": render_quantitative_audit_template(passage),
        f"{prefix}_QUALITATIVE_REVIEW_REPORT.md": render_qualitative_review_template(passage),
        f"{prefix}_SERMON_OUTLINE.md": render_sermon_outline_template(passage),
    }

    written: list[Path] = []
    for filename, content in files.items():
        path = project_dir / filename
        if path.exists() and not overwrite:
            raise FileExistsError(f"File already exists (use --force to overwrite): {path}")
        path.write_text(content, encoding="utf-8")
        written.append(path)

    return written
