# 1nen-kimatsuTEST-taisaku 元データ（src）

期末テスト対策の問題集サイト（リポジトリ直下の index.html ほか）を作るための元データです。
新しい方面・単元を追加するときは、ここから作業を始めます。

## ページ構成
| 公開ファイル | 内容 | 元になるファイル |
|---|---|---|
| index.html | 問題集メニュー（世界の諸地域。方面ごとのカードに目次と問題数） | リポジトリ直下の index.html を直接編集 |
| af-qa.html | ④-1 アフリカ 一問一答52問（①自然環境 ②歴史・人口・民族・宗教 ③産業） | quiz3_template.html + quizzes_world.json + world_audio_af.json |
| na-qa.html | ④-2 北アメリカ 一問一答56問（①自然環境 ②人口・民族・宗教・文化 ③農牧業 ④鉱工業，貿易） | quiz3_template.html + quizzes_world.json + world_audio_na.json |
| sa-qa.html | ④-3 南アメリカ 一問一答45問（①自然環境 ②民族・宗教 ③産業） | quiz3_template.html + quizzes_world.json + world_audio_sa.json |

## 出典
- 問題集「9 アフリカ」「10 北アメリカ」「11 南アメリカ」（p.60〜71）と「9〜12のまとめの問題」（p.76〜78）の写真
- 問題集に答えがないため、答えは要点ページと地図から取り、首都などは一般的な知識で補った
- まだ使っていないページ：12 オセアニア（p.72〜75）、探究問題（p.84〜85）、地形図（p.86〜87）、地図で整理（p.88〜92）

## ファイル
- content_world.py：問題データ。教材の見出しを目次（sections）にし、問題ごとに sec（目次番号）と src（出典ページ）をつける。qa() は content_v3.py（中間テスト版の共通部品）を使う
- quizzes_world.json：content_world.py で作った出題データ（accept＝文字入力で正解にする表記、voice＝聞きまちがい候補）
- world_audio_af/na/sa.json：問題（青山龍星）と答え（ずんだもん）の声（MP3 40k をbase64）と字幕。アップロード上限のため方面ごとに分けて保存
- quiz3_template.html：共通ページ。データに sections があると、スタート画面に目次（ぜんぶ／単元ごと、いくつでも選べる。選んだ単元はブラウザがおぼえる）が出る
- textjudge.js：文字入力の判定（ひらがな・カタカナ・漢字対応、1文字ちがいは「おしい」で✕）
- test_world.py / mock_sr.js：判定の単体テスト、文字・声（模擬）の通し実行、字幕、やり直し、目次、393px の画面確認

## 作り直し・追加の流れ（作業フォルダ D）
D に quiz3_template.html・textjudge.js・world_audio_*.json、D/scripts に *.py と mock_sr.js、D/vv に VOICEVOX core 0.16（onnxruntime 1.17.3・open_jtalk 辞書・0.vvm・15.vvm を GitHub Releases から取得）
1. 問題：content_world.py に方面（区分と問題）を足して WORLD に追加 → `python3 content_world.py D` → quizzes_world.json
2. 読みの確認：`gen_world_audio.py D kana`（読みまちがいは SPEAK_FIX に書きかえを追加。例：五大湖→ゴダイコ、焼畑→やきはた、赤道付近→せきどう付近）
3. 声：`gen_world_audio.py D build` → world_audio.json（追加分だけなら `ONLY=xx-qa`）。src に置くときは方面ごとに分ける
4. 組み立て：`assemble_world.py D` → D/site/*.html（新しい方面は THEME に色を足す）
5. テスト：`test_world.py D`（SPECIAL に方面ごとの確認ケースを足す）
6. 公開：GitHub のアップロード画面からリポジトリ直下へ（公開前に必ず確認）。1回のアップロードは約3.8MBまで

## クレジット
- 声：VOICEVOX:青山龍星／VOICEVOX:ずんだもん
