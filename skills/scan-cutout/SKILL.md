---
name: scan-cutout
description: >
  从扫描件/正拍照片里把证件抠出来：自动检测边界、按国标比例收紧、裁切转正、
  按实物尺寸 300dpi 标准化，支持双面合成、防挪用水印、多页 PDF 合并。
  Trigger phrases: 证件抠图, 抠证件, 裁切转正, 证件标准化, 扫描件裁切,
  双面合成, 证件加水印, 合并证件PDF, extract ID card from scan, crop scan,
  standardize ID photo.
---

# scan-cutout — 证件扫描件抠图与标准化

把「一整页扫描件中间躺着一张证件」变成「能直接出示/存档的标准化成品」。
纯 Pillow 实现（无 OpenCV），一个脚本走完 检测 → 抠图 → 转正 → 标准尺寸 →
合成 → 水印 → PDF 全流程。

## 适用与不适用

- ✅ 平板扫描仪扫描件、正对拍摄的照片（手机 EXIF 方向自动处理）
- ✅ 白底上的任意颜色证件（含白色证件——靠彩色元素和文字检测）
- ❌ 斜拍、有透视变形的照片——本工具只做轴对齐裁切 + 90° 旋转，
  不做透视/歪斜矫正。歪斜严重的输入应让用户重扫，而不是硬抠。
- ❌ HEIC（iPhone 默认格式）Pillow 打不开，先转 JPEG：
  macOS 上 `sips -s format jpeg 输入.heic --out 输入.jpg`

## 工具

- 脚本：`scripts/scan_cutout.py`（子命令 probe / card / page / stack / watermark / pdf）
- 尺寸速查：`references/doc-sizes.md`（常见证件国标尺寸与宽高比）

## 环境准备

只依赖 Pillow。建一次性 venv，不污染系统环境（有 scratchpad 目录就用它，
没有就落到 mktemp）。`SKILL` 指向本 SKILL.md 所在目录——脚本路径相对
技能目录解析，不要假设 cwd 在技能目录里：

```bash
WORK="${SCRATCHPAD:-$(mktemp -d)}"
python3 -m venv "$WORK/venv" && "$WORK/venv/bin/pip" install -q Pillow
PY="$WORK/venv/bin/python"
SKILL="<本技能目录的绝对路径>"   # 例如 .../skills/scan-cutout
```

下文所有命令沿用这两个变量。

## 工作流程

### Step 1: probe — 先探测，不要盲抠

```bash
"$PY" "$SKILL/scripts/scan_cutout.py" probe 扫描件1.jpeg 扫描件2.jpeg
```

对每个输入报告：检出框、长短边比、最接近的证件类型、是否竖放。
**检出比例应与目标证件的标准比例吻合**（身份证长/短边比 1.585，
行驶证 1.467，详见 doc-sizes.md）。比例对不上说明检测抓到了阴影、
卡套或别的东西——先调参再继续：

- 深色背景 / 检出整页 → 调低 `--lum`（如 235）
- 证件很淡检不出 → 调低 `--sat`（如 8）或调高 `--lum`
- 检出框偏大偏小 → 调 `--frac`（0.25–0.55 之间试）

### Step 2: card / page — 抠图

**probe 里调过的 `--lum/--sat/--frac/--margin` 必须原样带到 card 命令**
（两边独立跑检测，参数不带过去就退回默认值）。

小卡片（身份证、行驶证、驾驶证等，会重采样到实物尺寸 300dpi）：

```bash
"$PY" "$SKILL/scripts/scan_cutout.py" card 扫描件.jpeg -o 成品.jpg --mm 85.6x54
"$PY" "$SKILL/scripts/scan_cutout.py" card 深色底扫描.jpeg -o 成品.jpg --mm 88x60 --lum 235
```

整幅文档（登记证书、合同页等，只裁边噪+旋转，保留原分辨率）：

```bash
"$PY" "$SKILL/scripts/scan_cutout.py" page 扫描件.jpeg -o 成品.jpg --rotate cw
```

### Step 3: 肉眼核对 — 必做，不可跳过

用 Read 工具打开每张成品图检查：

1. **方向对不对**——竖放转正默认顺时针（`--turn cw`，适用于证件上边朝左
   放进扫描仪的情况）；如果成品是倒的，加 `--rot180` 重跑；上边朝右的
   扫描件用 `--turn ccw`。
2. **裁切紧不紧**——四边应贴合证件边缘，无大片背景、无切到内容。
3. **关键信息可读**——号码、姓名、日期清晰。

方向错误是最常见的问题，脚本猜不了语义方向，必须看图确认。

### Step 4: stack — 双面合成（可选）

```bash
"$PY" "$SKILL/scripts/scan_cutout.py" stack 正面.jpg 背面.jpg -o 双面合成.jpg
```

### Step 5: watermark — 对外提供必加水印

**铁律：凡是要发给别人（中介、租赁方、机构）的证件成品，一律用水印版；
无水印版只留本地存档。** 水印文字必须写明用途和日期，限定这份复印件
只能干这一件事：

```bash
"$PY" "$SKILL/scripts/scan_cutout.py" watermark 双面合成.jpg -o 双面合成-水印版.jpg \
  --text "仅供办理XX业务使用 · $(date +%F)"
```

也可以在 stack 时直接 `--watermark "文字"` 一步出水印版。
水印生成后同样 Read 核对：文字应铺满整幅、半透明不遮挡关键信息。

### Step 6: pdf — 多页合并（可选）

```bash
"$PY" "$SKILL/scripts/scan_cutout.py" pdf 封面.jpg 第1-2页.jpg 第3-4页.jpg -o 全本.pdf
```

多页文档（如机动车登记证书）合并成单个 PDF 方便整体出示，
默认单页最长边 1700px 控制体积。

## 归档约定

1. **原始扫描件不动**——留在原目录，成品放到用户指定的证件/成品目录。
2. 成品命名说人话：`行驶证-正面-京A12345.jpg`、`身份证-双面合成-水印版.jpg`。
3. 目录里有 README/索引文件的，给成品登记一行（规格、内容摘要）。
4. JPEG 质量：卡片 95、整页 88–90，都带 `dpi=(300,300)` 标签和
   `subsampling=0`（保号码、文字边缘清晰）。
5. 敏感证件成品建议用户存密码保管箱；对外只给水印版。

## 常见证件参数速查

| 证件 | `--mm` | 备注 |
|---|---|---|
| 身份证 / 银行卡 / 社保卡 | `85.6x54` | ISO ID-1，成品 1011×638 px |
| 行驶证 / 驾驶证卡片 | `88x60` | 成品 1039×709 px |
| 名片 | `90x54` | |
| 登记证书 / A5 文档 | 用 `page` | 不重采样，保留原分辨率 |

更多尺寸与检测参数调优见 `references/doc-sizes.md`。
