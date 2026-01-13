# How to use these files in Overleaf

To use the drafted report in Overleaf, follow these steps:

1. **Log in to Overleaf**: Go to [https://www.overleaf.com](https://www.overleaf.com).
2. **Create a New Project**: Click on "New Project" -> "Blank Project". Name it (e.g., "Intent-Based Security Report").
3. **Upload Files**:
   - Upload `main.tex` and `references.bib` from the `report/` folder.
   - **Create a 'docs' folder**: In the Overleaf file browser, create a folder named `docs`.
   - **Upload Images**: Upload all images from your local `docs/` folder (`intent_01.png`, `intent_02.png`, `intent_03.png`, `zero-downtime.png`) into the `docs` folder in Overleaf.
4. **Compile**: Click the "Recompile" button in Overleaf.

## Applied Specifications:
- **Font**: Times New Roman equivalent (`times` package).
- **Size**: 12pt.
- **Margins**: 2.5cm (`geometry` package).
- **Spacing**: 1.5 line spacing (`setspace` package).
- **Citations**: IEEE style (`biblatex` with `ieee` style).
