# AI navigation index

## Statement and status

[paper.md](paper.md), Theorem 2.1, states finite-window invariance for bounded normal operators. Definitions in Section 2 specify the spectral branch, sensor countability and two-sided integrated frame premise. [STATUS.md](STATUS.md) identifies the unrefereed candidate; [CLAIMS.json](CLAIMS.json) separates theorem, auxiliary estimate, examples and elementary consequences.

## Proof and evidence

[paper.md](paper.md) Sections 3–5 provide the complete analytic proof. Section 6 gives sharp scope examples and the delayed-window criterion. [verify_normal_frames.py](verify_normal_frames.py) checks exact rational expansion coefficients and finite numerical illustrations. [test_verification.py](test_verification.py) reruns normal/optimized code with semantic corruptions. [README.md](README.md) gives replay/build commands and expected results; [ENVIRONMENT.txt](ENVIRONMENT.txt) records requirements.

## Trust boundaries

[ASSURANCE.md](ASSURANCE.md) distinguishes proof from finite exact arithmetic, numerical evidence, internal checking and unperformed formal/human verification. [SOURCES.md](SOURCES.md) and [CITATION_AUDIT.md](CITATION_AUDIT.md) map references and bounded search limitations. [RESEARCH_GATES.json](RESEARCH_GATES.json) records contributions, limitations and extension choices, not automatic proof validity.

## Provenance and rights

[PROVENANCE.md](PROVENANCE.md) records anonymous authorship and AI assistance. [LICENSES.md](LICENSES.md) maps original prose/data to CC0 and original code to MIT. No private reports or third-party full texts are shipped. [MANIFEST.sha256](MANIFEST.sha256) identifies package bytes; hashes are integrity evidence, not proof verification.
