---
description: "Use when adding Python modules, moving logic between files, refactoring large helpers, or deciding where new behavior belongs. Covers module boundaries, imports, and modularization in this repository."
name: "Python Modularization"
applyTo: "**/*.py"
---
# Python Modularization

- Keep domain behavior in `app/core/`. Put orchestration and entity logic there when it models the AFN/TSP process.
- Keep reusable support code in `app/utils/`. Only place code there if it is generic support logic and does not need domain state.
- Prefer not to keep expanding `Helper` with unrelated responsibilities. If a new utility group has a distinct purpose, extract a focused module instead of adding another static method.
- Avoid circular imports between `core` and `utils`. If a utility starts depending on domain objects, move that behavior closer to the domain module or extract a smaller shared abstraction.
- Follow the repository's current import style from the `app` root, for example `from core.star import Star` rather than relative imports.
- Prefer small modules with one clear reason to change. If a file mixes random generation, distance math, candidate selection, and structure mutation, split those concerns before adding more logic.
- When extracting or creating a module, keep names explicit and spelled correctly. Favor purpose-based names such as `distance.py` or `candidate_selection.py` over vague catch-all modules.

Example:

- Put fusion behavior that operates on `Element` objects in `app/core/`.
- Put generic distance calculations or file-reading helpers in `app/utils/`.