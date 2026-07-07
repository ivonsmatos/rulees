import io

from pypdf import PdfReader

from app.modules.documents.pdf import build_simple_pdf


def _extract_all_text(pdf_bytes: bytes) -> str:
    reader = PdfReader(io.BytesIO(pdf_bytes))
    return "\n".join(page.extract_text() or "" for page in reader.pages)


def test_build_simple_pdf_returns_valid_pdf_bytes() -> None:
    pdf_bytes = build_simple_pdf("Documento de teste", "# Documento de teste\n\nConteudo simples.")
    assert pdf_bytes.startswith(b"%PDF-")


def test_build_simple_pdf_contains_title_and_has_pages() -> None:
    title = "Documento funcional - Reuniao de Kickoff"
    content = f"# {title}\n\n## Resumo\nTexto de resumo da reuniao.\n"
    pdf_bytes = build_simple_pdf(title, content)

    reader = PdfReader(io.BytesIO(pdf_bytes))
    assert len(reader.pages) >= 1
    full_text = _extract_all_text(pdf_bytes)
    assert title in full_text


def test_build_simple_pdf_paginates_long_content_across_multiple_pages() -> None:
    title = "Documento longo"
    sections = []
    for index in range(1, 41):
        sections.append(f"## Secao {index}: Regra de negocio {index}")
        sections.append(
            f"- REG-{index:03d}: Quando a condicao {index} for satisfeita, o sistema deve aplicar "
            f"a regra correspondente e registrar a decisao para auditoria posterior. "
            f"Esta e a linha de corpo numero {index} do documento gerado para forcar paginacao real."
        )
        sections.append(f"- Evidencia {index}: fala transcrita relacionada a regra {index}.")
    content = f"# {title}\n\n" + "\n\n".join(sections)

    # Sanity check: this content has well over 60 lines of section material,
    # which is exactly the kind of document the old hand-rolled PDF writer
    # used to truncate silently at 38 visible lines.
    assert len(content.splitlines()) > 60

    pdf_bytes = build_simple_pdf(title, content)
    reader = PdfReader(io.BytesIO(pdf_bytes))
    assert len(reader.pages) > 1

    full_text = _extract_all_text(pdf_bytes)
    assert "Secao 1:" in full_text
    assert "Secao 40:" in full_text


def test_build_simple_pdf_escapes_xml_special_characters() -> None:
    title = "Documento com caracteres especiais"
    content = (
        f"# {title}\n\n"
        "## Regras\n"
        "- REG-001: Se valor < 100 & score > 80%, aplicar desconto para cliente & fornecedor.\n"
    )

    # Must not raise -- unescaped '<', '>', '&' would break reportlab's
    # Paragraph mini-XML parser or silently drop content.
    pdf_bytes = build_simple_pdf(title, content)
    assert pdf_bytes.startswith(b"%PDF-")

    full_text = _extract_all_text(pdf_bytes)
    assert "valor" in full_text
    assert "100" in full_text
    assert "80%" in full_text
    assert "cliente" in full_text
    assert "fornecedor" in full_text
