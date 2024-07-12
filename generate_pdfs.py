import os
import fitz
import random
from reportlab.pdfgen import canvas
from reference_pdf_vs_pdfs_tests.related_files.pdf_reader import pdf_reader
from reference_pdf_vs_pdfs_tests.related_files.path import get_path


def extract_text_positions_and_font_sizes():
    """Extract text positions and font sizes from a PDF file."""
    doc = fitz.open(get_path('reference_pdf'))
    page = doc[0]
    text_instances = page.get_text("dict")["blocks"]

    positions_and_sizes = {}
    for block in text_instances:
        if block["type"] == 0:  # block contains text
            for line in block["lines"]:
                for span in line["spans"]:
                    text = span["text"].strip()
                    if text:
                        font = "Helvetica"
                        positions_and_sizes[text] = {
                            "bbox": span["bbox"],
                            "size": span["size"],
                            "font": font,  # Using Helvetica
                        }
                        # print(f"Extracted field: {text} at {span['bbox']} with size {span['size']} and font {font}")

    return positions_and_sizes, (page.rect.width, page.rect.height)  # Return page size


def create_pdf_with_positions_and_font_sizes(
    output_path, text_positions_and_sizes, page_size
):
    c = canvas.Canvas(output_path, pagesize=page_size)

    for text, info in text_positions_and_sizes.items():
        x, y = info["bbox"][0], page_size[1] - info["bbox"][1]
        font_size = info["size"]

        c.setFont(info["font"], font_size)
        c.setFillColorRGB(0, 0, 0)
        c.drawString(x, y, text)
        # print(f"Drawing text: {text} at ({x}, {y}) with font size {font_size}")

    c.showPage()
    c.save()


def generate_new_pdf_with_positions_and_font_sizes(
    output_dir=get_path('generated_pdfs'), dicts=[]
):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    text_positions_and_sizes, page_size = extract_text_positions_and_font_sizes()

    for i, custom_dict in enumerate(dicts):
        page_dict = {}
        for key, value in custom_dict.items():
            for field_key in text_positions_and_sizes.keys():
                if field_key.startswith(key):
                    updated_text = f"{key}: {value}"
                    page_dict[updated_text] = text_positions_and_sizes[field_key]
                    break

        output_path = os.path.join(output_dir, f"test_task_variant_{i + 1}.pdf")
        create_pdf_with_positions_and_font_sizes(output_path, page_dict, page_size)
        print(f"Generated file: {output_path}")


def update_dict(original_dict: dict):
    updated_values = {
        "PN": f"tst_{random.randint(100, 999)}",
        "DESCRIPTION": f"PART_{random.randint(100, 999)}",
        "LOCATION": f"{random.randint(100, 999)}",
        "RECEIVER#": f"{random.randint(1, 100)}",
        "CONDITION": f"{random.choice(['FN', 'NEW', 'USED'])}",
    }
    for k, v in updated_values.items():
        original_dict[k] = v
    return original_dict


def get_dict(num_variants: int):
    original_pdf_dict = pdf_reader(get_path('reference_pdf'))
    list_of_pdfs = []
    for i in range(num_variants):
        list_of_pdfs.append(update_dict(original_pdf_dict))
    return list_of_pdfs


generate_new_pdf_with_positions_and_font_sizes(dicts=get_dict(num_variants=10))