#!/usr/bin/env python3
"""scan-cutout — 证件扫描件抠图 / 裁切转正 / 标准化工具

依赖: Pillow (pip install Pillow)。纯 PIL 实现，无 OpenCV。

子命令:
  probe      检测扫描件里的证件边界，报告比例并猜测证件类型（只读，先跑这个）
  card       抠出小卡片证件 → 按标准比例收紧 → 转正 → 实物尺寸 300dpi
  page       整幅文档清理：裁扫描边噪 + 旋转，保留原分辨率
  stack      多张图上下拼合成（如身份证正背面双面合成）
  watermark  加斜向平铺半透明水印（对外提供版本必加）
  pdf        多张图合并为一个 PDF，控制体积

适用输入: 平板扫描仪扫描件、正对拍摄的照片。
不做透视矫正——歪斜严重的斜拍照片请重扫，不在本工具能力内。
"""
import argparse
import os
import sys

from PIL import Image, ImageChops, ImageDraw, ImageFont, ImageOps

DPI = 300


def mm2px(v):
    return round(v / 25.4 * DPI)


# 常见证件/文档实物尺寸 (宽mm, 高mm)，横向表示
REF_SIZES = {
    "身份证/银行卡/社保卡 (ISO ID-1)": (85.6, 54.0),
    "行驶证/驾驶证 卡片": (88.0, 60.0),
    "名片": (90.0, 54.0),
    "护照资料页 (ISO ID-3)": (125.0, 88.0),
    "机动车登记证书 单页 (A5)": (210.0, 148.0),
    "机动车登记证书 跨页 (双A5)": (296.0, 210.0),
    "A4 文档": (297.0, 210.0),
}


def load(path):
    """打开图片：先落地 EXIF 方向（手机拍照），再转 RGB。"""
    im = Image.open(path)
    im = ImageOps.exif_transpose(im)
    return im.convert("RGB")


# ---------------- 检测 ----------------

def fg_mask(img_rgb, lum=250, sat=10):
    """前景掩码 = 偏暗 或 有色彩。

    白底扫描件上连白色证件也能检出：靠证件上的彩色元素和文字。
    深色背景的扫描件需要调高 lum 意义不大，改用 --lum/--sat 微调。
    """
    L = img_rgb.convert("L").point(lambda v: 255 if v < lum else 0)
    S = img_rgb.convert("HSV").split()[1].point(lambda v: 255 if v >= sat else 0)
    return ImageChops.lighter(L, S)


def _profile(mask, axis):
    """每行/每列的前景像素数。"""
    w, h = mask.size
    n = h if axis == "row" else w
    out = []
    for i in range(n):
        box = (0, i, w, i + 1) if axis == "row" else (i, 0, i + 1, h)
        out.append(mask.crop(box).histogram()[255])
    return out


def _longest_run(vals, lim):
    """值 >= lim 的最长连续区间 [起, 止]。"""
    best = cur = None
    for i, v in enumerate(vals):
        if v >= lim:
            cur = [i, i] if cur is None else [cur[0], i]
        else:
            if cur and (best is None or cur[1] - cur[0] > best[1] - best[0]):
                best = cur
            cur = None
    if cur and (best is None or cur[1] - cur[0] > best[1] - best[0]):
        best = cur
    return best


def detect(path, scale=4, margin=0.04, frac=0.40, lum=250, sat=10):
    """检测证件外接框，返回原图坐标 (x0,y0,x1,y1)；检不出返回 None。

    缩小 scale 倍加速；先裁掉 margin 比例的扫描仪边框噪声；
    投影剖面里超过峰值 frac 的最长连续段视为证件所在区间。
    """
    im = load(path)
    W, H = im.size
    mx, my = int(W * margin), int(H * margin)
    core = im.crop((mx, my, W - mx, H - my))
    cw, ch = core.size
    sw, sh = max(1, cw // scale), max(1, ch // scale)
    sm = core.resize((sw, sh), Image.LANCZOS)
    m = fg_mask(sm, lum=lum, sat=sat)
    rows, cols = _profile(m, "row"), _profile(m, "col")
    if not rows or not cols or max(rows) == 0 or max(cols) == 0:
        return None
    ry = _longest_run(rows, max(rows) * frac)
    rx = _longest_run(cols, max(cols) * frac)
    if not ry or not rx:
        return None
    # 回映射用真实缩放因子（floor 除导致 *scale 不精确），并钳回图像边界
    fx, fy = cw / sw, ch / sh
    return (
        max(0, min(W, round(mx + rx[0] * fx))),
        max(0, min(H, round(my + ry[0] * fy))),
        max(0, min(W, round(mx + (rx[1] + 1) * fx))),
        max(0, min(H, round(my + (ry[1] + 1) * fy))),
    )


def guess_type(w, h):
    """按长短边比排序候选证件类型。返回 (实测比, [(名称, 标准比, 相对偏差)前两名])。"""
    rr = max(w, h) / min(w, h)
    scored = sorted(
        (abs(max(sz) / min(sz) - rr) / (max(sz) / min(sz)), name, max(sz) / min(sz))
        for name, sz in REF_SIZES.items()
    )
    return rr, [(name, ratio, dev) for dev, name, ratio in scored[:2]]


# ---------------- 抠卡片 ----------------

def fit_ratio(box, ratio):
    """把检测框按目标宽高比居中收紧（去掉卡套、阴影等多余边）。

    ratio = 目标 w/h（与检测框同方向）。只收不放。
    """
    x0, y0, x1, y1 = box
    w, h = x1 - x0, y1 - y0
    if w / h > ratio:
        nw = h * ratio
        dx = (w - nw) / 2
        return (round(x0 + dx), y0, round(x1 - dx), y1)
    nh = w / ratio
    dy = (h - nh) / 2
    return (x0, round(y0 + dy), x1, round(y1 - dy))


def extract_card(path, w_mm, h_mm, pad=6, turn="cw", rot180=False, **det_kw):
    """检测 → 按标准比例收紧 → 转正 → 实物尺寸 300dpi。

    turn: 检出竖放时的转正方向。扫描时证件上边朝左 → cw（顺时针）；
          上边朝右 → ccw。抠完必须肉眼核对方向，反了换方向重跑。
    """
    box = detect(path, **det_kw)
    if not box:
        raise SystemExit(f"✗ 未检出证件: {path}（试试 probe 调 --lum/--sat/--frac）")
    im = load(path)
    W, H = im.size
    x0, y0, x1, y1 = box
    landscape = (x1 - x0) >= (y1 - y0)
    target = w_mm / h_mm if landscape else h_mm / w_mm
    x0, y0, x1, y1 = fit_ratio(box, target)
    # 外扩与目标比例同步（等量外扩会引入非等比拉伸）
    pad_y, pad_x = pad, round(pad * target)
    card = im.crop((max(0, x0 - pad_x), max(0, y0 - pad_y),
                    min(W, x1 + pad_x), min(H, y1 + pad_y)))
    if not landscape:
        card = card.transpose(
            Image.Transpose.ROTATE_270 if turn == "cw" else Image.Transpose.ROTATE_90
        )
    if rot180:
        card = card.transpose(Image.Transpose.ROTATE_180)
    return card.resize((mm2px(w_mm), mm2px(h_mm)), Image.LANCZOS)


# ---------------- 整幅文档 ----------------

def process_page(path, rotate="none", trim=0.018):
    """裁掉扫描边噪 + 旋转，保持原分辨率与比例。rotate: none/cw/ccw/180。"""
    im = load(path)
    W, H = im.size
    m = round(min(W, H) * trim)
    im = im.crop((m, m, W - m, H - m))
    if rotate == "cw":
        im = im.transpose(Image.Transpose.ROTATE_270)
    elif rotate == "ccw":
        im = im.transpose(Image.Transpose.ROTATE_90)
    elif rotate == "180":
        im = im.transpose(Image.Transpose.ROTATE_180)
    return im


# ---------------- 合成 / 水印 / PDF ----------------

def stack(imgs, gap=46, margin=40):
    """白底画布上纵向居中拼接（双面合成）。gap/margin 单位 px@300dpi。"""
    w = max(i.size[0] for i in imgs)
    h = sum(i.size[1] for i in imgs) + gap * (len(imgs) - 1)
    canvas = Image.new("RGB", (w + margin * 2, h + margin * 2), (255, 255, 255))
    y = margin
    for i in imgs:
        canvas.paste(i, (margin + (w - i.size[0]) // 2, y))
        y += i.size[1] + gap
    return canvas


# 中文字体候选：macOS 优先，其次 Linux Noto。逐个试到能真正渲染中文为止。
FONT_CANDIDATES = [
    "/System/Library/Fonts/Supplemental/Songti.ttc",
    "/System/Library/Fonts/STHeiti Medium.ttc",
    "/System/Library/Fonts/Hiragino Sans GB.ttc",
    "/System/Library/Fonts/PingFang.ttc",
    "/System/Library/Fonts/Supplemental/Arial Unicode.ttf",
    "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",
    "/usr/share/fonts/noto-cjk/NotoSansCJK-Regular.ttc",
]


def _renders_cjk(font):
    """豆腐块检测：渲染两个不同汉字，位图相同或全空 = 该字体渲染不了中文。"""
    def bitmap(ch):
        a = Image.new("L", (80, 80), 255)
        ImageDraw.Draw(a).text((5, 5), ch, font=font, fill=0)
        return a
    a, b = bitmap("仅"), bitmap("车")
    return a.getbbox() is not None and a.tobytes() != b.tobytes()


def load_cjk_font(size):
    # 固定小字号探测（大字号字形会画出探测画布，把有效字体误判成豆腐块），
    # 通过后再按目标字号重新加载同一字体
    PROBE_SIZE = 40
    for path in FONT_CANDIDATES:
        if not os.path.exists(path):
            continue
        for idx in range(6):
            try:
                probe = ImageFont.truetype(path, PROBE_SIZE, index=idx)
            except Exception:
                break
            if _renders_cjk(probe):
                return ImageFont.truetype(path, size, index=idx)
    raise SystemExit("✗ 未找到可渲染中文的字体，检查 FONT_CANDIDATES")


def watermark(img, text, alpha=60, angle=30):
    """整幅斜向平铺半透明水印，防复印件被挪作他用。

    文字应写明用途和日期，如「仅供办理XX业务使用 · YYYY-MM-DD」。
    """
    import math

    if not 1 <= alpha <= 255:
        raise SystemExit(f"✗ --alpha 必须在 1-255（当前 {alpha}）；0 或负值会静默产出无水印副本")
    W, H = img.size
    fs = max(28, W // 26)  # 字号随图宽自适应
    font = load_cjk_font(fs)

    # 在对角线方形透明层上铺满水平文字，整体旋转后居中裁回原尺寸，
    # 保证旋转后四角无空白
    diag = int(math.hypot(W, H)) + fs * 4
    layer = Image.new("RGBA", (diag, diag), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    tw = d.textlength(text, font=font)
    step_x = int(tw + fs * 3)
    step_y = int(fs * 3.2)
    for i, y in enumerate(range(0, diag, step_y)):
        offset = (step_x // 2) if (i % 2) else 0  # 交错排布更均匀
        for x in range(-step_x, diag, step_x):
            d.text((x + offset, y), text, font=font, fill=(110, 110, 110, alpha))

    layer = layer.rotate(angle, expand=0)
    left, top = (diag - W) // 2, (diag - H) // 2
    layer = layer.crop((left, top, left + W, top + H))
    return Image.alpha_composite(img.convert("RGBA"), layer).convert("RGB")


def _ensure_dir(path):
    d = os.path.dirname(path)
    if d:
        os.makedirs(d, exist_ok=True)


def make_pdf(paths, out, max_px=1700):
    """多张图合并 PDF；先缩到 max_px 内控制体积。输出强制 PDF 格式。"""
    if not out.lower().endswith(".pdf"):
        out += ".pdf"
    _ensure_dir(out)
    ims = []
    for p in paths:
        im = load(p)
        im.thumbnail((max_px, max_px), Image.LANCZOS)
        ims.append(im)
    ims[0].save(out, "PDF", save_all=True, append_images=ims[1:], resolution=150.0)
    return out


def save_jpg(img, path, quality=92):
    _ensure_dir(path)
    img.save(path, "JPEG", quality=quality, dpi=(DPI, DPI), subsampling=0, optimize=True)
    print(f"→ {path}  {img.size[0]}x{img.size[1]} px @{DPI}dpi  "
          f"{os.path.getsize(path) / 1024:.0f} KB")


# ---------------- CLI ----------------

def parse_mm(s):
    try:
        w_mm, h_mm = (float(v) for v in s.lower().replace("×", "x").split("x"))
    except ValueError:
        raise SystemExit(f"✗ --mm 格式应为 宽x高（mm，横向表示），如 85.6x54；收到: {s}")
    if w_mm < h_mm:
        print(f"⚠ --mm 应横向表示（宽≥高），已自动交换为 {h_mm}x{w_mm}")
        w_mm, h_mm = h_mm, w_mm
    return w_mm, h_mm


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)

    def add_det_args(p):
        p.add_argument("--lum", type=int, default=250, help="前景亮度阈值 (默认 250)")
        p.add_argument("--sat", type=int, default=10, help="前景饱和度阈值 (默认 10)")
        p.add_argument("--frac", type=float, default=0.40,
                       help="投影峰值比例阈值 (默认 0.40)")
        p.add_argument("--margin", type=float, default=0.04,
                       help="预裁扫描边框比例 (默认 0.04)")

    p = sub.add_parser("probe", help="检测边界并猜测证件类型（只读）")
    p.add_argument("scans", nargs="+")
    add_det_args(p)

    p = sub.add_parser("card", help="抠出小卡片证件并标准化")
    p.add_argument("scan")
    p.add_argument("-o", "--out", required=True)
    p.add_argument("--mm", default="85.6x54", help="实物尺寸 宽x高 mm (默认身份证 85.6x54)")
    p.add_argument("--pad", type=int, default=6, help="收紧后外扩像素 (默认 6)")
    p.add_argument("--turn", choices=["cw", "ccw"], default="cw",
                   help="竖放转正方向 (默认 cw=顺时针)")
    p.add_argument("--rot180", action="store_true", help="结果再转 180°")
    p.add_argument("-q", "--quality", type=int, default=95)
    add_det_args(p)

    p = sub.add_parser("page", help="整幅文档：裁边噪 + 旋转")
    p.add_argument("scan")
    p.add_argument("-o", "--out", required=True)
    p.add_argument("--rotate", choices=["none", "cw", "ccw", "180"], default="none")
    p.add_argument("--trim", type=float, default=0.018, help="裁边比例 (默认 0.018)")
    p.add_argument("-q", "--quality", type=int, default=90)

    p = sub.add_parser("stack", help="多张图纵向拼接（双面合成）")
    p.add_argument("imgs", nargs="+")
    p.add_argument("-o", "--out", required=True)
    p.add_argument("--gap", type=int, default=46)
    p.add_argument("--margin", type=int, default=40)
    p.add_argument("--watermark", help="拼接后加水印文字")
    p.add_argument("-q", "--quality", type=int, default=92)

    p = sub.add_parser("watermark", help="给已有图片加平铺水印")
    p.add_argument("img")
    p.add_argument("-o", "--out", required=True)
    p.add_argument("--text", required=True, help="水印文字（写明用途+日期）")
    p.add_argument("--alpha", type=int, default=60, help="不透明度 0-255 (默认 60)")
    p.add_argument("--angle", type=int, default=30)
    p.add_argument("-q", "--quality", type=int, default=88)

    p = sub.add_parser("pdf", help="多张图合并 PDF")
    p.add_argument("imgs", nargs="+")
    p.add_argument("-o", "--out", required=True)
    p.add_argument("--max-px", type=int, default=1700, help="单页最长边像素 (默认 1700)")

    a = ap.parse_args()

    if a.cmd == "probe":
        det_kw = dict(lum=a.lum, sat=a.sat, frac=a.frac, margin=a.margin)
        for path in a.scans:
            im = load(path)
            name = os.path.basename(path)
            box = detect(path, **det_kw)
            if not box:
                print(f"{name}\n  ✗ 未检出（调 --lum/--sat/--frac 再试）\n")
                continue
            x0, y0, x1, y1 = box
            w, h = x1 - x0, y1 - y0
            rr, cands = guess_type(w, h)
            (n1, r1, d1), (n2, r2, d2) = cands
            print(f"{name}")
            print(f"  原图 {im.size[0]}x{im.size[1]}  bbox=({x0},{y0},{x1},{y1})"
                  f"  检出 {w}x{h}  长/短边比 {rr:.3f}")
            line = f"  最接近: {n1} (标准 {r1:.3f}, 偏差 {d1 * 100:.1f}%)"
            if d2 - d1 < 0.02:
                line += f"；次接近: {n2} (标准 {r2:.3f}, 偏差 {d2 * 100:.1f}%)"
            print(line)
            if d1 > 0.08:
                print("  ⚠ 比例偏离所有标准证件较远——可能不是证件，"
                      "或检测框混入卡套/阴影/多个物体，以用户说明的证件类型为准")
            print(f"  {'竖放，抠卡时会转 90°' if w < h else '横放'}\n")

    elif a.cmd == "card":
        w_mm, h_mm = parse_mm(a.mm)
        card = extract_card(a.scan, w_mm, h_mm, pad=a.pad, turn=a.turn,
                            rot180=a.rot180, lum=a.lum, sat=a.sat,
                            frac=a.frac, margin=a.margin)
        save_jpg(card, a.out, a.quality)

    elif a.cmd == "page":
        save_jpg(process_page(a.scan, rotate=a.rotate, trim=a.trim), a.out, a.quality)

    elif a.cmd == "stack":
        canvas = stack([load(p) for p in a.imgs], gap=a.gap, margin=a.margin)
        if a.watermark:
            canvas = watermark(canvas, a.watermark)
        save_jpg(canvas, a.out, a.quality)

    elif a.cmd == "watermark":
        save_jpg(watermark(load(a.img), a.text, alpha=a.alpha, angle=a.angle),
                 a.out, a.quality)

    elif a.cmd == "pdf":
        out = make_pdf(a.imgs, a.out, max_px=a.max_px)
        print(f"→ {out}  {len(a.imgs)} 页  {os.path.getsize(out) / 1024:.0f} KB")


if __name__ == "__main__":
    main()
