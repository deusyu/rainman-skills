# Phrase Bank — swap-in vocabulary per dimension

Vocabulary to fill the 8-dimension framework. Mix, don't copy wholesale: two
or three specific choices per dimension beat ten generic ones.

## 1. Persona 主体人设

**Life traces** (pick ≥2):
crow's feet · sun-weathered complexion · faint age spots · freckles across the
nose bridge · a faded scar above the eyebrow · deep smile lines · slightly
crooked front teeth · a sunburn line at the collar · calloused hands · chapped
lower lip · faint dark circles

**Asymmetry / individual details** (pick 1 — anti-mean-face):
one eyebrow set slightly higher than the other · an asymmetric smile · a nose
once broken and slightly off-line · one eyelid marginally heavier

**Hair imperfections**:
a few stray strands lifted by the breeze · salt-and-pepper hair combed back
imperfectly · flyaways catching the light · hairline beginning to recede

**Occupation anchors** (identity beats adjectives):
retired investment banker · fencing coach · ceramic artist · line cook · trial
lawyer · marine biologist · orchestra conductor · master carpenter

Ages: always numerals — 23, 34, 47, 58, 72. Never "young/middle-aged/old".

## 2. Fabric 服装材质

**Weave / knit structure words** (mandatory, pick 1):
herringbone · houndstooth · twill · tweed · cable-knit · rib-knit · waffle-knit
· seersucker · corduroy · raw denim · boiled wool · brushed flannel · slubbed
linen

**Weight / hand**: heavy · midweight · crisp · washed-soft · starched

**Wear traces** (pick 1):
natural creasing at the elbows · collar slightly askew · fabric pilling at the
cuffs · damp and clinging at the collar · hem wrinkled from sitting · a soft
visible nap

**Sheen control**: matte wool · dry cotton · unpolished leather. Avoid shiny /
glossy / silk unless the brief demands it.

## 3. Moment 表情瞬间

**Temporal verbs** (mandatory, pick 1):
caught mid-sentence · mid-laugh, the laugh just fading · just turned toward ·
about to speak · exhaling after · caught between expressions · adjusting a
cufflink · tucking hair behind an ear · glancing up from a book

**Gaze anchors** (mandatory, pick 1):
eyes on someone off-frame to the left · gaze resting on the middle distance ·
looking down at his hands · following something beyond the window · eyes locked
on the incoming ball outside the frame

**Micro-expressions**:
the trace of a dry smile · a slight frown of concentration · lips parted
mid-exhale · jaw set with effort

## 4. Lens 镜头构图

**Focal grammar** (focal length decides the picture's character):
- 35mm f/2.8 — environmental storytelling, subject in context
- 50mm f/2 — natural perspective, documentary feel
- 85mm f/1.8–2.2 — classic head-and-shoulders portrait
- 105–135mm f/2 — beauty/editorial compression
- 300–400mm f/2.8–4 — sports/broadcast telephoto compression

**Camera height**: eye level · chest height · slightly below eye level
**Distance**: 1.5 m intimate · 2.5 m portrait · 20 m+ telephoto
**Crop** (limb-risk ascending): extreme close-up · chest-up · waist-up ·
three-quarter · full length (avoid unless briefed)
**Placement**: eyes on the upper-third line · generous negative space on the
left/right · subject slightly off-center following the action

## 5. Light & skin 光线皮肤

**Single motivated key recipes** (pick 1, never mix):
- north-facing window light from camera left, soft falloff, 2:1 ratio
- late-afternoon sun through blinds, hard slatted shadows, 4:1
- overcast open shade, near-shadowless 1.5:1 — MUST add a tonal-separation anchor
- single strip softbox 45° camera right, controlled spill, dark background
- stadium floodlights from high behind, rim light plus bounced fill
- a tungsten practical lamp at frame edge, warm pool of light, rest falling dark

**Skin four-pack** (all four, every time):
visible pores · uneven skin tone · natural oil sheen on the T-zone (elderly:
the natural dryness of aged skin) · fine vellus hair catching the light

**Optional reinforcement**: subsurface scattering on the ear rims · faint
redness around the nostrils · specular sweat highlights (sport)

## 6. Background 背景氛围

**Depth formula**: name near / subject-plane / far elements explicitly, e.g.
"out-of-focus bookshelf edge in the foreground, subject at middle distance, a
practical desk lamp glowing warm in the far background".

**Practical lights**: desk lamp · neon sign far out of focus · string lights ·
lit shop windows

**Air** (use at most ONE contrast-lowering effect):
faint dust motes in the light · thin morning haze

**Bokeh**: smooth optical bokeh · deep telephoto bokeh — never "blurry
background".

## 7. Finishing 画质处理

**Film / color references** (pick exactly 1):
- Kodak Portra 400 — neutral-warm skin, the safe default
- Kodak Portra 800 — dusk, indoor warmth
- Fuji Pro 400H — airy green-cyan, editorial
- Kodak Gold 200 — nostalgic consumer warmth
- Ilford HP5 — B&W reportage
- CineStill 800T — tungsten night, built-in halation
- Rec.709 broadcast color — live TV
- 16mm documentary stock — grit

**Imperfection budget** (pick exactly 2):
fine film grain · subtle lens vignette · slight halation on highlights · faint
chromatic aberration at the frame edges · mild broadcast softness

**Anti-cheap clause** (always append):
muted colors, soft contrast curve, lifted blacks, no HDR look

## 8. Negatives 负面词（四组 + 场景附加）

**plastic-skin 塑料皮肤组**:
plastic skin, airbrushed, waxy skin, beauty filter, flawless skin, glowing
skin, porcelain skin

**cheap-grading 廉价影调组**:
HDR, oversaturated, overexposed, oversharpened, glossy

**anatomy 结构畸形组**:
deformed hands, extra fingers, fused fingers, bad anatomy, distorted face,
twisted limbs, cross-eyed

**non-photo 非摄影组**:
CGI, 3D render, illustration, painting, anime, cartoon, watermark, text, logo

**Scene add-ons 按需附加**:
garbled text · jersey lettering · scoreboard graphics · distorted crowd faces ·
broken racket strings · warped geometry · motion blur on the face

## Negative → positive conversion (Flux / GPT-Image / Nano Banana)

These models have no negative channel — restate as positives inside the main
prompt:

| Negative | Positive replacement |
|---|---|
| plastic skin, airbrushed | skin with visible pores and uneven tone |
| flawless skin | natural oil sheen on the T-zone, fine vellus hair |
| HDR, oversaturated | muted colors, soft contrast curve, lifted blacks, no HDR look |
| oversharpened | one plane of sharp focus, gentle optical falloff |
| beauty filter | unretouched editorial skin texture |
| deformed hands | hands out of frame (or a named object being held) |
| text, logo | plain unbranded garments, no lettering anywhere in frame |
| CGI, 3D render | a photograph with fine film grain and subtle lens vignette |
