# Gold-standard examples

Two finals that passed the full 8-dimension build + self-check pass. Use them
as few-shot anchors for tone and density — not as templates to lightly reword.

## Example 1 — Restrained old money 克制老钱风

```text
A 58-year-old estate owner, deep crow's feet, sun-weathered complexion with
faint age spots, one eyebrow set slightly higher than the other, silver hair
combed back imperfectly with a few stray strands lifted by the breeze. He wears
a heavy charcoal cashmere overcoat with a visible soft nap over a cream
cable-knit sweater, natural creasing at the elbows, hands out of frame. Caught
just as he turns away from a conversation, the last trace of a dry smile
fading, gaze resting on the grounds beyond the left edge of the frame. Shot on
a full-frame camera, 85mm lens at f/2.2, camera at chest height about 2.5
meters away, chest-up framing, eyes on the upper-third line, negative space on
the left. Overcast late-autumn daylight from camera right as the only light
source, soft 2:1 lighting ratio, a gentle shadow under the jaw, quiet tonal
separation between the dark coat and the lighter background; skin with visible
pores, uneven tone, the natural dryness of aged skin, fine vellus hair along
the cheek. Background: out-of-focus stone manor facade and bare oak trees
receding in layered depth, smooth optical bokeh. Kodak Portra 400 palette, fine
film grain, subtle lens vignette, muted greens and browns, soft contrast with
lifted blacks, no HDR look.
```

```text
Negative: plastic skin, airbrushed, waxy skin, beauty filter, flawless skin,
glowing skin, HDR, oversaturated, oversharpened, glossy, deformed hands, extra
fingers, fused fingers, bad anatomy, distorted face, cross-eyed, CGI, 3D
render, illustration, painting, anime, cartoon, watermark, text, logo
```

**Why it works:**
- `one eyebrow set slightly higher` + `stray strands lifted by the breeze` —
  two anti-mean-face anchors; without them this drifts to a stock-photo
  patriarch.
- `hands out of frame` — hands were the single biggest deformity risk in a
  chest-up crop.
- Overcast + Portra was already two layers of low contrast, so no haze was
  added and `quiet tonal separation` anchors the tones (self-check rule 2).
- Elderly skin swaps oil sheen for `natural dryness of aged skin` — the
  four-pack adapts, it doesn't disappear.

## Example 2 — Sports broadcast frame grab 体育赛事广播截图风

```text
Live sports broadcast frame grab, 16:9. A 26-year-old professional tennis
player mid-rally on a clay court, framed from the waist up, sweat beading on
his forehead, flushed uneven redness on his cheeks from exertion, clay dust
streaked on one forearm. He wears a plain white performance polo with no
lettering, the fabric damp and clinging at the collar. Face tense with effort,
eyes locked on the incoming ball outside the frame, mouth slightly open
mid-exhale; body frozen at a high shutter speed, with faint motion blur only on
the racket head at the edge of the frame. Shot from an elevated courtside
broadcast position, 400mm telephoto lens at f/3.2, heavy background
compression, subject slightly off-center as the camera follows the action.
Harsh mid-afternoon sunlight from high camera-left, hard-edged shadows,
specular highlights on the sweat, deep shadow on the far side of the face; skin
with visible pores. Background: heavily compressed, far-out-of-focus stadium
crowd with individual faces indistinct, blurred colored advertising hoardings
with no legible text, deep telephoto bokeh, natural muted clay orange rather
than saturated red. Broadcast video look: Rec.709 color, slight sensor noise,
faint chromatic aberration at the frame edges, mild broadcast softness, no
on-screen graphics.
```

```text
Negative: garbled text, jersey lettering, logos, scoreboard graphics,
watermark, deformed hands, extra fingers, fused fingers, twisted limbs, broken
racket strings, warped racket, distorted crowd faces, plastic skin, airbrushed,
flawless skin, beauty filter, HDR, oversaturated, motion blur on the face, CGI,
3D render, illustration, anime, cartoon
```

**Why it works:**
- Racket strings are a dense repeating structure → the racket head carries the
  only motion blur and sits at the frame edge; negatives back it up with
  `broken racket strings, warped racket`.
- `waist-up` instead of full body — sliding legs on clay were the top
  limb-deformity risk.
- Sponsors exist as `blurred colored advertising hoardings with no legible
  text` — brand feel without generating text.
- `natural muted clay orange rather than saturated red` defuses the
  sun-plus-clay saturation trap (self-check rule 3).
- The scorebug/on-screen graphics were deliberately cut: AI-rendered text
  always breaks the illusion. For full broadcast realism, composite a real
  scorebug PNG in post.
