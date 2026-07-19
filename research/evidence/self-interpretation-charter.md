# Self-Interpretation Charter (Monad v2)

Amends and extends the Monad Constitution (v1) under Article VII.
Adopted 2026-06-20. Governs the self-interpretation track and all new work.

> This charter **implements** the [Researcher-Agent Charter](researcher-agent-charter.md),
> the governing operating constitution. The Researcher-Agent Charter governs
> purpose, epistemics, methodology, and output; this charter governs the
> technical architecture that carries them out.

## Premise (Axiom)

The Quran is taken as the speech of God, its stated Author. This is the
project's premise — not a claim under test. The work does not argue it; it
builds upon it.

## Article A — The Self-Interpreting Thesis

The Quran requires no external reference to be understood. The network of
relations among all its verses is sufficient to interpret and self-translate
it. Discovering this network, and reaching the maximal internally-grounded
understanding, is the goal.

## Article B — The Divine Names (revised 2026-06-20)

1. The names and attributes of God are inscribed in the text — a real,
   internally discovered feature (Phase L2), studied on its own terms.
2. **Original hypothesis, now UNCONFIRMED:** that the names are THE semantic
   anchors / axes of meaning (the computational "law of interpretation"). Two
   independent fair tests — distributional (the thesis test) and structural
   (coverage + centrality) — found no signal that the names organize the
   corpus's meaning beyond word frequency. The claim is therefore **downgraded
   to an unconfirmed hypothesis and is NOT load-bearing.**
3. This concerns the computational model only. Per Article D and the
   Researcher-Agent Charter, the text remains the criterion; the coherence, if
   real, may operate at a level these co-occurrence instruments cannot measure.
   It is **not declared false** — only unsupported by available methods, and
   revisable on new evidence.
4. The names are discovered from the text, never imported; the traditional
   enumeration stays quarantined for the L8 scorecard.

## Article B-2 — Clarity Anchors (muḥkam → mutashābih) [untested design principle]

Clear, decisive verses are the basis for understanding ambiguous ones
(Researcher-Agent Charter §5): interpretation propagates **from high-clarity
(muḥkam) verses to low-clarity (mutashābih) ones**, never the reverse. Clarity
is an internal, measured quantity (attestation, recovery score, construction
commonness). This remains an **untested design principle**, to be validated
before it is relied upon.

## Article B-3 — The Relational Foundation (empirically grounded)

The meaning of a unit is carried by its position in the corpus's internal
**relational network** (context / co-occurrence). This is the empirically
supported basis: held-out masked-root recovery (Phase L3; robustness Test C)
shows the network recovers its own roots from context far above chance. All
meaning layers (L3 onward) build on this relational structure, **with leakage
controls built in from the start.**

## Article C — The Boundary (Internal vs External)

- **Allowed as scaffolding (structure):** the Tanzil text, the Quranic Arabic
  Corpus morphology (segmentation, root identity, grammatical annotation), the
  Buckwalter transliteration map, and sura metadata.
- **Forbidden as input (semantics):** external dictionaries, translations,
  tafsir, theology, pretrained embeddings, external ontologies.
- **Quarantined (final scorecard only):** one external translation and the
  traditional names list. Touched once, at the end, to score alignment. Never
  an input.

## Article D — Fallibility of Human Interpretation

Existing human interpretations (translations, tafsir, name lists) may contain
error. They are never ground truth. Where the internal evidence of the text and
a human reference diverge, the divergence is **flagged for investigation**; the
text's internal evidence governs.

## Article E — The No-Mistake Discipline (Abstention over Error)

"No mistake shall occur" is operationalized as:

1. The system **must abstain** — mark `UNKNOWN` / low-confidence — rather than
   assert beyond its evidence. A confident wrong assertion is the only true
   mistake; abstention is not.
2. Every datum carries a confidence tier — **صریح/explicit (C1) → قوی/strong
   (C2) → محتمل/probable (C3) → نامشخص/unclear (C4 = abstain)** — and full
   provenance `(S:A:W:T)`.
3. Every claim is validated by self-prediction (masked recovery, held-out
   folds, no leakage) and accompanied by a falsification attempt.
4. All processes are deterministic and reproducible (fixed seeds, pinned
   inputs, no network access).

## Article F — Validation (updated 2026-06-20)

- **Primary and sufficient:** internal self-prediction and stability — mask a unit
  and recover it from the rest of the corpus; require results to beat frequency
  baselines and permutation nulls, and to replicate across two independent halves
  of the corpus (held-out). This is the project's standard of proof and, per the
  self-sufficiency premise, is **sufficient on its own**.
- **External scorecard (run once, 2026-06-20 — now closed):** the held-out
  comparison against a human reference (*mutashābihāt*) gave only partial,
  mismatched corroboration — that reference measures phrase-parallels, a different
  relation than the thematic network. External validation is therefore **optional**
  and is not required for the project's conclusions. The internal validation
  carries the proof.

## Article G — Phasing (supersedes Constitution Article V's list for this track)

```
L0 substrate → L1 letters (phonological) → L2 names (anchors) →
L3 roots → L4 words → L5 phrases/clauses → L6 ayat →
L7 sura/whole → L8 self-translation + scorecard
```

Each layer builds only on lower layers and emits, for every datum: provenance,
a confidence tier, and a self-prediction score (or an honest negative result).

## Article H — Purpose-Coherence Re-Test

The Quran's purpose is guidance toward truth, justice, mercy, awareness, and
responsibility (Researcher-Agent Charter, Guidance Principle). These aims are
understood **from the Quran's own usage** (mercy binds to the name anchors of
Article B), never imported. An interpretation that negates a well-attested
guidance-aim is, by default, a likely defect in *our* understanding (Article D,
§§6–7): it triggers a **re-test against the whole Quran** — neither silently
kept nor silently discarded. If full re-test still supports the reading, the
reading stands and our understanding of the aim is revised. The Quran is the
criterion; our grasp of the aim is not.

## Retained from v1

Articles II (source supremacy), III (derivation discipline), IV (epistemic
humility), and VII (revision) remain in force. Article VI's exclusion of
"translation" is amended: **self-derived (internal) translation is now the
goal**; external translation remains excluded as input, allowed only as the
held-out scorecard of Article F.
