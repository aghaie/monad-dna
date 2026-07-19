# The Quran's Self-Interpreting Network — Complete Findings Reference

> Canonical reference for the validated phenomenon. Written to be the basis of
> future prompts. Everything here is internal (no external semantics), reproducible
> (byte-identical), and leakage-controlled. Numbers are exact as produced.
> Date: 2026-06. Supersedes the legacy `docs/` report track for what is *validated*.

---

## 0. How to use this document

- **Build on Section 2–4** (the validated network). These are the confirmed facts.
- **Respect Section 5** (the falsified premises) — do not rebuild on them.
- **Section 7** = how to extend this for new work.
- When in doubt, the **method** (Section 1) is the real asset: it tells you how to
  validate any new claim so it earns the same trust.

---

## 1. The phenomenon, stated precisely

**Claim (confirmed):** The Quran is *self-interpreting at the level of the
relational network of roots across verses*. Concretely:

> The set of verses is a weighted graph whose edges are **shared content roots**
> (weighted toward rare, specific roots). This graph carries real, non-random,
> stable structure: verses predict one another's content, that structure
> organizes into suras, and the meanings it encodes replicate across independent
> halves of the corpus — **all derivable from the text alone.**

**Where meaning does and does not live:**
- ✅ at the **root** (concept) level, and in the **network of co-occurrence across
  verses**.
- ❌ not in individual **letters**, not in **word-forms** beyond the root, and
  (per fair test) **not** organized by the **divine names as semantic axes**.

---

## 2. The method (the real asset — how anything here earned trust)

Every claim was put through the same discipline. To trust a *new* claim, do the same:

1. **Internal only.** Input = the corpus (Tanzil text + Quranic Arabic Corpus
   morphology) and structures derived from it. No dictionary/translation/tafsir as
   input. Buckwalter↔Arabic is structural transliteration only.
2. **Baseline.** Beat the obvious null (most-frequent answer / frequency).
3. **Permutation null.** Destroy the claimed structure (shuffle labels/contexts);
   the real effect must sit far outside the null distribution (report empirical p).
4. **Leakage control.** Ensure the model can't see the answer it's predicting
   (e.g. hold the root fixed; remove the target's own root; cross-sura only).
5. **Held-out.** k-fold or split; never score on training data.
6. **Reproducibility.** Fixed seeds, no network; a re-run is byte-identical
   (`validate_*.py` checks this).
7. **Abstention + tiers.** Mark UNKNOWN where evidence is absent; tag every datum
   صریح/قوی/محتمل/نامشخص with provenance `(sura:ayah[:word:token])`.
8. **Honest negatives.** A failed test is recorded as a finding, not hidden.

---

## 3. The evidence — four validated positives

### L3 — Roots carry relational meaning
- **Task:** mask a content root in an ayah; recover it from the other roots
  (root–root PPMI). Held-out 5-fold, 35,596 instances, 1,635 candidate roots.
- **Result:** model **9.70% top-1 / 17.73% top-3** vs baseline 3.54% / 8.68% vs
  random 0.061%.
- **Robustness (decisive):** with a *random* (mismatched) context the score
  collapses to **0.18%**; with the true context it is **4.93%** (single split),
  p=0.048 → the signal is genuinely contextual, not frequency.
- **Artifacts:** `scripts/build_L3_roots.py`, `generated/layers/L3_roots/`,
  `docs/L3-roots-report.md`, `docs/L2-L3-robustness-report.md`.

### L6 — Verses explain one another (the heart of the thesis)
- **Task (leakage-controlled):** split an ayah's roots into KEY/TARGET; find its
  top-10 neighbours using only the KEY roots and only from **other suras**; test
  whether those neighbours contain the TARGET roots (never used to find them) more
  than 10 random ayat do. 4,509 ayat, 200-permutation null.
- **Result:** ALL target roots **0.545 vs random 0.325** (max null 0.334),
  p=0.005. **RARE** target roots (the strict test) **0.200 vs random 0.019**
  (max 0.030), p=0.005 — **~10×**.
- **Meaning:** knowing half a verse lets the corpus's own network locate verses
  across the Quran that supply the other half, especially the rare/meaningful
  content. This is *tafsīr al-Qurʾān bi-l-Qurʾān*, measured.
- **Artifacts:** `scripts/build_L6_network.py`, `generated/layers/L6_network/`,
  `docs/L6-network-report.md`.

### L7 — Suras are coherent communities + the cross-reference map
- **Task:** build the global rare-root-weighted ayah graph; test whether
  connections concentrate within suras vs a sura-label permutation null (200×).
- **Result:** intra-sura weight fraction **0.052 vs null 0.017** (max 0.0185),
  p=0.005 — **~3×**. Suras are real network communities, not arbitrary groupings.
- **Product:** `crossref_index.json` — for every ayah, the verses that most
  explain it (the Quran-by-Quran map). *(Caveat: raw "hub" verses are
  length-dominated; reported descriptively.)*
- **Artifacts:** `scripts/build_L7_global.py`, `generated/layers/L7_global/`,
  `docs/L7-global-report.md`.

### L8 — Self-derived meanings are stable + real self-tafsir
- **Task:** split the corpus into two independent halves; for each well-attested
  root compute its top-10 co-root associates in each half; measure agreement
  (Jaccard) vs mismatched roots. 512 roots, 200-permutation null.
- **Result:** real **0.119 vs mismatched 0.012** (max 0.016), p=0.005 — **~10×**.
  A concept's meaning-neighbourhood replicates across independent halves → the
  meanings are reliable, not noise.
- **Artifacts:** `scripts/build_L8_interpret.py`, `generated/layers/L8_interpret/`,
  `docs/L8-interpret-report.md`.

---

## 4. Concrete self-tafsir (zero external input)

| Verse | Linked verse | Shared concept-root |
|---|---|---|
| 2:255 Āyat al-Kursī — "no slumber nor sleep" | 7:97 | **نوم** sleep |
| 24:35 Light Verse — "neither east nor west" | 7:137 | **شرق · غرب · برك** east/west/blessing |
| 3:7 — "in whose hearts is deviation" | 9:117 | **زيغ** deviation |
| 17:1 Isrāʾ — "whose surroundings We blessed" | 27:8 | **حول · برك** around/blessing |
| 96:1 "Read!" | 2:228 | **قرأ** read |
| 53:1 "By the star" | 6:97 | **نجم** star |

---

## 5. What was tested and FALSIFIED (do not rebuild on these)

- **Name-anchoring** — the founding premise that the divine names are the semantic
  axes / "law of interpretation". **Two independent fair tests, both negative:**
  - *Distributional, leakage-free:* predict an ayah's sealing name from its content
    (all name-roots removed) — exact-name **11.4% vs 21.6% baseline** (worse);
    family-level model ties/loses (k=3 71.9 vs 76.9; k=5 48.0 vs 45.7).
  - *Structural:* do the 16 name-roots cover concepts better than frequency-matched
    random word-sets? **coverage 0.523 vs null 0.599, p=0.96 (no);** are they more
    central? **0.881 vs 0.873, p=0.33 (no, only as much as any frequent word).**
  - **Honest framing:** *not declared false* — it may operate at a level
    word-co-occurrence cannot see; the text remains the criterion. **Downgraded** to
    an unconfirmed hypothesis (Charter Art. B). The earlier L2 "support" (30.9%) was
    shown to be ~all **leakage** (the name's own root repeating in the ayah).
  - *Useful by-product:* 16 names *were* discovered internally (غفور علیم رحیم حکیم
    سمیع خبیر واسع قدیر حلیم بصیر عفوّ رؤوف قوی محیط شهید وکیل) — kept as a studied
    feature, not the axis.
- **Letters** (L1) — masked middle-radical recovery **2.25% vs 9.24% baseline**
  (below baseline). Letters give *structural* constraints only (OCP is real:
  R1=R2 ratio 0.00, R2=R3 1.87, R1=R3 0.12), no semantic signal. (Hamzated count
  **abstained** — QAC normalizes hamza→alif.)
- **Word-forms** (L4) — within-root form disambiguation from context **59.8%
  (ayah) / 57.6% (local) vs 62.1% baseline** → no signal beyond the root.

> **Why this matters for future prompts:** the project's most valuable move was
> *letting these go honestly.* Don't reintroduce name-axis or letter-semantics
> assumptions without a fair, leakage-controlled test that beats them.

---

## 6. External scorecard (one-time, quarantined) — partial, mismatched

Compared the network to a human reference (mutashābihāt, `external/`). Recall:
rare-concept **14–31× above chance** but low absolute (~5%); all-root surface
~11%. Diagnosis: that reference measures **phrase/sequence parallels** (for
memorisers), a *different* relation than our thematic network → mismatched
yardstick. **Standing conclusion (Charter Art. F): internal self-validation
(esp. L8 stability) is the standard and is sufficient; external validation is
optional.**

---

## 7. Related meaningful findings

- **Book audit — Jannatkhah, *نظریهٔ آزادی، ایران و دین*** (`docs/book-quran-grounding-audit/`,
  `generated/book-quran-audit/`, `scripts/book_audit_*.py`). Tested the claim that
  its axioms are Quran-based, using only the internal network. **Verdict: rationally
  axiomatized and Quran-confirmed, *not* Quran-axiomatized.** Q1: 42/42 cited
  verses real & faithful. Q2: 3 underived axioms are secular-rational (67% derivable
  with no theology); 7 theological axioms are derived & verse-anchored. Q3: the
  cited verse-set is **4.17× more root-coherent than chance (p=0.0003)**, co-citations
  8–12×, 33× L6 adjacency → genuine context, not proof-texting. F-series: F1
  consistent = SUPPORTED (network consistency 0.95, 0/6,832 surviving
  contradictions); F3 "formal" = NO (31/100, proto-formal); F4 CFS-inheritance =
  NOT SUPPORTED (reference ≠ entailment).
- **Legacy observation (not re-validated):** "engine vs book" — the Quran leans a
  **process/command register** over a static repository (process verb-aspect 52.7%,
  1,876 imperatives, 1,049 conditionals). Suggestive; re-test under current
  discipline before relying on it.
- **Method assets:** the **Generative Kernel** (`docs/هستهٔ-مولد.md`) and worked
  applications to city-planning and commerce (`docs/مثال-کاربرد-*.md`) — the
  reusable, domain-independent methodology this project produced.

---

## 8. Limits & open questions

- The network captures **lexical/conceptual relatedness** (which verses are
  related, via which concepts) — **not** word-for-word translation, which would
  require an external language bridge (forbidden as input).
- "Hub" centrality is confounded by verse length; needs length-normalisation to be
  meaningful.
- Open: a *non-distributional* (structural/semantic) test of the name-coherence
  principle; a thematic (tafsir-based) external reference; syntactic (treebank)
  data to revisit word-form meaning; turning the cross-reference map into an
  interactive study tool.

---

## 9. How to build on this (for future prompts)

- **The data is ready:** `crossref_index.json` (verse→explaining-verses) and the
  L3/L8 root lexicons are usable now — e.g. an interactive "Quran-by-Quran"
  explorer, a concept-network browser, a "candidate novel cross-reference" tool
  (flag as hypotheses, not rulings).
- **Anchor new claims to Section 2's method.** Any new finding must beat baseline,
  survive a permutation null, control leakage, and reproduce byte-identically —
  otherwise it is suggestive, not validated.
- **Keep the criterion external to the tool:** the text/data governs; downgrade
  cherished hypotheses when the data doesn't support them (as we did with
  name-anchoring).

والحمد لله رب العالمین.
