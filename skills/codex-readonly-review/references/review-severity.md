# Review severity

Use these thresholds only for findings supported by concrete triggering evidence and impact.

- `P0 — Critical`: immediate catastrophic security, data, availability, or safety impact.
- `P1 — High`: likely production breakage, exploitable vulnerability, or major data/correctness failure.
- `P2 — Medium`: real defect with bounded impact or a credible regression in common use.
- `P3 — Low`: limited-impact defect or maintainability issue with a concrete failure mode.

Choose the highest severity supported by the observed evidence and impact, not by a hypothetical worst case. Unsupported speculation and style preference alone are not findings.
