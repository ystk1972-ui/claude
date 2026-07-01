# GUI スタイル改善 設計仕様

**日付:** 2026-07-01  
**対象ファイル:** `thread_cutting.py`  
**アプローチ:** カード UI + アクセントカラー + G コード Syntax Highlighting

---

## 概要

`ThreadCuttingApp` の GUI を、現在のレイアウト構造を維持しつつビジュアルを大幅改善する。  
ダークテーマを深化させ、左ボーダーライン付きカードセクション・青アクセントボタン・VS Code 風 syntax highlighting を導入する。

---

## カラーパレット

| 用途 | 色コード |
|------|----------|
| ウィンドウ背景 | `#1e1e2e` |
| カード（セクション）背景 | `#252535` |
| アクセント（青） | `#4a9fd4` |
| アクセント ホバー | `#74b8e0` |
| メインテキスト | `#cdd6f4` |
| サブテキスト・ラベル | `#6c7086` |
| 入力背景 | `#313244` |
| 出力背景 | `#11111b` |
| 生成ボタン bg | `#4a9fd4` |
| 生成ボタン fg | `#ffffff` |
| クリア/コピーボタン bg | `#313244` |
| クリア/コピーボタン fg | `#cdd6f4` |

### Syntax Highlighting（出力テキスト）

| トークン | 色 | スタイル |
|----------|-----|---------|
| コメント `( ... )` | `#6c7086` | italic |
| G/M コード | `#4a9fd4` | 通常 |
| 軸文字 X/Z/I/F/P/U/H/D/B/R/Q | `#f9e2af` | 通常 |
| 数値 | `#a6e3a1` | 通常 |
| N 行番号 | `#cba6f7` | 通常 |
| O 番号 / `%` | `#f38ba8` | 通常 |

---

## タイポグラフィ

- ラベル・UI テキスト: `Yu Gothic UI 10`
- セクションタイトル: `Yu Gothic UI 9 bold`、色 `#4a9fd4`
- 出力テキスト: `Consolas 10`

---

## レイアウト構造

### タイトルバー

ウィンドウ最上部に固定高さ（36px）のタイトルバーを追加。

```
bg=#11111b
左: "⚙ NC旋盤 ねじ切りプログラム生成"  fg=#4a9fd4 bold
右: "v1.4.4"                            fg=#6c7086
```

### 左パネル — カードセクション

`ttk.LabelFrame` を廃止し、以下の構造に置き換える：

```
tk.Frame(bg=#1e1e2e, pady=4)          ← セクション外枠
  tk.Canvas(width=3, bg=#4a9fd4)      ← 左ボーダーライン
  tk.Frame(bg=#252535)                ← カード本体
    tk.Label(text="N. タイトル",
             fg=#4a9fd4, bg=#252535,
             font=bold)               ← セクションタイトル
    [コンテンツ widgets]
```

対象セクション（7 つ）：
1. ねじ種類
2. 雄ねじ・雌ねじ
3. NC コントロール
4. ねじサイズ / ピッチ
5. Z 座標
6. インサートチップ ノーズR
7. パス数

### ボタン

`ttk.Button` を `tk.Button` に変更し直接スタイル指定：

- **プログラム生成**: `bg=#4a9fd4 fg=white font=bold relief=flat cursor=hand2`  
  ホバー時: `bg=#74b8e0`（`<Enter>`/`<Leave>` バインド）
- **クリア**: `bg=#313244 fg=#cdd6f4 relief=flat`
- **クリップボードにコピー**: `bg=#313244 fg=#cdd6f4 relief=flat`

### 右パネル

**計算情報エリア:**
- `bg=#11111b fg=#a6e3a1`（緑）
- ラベル: `fg=#4a9fd4 bold`

**生成プログラムエリア:**
- `bg=#11111b fg=#cdd6f4`
- 生成後に `_apply_syntax_highlight()` を呼び出してタグ適用

---

## Syntax Highlighting 実装

`_apply_syntax_highlight(widget)` メソッドを追加。生成プログラムテキストに対して正規表現でタグを適用する。

適用順序（後から適用したものが優先されるため、コメントを最後に適用）：

```python
# タグ定義（__init__ 内で一度だけ設定）
widget.tag_configure("num",     foreground="#a6e3a1")
widget.tag_configure("axis",    foreground="#f9e2af")
widget.tag_configure("gm_code", foreground="#4a9fd4")
widget.tag_configure("n_line",  foreground="#cba6f7")
widget.tag_configure("o_pct",   foreground="#f38ba8")
widget.tag_configure("comment", foreground="#6c7086", font=("Consolas", 10, "italic"))
```

正規表現パターン（適用順）：
1. `-?\d+\.?\d*` → `num`
2. `(?<=[A-Za-z])-?\d+\.?\d*` で軸文字直後の数値は `axis` で上書き  
   → 実際には `[XxZzIiFfPpUuHhDdBbRrQq](?=-?\d+)` で軸文字自体に `axis` タグ
3. `\b[GgMm]\d+\.?\d*` → `gm_code`
4. `\b[Nn]\d+` → `n_line`
5. `^[Oo]\d+|^%` → `o_pct`（行頭マッチ）
6. `\(.*?\)` → `comment`（最後に適用して最優先）

---

## 変更スコープ

- **変更対象:** `ThreadCuttingApp.__init__`、`_build_ui`、新規 `_apply_syntax_highlight`、`_generate`（highlight 呼び出し追加）、`_set_text`（highlight 連携）
- **変更なし:** ねじ計算ロジック（`calc_thread_depth`、`_okuma_cuts`、`generate_okuma`、`generate_fanuc` など）、データベース定義
- **後方互換:** ウィンドウサイズ・リサイズ動作は維持

---

## 非機能要件

- `tkinter` 標準ライブラリのみ使用（外部パッケージ追加なし）
- Windows 11 + Python 3.x で動作確認
- syntax highlighting は生成ごとに再適用（前回タグを削除してから適用）
