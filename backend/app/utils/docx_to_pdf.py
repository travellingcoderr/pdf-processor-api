"""Convert Word (.docx) to PDF using LibreOffice headless. Used so we can process Word resumes the same as PDF."""
import os
import shutil
import subprocess
import tempfile


def docx_to_pdf(docx_bytes: bytes) -> bytes:
    """Convert docx bytes to PDF bytes. Raises on failure."""
    with tempfile.TemporaryDirectory() as tmpdir:
        docx_path = os.path.join(tmpdir, "resume.docx")
        with open(docx_path, "wb") as f:
            f.write(docx_bytes)
        outdir = os.path.join(tmpdir, "out")
        os.makedirs(outdir, exist_ok=True)
        subprocess.run(
            [
                "libreoffice",
                "--headless",
                "--convert-to", "pdf",
                "--outdir", outdir,
                docx_path,
            ],
            check=True,
            capture_output=True,
            timeout=60,
        )
        pdf_path = os.path.join(outdir, "resume.pdf")
        if not os.path.isfile(pdf_path):
            raise RuntimeError("LibreOffice did not produce resume.pdf")
        with open(pdf_path, "rb") as f:
            return f.read()
