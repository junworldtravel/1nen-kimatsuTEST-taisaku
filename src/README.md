# 1nen-kimatsuTEST-taisaku 元データ（src）

期末テスト対策の問題集サイト（リポジトリ直下の index.html ほか）を作るための元データです。
新しい方面・単元を追加するときは、ここから作業を始めます。

## ページ構成
| 公開ファイル | 内容 | 元になるファイル |
|---|---|---|
| index.html | 問題集メニュー（世界の諸地域。方面ごとのカードに、目次つき一問一答と白地図） | index_world.py で作る（quizzes_world.json から目次と問題数を入れる） |
| af-qa.html | ④-1 アフリカ 一問一答61問（①自然環境 ②歴史・人口・民族・宗教 ③産業 ④説明（5択）） | quiz3_template.html + quizzes_world.json + world_audio_af.json |
| na-qa.html | ④-2 北アメリカ 一問一答64問（①自然環境 ②人口・民族・宗教・文化 ③農牧業 ④鉱工業，貿易 ⑤説明（5択）） | 同上 + world_audio_na.json |
| sa-qa.html | ④-3 南アメリカ 一問一答53問（①自然環境 ②民族・宗教 ③産業 ④説明（5択）） | 同上 + world_audio_sa.json |
| oc-qa.html | ④-4 オセアニア 一問一答52問（①自然環境 ②人口・民族・宗教 ③産業 ④説明（5択）） | 同上 + world_audio_oc.json |
| af-map.html / na-map.html / sa-map.html / oc-map.html | 白地図（地図で整理 8〜11 と同じ番号。10・12・9・9問） | quiz3_template.html + quizzes_world.json + world_audio_xx-map.json + out/xx_map.* |

## 出典
- 問題集「9 アフリカ」〜「12 オセアニア」（p.60〜75）、「9〜12のまとめの問題」（p.76〜79）、「地図で整理」8〜11（p.91〜92）の写真
- 問題集に答えがないため、答えは要点ページと地図から取り、首都などは一般的な知識で補った
- まだ使っていないページ：9〜12単元総合（p.80〜83）、探究問題（p.84〜85）、地形図（p.86〜87）、地図で整理 1〜7（p.88〜90）

## 問題の形
- 一問一答（kind t）：文字（ひらがな・カタカナ・漢字）または声で答える
- 説明（5択）（kind m）：説明を読んで、5つの似た言葉から正しいものを選ぶ。文字モードはタップ、声モードは言葉か番号（「2番」など）を言う。「わからない」も可。選択肢の順番は作るときに決める（content_world.py の C5）
- 白地図（type map）：地図の番号の地名を答える。地図は maps_world.py が Natural Earth（パブリックドメイン）から作る

## ファイル
- content_world.py：問題データ（区分＝目次、出典ページ、5択、白地図の番号の位置）。qa() は content_v3.py（中間テスト版の共通部品）を使う
- quizzes_world.json：content_world.py で作った出題データ
- world_audio_*.json：問題（青山龍星）と答え（ずんだもん）の声（MP3 32k をbase64）と字幕。アップロード上限のため、ページごとに分けて保存
- out/xx_map.webp・.json：白地図の画像と番号の位置
- quiz3_template.html：共通ページ。sections があると目次（ぜんぶ／単元ごと）、choices があると5択になる
- maps_world.py / index_world.py / assemble_world.py / gen_world_audio.py / test_world.py：地図・トップ・組み立て・声・テスト

## 作り直し・追加の流れ（作業フォルダ D）
D に quiz3_template.html・textjudge.js・world_audio_*.json、D/scripts に *.py と mock_sr.js（中間テストの src から）、D/out に xx_map.*、D/map に Natural Earth の geojson（ne_50m_admin_0_countries・ne_50m_rivers_lake_centerlines・ne_50m_lakes・ne_10m_geography_regions_polys・ne_10m_reefs）、D/vv に VOICEVOX core 0.16（onnxruntime 1.17.3・open_jtalk 辞書・0.vvm・15.vvm）
1. 問題：content_world.py に追加 → `python3 content_world.py D` → quizzes_world.json
2. 地図：`maps_world.py D af na sa oc`
3. 読みの確認：`gen_world_audio.py D kana`（読みまちがいは SPEAK_FIX に追加。例：五大湖→ゴダイコ、焼畑→やきはた、白豪主義→ハクゴウ主義、北島と南島→きたじまと、みなみじま）
4. 声：`gen_world_audio.py D build` → world_audio.json（声は 40k で作って 32k に変換）
5. 組み立て：`assemble_world.py D` → D/site/*.html、`index_world.py D` → index.html
6. テスト：`test_world.py D`
7. 公開：GitHub のアップロード画面からリポジトリ直下へ（公開前に必ず確認）。1回のアップロードは約3.8MBまで

## クレジット
- 声：VOICEVOX:青山龍星／VOICEVOX:ずんだもん
- 地図：Natural Earth（パブリックドメイン）
