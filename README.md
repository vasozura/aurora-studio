# Aurora Studio

Aurora Studio is the implementation repository for the Aurora AI filmmaking system.

The source of truth for requirements is the separate specification repository:

```text
aurora-spec
```

This repository is currently a minimal implementation skeleton.

## Current Status

This skeleton is not feature-complete.

It does not include:

- GUI implementation
- Database implementation
- AI provider integration
- Prompt export implementation
- Plugin execution
- Video generation
- Asset processing
- Scene editing behavior
- Shot editing behavior

## Runtime Dependencies

The runtime skeleton uses Python standard library only.

No external runtime dependencies are required.

## Python Version

```text
Python 3.11+
```

## Run Tests

From the repository root:

```bash
python -m unittest
```

## Specification Authority

Implementation must follow `aurora-spec`.

Do not implement features unless a controlled implementation task explicitly authorizes the work.
