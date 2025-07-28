# Challenge 1b – Approach Explanation

## Methodology Overview

This solution implements a generic, persona-driven document intelligence pipeline for extracting and prioritizing relevant content from a collection of PDFs. The approach is designed to generalize across domains, personas, and tasks, while remaining lightweight and CPU-friendly.

---

### 1. **Input Parsing and Preprocessing**

- The system reads a `challenge1b_input.json` specifying:
  - The collection of PDF documents (filenames and titles)
  - The persona (role/expertise)
  - The job-to-be-done (task description)
- PDFs are loaded from a specified directory.
- The code uses PyMuPDF to extract page-wise text from each document.

---

### 2. **Section Extraction**

- A simple but effective heuristic is used to identify section headers:
  - Lines that are Title Case, not too short, and not pure numbers are treated as section titles.
  - The following few lines are grouped as a section preview.
- Each section is associated with its document, title, page number, and preview text.

---

### 3. **Semantic Ranking**

- To ensure relevance to the persona and job, each section is ranked by semantic similarity:
  - The persona and job-to-be-done are concatenated into a single query string.
  - Both query and section texts are embedded using a compact sentence-transformer model (`all-MiniLM-L6-v2`, <100MB, CPU-friendly).
  - Cosine similarity scores are computed; the top-ranked sections are selected for output.
- This semantic approach allows the system to generalize to new domains and tasks.

---

### 4. **Subsection Analysis**

- For each top-ranked section, further refinement is done:
  - The section preview text is split into smaller units (paragraphs or bullet points).
  - The top few refined snippets are selected for the `subsection_analysis`.
- This allows more granular, focused suggestions for the end-user.

---

### 5. **Output Formatting**

- The system outputs a structured JSON with:
  - Metadata (input docs, persona, job, timestamp)
  - The top relevant sections (with document, title, importance rank, page number)
  - Subsection analysis (granular text, doc, page)
- The pipeline runs offline, on CPU, and processes 3–5 documents within 60 seconds.

---

### 6. **Portability & Extensibility**

- The solution is packaged with a Dockerfile for reproducible, dependency-controlled execution.
- The methodology is modular, allowing easy customization for different document types or extraction heuristics.