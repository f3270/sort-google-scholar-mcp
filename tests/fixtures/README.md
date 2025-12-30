# PDF Fixtures for Testing

## Synthetic Fixtures (Primary)

All synthetic PDFs are generated with `tests/fixtures/generate_fixtures.py`.
The script uses reportlab when available and falls back to PyMuPDF for generation.

To regenerate fixtures:

```bash
python tests/fixtures/generate_fixtures.py
```

- `synthetic_normal.pdf`: 10 pages with repeated lorem text and section markers
- `synthetic_corrupted.pdf`: truncated version of `synthetic_normal.pdf`
- `synthetic_short.pdf`: single-page PDF with short content (< chunk size)
- `synthetic_empty.pdf`: blank PDF with no extractable text

All synthetic content is generated locally and is public domain.
