> **⚠️ 주의:** 이 프로젝트는 AI(Claude)로 작업한 결과물입니다. 제대로 실행이 안 되거나 버그가 존재할 수 있습니다.

# SimpleClock

커스터마이즈 가능한 시계 프로그램입니다.

<img width="1440" height="285" alt="image" src="https://github.com/user-attachments/assets/07e176ff-d40b-4a03-a94c-bd397165610b" />


**커스터마이즈 메뉴**
<img width="771" height="487" alt="image" src="https://github.com/user-attachments/assets/608bc755-6178-4b5e-a1c6-d2d00e4a7b1a" />


**윈도우 창 최소 크기 없음**
<img width="187" height="150" alt="image" src="https://github.com/user-attachments/assets/d19f2ebd-3aee-4248-91d7-6cfb78787bd2" />


## 설치

[GitHub Releases](https://github.com/kimkun07/simple-clock/releases) 에서 최신 `SimpleClock.exe`를 받아 실행하세요.

## 주요 기능

### 커스터마이즈

우측 하단 `☰` 버튼을 눌러 설정 창을 엽니다.

설정은 `%APPDATA%\SimpleClock\config.json`에 자동 저장됩니다.

### 시간 변수 텍스트박스

템플릿 텍스트에 변수를 삽입하면 자동으로 현재 시각으로 치환됩니다.

| 입력 예시 | 출력 예시 | 설명 |
|------|---------|------|
| `{HH}:{mm}:{ss}` | `09:07:03` | 시/분/초 (0 패딩) |
| `{H}:{m}:{s}` | `9:7:3` | 시/분/초 (패딩 없음) |
| `{YYYY}-{MM}-{DD}` | `2026-05-04` | 연/월/일 (0 패딩) |
| `{M}/{D}` | `5/4` | 월/일 (패딩 없음) |
| `{YY}` | `26` | 연도 2자리 |
| `{ddd}` | `Mon` | 영문 요일 축약 |
| `{KW}` | `월` | 한국어 요일 |

