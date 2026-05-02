# simple-clock 프로젝트 작업 규칙

## 필수 워크플로우

이 프로젝트는 **반드시** 아래 방식으로만 작업한다.

### 실행 파이프라인
`deep-interview spec → ralplan (consensus) → autopilot execution`

### Phase 브랜치 전략
- 각 Phase는 **별도 브랜치**에서 작업한다
  - Phase 1: `phase/1-basic-exe`
  - Phase 2: `phase/2-window-behavior`
  - Phase 3: `phase/3-customizable-clock`
- 브랜치 내에서 작업 단위마다 커밋한다
- **Phase 완료 시 반드시 멈추고 사용자 확인을 받는다**
- 사용자 확인 후에만 `main`으로 머지하고 push한다
- 확인 없이 main 머지 또는 push 금지

### 확인 없이 절대 금지되는 행동
- `git merge` to main
- `git push` (어떤 브랜치든 main push는 확인 후만)
- 다음 Phase 작업 시작 (이전 Phase 확인 전)

## 프로젝트 스펙
- 스펙 파일: `.omc/specs/deep-interview-simple-clock.md`
- 스택: Python 3.11+ + PyQt6 + PyInstaller
- 설정 저장: `%APPDATA%\SimpleClock\config.json`

## Phase 정의
| Phase | 브랜치 | 내용 |
|-------|--------|------|
| 1 | `phase/1-basic-exe` | PyQt6 창 + "테스트" 텍스트 + PyInstaller EXE 빌드 |
| 2 | `phase/2-window-behavior` | 프레임리스, Alt+Tab 제외, 트레이 아이콘/컨텍스트 메뉴 |
| 3 | `phase/3-customizable-clock` | 시간 변수 텍스트박스, 커스터마이즈 다이얼로그, 설정 저장 |
