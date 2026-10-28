"""여러 턴 riff 켬/끔 비교 — AI 사용자가 숨은 사실을 '물어볼 때만' 답한다.

claude plugin eval에는 사용자 시뮬레이터가 없어서 claude -p 세션을 이어 붙인다.
격리: --setting-sources project,local(전역 설정·플러그인·훅·CLAUDE.md 제외) + 빈 작업 폴더.
사용: python3 benchmarks/multiturn.py --runs 1 --rounds 6 [--personas freelancer salon pilates]

비용: 켬/끔 각 3회 × 6라운드 실측 약 $15(2026-10-28). riff 켬 1회 ≈ $2.5~3.7, 끔 ≈ $1.6~2.8.
(10-23·10-28 실행은 누적 비용을 합산하는 버그로 $23.4·$82.6이 찍혔다 — 결과 JSON의 cost는 과대값.)
알려진 한계: AI 사용자가 묻지 않은 사실을 가끔 먼저 말한다(양쪽 모두 관찰).
판정기는 엄격해서 부분 반영(예: 계약금만 있고 50%·착수 조건 없음)은 false.
"""
import argparse, json, re, subprocess, sys, tempfile, time, uuid
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
FINAL = "이제 지금까지 정한 내용으로 최종 기획안(만들 기능·화면·데이터·규칙)을 한 번에 정리해서 보여주세요. 구현은 아직 하지 마세요."
# 고객 유형별 첫 요청 + AI 사용자만 아는 사실 8개. 사실은 '물어볼 때만' 답한다.
PERSONAS = {
    "freelancer": {
        "role": "앱 개발을 의뢰한 비개발자 프리랜서 디자이너",
        "opening": "프리랜서 디자이너인데 견적서 만들고 고객별로 진행 상태 관리하는 앱 하나 만들어주세요.",
        "facts": {
            "tax": "사업자등록을 안 한 프리랜서라 부가세가 없고, 고객이 3.3% 원천징수 후 입금한다",
            "package": "견적은 수량×단가가 아니라 패키지 고정가(로고 A/B/C 패키지) + 옵션 추가 방식이다",
            "deposit": "계약금 50%를 받아야 작업을 시작하고 잔금 50%는 납품 후 받는다",
            "revisions": "수정은 2회까지 포함이고 3회째부터 회당 5만원 추가 비용이다",
            "import": "지금 구글시트에 고객 약 120명이 있어서 그대로 옮겨와야 한다",
            "overseas": "고객의 30%가 해외라 영문 견적서와 달러 금액이 필요하다",
            "kakao": "견적서는 주로 카카오톡으로 이미지나 PDF로 보낸다(휴대폰에서 바로 공유)",
            "status-undo": "상태를 실수로 잘못 바꾼 적이 많아서 이전 상태로 되돌릴 수 있어야 한다",
        },
    },
    "salon": {
        "role": "앱 개발을 의뢰한 비개발자 동네 미용실 원장",
        "opening": "동네 미용실 하는데요, 예약이랑 노쇼 관리하는 앱 하나 만들어주세요.",
        "facts": {
            "designers": "디자이너가 3명이고 손님이 디자이너를 지정해서 예약한다",
            "duration": "시술마다 걸리는 시간이 다르다(커트 30분, 펌 2시간, 염색 1시간 반)",
            "channels": "네이버 예약과 카카오톡 문의가 섞여 들어와서 중복 예약이 자주 생긴다",
            "deposit": "펌·염색은 예약금 1만원을 받고, 당일 노쇼면 예약금을 돌려주지 않는다",
            "repeat-noshow": "노쇼를 2번 한 손님은 다음부터 모든 시술에 예약금을 받는다",
            "reminder": "예약 전날 문자로 알림을 보내고 싶다",
            "walk-in": "예약 없이 오는 손님도 하루 5명쯤 있어서 빈 시간에 끼워 넣는다",
            "import": "기존 손님 약 600명 연락처가 엑셀에 있다",
        },
    },
    "pilates": {
        "role": "앱 개발을 의뢰한 비개발자 필라테스 스튜디오 대표",
        "opening": "필라테스 스튜디오 운영하는데 회원이랑 수업 예약 관리하는 앱 하나 만들어주세요.",
        "facts": {
            "passes": "이용권은 10회권(유효 3개월)과 30회권(유효 6개월) 두 가지다",
            "hold": "출산·부상이면 최대 1개월까지 홀딩(일시정지)해 준다",
            "cancel": "수업 4시간 전까지만 취소 가능하고, 그 이후 취소나 노쇼는 1회 차감한다",
            "capacity": "그룹 수업 정원은 6명이고 꽉 차면 대기자를 받는다",
            "instructors": "강사 4명이 프리랜서라 강사별 진행 수업 수로 매달 정산한다",
            "refund": "중도 해지 시 위약금 10%를 공제하고 남은 횟수만큼 환불한다",
            "marketing": "생일 쿠폰이나 이벤트 문자를 회원에게 보내고 싶다",
            "import": "기존 회원 약 200명 정보가 엑셀에 있다",
        },
    },
}
USER_RULES = """규칙:
1. 상대가 물어본 것에만 답한다. 질문과 관련된 사실만 말하고, 묻지 않은 사실은 절대 먼저 말하지 않는다.
2. 질문이 위 사실과 무관하면 "잘 모르겠어요, 알아서 정해주세요"라고 답한다.
3. 선택지를 주면 사실에 맞는 것을 고른다. 사실과 무관한 선택지면 추천안을 고른다.
4. 플러그인·도구 설치나 설정을 물으면 "건너뛸게요"라고 답한다.
5. 기획안 확인·승인을 요청하면 "네 좋아요, 그대로 진행해주세요"라고 답한다(묻지 않은 사실은 덧붙이지 않는다).
6. 1~3문장, 비개발자 말투, 한국어. 당신의 답변 텍스트만 출력한다."""


def user_system(persona):
    facts = PERSONAS[persona]["facts"].values()
    return f"당신은 {PERSONAS[persona]['role']}이다. 아래 사실을 알고 있다.\n" + "\n".join("- " + v for v in facts) + "\n" + USER_RULES


JARGON = re.compile(r"FRAME|SHAPE|BUILD|PROVE|LEARN|CANVAS(?!\.md)|depth|깊이 판정|신호 \d|A-0\d\d|K-0\d\d|Knowledge Ledger|verdict|잼|프로파일")
COMMON = ["--setting-sources", "project,local", "--strict-mcp-config", "--output-format", "json"]
# acceptEdits: 쓰기는 작업 폴더 안에서만 자동 승인 — 코드가 대화창 대신 파일로 가서 턴당 비용이 준다
AGENT_TOOLS = ["--permission-mode", "acceptEdits", "--allowedTools", "Read", "Glob", "Grep", "Skill",
               "--disallowedTools", "Bash", "AskUserQuestion", "Agent", "WebFetch", "WebSearch"]


def claude(args, prompt, cwd, timeout=600, retries=2):
    """claude -p 1회 호출 → (텍스트, 비용, 지연초). 실패 시 재시도."""
    for attempt in range(retries + 1):
        start = time.time()
        proc = subprocess.run(["claude", "-p", prompt, *COMMON, *args], cwd=cwd,
                              capture_output=True, text=True, timeout=timeout)
        try:
            data = json.loads(proc.stdout)
            result = data[-1] if isinstance(data, list) else data
            if result.get("is_error"):
                raise ValueError(result.get("result"))
            return result.get("result") or "", result.get("total_cost_usd") or 0.0, time.time() - start
        except (ValueError, IndexError, subprocess.TimeoutExpired) as error:
            if attempt == retries:
                raise RuntimeError(f"claude 호출 실패: {error} / {proc.stderr[-500:]}")
            time.sleep(5)


def run_arm(persona, arm, index, rounds, out_dir):
    workspace = tempfile.mkdtemp(prefix=f"mt-{persona}-{arm}-")
    session = str(uuid.uuid4())
    plugin = ["--plugin-dir", str(ROOT)] if arm == "with" else []
    log, cost, session_total = [], 0.0, 0.0
    message = PERSONAS[persona]["opening"]
    for turn in range(rounds + 1):
        session_flag = ["--session-id", session] if turn == 0 else ["--resume", session]
        prompt = FINAL if turn == rounds else message
        # 구현 턴은 10분을 넘기도 한다
        reply, cumulative, latency = claude(["--model", "opus", *plugin, *AGENT_TOOLS, *session_flag], prompt, workspace, timeout=1200)
        # --resume의 total_cost_usd는 세션 누적값 — 턴 비용은 차분으로 구한다
        spent, session_total = cumulative - session_total, cumulative
        cost += spent
        log.append({"turn": turn, "user": prompt, "agent": reply, "cost": spent, "latency": round(latency, 1)})
        print(f"[{persona}/{arm}#{index}] turn {turn} ${spent:.2f} {latency:.0f}s", file=sys.stderr)
        if turn == rounds:
            break
        message, spent, _ = claude(["--model", "sonnet", "--system-prompt", user_system(persona), "--tools", ""],
                                   f"상대(개발 도우미)의 마지막 메시지:\n\n{reply}\n\n이 메시지에 사용자로서 답하라.", workspace)
        cost += spent
    final_plan = log[-1]["agent"]
    verdict = judge(final_plan, PERSONAS[persona]["facts"], workspace)
    user_facing = "\n".join(entry["agent"] for entry in log)
    files = sorted(str(p.relative_to(workspace)) for p in Path(workspace).rglob("*") if p.is_file())
    record = {"persona": persona, "arm": arm, "index": index, "workspace": workspace, "files": files, "cost": round(cost, 3), "facts": verdict,
              "score": sum(verdict.values()), "jargon": len(JARGON.findall(user_facing)), "log": log}
    (out_dir / f"{persona}-{arm}-{index}.json").write_text(json.dumps(record, ensure_ascii=False, indent=1))
    return record


def judge(plan, facts_by_key, cwd):
    """최종 기획안이 각 사실을 '맞게' 반영했는지 Sonnet이 판정(모순되면 false)."""
    facts = "\n".join(f"- {key}: {value}" for key, value in facts_by_key.items())
    prompt = (f"아래 기획안이 각 사실을 올바르게 반영했는지 판정하라. 사실과 모순되는 내용"
              f"(예: 부가세 10% 부과)이 있으면 false. 언급이 없어도 false.\n\n사실:\n{facts}\n\n기획안:\n{plan}\n\n"
              f'JSON 객체 하나만 출력: {{"tax": true/false, ...}} — 키는 사실 키 8개.')
    text, _, _ = claude(["--model", "sonnet", "--tools", ""], prompt, cwd)
    found = re.search(r"\{[\s\S]*\}", text)
    parsed = json.loads(found.group(0)) if found else {}
    return {key: bool(parsed.get(key)) for key in facts_by_key}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--runs", type=int, default=2)
    parser.add_argument("--rounds", type=int, default=8)
    parser.add_argument("--arms", nargs="+", default=["with", "without"], choices=["with", "without"])
    parser.add_argument("--personas", nargs="+", default=list(PERSONAS), choices=list(PERSONAS))
    options = parser.parse_args()
    out_dir = ROOT / "benchmarks" / "results" / f"multiturn-{time.strftime('%Y%m%d-%H%M%S')}"
    out_dir.mkdir(parents=True)
    jobs = [(p, arm, i) for p in options.personas for i in range(options.runs) for arm in options.arms]
    # ponytail: 동시 4개 고정 — 계정 rate limit에 걸리면 낮출 것
    with ThreadPoolExecutor(max_workers=4) as pool:
        records = list(pool.map(lambda job: run_arm(*job, options.rounds, out_dir), jobs))
    for persona in options.personas:
        for arm in options.arms:
            rows = [r for r in records if r["arm"] == arm and r["persona"] == persona]
            hits = {key: sum(r["facts"][key] for r in rows) for key in PERSONAS[persona]["facts"]}
            print(f"{persona}/{arm}: 평균 {sum(r['score'] for r in rows) / len(rows):.1f}/8 · 비용 ${sum(r['cost'] for r in rows):.2f}"
                  f" · 내부용어 {[r['jargon'] for r in rows]} · 사실별 {hits}")
    print(f"결과: {out_dir}")


if __name__ == "__main__":
    main()
