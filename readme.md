# Challenge 1b: Persona-Driven Document Intelligence

## Directory Structure

```
Challenge_1b/
├── Collection_1/
│   ├── PDFs/
│   │   ├── doc1.pdf
│   │   └── doc2.pdf
│   ├── challenge1b_input.json
│   └── challenge1b_output.json
├── main.py
├── requirements.txt
├── Dockerfile
├── approach_explanation.md
└── README.md
```

## Local Setup Instructions

### 1. **Install Python and Dependencies**

- Install Python 3.8+.
- Install dependencies:
  ```bash
  pip install -r requirements.txt
  ```

### 2. **Prepare Data**

- Place your PDFs in the relevant `PDFs/` directory in each collection folder.
- Edit `challenge1b_input.json` in the collection folder to reference those PDFs and specify persona and job.

### 3. **Run the Analysis**

From the project root:
```bash
python main.py --input Collection_1/challenge1b_input.json --pdf_dir Collection_1/PDFs --output Collection_1/challenge1b_output.json
```
Change `Collection_1` as appropriate.

### 4. **Check Results**

- Results will be written to `challenge1b_output.json` in the collection folder.
- Output includes metadata, extracted_sections, and subsection_analysis.

---

## Docker Usage (Optional)

1. **Build Docker Image**
   ```bash
   docker build -t challenge1b .
   ```

2. **Run Container**
   ```bash
   docker run --rm -v $(pwd)/Collection_1:/data challenge1b \
       --input /data/challenge1b_input.json --pdf_dir /data/PDFs --output /data/challenge1b_output.json
   ```

---

**Methodology is detailed in `approach_explanation.md`.**