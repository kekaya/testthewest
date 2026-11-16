import os
import sys
import tempfile
import difflib
from pptx import Presentation

try:
    import comtypes.client
    HAS_COM = True
except ImportError:
    HAS_COM = False

def extract_text(slide):
    text_runs = []
    for shape in slide.shapes:
        if shape.has_text_frame:
            for paragraph in shape.text_frame.paragraphs:
                for run in paragraph.runs:
                    text_runs.append(run.text)
    return "\n".join(text_runs)

def export_slides_to_images(pptx_path, output_dir):
    images = {}
    if not HAS_COM:
        return images
    
    abs_pptx = os.path.abspath(pptx_path)
    abs_out = os.path.abspath(output_dir)
    os.makedirs(abs_out, exist_ok=True)
    
    powerpoint = None
    presentation = None
    try:
        powerpoint = comtypes.client.CreateObject("Powerpoint.Application")
        presentation = powerpoint.Presentations.Open(abs_pptx, WithWindow=False)
        for i, slide in enumerate(presentation.Slides, start=1):
            img_path = os.path.join(abs_out, f"slide_{i}.png")
            slide.Export(img_path, "PNG")
            images[i] = img_path
        presentation.Close()
    except Exception as e:
        print(f"Hinweis: Konnte keine Vorschaubilder exportieren ({e}).")
    finally:
        if presentation:
            try: presentation.Close()
            except: pass
        if powerpoint:
            try: powerpoint.Quit()
            except: pass
            
    return images

def load_conf(conf_path):
    pairs = []
    if os.path.exists(conf_path):
        with open(conf_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith('#'):
                    continue
                parts = line.split()
                if len(parts) >= 2:
                    try:
                        pairs.append((int(parts[0]), int(parts[1])))
                    except ValueError:
                        pass
    return pairs

def main():
    args = sys.argv[1:]
    if not args:
        print("Fehler: Bitte mindestens eine PowerPoint-Datei per Drag-and-Drop übergeben.")
        return

    ppt1_path = args[0]
    ppt2_path = args[1] if len(args) > 1 else None

    prs1 = Presentation(ppt1_path)
    slides1 = list(prs1.slides)
    
    prs2 = Presentation(ppt2_path) if ppt2_path else None
    slides2 = list(prs2.slides) if prs2 else []

    img_dir = tempfile.mkdtemp(prefix="ppt_img_")
    imgs1 = export_slides_to_images(ppt1_path, os.path.join(img_dir, "ppt1"))
    imgs2 = export_slides_to_images(ppt2_path, os.path.join(img_dir, "ppt2")) if ppt2_path else {}

    conf_pairs = load_conf("powerpoint.conf")
    comparisons = []

    if conf_pairs and ppt2_path:
        for s1_idx, s2_idx in conf_pairs:
            t1 = extract_text(slides1[s1_idx - 1]) if 0 < s1_idx <= len(slides1) else ""
            t2 = extract_text(slides2[s2_idx - 1]) if 0 < s2_idx <= len(slides2) else ""
            i1 = imgs1.get(s1_idx, "")
            i2 = imgs2.get(s2_idx, "")
            
            diff = difflib.unified_diff(t1.splitlines(), t2.splitlines(), lineterm='')
            delta = "\n".join(diff)
            comparisons.append((s1_idx, s2_idx, t1, t2, i1, i2, delta))
    else:
        max_slides = max(len(slides1), len(slides2)) if ppt2_path else len(slides1)
        for idx in range(1, max_slides + 1):
            t1 = extract_text(slides1[idx - 1]) if idx <= len(slides1) else ""
            t2 = extract_text(slides2[idx - 1] if ppt2_path and idx <= len(slides2) else "") if ppt2_path else ""
            i1 = imgs1.get(idx, "")
            i2 = imgs2.get(idx, "") if ppt2_path else ""
            
            delta = ""
            if ppt2_path:
                diff = difflib.unified_diff(t1.splitlines(), t2.splitlines(), lineterm='')
                delta = "\n".join(diff)
                
            comparisons.append((idx, idx if ppt2_path else None, t1, t2, i1, i2, delta))

    html_output = "ppt_integrity_report.html"
    with open(html_output, "w", encoding="utf-8") as f:
        f.write("<!DOCTYPE html>\n<html>\n<head>\n<meta charset=\"utf-8\">\n")
        f.write("<title>PowerPoint Integrity Report</title>\n")
        f.write("<style>\n")
        f.write("body { font-family: Arial, sans-serif; margin: 20px; background: #f9f9f9; }\n")
        f.write("table { width: 100%; border-collapse: collapse; background: white; box-shadow: 0 2px 5px rgba(0,0,0,0.1); }\n")
        f.write("th, td { border: 1px solid #ddd; padding: 10px; vertical-align: top; }\n")
        f.write("th { background-color: #007acc; color: white; }\n")
        f.write("img { max-width: 220px; height: auto; border: 1px solid #ccc; }\n")
        f.write("pre { white-space: pre-wrap; word-wrap: break-word; background: #f4f4f4; padding: 6px; }\n")
        f.write(".diff { color: #c0392b; font-family: monospace; }\n")
        f.write("</style>\n</head>\n<body>\n")
        f.write("<h1>PowerPoint Integrity & Comparison Report</h1>\n")
        f.write("<table>\n<thead>\n<tr>\n")
        
        if ppt2_path:
            f.write("<th>Slide PPT 1 (Bild)</th><th>Slide PPT 1 (Text)</th>\n")
            f.write("<th>Slide PPT 2 (Bild)</th><th>Slide PPT 2 (Text)</th>\n")
            f.write("<th>Text Delta</th>\n")
        else:
            f.write("<th>Slide Nr</th><th>Bild</th><th>Text</th>\n")
            
        f.write("</tr>\n</thead>\n<tbody>\n")
        
        for item in comparisons:
            s1_no, s2_no, t1, t2, i1, i2, delta = item
            f.write("<tr>\n")
            if ppt2_path:
                img_rel1 = os.path.relpath(i1, os.path.dirname(os.path.abspath(html_output))) if i1 else ""
                img_rel2 = os.path.relpath(i2, os.path.dirname(os.path.abspath(html_output))) if i2 else ""
                f.write(f"<td><b>#{s1_no}</b><br>{f'<img src=\"{img_rel1}\">' if i1 else 'Kein Bild'}</td>\n")
                f.write(f"<td><pre>{t1}</pre></td>\n")
                f.write(f"<td><b>#{s2_no}</b><br>{f'<img src=\"{img_rel2}\">' if i2 else 'Kein Bild'}</td>\n")
                f.write(f"<td><pre>{t2}</pre></td>\n")
                f.write(f"<td><pre class=\"diff\">{delta}</pre></td>\n")
            else:
                img_rel1 = os.path.relpath(i1, os.path.dirname(os.path.abspath(html_output))) if i1 else ""
                f.write(f"<td><b>#{s1_no}</b></td>\n")
                f.write(f"<td>{f'<img src=\"{img_rel1}\">' if i1 else 'Kein Bild'}</td>\n")
                f.write(f"<td><pre>{t1}</pre></td>\n")
            f.write("</tr>\n")
            
        f.write("</tbody>\n</table>\n</body>\n</html>\n")

    print(f"Bericht erstellt: {html_output}")

if __name__ == "__main__":
    main()