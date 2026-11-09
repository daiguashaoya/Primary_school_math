# Project guidance

- This is a static Chinese primary school mathematics teaching site for GitHub Pages.
- The content sources are Markdown documents and `content/catalog.json`. Run `python scripts/build_site.py` after content or template changes and commit the generated HTML pages too.
- Keep all website asset and internal links relative so the site works under `/Primary_school_math/` as well as at localhost.
- Use the `preparation` category for preparation materials and `chapters` for actual classroom chapters. Do not publish invented lesson progress or example catalog entries as completed content.
- Preserve the user's original paper, PDF and existing teaching material. Verify mathematical results before changing them. Adapt explanations to the student's stated grade and prior knowledge.
- `_核对过程/` and `.local/` are local intermediate outputs and must stay ignored.
- The PDF and original printable HTML are independently maintained resources. Do not claim that the site build refreshes them.
- Use Python standard library for the site generator. Keep the site readable without JavaScript and keep mobile navigation, search, local links and print layouts usable.
