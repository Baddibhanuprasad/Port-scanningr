# Smart Agriculture Prototype Video — Script & Shot List

**Structure:** Problem → Solution → How it works (Hardware) → How it works (App) → Impact/Close
**Target length:** 2.5–3.5 minutes
**Tool mix:** Gemini (Veo) for 8-sec generative B-roll clips + your own screen recordings/app mockup footage + voiceover, stitched in CapCut/DaVinci Resolve/Google Vids.

> Note on Gemini/Veo: it generates short (~8 second), independent clips from a text or image prompt, with auto sound. It won't hold characters/scenes consistent across many clips on its own, so keep each generated clip visually simple (a field, a sensor, a farmer's hand, weather) and use your own footage/UI recordings for anything that must look exactly like your product.

---

## PART 1 — THE PROBLEM (0:00–0:35)

**Tone:** documentary, slightly somber, real-world.

**Scene 1.1 (0:00–0:08)**
Visual: Wide shot of a dry, cracked farmland under harsh sun.
Veo prompt: *"Cinematic wide shot of a dry cracked agricultural field under a harsh midday sun, dust in the air, documentary style, natural lighting, no text"*
VO: "Every year, millions of farmers lose their crops — not because they don't work hard, but because they don't know in time."

**Scene 1.2 (0:08–0:16)**
Visual: Close-up of a farmer's hands checking dry soil.
Veo prompt: *"Close-up shot of a farmer's weathered hands crumbling dry soil in a field, documentary realism, warm natural light"*
VO: "They can't tell exactly when soil is too dry, when rain is coming, or when a plant disease has already spread."

**Scene 1.3 (0:16–0:24)**
Visual: A water pump/motor running unattended, wasting water.
Veo prompt: *"Wide shot of an old water irrigation motor pump running in a farm field, water overflowing, daytime, documentary style"*
VO: "Manual irrigation wastes water and labor. A missed weather alert can wipe out an entire harvest."

**Scene 1.4 (0:24–0:35)**
Visual: Farmer looking worried at a wilting crop / phone with no signal.
Veo prompt: *"Farmer standing in a field looking concerned at wilting crops, holding a basic phone, golden hour lighting, documentary style"*
VO: "Most small farmers still rely on guesswork, experience, and luck — not data."

*(Text overlay, no voice): "There has to be a smarter way."*

---

## PART 2 — INTRODUCING THE SOLUTION (0:35–0:50)

**Scene 2.1**
Visual: Your actual hardware prototype (real footage — film this yourself), close-up of the ESP32 boards, sensors, LoRa module.
VO: "Meet [Your Project Name] — a smart agriculture system that senses, decides, and acts, so farmers don't have to guess."

**Scene 2.2**
Visual: Simple animated/diagram overlay (build this as a slide, not Veo) showing: Field Node → LoRa → Main Node → Cloud/App → Farmer.
VO: "Two ESP32 units, a network of sensors, and an app that puts the whole farm in the farmer's pocket."

---

## PART 3 — HOW THE HARDWARE WORKS (0:50–1:40)

**Scene 3.1 — Field Unit**
Visual: Real footage of the field ESP32 + soil sensor being buried in soil.
VO: "The field unit is buried near the crop roots. It constantly measures soil moisture."

**Scene 3.2 — Communication**
Visual: Simple animated diagram (arrow/pulse) between the two ESP32 icons, labeled "LoRa SX1278."
VO: "When the soil dries beyond a safe threshold, it sends a signal over LoRa — long-range, low-power — straight to the main unit."

**Scene 3.3 — Main Unit**
Visual: Real footage of the main ESP32 box with GPS/GPRS/LoRa/rain/humidity sensors.
VO: "The main unit combines that signal with live GPS location, rainfall, and humidity data, then decides what to do next."

**Scene 3.4 — Decision & Action**
Visual: Split screen — phone buzzing with SMS notification / app notification, then a motor switch triggering.
VO: "It notifies the farmer instantly by SMS or app. If there's no response in time, it can turn the motor on automatically — no water wasted, no crop lost to delay."

**Scene 3.5 — Rain Prediction**
Visual: Veo clip of dark rain clouds approaching over a field.
Veo prompt: *"Time-lapse style shot of dark rain clouds approaching over a green agricultural field, cinematic, natural lighting"*
VO: "The rain sensor and weather data also warn farmers before the rain arrives — and logs exactly how many rain-free days the field has gone, so irrigation is never guesswork again."

---

## PART 4 — HOW THE APP WORKS (1:40–2:40)

*(Screen-record your actual app UI/prototype/Figma clickthrough here — this is the most important part, don't use Veo for this.)*

**Scene 4.1 — Setup & Field Analysis**
Visual: App screen — GPS scan → "Analyzing field..." → recommended crop type.
VO: "On setup, the app scans the field's GPS location and analyzes surroundings and historical data to suggest the best-suited crop."

**Scene 4.2 — Live Dashboard**
Visual: Dashboard showing soil moisture %, humidity, rain history, motor status.
VO: "Farmers get a live dashboard — moisture levels, humidity trends, and full irrigation history at a glance."

**Scene 4.3 — Plant Disease Detection**
Visual: User taking a photo of a leaf → app shows disease name + treatment.
VO: "Snap a photo of a sick plant, and the app identifies the disease and suggests a solution."

**Scene 4.4 — Weather Alerts + Govt Schemes**
Visual: Notification screen: "Rain expected in 3 hours" + a schemes list screen.
VO: "It sends rain and weather alerts ahead of time, and keeps farmers informed about government schemes they're eligible for."

**Scene 4.5 — Crop Tracking & Recommendation**
Visual: A simple crop growth timeline screen + "Next season recommendation" card.
VO: "Farmers can track their crop's full lifecycle and get recommendations for what to plant next season."

**Scene 4.6 — Multilingual AI Assistant**
Visual: Chat interface, farmer typing/speaking in a regional language, AI responding.
VO: "And if they're ever unsure, an AI assistant is there — in their own language."

---

## PART 5 — THE IMPACT / CLOSE (2:40–3:00)

**Scene 5.1**
Visual: Veo clip — healthy, thriving green field, sunrise.
Veo prompt: *"Wide cinematic shot of a healthy thriving green crop field at sunrise, drone-style low angle, warm golden light"*
VO: "Less guesswork. Less waste. More harvest."

**Scene 5.2**
Visual: Logo/title card with tagline.
VO: "[Your Project Name] — smart farming, in every farmer's hand."

*(End card: team name, college, contact/QR code)*

---

## Practical tips for filming
- Film the real hardware close-ups yourself with a phone macro shot — it'll look more credible than any AI clip for the actual product.
- Keep every Veo prompt to ONE clear subject/action; don't try to cram your product into the AI clip — use Veo only for generic "problem" B-roll (dry field, clouds, farmer hands) and generic "impact" B-roll (green field, sunrise).
- Record your app UI with screen recording (even a clickable Figma prototype works) rather than trying to generate UI with AI.
- Keep voiceover script timing to ~2.3 words/second average pace so it matches an ~8-second Veo clip length per scene.
- Add simple animated arrows/diagrams (Canva or PowerPoint export) for the "how the hardware talks to itself" parts — clearer than any AI-generated diagram.
