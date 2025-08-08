from fpdf import FPDF
from .base_template import BaseTemplate
from typing import Dict, Any, List
from num2words import num2words
import locale


class InvoiceTemplate(BaseTemplate):
    @property
    def template_type(self) -> str:
        return "Invoice"

    def get_template(self) -> Dict[str, Any]:
        return {
            "type": self.template_type,
            "header_fields": [
                ("M/s", "text"),
                ("Campaign", "text"),
                ("Date", "date"),
                ("Invoice No", "text"),
                ("Invoice Month", "text")
            ],
            "line_items": {
                "columns": [
                    "Description",
                    "Campaign Start Date",
                    "Campaign End Date",
                    "Size",
                    "Duration",
                    "Amount"
                ]
            },
            "footer": {
                "total": True,
                "amount_in_words": True
            }
        }

    def validate_data(self, data: Dict[str, Any]) -> bool:
        required = ["M/s", "Campaign", "Date", "Invoice No", "line_items", "Invoice Month"]
        for field in required:
            if field not in data or not data[field]:
                return False
        if not isinstance(data["line_items"], list):
            return False
        for item in data["line_items"]:
            if not all(k in item for k in self.get_template()["line_items"]["columns"]):
                return False
        return True

    def generate_pdf_content(self, pdf: FPDF, data: Dict[str, Any]) -> None:
        pdf.set_font("Arial", 'B', 16)
        pdf.cell(0, 10, self.template_type.upper(), 0, 1, 'C')
        pdf.set_draw_color(0, 0, 0)
        pdf.set_line_width(0.4)
        pdf.line(10, pdf.get_y(), 200, pdf.get_y())
        pdf.ln(5)

        self._add_header_fields(pdf, data)
        self._add_line_items(pdf, data["line_items"])
        self._add_totals_and_footer(pdf, data["line_items"])

    def _add_header_fields(self, pdf: FPDF, data: Dict[str, Any]) -> None:
        left_x, right_x, y = 10, 110, pdf.get_y()
        line_height = 7

        def write_field(x, label, value):
            pdf.set_xy(x, pdf.get_y())
            pdf.set_font("Arial", 'B', 10)
            pdf.cell(30, line_height, f"{label}:", 0, 0)
            pdf.set_font("Arial", '', 10)
            pdf.cell(60, line_height, str(value), 0, 1)

        pdf.set_xy(left_x, y)
        write_field(left_x, "M/s", data.get("M/s", ""))
        write_field(left_x, "Campaign", data.get("Campaign", ""))

        pdf.set_xy(right_x, y)
        write_field(right_x, "Date", data.get("Date", ""))
        write_field(right_x, "Invoice No", data.get("Invoice No", ""))
        write_field(right_x, "Invoice Month", data.get("Invoice Month", ""))

        pdf.ln(15)

    def _add_line_items(self, pdf: FPDF, items: List[Dict[str, str]]) -> None:
        headers = ["#", "Description", "Size", "Duration", "Amount"]
        col_widths = [10, 90, 20, 25, 35]
        start_x = 10

        pdf.set_font("Arial", 'B', 9)
        pdf.set_fill_color(240, 240, 240)

        pdf.set_x(start_x)
        for i, header in enumerate(headers):
            pdf.cell(col_widths[i], 8, header, 1, 0, 'C', fill=True)
        pdf.ln()

        pdf.set_font("Arial", '', 9)

        for idx, item in enumerate(items, 1):
            description = item.get("Description", "").strip()
            start = item.get("Campaign Start Date", "").strip()
            end = item.get("Campaign End Date", "").strip()
            full_desc = description
            if start:
                full_desc += f"\nCampaign Start: {start}"
            if end:
                full_desc += f"\nCampaign End: {end}"

            desc_lines = pdf.multi_cell(col_widths[1], 5, full_desc, border=0, split_only=True)
            row_height = max(10, len(desc_lines) * 5)

            x_start = start_x
            y_start = pdf.get_y()

            pdf.set_xy(x_start, y_start)
            pdf.cell(col_widths[0], row_height, str(idx), 1, 0, 'C')

            pdf.set_xy(x_start + col_widths[0], y_start)
            pdf.multi_cell(col_widths[1], 5, full_desc, border=1)

            x = x_start + col_widths[0] + col_widths[1]
            for i, key in enumerate(["Size", "Duration", "Amount"]):
                val = item.get(key, "")
                pdf.set_xy(x, y_start)
                pdf.cell(col_widths[i + 2], row_height, val, 1, 0, 'C')
                x += col_widths[i + 2]

            pdf.set_y(y_start + row_height)

        # Add empty rows to ensure minimum 6 rows
        remaining_rows = max(0, 6 - len(items))
        for _ in range(remaining_rows):
            pdf.set_x(start_x)
            for width in col_widths:
                pdf.cell(width, 10, "", 1, 0)
            pdf.ln()

        pdf.ln(4)

    def _add_totals_and_footer(self, pdf: FPDF, items: List[Dict[str, str]]) -> None:
        total = 0
        for item in items:
            try:
                amt = float(item.get("Amount", "0").replace(",", ""))
                total += amt
            except:
                continue

        try:
            total_str = locale.currency(total, grouping=True, symbol=False)
        except:
            total_str = f"{total:,.2f}"

        pdf.set_font("Arial", 'B', 10)
        pdf.set_fill_color(245, 245, 245)
        pdf.set_draw_color(0, 0, 0)

        # x_start = 10 + 10 + 90 + 20 + 25  # Total left offset from columns
        pdf.set_x(10)
        pdf.cell(50, 10, "TOTAL:", 1, 0, 'L', fill=True)
        pdf.set_font("Arial", '', 10)
        pdf.cell(35, 10, f"PKR {total_str}", 1, 1, 'R', fill=True)

        pdf.ln(5)

        # Amount in words
        pdf.set_font("Arial", 'I', 9)
        try:
            amount_words = num2words(int(round(total)), lang='en_IN').capitalize()
            words = f"Amount in words: {amount_words} rupees only"
        except:
            words = f"Amount in words: {total} rupees only"
        pdf.set_x(10)
        pdf.multi_cell(0, 6, words, 0, 'L')


def get_template_class():
    return InvoiceTemplate()
