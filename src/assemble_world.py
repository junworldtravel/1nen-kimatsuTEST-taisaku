# ④ 世界の諸地域（アフリカ・北アメリカ・南アメリカ）のページを組み立てる：quiz3_template.html + quizzes_v3.json + v3_audio.json + 地図 → site/*.html
import sys, json, base64, os, re
D = sys.argv[1]
Q = json.load(open(D + "/quizzes_world.json"))
import glob
if os.path.exists(D + "/world_audio.json"): AU = json.load(open(D + "/world_audio.json"))
else:   # src には方面ごとに分けて保存（world_audio_af.json など）
    AU = {}
    for f in sorted(glob.glob(D + "/world_audio_*.json")): AU.update(json.load(open(f)))
T = open(D + "/quiz3_template.html", encoding="utf-8").read()

# 漢字の答えを、ひらがな・カタカナで入力しても正解にするための読み（長い順に置きかえる）
YOMI = {
 "北大西洋海流": "キタタイセイヨウカイリュウ", "北大西洋": "キタタイセイヨウ", "海流": "カイリュウ",
 "石油輸出国機構": "セキユユシュツコクキコウ", "西岸海洋性気候": "セイガンカイヨウセイキコウ", "西岸海洋性": "セイガンカイヨウセイ",
 "地中海性気候": "チチュウカイセイキコウ", "地中海性": "チチュウカイセイ", "地中海": "チチュウカイ",
 "亜寒帯気候": "アカンタイキコウ", "亜寒帯": "アカンタイ", "冷帯気候": "レイタイキコウ", "冷帯": "レイタイ", "気候": "キコウ",
 "首長国連邦": "シュチョウコクレンポウ", "東方正教会": "トウホウセイキョウカイ", "正教会": "セイキョウカイ", "教会": "キョウカイ",
 "湾岸戦争": "ワンガンセンソウ", "希少金属": "キショウキンゾク", "鉱産資源": "コウサンシゲン", "石油製品": "セキユセイヒン",
 "合衆国": "ガッシュウコク", "復活祭": "フッカツサイ", "工業化": "コウギョウカ", "偏西風": "ヘンセイフウ", "多文化": "タブンカ",
 "半島": "ハントウ", "山脈": "サンミャク", "平原": "ヘイゲン", "白夜": "ビャクヤ", "難民": "ナンミン", "多様": "タヨウ", "文化": "ブンカ",
 "黒海": "コッカイ", "北海": "ホッカイ", "原油": "ゲンユ", "石油": "セキユ", "輸出": "ユシュツ", "問題": "モンダイ", "利益": "リエキ",
 "大地溝帯": "ダイチコウタイ", "地溝帯": "チコウタイ", "人口増加率": "ジンコウゾウカリツ", "増加率": "ゾウカリツ",
 "第二次世界大戦": "ダイニジセカイタイセン", "企業的農業": "キギョウテキノウギョウ", "世界の食料庫": "セカイノショクリョウコ",
 "貿易赤字": "ボウエキアカジ", "貿易摩擦": "ボウエキマサツ", "多国籍企業": "タコクセキキギョウ", "北米自由貿易協定": "ホクベイジユウボウエキキョウテイ",
 "焼畑農業": "ヤキハタノウギョウ", "焼畑": "ヤキハタ", "高山気候": "コウザンキコウ", "熱帯林": "ネッタイリン", "持続可能": "ジゾクカノウ",
 "日系人": "ニッケイジン", "鉄鉱石": "テッコウセキ", "民族紛争": "ミンゾクフンソウ", "乾燥地域": "カンソウチイキ",
 "キリスト教": "キリストキョウ", "川": "ガワ", "湾": "ワン", "系": "ケイ", "海": "カイ", "北": "キタ", "東": "ヒガシ",
}
YL = sorted(YOMI.items(), key=lambda kv: -len(kv[0]))
THEME = {
 "me": ("#B05A12", "#F7E7D9", "#E8A267", "#3A2A1C"),
 "as": ("#24658A", "#DCEAF1", "#73B6D8", "#1E3540"),
 "eu": ("#6B48B0", "#ECE5F8", "#B79BF0", "#2B2340"),
 "af": ("#9A5B13", "#F5E9D6", "#E0A75A", "#3A2C18"),
 "na": ("#1F6F5C", "#DDEFE9", "#6CC3A8", "#1B3530"),
 "sa": ("#A8414F", "#F7E2E5", "#E68A97", "#3E2328"),
}
MAPS = {"me-map": ("me_map", "中東・湾岸の白地図（①〜⑪とA〜Fの番号つき）"), "eu-map": ("eu_map", "ヨーロッパの地図（国名と①〜⑳の番号つき）")}
for qz in Q:
    d = dict(qz)
    d["yomi"] = YL
    d.update(AU[qz["id"]])
    if qz["id"] in MAPS:
        name, alt = MAPS[qz["id"]]
        m = json.load(open(f"{D}/out/{name}.json"))
        d["map"] = m; d["mapAlt"] = alt
        d["mapImg"] = "data:image/webp;base64," + base64.b64encode(open(f"{D}/out/{name}.webp", "rb").read()).decode()
        labels = {it["label"] for it in qz["items"]}
        assert labels == set(m["pos"]), (labels ^ set(m["pos"]))
    # 全ステップに問題と答えの声があるか
    for i, it in enumerate(qz["items"]):
        for j, _ in enumerate(it["steps"]):
            assert f"q{i}_{j}" in d["clips"] and f"a{i}_{j}" in d["clips"], (qz["id"], i, j)
    s = json.dumps(d, ensure_ascii=False); assert "</script" not in s
    a, a2, ad, ad2 = THEME[qz["id"][:2]]
    page = (T.replace("__DATA__", s).replace("__TITLE__", qz["title"]).replace("__THEME__", a)
             .replace("__ACCENT_SOFT_D__", ad2).replace("__ACCENT_SOFT__", a2).replace("__ACCENT_D__", ad).replace("__ACCENT__", a))
    assert not re.search(r"__(TITLE|THEME|ACCENT[A-Z_]*|DATA)__", page), "placeholder left"
    open(f"{D}/site/{qz['file']}", "w", encoding="utf-8").write(page)
    print(qz["file"], round(os.path.getsize(f"{D}/site/{qz['file']}") / 1e6, 2), "MB")
