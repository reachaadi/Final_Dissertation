from fastapi import FastAPI, Request, UploadFile, File
from fastapi.responses import HTMLResponse, FileResponse, JSONResponse
from fastapi.templating import Jinja2Templates
import os
import shutil
from docx import Document
from atg.services.llm_service import TestCaseGenerator
from dotenv import load_dotenv, find_dotenv
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment
import re
import uvicorn
import os

load_dotenv(find_dotenv())
app = FastAPI()
templates = Jinja2Templates(directory="atg/templates")

UPLOAD_DIR = os.path.join("atg", "uploads")
# Export Excel to TestAutomation/Test_Cases as requested
# Get project root directory (2 levels up from autotestgen/atg/main.py)
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
TEST_CASES_DIR = os.path.join(PROJECT_ROOT, "TestAutomation", "Test_Cases")

os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(TEST_CASES_DIR, exist_ok=True)

# Global variables to store current session data
current_test_cases = []
current_requirement_name = ""


@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.post("/upload")
async def upload_file(request: Request, file: UploadFile = File(...)):
    file_location = os.path.join(UPLOAD_DIR, file.filename)
    with open(file_location, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # Return success message instead of redirecting
    return templates.TemplateResponse(
        "index.html", {"request": request, "upload_success": True, "uploaded_filename": file.filename}
    )


@app.post("/generate")
async def generate_tc(request: Request):
    global current_test_cases, current_requirement_name

    # Find the latest uploaded Word document
    files = [f for f in os.listdir(UPLOAD_DIR) if f.lower().endswith((".docx"))]
    if not files:
        return templates.TemplateResponse(
            "index.html", {"request": request, "error": "No Word document found in uploads."}
        )
    latest_file = max([os.path.join(UPLOAD_DIR, f) for f in files], key=os.path.getctime)

    # Extract requirement name from filename
    filename = os.path.basename(latest_file)
    current_requirement_name = os.path.splitext(filename)[0]

    doc = Document(latest_file)

    # Extract paragraphs
    paragraphs = [p.text for p in doc.paragraphs if p.text.strip()]

    # Extract tables as list of lists (for Jinja2 rendering)
    tables = []
    for table in doc.tables:
        table_data = []
        for row in table.rows:
            row_data = [cell.text.strip().replace("\n", " ") for cell in row.cells]
            table_data.append(row_data)
        tables.append(table_data)

    # Prepare markdown for LLM
    all_tables_markdown = []
    for table_index, table in enumerate(tables):
        table_markdown = f"### Table {table_index + 1}\n"
        header_cells = table[0]
        header_line = "| " + " | ".join(header_cells) + " |"
        separator_line = "| " + " | ".join(["---"] * len(header_cells)) + " |"
        table_markdown += header_line + "\n"
        table_markdown += separator_line + "\n"
        for row in table[1:]:
            row_line = "| " + " | ".join(row) + " |"
            table_markdown += row_line + "\n"
        all_tables_markdown.append(table_markdown)

    requirements_text = "\n\n---\n\n".join(all_tables_markdown)

    # Generate initial test cases
    generator = TestCaseGenerator()
    generated_test_cases = generator.generate_test_cases(
        requirements=requirements_text, max_cases=5
    )

    # Verify and improve test cases
    verified_test_cases = generator.verify_and_modify_test_cases(
        requirements=requirements_text, test_cases=generated_test_cases
    )

    # Store verified test cases globally for export
    current_test_cases = verified_test_cases

    # Render the extracted content
    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "paragraphs": paragraphs,
            "tables": tables,  # Pass as list of lists
            "test_cases": verified_test_cases,
        },
    )


@app.post("/export-excel")
async def export_to_excel():
    global current_test_cases, current_requirement_name

    if not current_test_cases:
        return {"error": "No test cases available to export. Please generate test cases first."}

    # Create filename with requirement name
    safe_filename = re.sub(r"[^\w\s-]", "", current_requirement_name).strip()
    safe_filename = re.sub(r"[-\s]+", "_", safe_filename)
    excel_filename = f"{safe_filename}_Test_cases.xlsx"
    excel_path = os.path.join(TEST_CASES_DIR, excel_filename)

    # Create workbook and worksheet
    wb = Workbook()
    ws = wb.active
    ws.title = "Test Cases"

    # Define styles
    header_font = Font(bold=True, color="FFFFFF")
    header_fill = PatternFill(start_color="366092", end_color="366092", fill_type="solid")
    header_alignment = Alignment(horizontal="center", vertical="center")

    # Add headers
    if current_test_cases and len(current_test_cases) > 0:
        if isinstance(current_test_cases[0], dict):
            # Test cases are dictionaries
            headers = list(current_test_cases[0].keys())
            for col, header in enumerate(headers, 1):
                cell = ws.cell(row=1, column=col, value=header.title())
                cell.font = header_font
                cell.fill = header_fill
                cell.alignment = header_alignment

            # Add data rows
            for row_idx, test_case in enumerate(current_test_cases, 2):
                for col_idx, value in enumerate(test_case.values(), 1):
                    ws.cell(row=row_idx, column=col_idx, value=str(value))
        else:
            # Test cases are simple strings
            ws.cell(row=1, column=1, value="Test Case").font = header_font
            ws.cell(row=1, column=1).fill = header_fill
            ws.cell(row=1, column=1).alignment = header_alignment

            for row_idx, test_case in enumerate(current_test_cases, 2):
                ws.cell(row=row_idx, column=1, value=str(test_case))

    # Auto-adjust column widths
    for column in ws.columns:
        max_length = 0
        column_letter = column[0].column_letter
        for cell in column:
            try:
                if len(str(cell.value)) > max_length:
                    max_length = len(str(cell.value))
            except:
                pass
        adjusted_width = min(max_length + 2, 50)  # Cap at 50 characters
        ws.column_dimensions[column_letter].width = adjusted_width

    # Save the workbook
    wb.save(excel_path)

    # Return JSON so UI can show path and then trigger download separately
    return JSONResponse(
        {
            "saved_path": "/".join(excel_path.split("/")[-3:]),
            "filename": excel_filename,
            "download_url": f"/download-excel?filename={excel_filename}",
        }
    )


@app.get("/download-excel")
async def download_excel(filename: str):
    file_path = os.path.join(TEST_CASES_DIR, filename)
    return FileResponse(
        path=file_path,
        filename=filename,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )


if __name__ == "__main__":
    uvicorn.run("atg.main:app", reload=True)
