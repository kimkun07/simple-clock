# Deep Interview Spec: Windows 커스터마이즈 시계 앱

## Metadata
- Interview ID: di-simple-clock-001
- Rounds: 5
- Final Ambiguity Score: 18.2%
- Type: greenfield
- Generated: 2026-05-02
- Threshold: 0.2 (20%)
- Initial Context Summarized: no
- Status: PASSED

## Clarity Breakdown
| Dimension | Score | Weight | Weighted |
|-----------|-------|--------|----------|
| Goal Clarity | 0.83 | 40% | 0.332 |
| Constraint Clarity | 0.82 | 30% | 0.246 |
| Success Criteria | 0.80 | 30% | 0.240 |
| **Total Clarity** | | | **0.818** |
| **Ambiguity** | | | **18.2%** |

## Goal
타이틀바 없는 프레임리스 Windows 오버레이 시계 앱. 텍스트박스에 시간 포맷 변수(`{HH}`, `{mm}`, `{ss}`, `{YYYY}`, `{MM}`, `{DD}` 등)를 입력하면 실시간으로 현재 시간/날짜가 표시됨. 트레이 아이콘으로만 제어하며, EXE 배포 후 사용자가 자유롭게 레이아웃을 커스터마이즈할 수 있음.

## Tech Stack
- **언어/프레임워크:** Python 3.11+ + PyQt6
- **패키징:** PyInstaller (단독 실행 EXE)
- **설정 저장:** JSON 파일 (`%APPDATA%\SimpleClock\config.json`)
- **선택 근거:**
  - `FramelessWindowHint` → 타이틀바 제거
  - `Qt.WindowType.Tool` + Win32 `WS_EX_TOOLWINDOW` → Alt+Tab 제외
  - `QSystemTrayIcon` + `QMenu` → 트레이 컨텍스트 메뉴
  - `QTextEdit` HTML 렌더링 → 범위별 리치텍스트
  - `QTimer` → 초 단위 실시간 업데이트
  - PyInstaller → 의존성 없는 단독 EXE

## Constraints
- 창에 최소 크기 제한 없음 (사용자가 원하는 크기로 조절 가능)
- 타이틀바, 닫기/최소화/최대화 버튼 없음 (완전 프레임리스)
- Alt+Tab 창 전환 목록에서 제외 (`WS_EX_TOOLWINDOW` 스타일)
- 창 이동은 트레이 메뉴 "창 이동" 통해서만 가능 (클릭 후 마우스 위치로 이동)
- 시계 창에서 마우스 클릭은 시계가 수신 (커스터마이즈 모드에서 텍스트박스 선택 등)
- 설정은 `%APPDATA%\SimpleClock\config.json`에 자동 저장/로드

## Non-Goals
- 항상 최상위(Always-on-top) 고정 여부는 Phase 3에서 사용자 설정으로 결정
- 아날로그 시계 UI (디지털/텍스트 기반만)
- 클릭 투과(click-through) 기능 (시계가 클릭을 직접 수신)
- 원격 동기화, 알람, 타이머 기능
- macOS/Linux 지원

## Acceptance Criteria

### Phase 1: 기본 EXE
- [ ] `python main.py` 실행 시 "테스트" 텍스트가 포함된 창이 표시됨
- [ ] PyInstaller로 단독 실행 EXE 빌드 성공
- [ ] EXE 더블클릭 시 창이 표시됨

### Phase 2: 창 동작
- [ ] 창에 타이틀바, 닫기/최소화 버튼이 없음 (프레임리스)
- [ ] Alt+Tab 창 전환 목록에 시계가 나타나지 않음
- [ ] 작업 표시줄 트레이에 아이콘이 표시됨
- [ ] 트레이 아이콘 우클릭 시 컨텍스트 메뉴 표시: "창 이동", "커스터마이즈", "종료"
- [ ] "종료" 선택 시 앱 종료
- [ ] "창 이동" 선택 시 마우스 커서 위치로 창 이동
- [ ] 작업 표시줄에 창 버튼이 표시되지 않음

### Phase 3: 커스터마이즈 시계
- [ ] 텍스트박스에 `{HH}`, `{mm}`, `{ss}` 변수 입력 시 실시간(1초 간격) 업데이트
- [ ] 날짜 변수 `{YYYY}`, `{MM}`, `{DD}`, `{ddd}(요일)` 지원
- [ ] 텍스트박스 추가/삭제 가능 (개수 제한 없음)
- [ ] 텍스트박스 위치 자유롭게 설정 가능
- [ ] 텍스트박스 내 텍스트 전체 폰트 패밀리 설정 가능
- [ ] 텍스트박스 내 텍스트 전체 폰트 크기 설정 가능
- [ ] 텍스트박스 내 선택 범위별 색상, 굵기, 기울임 변경 가능
- [ ] 배경 색상 변경 가능 (단색)
- [ ] 설정이 `%APPDATA%\SimpleClock\config.json`에 저장되어 재시작 후에도 유지
- [ ] "커스터마이즈" 메뉴 선택 시 별도 설정 다이얼로그 창이 열림
- [ ] 설정 다이얼로그에서 변경 사항이 시계 창에 실시간 반영됨

## Assumptions Exposed & Resolved
| Assumption | Challenge | Resolution |
|------------|-----------|------------|
| 시계 = 별도 위젯 요소 | 텍스트박스에 시간 변수가 있으면 시계가 텍스트박스 자체 | 텍스트박스에 `{HH:mm:ss}` 형식 변수 사용, 시계 전용 요소 없음 |
| 창 이동 = 직접 드래그 | 타이틀바 없는 앱에서 드래그는 일반적이나, 사용 목적상 단순화 가능 | 트레이 메뉴 "창 이동" 통해서만 이동 |
| Formatted text = 리치텍스트 에디터 | 단일 스타일도 충분할 수 있음 | 전체 스타일 + 선택 범위 세밀 변경 (라이트 리치텍스트) |
| 커스터마이즈 = 인라인 편집 | 별도 다이얼로그가 더 명확한 UX | 별도 설정 다이얼로그 창 |

## Technical Context (Greenfield)
새 프로젝트. 기존 코드 없음. 의존성:
```
PyQt6>=6.6.0
PyInstaller>=6.0
```

빌드 명령: `pyinstaller --onefile --windowed --name SimpleClock main.py`

## Ontology (Key Entities)

| Entity | Type | Fields | Relationships |
|--------|------|--------|---------------|
| ClockWindow | core domain | size, position, background_color, always_on_top | contains TextBox[], owns TrayIcon |
| TextBox | core domain | id, x, y, width, height, content_template, base_font, base_size, rich_spans | belongs to ClockWindow |
| TrayIcon | supporting | icon_path, context_menu | owned by ClockWindow |
| CustomizeDialog | supporting | target_window, open_state | edits ClockWindow & TextBox[] |

## Ontology Convergence
| Round | Entity Count | New | Changed | Stable | Stability Ratio |
|-------|-------------|-----|---------|--------|----------------|
| 1 | 3 | 3 | - | - | N/A |
| 2 | 3 | 0 | 0 | 3 | 100% |
| 3 | 3 | 0 | 0 | 3 | 100% |
| 4 | 3 | 0 | 0 | 3 | 100% |
| 5 | 4 | 1 (CustomizeDialog) | 0 | 3 | 75% |

## Phase Implementation Plan

### Phase 1: 기본 EXE
- `main.py`: QApplication + QMainWindow + "테스트" QLabel
- PyInstaller 빌드 스크립트 작성

### Phase 2: 창 동작
- `FramelessWindowHint` 적용
- `WS_EX_TOOLWINDOW` Win32 스타일 설정 (Alt+Tab 제외)
- `QSystemTrayIcon` + `QMenu` ("창 이동", "커스터마이즈", "종료")
- "창 이동": `QApplication.instance().exec()` 루프에서 마우스 위치 추적 후 창 이동

### Phase 3: 커스터마이즈 시계
- `ClockWindow`: 배경색, TextBox 컬렉션, 설정 로드/저장
- `TextBox`: QLabel(HTML) + 시간 변수 치환 엔진
- 시간 변수 엔진: `{HH}`, `{mm}`, `{ss}`, `{YYYY}`, `{MM}`, `{DD}`, `{ddd}` → `QTimer` 1초 업데이트
- `CustomizeDialog`: QDialog, 텍스트박스 추가/삭제/편집, 배경색 선택, 위치 설정
- 설정 저장: `json.dump()` → `%APPDATA%\SimpleClock\config.json`

## Interview Transcript
<details>
<summary>Full Q&A (5 rounds)</summary>

### Round 1
**Q:** 텍스트 박스가 현재 시간을 동적으로 표시할 수 있어야 하나요? (시간 변수 포함 여부)
**A:** 시간 변수 포함 — `{HH:mm:ss}` 형식 변수가 실시간 업데이트됨
**Ambiguity:** 37.5% (Goal: 0.70, Constraints: 0.60, Criteria: 0.55)

### Round 2
**Q:** 타이틀바 없는 시계 창을 어떻게 이동할 수 있어야 하나요?
**A:** 트레이 메뉴 통해서만
**Ambiguity:** 32.2% (Goal: 0.72, Constraints: 0.72, Criteria: 0.58)

### Round 3
**Q:** 텍스트 박스의 '포맷' 지원 범위는 어떻게 되어야 하나요?
**A:** 단일 스타일 + 범위 선택 시 세밀 변경
**Ambiguity:** 28% (Goal: 0.75, Constraints: 0.72, Criteria: 0.68)

### Round 4 [Contrarian Mode]
**Q:** 시계 창이 화면에 있을 때, 시계 위에서 마우스를 클릭하면 어떻게 되어야 하나요?
**A:** 시계가 클릭 받음
**Ambiguity:** 23.2% (Goal: 0.78, Constraints: 0.80, Criteria: 0.72)

### Round 5 [Contrarian Mode]
**Q:** 트레이의 '커스터마이즈' 메뉴를 누르면 어떻게 동작해야 하나요?
**A:** 별도 설정 다이얼로그
**Ambiguity:** 18.2% (Goal: 0.83, Constraints: 0.82, Criteria: 0.80)

</details>
