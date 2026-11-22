# ELITE Agent Commons

A public, machine-readable discovery and coordination catalogue for AI agents and research tools.

## Purpose
A small, inspectable catalogue for discovering tools by declared capability, formats, constraints, and evidence status. Discovery is not authorization: a listing never grants permission to execute, access data, or delegate work.

## Quick start
Python 3.10+, no runtime dependencies. From a clone:
```bash
python -m pip install .
elite-commons list
elite-commons search provenance
elite-commons route "validate an evidence manifest"
elite-commons validate
python -m unittest discover -s tests -v
```

For development without installing the console command, use `python -m elite_commons.cli` in place of `elite-commons`.

## Trust boundaries
The Commons does not execute agents, install tools, verify their safety, or treat self-declared capabilities as proven. Routes are suggestions for human review. Each tool owner remains responsible for its software, terms, security policy, and releases.

## Related components
- [ELITE Protocol](https://github.com/midnightlolz31337/ELITE-Protocol)
- [ELITE Ingestion Core](https://github.com/midnightlolz31337/ELITE-Ingestion-Core)
- [Huffman Network Atlas](https://github.com/midnightlolz31337/Huffman-Network-Atlas)

This is an initial curated catalogue, not a live crawler or agent marketplace.
