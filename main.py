import os
import json
import time
import re
from typing import List, Dict, Any
import fitz  # PyMuPDF
from sentence_transformers import SentenceTransformer, util


def load_input_json(input_json_path: str) -> Dict[str, Any]:
    if not os.path.exists(input_json_path):
        raise FileNotFoundError(f"Input JSON file not found: {input_json_path}")
    with open(input_json_path, "r", encoding="utf-8") as f:
        return json.load(f)


def extract_sections_from_pdf(pdf_path: str) -> List[Dict]:
    sections = []
    try:
        doc = fitz.open(pdf_path)
    except Exception as e:
        print(f"Error opening PDF {pdf_path}: {e}")
        return sections

    for page_num, page in enumerate(doc, start=1):
        text = page.get_text("text")
        lines = text.split("\n")
        for idx, line in enumerate(lines):
            clean_line = line.strip()
            # Heuristic for section headings
            if (
                len(clean_line) > 6
                and not clean_line.isdigit()
                and clean_line[0].isupper()
                and re.match(r"^[A-Za-z0-9 ,\-:'&]+$", clean_line)
            ):
                # Capture next 5 lines for context
                content = []
                for j in range(1, 6):
                    if idx + j < len(lines):
                        content.append(lines[idx + j])
                sections.append({
                    "title": clean_line,
                    "page_number": page_num,
                    "text": "\n".join(content)
                })
    return sections


def extract_subsections(section_text: str) -> List[str]:
    candidates = re.split(r'\n\s*\n|•\s+', section_text)
    return [c.strip() for c in candidates if len(c.strip()) > 25]


def get_model():
    try:
        return SentenceTransformer("all-MiniLM-L6-v2", device="cpu")
    except Exception as e:
        print(f"Model loading failed: {e}")
        raise


def rank_sections(sections: List[Dict], persona: str, job_to_be_done: str, model, top_k: int = 6) -> List[Dict]:
    if not sections:
        return []
    query = f"{persona}: {job_to_be_done}"
    corpus = [f"{s['title']}. {s['text']}" for s in sections]
    query_emb = model.encode([query], convert_to_tensor=True)
    corpus_emb = model.encode(corpus, convert_to_tensor=True)
    scores = util.cos_sim(query_emb, corpus_emb)[0].cpu().tolist()
    zipped = sorted(zip(sections, scores), key=lambda x: x[1], reverse=True)[:min(top_k, len(sections))]
    for rank, (section, score) in enumerate(zipped, 1):
        section['importance_rank'] = rank
        section['score'] = round(score, 4)
    return [z[0] for z in zipped]


def main(input_json_path: str, pdf_dir: str, output_json_path: str):
    input_data = load_input_json(input_json_path)
    persona = input_data["persona"]["role"]
    job = input_data["job_to_be_done"]["task"]
    docs = input_data["documents"]
    doc_files = [os.path.join(pdf_dir, d["filename"]) for d in docs]

    model = get_model()
    all_sections = []

    for doc_info, pdf_path in zip(docs, doc_files):
        if not os.path.exists(pdf_path):
            print(f"PDF not found: {pdf_path}")
            continue
        sections = extract_sections_from_pdf(pdf_path)
        for s in sections:
            s['document'] = doc_info["filename"]
        all_sections.extend(sections)

    ranked_sections = rank_sections(all_sections, persona, job, model, top_k=8)

    extracted_sections = [{
        "document": s["document"],
        "section_title": s["title"],
        "importance_rank": s["importance_rank"],
        "page_number": s["page_number"]
    } for s in ranked_sections]

    subsection_analysis = []
    for s in ranked_sections:
        subsections = extract_subsections(s.get("text", ""))
        for para in subsections[:2]:
            subsection_analysis.append({
                "document": s["document"],
                "refined_text": para,
                "page_number": s["page_number"]
            })

    output = {
        "metadata": {
            "input_documents": [d["filename"] for d in docs],
            "persona": persona,
            "job_to_be_done": job,
            "processing_timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        },
        "extracted_sections": extracted_sections,
        "subsection_analysis": subsection_analysis
    }

    with open(output_json_path, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)

    print(f"\n✅ Analysis complete! Output saved to {output_json_path}")


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Persona-Driven PDF Document Analyzer (Challenge 1B)")
    parser.add_argument("--input", required=True, help="Path to challenge1b_input.json")
    parser.add_argument("--pdf_dir", required=True, help="Directory containing PDFs")
    parser.add_argument("--output", required=True, help="Path to output JSON")
    args = parser.parse_args()
    main(args.input, args.pdf_dir, args.output)
