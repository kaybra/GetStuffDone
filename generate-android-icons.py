#!/usr/bin/env python3
"""Generate the Android launcher icons (adaptive + legacy + themed) and the splash
assets from the same source art the iOS build uses.

Usage:  python generate-android-icons.py
Needs:  pip install pillow

Reads   icons/icon-vibrant.png  icons/icon-light.png  icons/icon-rainbow.png
        resources/splash.png
Writes  android/app/src/main/res/mipmap-*/ic_launcher*.png
        android/app/src/main/res/drawable*/splash*.png
        store/android/*  (Play Store icon + feature graphic)

Each 1024px icon is split into a background layer (the gradient / stripes with the
glyph removed) and a foreground layer (the glyph alone, scaled to sit inside the
adaptive-icon safe zone), so Android can mask it to a circle, squircle, etc.
"""
import os, shutil
from PIL import Image, ImageDraw, ImageFilter, ImageFont, ImageChops
import numpy as np

ROOT = os.path.dirname(os.path.abspath(__file__))
RES = os.path.join(ROOT, "android/app/src/main/res")
STORE = os.path.join(ROOT, "store/android")

# (suffix in file names, source png, glyph colour or None for white-with-shadow)
ICONS = {
    "":         "icons/icon-vibrant.png",   # default (Synth Wave)
    "_light":   "icons/icon-light.png",
    "_rainbow": "icons/icon-rainbow.png",
}
DENSITIES = {"mdpi": 1, "hdpi": 1.5, "xhdpi": 2, "xxhdpi": 3, "xxxhdpi": 4}
GLYPH_SCALE = 0.70          # glyph size inside the 108dp adaptive layer (safe zone = 66%)


def load(path):
    return Image.open(os.path.join(ROOT, path)).convert("RGB")


def build_background(img, kind):
    """Rebuild the glyph-free background of a 1024px icon."""
    a = np.asarray(img).astype(float)
    h, w, _ = a.shape
    if kind == "_rainbow":
        col = a[:, 8, :]                      # glyph never reaches x=8
        bg = np.repeat(col[:, None, :], w, axis=1)
    else:
        # linear diagonal gradient: colour depends on t=(x+y)/(w+h-2)
        lut_t, lut_c = [], []
        for y in range(h):                    # left edge
            lut_t.append((6 + y)); lut_c.append(a[y, 6])
        for x in range(w):                    # bottom edge
            lut_t.append((x + h - 7)); lut_c.append(a[h - 7, x])
        order = np.argsort(lut_t)
        lut_t = np.array(lut_t)[order]; lut_c = np.array(lut_c)[order]
        yy, xx = np.mgrid[0:h, 0:w]
        t = xx + yy
        bg = np.stack([np.interp(t, lut_t, lut_c[:, k]) for k in range(3)], axis=-1)
    return Image.fromarray(bg.clip(0, 255).astype("uint8"), "RGB")


def glyph_layer(img, bg, kind):
    """RGBA layer holding just the glyph (alpha recovered against the background)."""
    a = np.asarray(img).astype(float)
    b = np.asarray(bg).astype(float)
    if kind == "_rainbow":
        target = np.array([255.0, 255.0, 255.0])
    else:
        # glyph colour = most common colour that differs strongly from the bg
        diff = np.linalg.norm(a - b, axis=-1)
        sel = a[diff > 60]
        target = np.median(sel, axis=0)
    d = target - b
    num = ((a - b) * d).sum(-1)
    den = (d * d).sum(-1) + 1e-6
    alpha = (num / den).clip(0, 1)
    alpha[alpha < 0.03] = 0
    rgba = np.zeros(a.shape[:2] + (4,), dtype="uint8")
    rgba[..., :3] = target.astype("uint8")
    rgba[..., 3] = (alpha * 255).astype("uint8")
    return Image.fromarray(rgba, "RGBA")


def fit_foreground(glyph, size):
    """Place the 1024px glyph layer on a transparent size x size canvas at GLYPH_SCALE."""
    g = glyph.resize((round(size * GLYPH_SCALE),) * 2, Image.LANCZOS)
    canvas = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    off = (size - g.width) // 2
    canvas.paste(g, (off, off), g)
    return canvas


def round_mask(size, radius_frac):
    m = Image.new("L", (size * 4, size * 4), 0)
    ImageDraw.Draw(m).rounded_rectangle([0, 0, size * 4 - 1, size * 4 - 1],
                                        radius=int(size * 4 * radius_frac), fill=255)
    return m.resize((size, size), Image.LANCZOS)


def save(img, *parts):
    p = os.path.join(*parts)
    os.makedirs(os.path.dirname(p), exist_ok=True)
    img.save(p, optimize=True)


def main():
    # wipe the Capacitor template's placeholder launcher icons
    for d in os.listdir(RES):
        full = os.path.join(RES, d)
        if d.startswith("mipmap-") and os.path.isdir(full):
            shutil.rmtree(full)
    for rel in ("drawable-v24/ic_launcher_foreground.xml", "drawable/ic_launcher_background.xml",
                "values/ic_launcher_background.xml"):
        try: os.remove(os.path.join(RES, rel))
        except FileNotFoundError: pass

    mono_done = False
    for suffix, src in ICONS.items():
        img = load(src)
        bg = build_background(img, suffix)
        glyph = glyph_layer(img, bg, suffix)
        # sanity check: bg + glyph must reproduce the original (ignoring rainbow's drop shadow)
        recon = bg.convert("RGBA"); recon.alpha_composite(glyph)
        err = np.abs(np.asarray(recon.convert("RGB")).astype(int) - np.asarray(img).astype(int)).mean()
        print(f"icon{suffix or '_default'}: reconstruction error {err:.2f} / 255")
        for dens, mult in DENSITIES.items():
            layer = round(108 * mult)
            legacy = round(48 * mult)
            folder = f"mipmap-{dens}"
            save(bg.resize((layer, layer), Image.LANCZOS), RES, folder, f"ic_launcher_background{suffix}.png")
            save(fit_foreground(glyph, layer), RES, folder, f"ic_launcher_foreground{suffix}.png")
            full = img.resize((legacy, legacy), Image.LANCZOS).convert("RGBA")
            sq = full.copy(); sq.putalpha(round_mask(legacy, 0.18))
            save(sq, RES, folder, f"ic_launcher{suffix}.png")
            rd = full.copy(); rd.putalpha(round_mask(legacy, 0.5))
            save(rd, RES, folder, f"ic_launcher_round{suffix}.png")
            if not mono_done:   # themed (Android 13+) icon: glyph silhouette, shared by all variants
                m = fit_foreground(glyph, layer)
                black = Image.new("RGBA", m.size, (0, 0, 0, 255)); black.putalpha(m.getchannel("A"))
                save(black, RES, folder, "ic_launcher_monochrome.png")
        mono_done = True

    # ---- splash ---------------------------------------------------------------
    # Built from the CURRENT icon glyph (icons/icon-vibrant.png) on the app's purple,
    # so the launch splash always matches the home-screen icon.
    vsrc = np.asarray(load("icons/icon-vibrant.png").convert("RGB")).astype(float)
    alpha = np.clip((vsrc[..., 1] - 45) / 55, 0, 1)
    ys, xs = np.where(alpha > 0.5)
    box = (xs.min(), ys.min(), xs.max() + 1, ys.max() + 1)
    glyph = Image.new("RGBA", (vsrc.shape[1], vsrc.shape[0]), (255, 110, 180, 0))
    glyph.putalpha(Image.fromarray((alpha * 255).astype("uint8")))
    glyph = glyph.crop(box)
    BG = (0x18, 0x0b, 0x2e, 255)

    def place(size, px, bg):
        c = Image.new("RGBA", size, bg)
        k = px / max(glyph.size)
        g = glyph.resize((round(glyph.width * k), round(glyph.height * k)), Image.LANCZOS)
        c.alpha_composite(g, ((size[0] - g.width) // 2, (size[1] - g.height) // 2))
        return c

    sizes = {"": 480, "-port-mdpi": 480, "-port-hdpi": 800, "-port-xhdpi": 1280, "-port-xxhdpi": 1600,
             "-port-xxxhdpi": 1920}
    for suffix, longside in sizes.items():
        short = round(longside * 9 / 16)
        save(place((short, longside), round(short * 0.42), BG).convert("RGB"), RES, f"drawable{suffix}", "splash.png")
    for dens, longside in {"mdpi": 480, "hdpi": 800, "xhdpi": 1280, "xxhdpi": 1600, "xxxhdpi": 1920}.items():
        short = round(longside * 9 / 16)
        save(place((longside, short), round(short * 0.42), BG).convert("RGB"), RES, f"drawable-land-{dens}", "splash.png")
    # Android 12+ system splash icon: glyph on transparent, inside the circular mask
    save(place((960, 960), 400, (0, 0, 0, 0)), RES, "drawable-nodpi", "splash_icon.png")

    # ---- Play Store assets ----------------------------------------------------
    vib = load("icons/icon-vibrant.png")
    save(vib.resize((512, 512), Image.LANCZOS), STORE, "play-store-icon-512.png")
    fg = Image.new("RGB", (1024, 500))
    fg.paste((0x18, 0x0b, 0x2e), (0, 0, 1024, 500))
    d = ImageDraw.Draw(fg)
    icon = vib.resize((260, 260), Image.LANCZOS).convert("RGBA"); icon.putalpha(round_mask(260, 0.22))
    fg.paste(icon, (130, 120), icon)
    try:
        f1 = ImageFont.truetype("/usr/share/fonts/opentype/inter/Inter-Bold.otf", 66)
        f2 = ImageFont.truetype("/usr/share/fonts/opentype/inter/Inter-Regular.otf", 30)
    except OSError:
        f1 = f2 = ImageFont.load_default()
    d.text((430, 128), "Get Stuff Done", font=f1, fill=(255, 255, 255))
    d.text((430, 205), "Randomly", font=f1, fill=(255, 150, 200))
    d.text((434, 305), "Let the app choose for you.", font=f2, fill=(220, 205, 245))
    save(fg, STORE, "feature-graphic-1024x500.png")


if __name__ == "__main__":
    main()
