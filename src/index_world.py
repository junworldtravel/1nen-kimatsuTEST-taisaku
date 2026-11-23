# 期末用トップページ：方面ごとのカード（目次つき一問一答 ＋ 白地図）を作りなおす
import sys, json, re
D = sys.argv[1]
Q = {q["id"]: q for q in json.load(open(D + "/quizzes_world.json"))}
s = open(D + "/site/index.html", encoding="utf-8").read()
if "--oc:" not in s:
    s = s.replace("--sa: #A8414F; --sa-soft: #F7E2E5;", "--sa: #A8414F; --sa-soft: #F7E2E5; --oc: #2B5FA8; --oc-soft: #DFE8F6;")
    s = s.replace("--sa: #E68A97; --sa-soft: #3E2328;", "--sa: #E68A97; --sa-soft: #3E2328; --oc: #86AEE8; --oc-soft: #1E2A3E;")
    s = s.replace(".wd .sa { --c: var(--sa); --cs: var(--sa-soft); }",
                  ".wd .sa { --c: var(--sa); --cs: var(--sa-soft); } .wd .oc { --c: var(--oc); --cs: var(--oc-soft); }\n.set h4 { margin: .3rem 0 0; font-size: .88rem; font-family: var(--font-display); color: var(--c); }")
REG = [("af", "④-1", "アフリカ", "9 アフリカ（p.60〜63）・まとめの問題 p.76", "地図で整理 8 アフリカ州（p.91）"),
       ("na", "④-2", "北アメリカ", "10 北アメリカ（p.64〜67）・まとめの問題 p.77", "地図で整理 9 北アメリカ州（p.91）"),
       ("sa", "④-3", "南アメリカ", "11 南アメリカ（p.68〜71）・まとめの問題 p.78", "地図で整理 10 南アメリカ州（p.92）"),
       ("oc", "④-4", "オセアニア", "12 オセアニア（p.72〜75）・まとめの問題 p.79", "地図で整理 11 オセアニア州（p.92）")]
def grid(f):
    return f'''      <div class="grid4">
        <span></span><span class="hd">声で答える</span><span class="hd">文字で答える</span>
        <span class="rl">a）声で出題<small>読み上げ</small></span><a class="home" href="{f}#a-voice">a・声</a><a class="train" href="{f}#a-text">a・文字</a>
        <span class="rl">b）文字で出題<small>画面の文</small></span><a class="home" href="{f}#b-voice">b・声</a><a class="train" href="{f}#b-text">b・文字</a>
      </div>'''
blocks = []
for k, no, nm, src, msrc in REG:
    qa, mp = Q[k + "-qa"], Q[k + "-map"]
    lis = "".join(f'<li>{c["name"]}<span>{sum(1 for it in qa["items"] if it["sec"] == c["id"])}問</span></li>' for c in qa["sections"])
    blocks.append(f'''    <div class="set {k}">
      <h3><span class="no">{no}</span>{nm}</h3>
      <h4>一問一答 {len(qa["items"])}問</h4>
      <p>問題集「{src}」から。スタート画面の目次で、単元をえらんで出題できます。「説明（5択）」は、説明を読んで5つの言葉から選びます。</p>
      <ol class="toc" aria-label="{nm}の目次">{lis}</ol>
{grid(qa["file"])}
      <h4>白地図 {len(mp["items"])}問</h4>
      <p>問題集「{msrc}」と同じ番号の地名を、地図を見て答えます。</p>
{grid(mp["file"])}
    </div>''')
sec = '  <section class="region wd" id="wd">\n    <h2>世界の諸地域</h2>\n' + "\n".join(blocks) + "\n  </section>\n\n"
s = re.sub(r'  <section class="region wd" id="wd">.*?</section>\n\n', lambda m: sec, s, flags=re.S)
open(D + "/site/index.html", "w", encoding="utf-8").write(s)
print("index ok", s.count('class="set '), "sets")
