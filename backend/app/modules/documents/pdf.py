def _escape_pdf_text(value: str) -> str:
    return value.replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")


def _wrap_line(value: str, limit: int = 88) -> list[str]:
    words = value.split()
    lines: list[str] = []
    current = ""
    for word in words:
        candidate = f"{current} {word}".strip()
        if len(candidate) > limit and current:
            lines.append(current)
            current = word
        else:
            current = candidate
    if current:
        lines.append(current)
    return lines or [""]


def build_simple_pdf(title: str, content: str) -> bytes:
    lines = [line for raw in content.splitlines() for line in _wrap_line(raw)]
    visible_lines = lines[:38]
    commands = [
        "0.216 0.365 0.380 rg",
        "0 728 612 64 re f",
        "0.784 0.890 0.902 rg",
        "0 724 612 4 re f",
        "BT",
        "/F2 18 Tf",
        "1 1 1 rg",
        "48 760 Td",
        "(Rulees) Tj",
        "/F1 10 Tf",
        "0 -18 Td",
        f"({_escape_pdf_text(title[:96])}) Tj",
        "ET",
        "BT",
        "/F1 11 Tf",
        "0 0 0 rg",
        "48 690 Td",
    ]
    for index, line in enumerate(visible_lines):
        if index:
            commands.append("0 -15 Td")
        prefix = ""
        if line.startswith("# "):
            prefix = ""
            line = line[2:]
            commands.append("/F2 13 Tf")
        elif line.startswith("## "):
            prefix = ""
            line = line[3:]
            commands.append("/F2 12 Tf")
        else:
            commands.append("/F1 11 Tf")
        commands.append(f"({_escape_pdf_text((prefix + line)[:100])}) Tj")
    commands.append("ET")
    stream = "\n".join(commands).encode("latin-1", errors="replace")

    objects: list[bytes] = []
    objects.append(b"<< /Type /Catalog /Pages 2 0 R >>")
    objects.append(b"<< /Type /Pages /Kids [3 0 R] /Count 1 >>")
    objects.append(
        b"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] "
        b"/Resources << /Font << /F1 4 0 R /F2 5 0 R >> >> /Contents 6 0 R >>"
    )
    objects.append(b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>")
    objects.append(b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica-Bold >>")
    objects.append(b"<< /Length " + str(len(stream)).encode("ascii") + b" >>\nstream\n" + stream + b"\nendstream")

    pdf = bytearray(b"%PDF-1.4\n")
    offsets = [0]
    for number, obj in enumerate(objects, start=1):
        offsets.append(len(pdf))
        pdf.extend(f"{number} 0 obj\n".encode("ascii"))
        pdf.extend(obj)
        pdf.extend(b"\nendobj\n")
    xref_start = len(pdf)
    pdf.extend(f"xref\n0 {len(objects) + 1}\n".encode("ascii"))
    pdf.extend(b"0000000000 65535 f \n")
    for offset in offsets[1:]:
        pdf.extend(f"{offset:010d} 00000 n \n".encode("ascii"))
    pdf.extend(
        f"trailer\n<< /Size {len(objects) + 1} /Root 1 0 R >>\nstartxref\n{xref_start}\n%%EOF\n".encode(
            "ascii"
        )
    )
    return bytes(pdf)
