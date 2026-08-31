# Template validation annotations investigation

## Attempt 1 — Match the annotation count to test paths

**Hypothesis:** The eight annotations are expected operational-failure diagnostics emitted by tests, rather than eight failing assertions.

**Action:** Compared the screenshot messages with `::error::` output in `panopticon/drift.py`, `panopticon/currency.py`, and `panopticon/diagram_check.py`, then counted the corresponding `main()` tests.

**Result:** The count matches exactly: doc-drift has three operational-failure tests, index-currency has three, and diagram-existence has two unsupported-format tests. Each invokes a CLI `main()` function that prints a GitHub `::error::` command.

**Next step:** Capture CLI stdout in those test helpers so expected failure-path output cannot become workflow annotations.

## Attempt 2 — Inspect workflow scope

**Hypothesis:** The template-validation workflow runs the affected tests directly and does not filter GitHub command output.

**Action:** Read `.github/workflows/template-validation.yml` and the three test helpers.

**Result:** The workflow runs `python3 -m unittest discover -t . -s tests`; the helpers returned `main(argv)` directly, allowing expected `::error::` lines to reach the runner.

**Next step:** Apply the minimal harness fix and run the targeted tests, then the full test suite.

## Attempt 3 — Capture expected CLI diagnostics

**Hypothesis:** Capturing and asserting stdout around each affected test helper will verify the user-facing failure while preventing GitHub annotation commands from reaching the workflow runner.

**Action:** Wrapped the doc-drift, index-currency, diagram-existence, interface-merge, and dependency-merge `main(argv)` calls in `contextlib.redirect_stdout(io.StringIO())`, retained the captured text, and asserted the expected failure diagnostics.

**Result:** The targeted suite passed 48 tests and the full suite passed 778 tests. `git diff --check` and Markdown lint also passed; the affected tests verify their failure diagnostics while no longer emitting the eight annotation lines.

**Next step:** None; the validation annotation noise is fixed.

## Attempt 4 — Reproduce OKF-enabled instance bootstrap failure

**Hypothesis:** The OKF-enabled instance fails because the public launcher's
in-memory default-payload loader does not register the newly imported feature
registry module before evaluating `panopticon.bootstrap`.

**Action:** Traced `_load_default_payload_from_github` and reproduced the
reported import path with a regression fixture whose bootstrap imports
`panopticon.features`.

**Result:** The regression failed with `ModuleNotFoundError: No module named
'panopticon.features'`, confirming the loader's dependency registration was
incomplete.

**Next step:** Register and execute `panopticon.features` before
`panopticon.bootstrap`, then run the focused installer tests and the complete
test suite.

## Attempt 5 — Register the feature registry dependency

**Hypothesis:** Loading `panopticon.features` into the synthetic package before
bootstrap evaluation will allow an OKF-enabled synced instance to start.

**Action:** Added the dependency registration to `install.py`, changed the
fixture to use the real `panopticon/features.py` source, and ran the focused
installer tests followed by the complete test suite.

**Result:** The focused tests passed 4/4 and the complete suite passed 778/778.

**Next step:** None; the reported missing-module failure is covered by a
regression test and resolved at the loader boundary.
