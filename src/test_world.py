# 続編4ページのテスト：判定の単体テスト／文字・声（模擬）での通し実行／字幕／やり直し／画面確認
import asyncio, json, sys, os, random
from playwright.async_api import async_playwright
D = sys.argv[1]
SITE = D + "/site/"
SUBLOG = """
window.__QUIZ_FAST = true; window.__subs = [];
document.addEventListener('DOMContentLoaded', () => {
  const el = document.getElementById('subCur'); if (!el) return;
  new MutationObserver(() => { const t = el.textContent; if (t) window.__subs.push(t); }).observe(el, {childList: true, subtree: true, characterData: true});
});
"""
MOCK = open(D + "/scripts/mock_sr.js").read()
Q = {q["id"]: q for q in json.load(open(D + "/quizzes_world.json"))}
PAGES = ["af-qa", "na-qa", "sa-qa"]
fails = []
def check(cond, msg):
    if not cond: fails.append(msg); print("  FAIL", msg)

def hira(s): return "".join(chr(ord(c) - 0x60) if "ァ" <= c <= "ヶ" else c for c in s)

async def open_page(b, name, hash_="", mock=False, w=393, h=852, ua=None):
    ctx = await b.new_context(viewport={"width": w, "height": h}, user_agent=ua) if ua else await b.new_context(viewport={"width": w, "height": h})
    pg = await ctx.new_page()
    errs = []
    pg.on("pageerror", lambda e: errs.append(str(e)))
    pg.on("console", lambda m: errs.append(m.text) if m.type == "error" and "Failed to load resource" not in m.text else None)
    await pg.add_init_script(SUBLOG + (MOCK if mock else ""))
    await pg.goto("file://" + SITE + name + ".html" + hash_)
    await pg.wait_for_function("!document.getElementById('startBtn').disabled", timeout=30000)
    return ctx, pg, errs

async def judge_tests(pg, qid):
    steps = await pg.evaluate("window.__steps")
    n = 0
    TJ = "([s,i]) => window.__textJudge(s,i).status"
    VJ = "([s,a]) => { const r = window.__voiceJudge(s,a); return r.status === 'hit' ? (r.correct ? 'correct' : 'wrong') : r.status; }"
    for st in steps:
        sid = st["sid"]
        if st["kw"]: continue
        for a in st["accept"]:
            r = await pg.evaluate(TJ, [sid, a]); n += 1; check(r == "correct", f"{qid} text {sid} {a} -> {r}")
            r = await pg.evaluate(TJ, [sid, hira(a)]); n += 1; check(r == "correct", f"{qid} text hira {sid} {hira(a)} -> {r}")
            r = await pg.evaluate(VJ, [sid, [a]]); n += 1; check(r == "correct", f"{qid} voice {sid} {a} -> {r}")
            r = await pg.evaluate(VJ, [sid, [f"えーと{a}です"]]); n += 1; check(r == "correct", f"{qid} voice phrase {sid} {a} -> {r}")
        r = await pg.evaluate(TJ, [sid, "わからない"]); n += 1; check(r == "pass", f"{qid} pass {sid} -> {r}")
        r = await pg.evaluate(VJ, [sid, ["わかりません"]]); n += 1; check(r == "pass", f"{qid} vpass {sid} -> {r}")
        r = await pg.evaluate(VJ, [sid, ["あいうえお"]]); n += 1; check(r == "none", f"{qid} vnone {sid} -> {r}")
        r = await pg.evaluate(TJ, [sid, "あいうえお"]); n += 1; check(r == "wrong", f"{qid} twrong {sid} -> {r}")
        # 別の問題の答え → ✕（同じ答えを共有する問題は除く）
        mine = set(st["accept"])
        others = [o for o in steps if o["sid"] != sid and not o["kw"] and not (set(o["accept"]) & mine)]
        for o in random.Random(sid).sample(others, min(3, len(others))):
            a = o["accept"][0]
            r = await pg.evaluate(TJ, [sid, a]); n += 1; check(r == "wrong", f"{qid} cross text {sid} <- {a} -> {r}")
            r = await pg.evaluate(VJ, [sid, [a]]); n += 1
            # 声は、別の答えにこの問題の答えがふくまれることがある（例：スカンディナビア山脈→⑥）ので、その場合は除く
            if not any(m in a for m in mine): check(r == "wrong", f"{qid} cross voice {sid} <- {a} -> {r}")
        # 1文字ちがい → おしい
        a = st["a"]
        if len(a) >= 4 and "（" not in a and "・" not in a and a in st["accept"]:
            near = a[:-2] + a[-1]
            r = await pg.evaluate(TJ, [sid, near]); n += 1; check(r in ("close", "correct"), f"{qid} close {sid} {near} -> {r}")
    return n

SPECIAL = {   # (種類, 正解表示, 入力, 期待)
 "af-qa": [("t","サハラ砂漠","さはら","correct"),("t","大地溝帯","だいちこうたい","correct"),("t","アパルトヘイト","アパルトヘイド","close"),
           ("t","1991年","1991","correct"),("t","レアメタル（希少金属）","きしょうきんぞく","correct"),("t","焼畑農業","やきはた","correct"),
           ("t","人口増加率","ぞうかりつ","correct"),("t","民族紛争","みんぞくふんそう","correct"),("t","第二次世界大戦","第2次世界大戦","correct"),
           ("t","カカオ豆","コーヒー豆","wrong"),("t","茶","こうちゃ","correct"),("v","スエズ運河","スエズ運河です","correct"),("v","価格","値段","correct"),
           ("t","キリマンジャロ山・ケニア山","ケニア山","correct"),("t","リベリア・エチオピア","エチオピア","correct")],
 "na-qa": [("t","ロッキー山脈","ろっきー","correct"),("t","五大湖","ごだいこ","correct"),("t","スペリオル湖・ミシガン湖・ヒューロン湖・エリー湖・オンタリオ湖","エリー湖","correct"),
           ("t","西経100度","せいけいひゃくど","correct"),("t","西経100度","東経100度","close"),("t","東","西","wrong"),("t","第3位","3位","correct"),
           ("t","適地適作","てきちてきさく","correct"),("t","北米自由貿易協定（NAFTA）","NAFTA","correct"),("t","北米自由貿易協定（NAFTA）","なふた","correct"),
           ("t","米国・メキシコ・カナダ協定（USMCA）","USMCA","correct"),("t","ワシントンD.C.","ワシントン","correct"),("t","ICT","ict","correct"),
           ("t","ヒスパニック","ひすぱにっく","correct"),("v","サンベルト","サンベルト","correct"),("t","貿易摩擦","ぼうえきまさつ","correct"),("t","多国籍企業","たこくせき","correct")],
 "sa-qa": [("t","アンデス山脈","あんです","correct"),("t","大西洋","太平洋","wrong"),("t","パンパ","ぱんぱ","correct"),("t","メスチーソ","メスティーソ","correct"),
           ("t","ポルトガル語","スペイン語","wrong"),("t","スペイン語","すぺいんご","correct"),("t","バイオ燃料（バイオエタノール）","バイオエタノール","correct"),
           ("t","持続可能な開発","じぞくかのう","correct"),("t","サンティアゴ","サンチアゴ","correct"),("t","熱帯林の破壊","森林破壊","correct"),
           ("t","日系人","にっけいじん","correct"),("t","別の場所に移動する","移動","correct"),("v","赤道","赤道","correct"),("t","高山気候","こうざんきこう","correct")],
}

async def run_text(pg, qid, qmode):
    """文字で答える：正解・ひらがな・まちがい・わからない・おしい を混ぜて通しで実行"""
    steps = await pg.evaluate("window.__steps")
    await pg.click(f"#qm-{qmode}"); await pg.click("#am-text")
    await pg.select_option("#order", "fixed")
    await pg.click("#startBtn")
    expect = {}
    for k, st in enumerate(steps):
        sid = st["sid"]
        await pg.wait_for_function("(sid) => { const s = window.__quizState(); return s.st.list[s.st.pos] === sid && window.__textWaiting(); }", arg=sid, timeout=15000)
        if st["kw"]: v, ok = ("原油を輸出したから", True) if k % 2 == 0 else ("わからない", False)
        elif k % 5 == 0: v, ok = "わからない", False
        elif k % 5 == 1: v, ok = hira(st["accept"][0]), True
        elif k % 5 == 2: v, ok = "にほん", False
        else: v, ok = st["accept"][-1], True
        expect[sid] = ok
        await pg.fill("#ans", v); await pg.press("#ans", "Enter")
        await pg.wait_for_function("(sid) => window.__quizState().res[sid] !== undefined", arg=sid, timeout=15000)
    await pg.wait_for_selector("#resCard:not([hidden])", timeout=20000)
    res = (await pg.evaluate("window.__quizState()"))["res"]
    for sid, ok in expect.items():
        check(res[sid]["ok"] == ok, f"{qid} text-run {qmode} {sid} expected {ok} got {res[sid]}")
    return expect

async def run_voice(pg, qid, qmode):
    steps = await pg.evaluate("window.__steps")
    answers, expect = [], {}
    for k, st in enumerate(steps):
        if st["kw"]: answers.append("石油を輸出したからです"); expect[st["sid"]] = True; continue
        m = k % 4
        if m == 0: answers.append(st["accept"][0]); expect[st["sid"]] = True
        elif m == 1: answers.append("えーと " + st["accept"][-1] + " かな"); expect[st["sid"]] = True
        elif m == 2: answers.append("わからない"); expect[st["sid"]] = False
        else:
            mine = set(st["accept"])
            other = next(o["accept"][0] for o in steps[k + 1:] + steps[:k] if not o["kw"] and not (set(o["accept"]) & mine) and not any(m in o["accept"][0] for m in mine))
            answers += [None, other]; expect[st["sid"]] = False     # 1回目は聞き取れず→もう一回→別の答え（まちがい）
    await pg.evaluate("(a) => { window.__answers = a; }", answers)
    await pg.click(f"#qm-{qmode}"); await pg.click("#am-voice"); await pg.select_option("#order", "fixed")
    await pg.click("#startBtn")
    await pg.wait_for_selector("#resCard:not([hidden])", timeout=60000)
    res = (await pg.evaluate("window.__quizState()"))["res"]
    for sid, ok in expect.items():
        check(sid in res and res[sid]["ok"] == ok, f"{qid} voice-run {qmode} {sid} expected {ok} got {res.get(sid)}")
    return expect

async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch()
        total = 0
        for qid in PAGES:
            print("==", qid)
            ctx, pg, errs = await open_page(b, qid)
            # テスト用：文字入力待ちか
            n = await judge_tests(pg, qid); total += n
            stp = await pg.evaluate("window.__steps")
            for kind, ans, inp, want in SPECIAL[qid]:
                sid = next(x["sid"] for x in stp if x["a"] == ans)
                if kind == "t": r = await pg.evaluate("([s,i]) => window.__textJudge(s,i).status", [sid, inp])
                else: r = await pg.evaluate("([s,a]) => { const r = window.__voiceJudge(s,a); return r.status === 'hit' ? (r.correct ? 'correct' : 'wrong') : r.status; }", [sid, [inp]])
                total += 1; check(r == want, f"{qid} special {kind} {sid} {inp} want {want} got {r}")
            print("  judge cases so far", total)
            # b）文字で出題 × 文字で答える
            exp = await run_text(pg, qid, "text")
            subs = await pg.evaluate("window.__subs")
            # まちがえた問題は、答えの字幕が出ているか
            sd = json.loads(await pg.evaluate("document.getElementById('qdata').textContent"))["subs"]
            for sid, ok in exp.items():
                if not ok:
                    t = sd["a" + sid]["text"]
                    check(any(t in s for s in subs), f"{qid} answer subtitle missing {sid} {t}")
            # 文字で出題では問題の読み上げ字幕は出ない
            check(not any(sd["q" + s]["text"] in x and "龍星" in x for s in list(exp)[:3] for x in subs), f"{qid} b-mode spoke questions")
            await pg.screenshot(path=f"{D}/out/t3_{qid}_result.png", full_page=True)
            # やり直し
            wrong = [s for s, ok in exp.items() if not ok]
            await pg.click("#retryBtn")
            for sid in wrong:
                await pg.wait_for_function("(sid) => { const s = window.__quizState(); return s.st.list[s.st.pos] === sid && window.__textWaiting(); }", arg=sid, timeout=15000)
                st = next(x for x in await pg.evaluate("window.__steps") if x["sid"] == sid)
                await pg.fill("#ans", "原油を輸出したから" if st["kw"] else st["accept"][0]); await pg.press("#ans", "Enter")
                await pg.wait_for_function("(sid) => window.__quizState().res[sid] !== undefined", arg=sid)
            await pg.wait_for_selector("#resCard:not([hidden])", timeout=20000)
            stt = await pg.evaluate("window.__quizState()")
            check(len(stt["st"]["list"]) == len(wrong) and all(stt["res"][s]["ok"] for s in wrong), f"{qid} retry run")
            check((await pg.text_content("#retryBtn")) == "まちがいなし！", f"{qid} retry button text")
            check(not errs, f"{qid} errors {errs}")
            await ctx.close()

            # a）声で出題 × 文字で答える（字幕：全問題文が龍星の字幕で出る）
            ctx, pg, errs = await open_page(b, qid)
            await run_text(pg, qid, "voice")
            subs = await pg.evaluate("window.__subs")
            sd = json.loads(await pg.evaluate("document.getElementById('qdata').textContent"))["subs"]
            missing = [k for k in sd if k.startswith("q") and not any(sd[k]["text"] in s for s in subs)]
            check(not missing, f"{qid} a-mode question subtitles missing {missing[:5]}")
            for k in ("intro_t", "intro_x", "kbd", "count", "go", "end"):
                check(any(sd[k]["text"] in s for s in subs), f"{qid} intro/end subtitle missing {k}")
            check(not errs, f"{qid} errors(a-text) {errs}")
            await ctx.close()

            # 声で答える（模擬の音声認識）：a と b
            for qm in ("voice", "text"):
                ctx, pg, errs = await open_page(b, qid, mock=True)
                await run_voice(pg, qid, qm)
                subs = await pg.evaluate("window.__subs")
                if qm == "voice":
                    for k in ("intro_v", "mic", "retry"):
                        check(any(sd[k]["text"] in s for s in subs), f"{qid} voice subtitle missing {k}")
                check(not errs, f"{qid} errors(voice {qm}) {errs}")
                await ctx.close()
            print("  runs ok" if not [f for f in fails if f.startswith(qid)] else "  runs had failures")

        for qid in PAGES:
            N = len(Q[qid]["items"])
            ctx, pg, errs = await open_page(b, qid, "#b-text")
            st = await pg.evaluate("window.__quizState()")
            check(st["qMode"] == "text" and st["ansMode"] == "text", f"{qid} hash b-text {st}")
            check(await pg.input_value("#order") == "random", f"{qid} qa default random")
            await pg.click("#startBtn"); await pg.wait_for_function("window.__quizState().st.list.length > 0")
            lst = (await pg.evaluate("window.__quizState()"))["st"]["list"]
            check(sorted(lst) == sorted(f"{i}_0" for i in range(N)) and lst != [f"{i}_0" for i in range(N)], f"{qid} random order {len(lst)}")
            await ctx.close()

            # 目次：単元をえらぶと、その単元の問題だけが出る／「ぜんぶ」でもどる／えらんだ単元はおぼえている
            secs = Q[qid]["sections"]
            ctx, pg, errs = await open_page(b, qid, "#b-text")
            sid2 = secs[1]["id"]
            await pg.click("#sec-" + sid2)               # ぜんぶ → この単元だけ
            want = sorted(f"{i}_0" for i, it in enumerate(Q[qid]["items"]) if it["sec"] == sid2)
            summ = await pg.text_content("#tocSum")
            check(str(len(want)) in summ and "えらんだ" in summ, f"{qid} toc summary {summ}")
            await pg.click("#startBtn"); await pg.wait_for_function("window.__quizState().st.list.length > 0")
            lst = (await pg.evaluate("window.__quizState()"))["st"]["list"]
            check(sorted(lst) == want, f"{qid} toc one section {len(lst)} vs {len(want)}")
            stage = await pg.text_content("#stage")
            check(stage == secs[1]["name"], f"{qid} stage chip {stage}")
            await pg.evaluate("document.getElementById('toStart').click()")
            await pg.click("#sec-" + secs[0]["id"])      # 2つ目の単元を追加
            want2 = sorted(f"{i}_0" for i, it in enumerate(Q[qid]["items"]) if it["sec"] in (sid2, secs[0]["id"]))
            await pg.click("#startBtn"); await pg.wait_for_function("window.__quizState().st.list.length > 0")
            lst = (await pg.evaluate("window.__quizState()"))["st"]["list"]
            check(sorted(lst) == want2, f"{qid} toc two sections {len(lst)} vs {len(want2)}")
            await pg.evaluate("document.getElementById('toStart').click()")
            await pg.click("#sec-" + secs[0]["id"]); await pg.click("#sec-" + sid2)   # 全部はずそうとしても1つは残る
            on = await pg.evaluate("[...document.querySelectorAll('#toc button[aria-pressed=true]')].map(b=>b.id)")
            check(on == ["sec-" + sid2], f"{qid} toc keep one {on}")
            await pg.reload(); await pg.wait_for_function("!document.getElementById('startBtn').disabled", timeout=30000)
            on = await pg.evaluate("[...document.querySelectorAll('#toc button[aria-pressed=true]')].map(b=>b.id)")
            check(on == ["sec-" + sid2], f"{qid} toc remembered {on}")
            await pg.click("#secAll")
            on = await pg.evaluate("[...document.querySelectorAll('#toc button[aria-pressed=true]')].length")
            check(on == len(secs) + 1, f"{qid} toc all {on}")
            check(not errs, f"{qid} errors(toc) {errs}")
            await ctx.close()

            # 単元だけのときは「全部で○問だ」を言わない
            ctx, pg, errs = await open_page(b, qid, "#a-text")
            await pg.evaluate("window.__setSecs(['" + secs[-1]["id"] + "'])")
            await pg.click("#startBtn")
            await pg.wait_for_function("window.__quizState().st.list.length > 0 && window.__textWaiting()", timeout=20000)
            subs = await pg.evaluate("window.__subs")
            sd = json.loads(await pg.evaluate("document.getElementById('qdata').textContent"))["subs"]
            check(not any(sd["count"]["text"] in x for x in subs), f"{qid} count spoken for partial")
            check(any(sd["intro_t"]["text"] in x for x in subs), f"{qid} intro missing for partial")
            await ctx.close()

        # 画面（393px）：スタート・出題中（地図ズーム）・文字入力
        for qid in PAGES:
            ctx = await b.new_context(viewport={"width": 393, "height": 852}, device_scale_factor=2)
            pg = await ctx.new_page(); await pg.add_init_script("window.__QUIZ_FAST = false;")
            await pg.goto("file://" + SITE + qid + ".html#a-text")
            await pg.wait_for_function("!document.getElementById('startBtn').disabled", timeout=30000)
            await pg.screenshot(path=f"{D}/out/t3_{qid}_start.png", full_page=True)
            await pg.evaluate("window.__setSecs(['1'])"); await pg.screenshot(path=f"{D}/out/t3_{qid}_toc1.png", full_page=False)
            await pg.click("#secAll")
            await pg.uncheck("#intro", force=True); await pg.click("#startBtn"); await pg.wait_for_timeout(2600)
            await pg.screenshot(path=f"{D}/out/t3_{qid}_quiz.png")
            await pg.click("#pauseBtn")
            sw = await pg.evaluate("document.documentElement.scrollWidth")
            check(sw <= 393, f"{qid} horizontal overflow {sw}")
            await ctx.close()
        ctx = await b.new_context(viewport={"width": 393, "height": 852}, device_scale_factor=2)
        pg = await ctx.new_page(); await pg.goto("file://" + SITE + "index.html")
        await pg.screenshot(path=f"{D}/out/t3_index.png", full_page=True)
        links = await pg.evaluate("[...document.querySelectorAll('a')].map(a=>a.getAttribute('href'))")
        for l in links:
            if l.startswith("#"): continue
            f = l.split("#")[0]; check(os.path.exists(SITE + f), f"index link {l}")
        check(await pg.evaluate("document.documentElement.scrollWidth") <= 393, "index overflow")
        await ctx.close()

        await b.close()
    print("TOTAL judge cases", total, "FAILS", len(fails))
    for f in fails[:40]: print(" -", f)

asyncio.run(main())
