# Finite observation windows for continuous powers of normal operators

Anonymous — version 0.1.0-candidate.

A complete time-dependent observation of a Hilbert-space state can remain stably invertible after shortening its observation window, even when its conditioning becomes much worse. This manuscript proves that qualitative statement for bounded normal operators with a fixed bounded spectral argument convention and finite or countable sensors. It does not promise finite-time sampling algorithms or uniform noise tolerance.

Read [paper.md](paper.md) for the self-contained statement, proof, examples and references; [paper.pdf](paper.pdf) is its typeset counterpart. Start with [CLAIMS.json](CLAIMS.json) and [ASSURANCE.md](ASSURANCE.md) for machine-readable scope and assurance boundaries.

## Replay

Python 3.10 or newer; standard library only. From this directory:

```sh
python3 -B verify_normal_frames.py --output /tmp/normal-example-results.json
python3 -B -O verify_normal_frames.py --output /tmp/normal-example-optimized.json
python3 -B test_verification.py --out /tmp/normal-frames-new-test-run
```

Choose a new test output directory: the test harness refuses an existing directory. Expect seven example groups to pass, then ten normal/optimized positive and deliberately corrupted cases to meet their expected outcomes. Numerical integrations are illustrations; rational series coefficients are exact; neither proves the infinite-dimensional theorem.

## Build

```sh
pandoc paper.md --from=markdown+tex_math_single_backslash --standalone --to=latex --output=paper.tex
pdflatex -interaction=nonstopmode -halt-on-error paper.tex
pdflatex -interaction=nonstopmode -halt-on-error paper.tex
```

Internal editorial re-review is complete; the work remains an unrefereed candidate. DOI: https://doi.org/10.5281/zenodo.23990540. Repository: https://github.com/ipitchford/finite-normal-observation-windows. No external peer review or formal verification is claimed. See [STATUS.md](STATUS.md), [SOURCES.md](SOURCES.md) and [LICENSES.md](LICENSES.md).
