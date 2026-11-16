#!/usr/bin/env python3
# -*- coding: utf-8 -*-

###############################################################################
#
# excel_compare.py
#
# Purpose
# -------
# Compare two Excel workbooks and generate:
#
#   - Non-verbose text report
#   - Verbose text report
#   - HTML report
#   - CSV summary
#
# Requirements
# ------------
#
#   py -m pip install pandas openpyxl
#
# Usage
# -----
#
#   py excel_compare.py file1.xlsx file2.xlsx
#
# Default Behaviour
# -----------------
#
#   * HTML enabled
#   * CSV enabled
#   * Verbose log enabled
#   * Formula mode = both
#   * Ignore <MISSING> != '' in non-verbose report
#
###############################################################################

import argparse
import csv
import html
import os
from datetime import datetime

from openpyxl import load_workbook
from openpyxl.utils import get_column_letter


###############################################################################
# Helper Functions
###############################################################################

def excel_address(row, col):
    return f"{get_column_letter(col)}{row}"


def norm(value, trim=True):

    if value is None:
        return ""

    value = str(value)

    if trim:
        value = value.strip()

    return value


def compare_strings(v1, v2, case_sensitive):

    if case_sensitive:
        return v1 == v2

    return v1.lower() == v2.lower()


###############################################################################
# HTML Report
###############################################################################

class HtmlReport:

    def __init__(self, filename):

        self.f = open(
            filename,
            "w",
            encoding="utf-8"
        )

        self.f.write("""
<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<title>Excel Compare Report</title>

<style>

body{
    font-family:Arial;
    margin:20px;
}

table{
    border-collapse:collapse;
    width:100%;
}

th{
    background:#4472C4;
    color:white;
    padding:6px;
}

td{
    border:1px solid #cccccc;
    padding:4px;
}

.diff{
    background:#ffd8d8;
}

.summary{
    background:#efefef;
    padding:10px;
    margin-bottom:20px;
}

</style>
</head>
<body>
""")

    def write(self, text):
        self.f.write(text)

    def close(self):
        self.f.write("</body></html>")
        self.f.close()


###############################################################################
# Workbook Access
###############################################################################

class WorkbookPair:

    def __init__(self, filename):

        self.filename = filename

        self.wb_formula = load_workbook(
            filename,
            data_only=False
        )

        self.wb_value = load_workbook(
            filename,
            data_only=True
        )


###############################################################################
# Comparison
###############################################################################

def compare_sheet(
        sheet_name,
        wb1,
        wb2,
        args,
        log_normal,
        log_verbose,
        html_report):

    ws1_formula = wb1.wb_formula[sheet_name]
    ws1_value = wb1.wb_value[sheet_name]

    ws2_formula = wb2.wb_formula[sheet_name]
    ws2_value = wb2.wb_value[sheet_name]

    rows = max(
        ws1_formula.max_row,
        ws2_formula.max_row
    )

    cols = max(
        ws1_formula.max_column,
        ws2_formula.max_column
    )

    log_normal.write("\n" + "=" * 80 + "\n")
    log_normal.write(f"SHEET: {sheet_name}\n")

    log_verbose.write("\n" + "=" * 80 + "\n")
    log_verbose.write(f"SHEET: {sheet_name}\n")

    html_report.write(
        f"<h2>{html.escape(sheet_name)}</h2>"
    )

    html_report.write("""
<table>
<tr>
<th>Cell</th>
<th>Formula 1</th>
<th>Formula 2</th>
<th>Value 1</th>
<th>Value 2</th>
</tr>
""")

    diff_count = 0

    for row in range(1, rows + 1):

        for col in range(1, cols + 1):

            f1 = norm(
                ws1_formula.cell(row, col).value,
                args.trim_whitespace
            )

            f2 = norm(
                ws2_formula.cell(row, col).value,
                args.trim_whitespace
            )

            v1 = norm(
                ws1_value.cell(row, col).value,
                args.trim_whitespace
            )

            v2 = norm(
                ws2_value.cell(row, col).value,
                args.trim_whitespace
            )

            if args.formula_mode == "value":

                different = not compare_strings(
                    v1,
                    v2,
                    args.case_sensitive
                )

            elif args.formula_mode == "formula":

                different = not compare_strings(
                    f1,
                    f2,
                    args.case_sensitive
                )

            else:

                different = (
                    not compare_strings(
                        f1,
                        f2,
                        args.case_sensitive
                    )
                    or
                    not compare_strings(
                        v1,
                        v2,
                        args.case_sensitive
                    )
                )

            if not different:
                continue

            location = excel_address(row, col)

            verbose_msg = (
                f"{location}\n"
                f"  Formula1: {f1}\n"
                f"  Formula2: {f2}\n"
                f"  Value1  : {v1}\n"
                f"  Value2  : {v2}\n"
            )

            log_verbose.write(verbose_msg)

            suppress = False

            if args.ignore_missing_empty:

                if (
                    (f1 == "<MISSING>" and f2 == "")
                    or
                    (f2 == "<MISSING>" and f1 == "")
                    or
                    (v1 == "<MISSING>" and v2 == "")
                    or
                    (v2 == "<MISSING>" and v1 == "")
                ):
                    suppress = True

            if not suppress:
                log_normal.write(verbose_msg)

            html_report.write(
                "<tr class='diff'>"
                f"<td>{location}</td>"
                f"<td>{html.escape(f1)}</td>"
                f"<td>{html.escape(f2)}</td>"
                f"<td>{html.escape(v1)}</td>"
                f"<td>{html.escape(v2)}</td>"
                "</tr>"
            )

            diff_count += 1

            if (
                args.max_diffs > 0
                and diff_count >= args.max_diffs
            ):
                break

    html_report.write("</table>")

    return diff_count


###############################################################################
# Main
###############################################################################

def main():

    parser = argparse.ArgumentParser(
        description="Excel workbook comparison"
    )

    parser.add_argument("workbook1")
    parser.add_argument("workbook2")

    parser.add_argument(
        "--logdir",
        default="logs"
    )

    parser.add_argument(
        "--formula-mode",
        choices=[
            "value",
            "formula",
            "both"
        ],
        default="both"
    )

    parser.add_argument(
        "--sheet",
        action="append"
    )

    parser.add_argument(
        "--case-sensitive",
        action="store_true"
    )

    parser.add_argument(
        "--trim-whitespace",
        action="store_true",
        default=True
    )

    parser.add_argument(
        "--ignore-missing-empty",
        action="store_true",
        default=True
    )

    parser.add_argument(
        "--max-diffs",
        type=int,
        default=0
    )

    parser.add_argument(
        "--quiet",
        action="store_true"
    )

    args = parser.parse_args()

    os.makedirs(
        args.logdir,
        exist_ok=True
    )

    timestamp = datetime.now().strftime(
        "%Y%m%d_%H%M%S"
    )

    normal_log_name = os.path.join(
        args.logdir,
        f"{timestamp}_excelcompare.log"
    )

    verbose_log_name = os.path.join(
        args.logdir,
        f"{timestamp}_excelcompare_verbose.log"
    )

    html_name = os.path.join(
        args.logdir,
        f"{timestamp}_excelcompare.html"
    )

    csv_name = os.path.join(
        args.logdir,
        f"{timestamp}_excelcompare_summary.csv"
    )

    wb1 = WorkbookPair(args.workbook1)
    wb2 = WorkbookPair(args.workbook2)

    sheets1 = set(wb1.wb_formula.sheetnames)
    sheets2 = set(wb2.wb_formula.sheetnames)

    html_report = HtmlReport(html_name)

    total_diffs = 0
    csv_rows = []

    with open(
        normal_log_name,
        "w",
        encoding="utf-8"
    ) as log_normal, open(
        verbose_log_name,
        "w",
        encoding="utf-8"
    ) as log_verbose:

        log_normal.write(
            f"Workbook1={args.workbook1}\n"
        )
        log_normal.write(
            f"Workbook2={args.workbook2}\n"
        )

        log_verbose.write(
            f"Workbook1={args.workbook1}\n"
        )
        log_verbose.write(
            f"Workbook2={args.workbook2}\n"
        )

        missing1 = sheets2 - sheets1
        missing2 = sheets1 - sheets2

        if missing1:

            for sheet in sorted(missing1):

                msg = (
                    f"Missing in Workbook1: "
                    f"{sheet}\n"
                )

                log_normal.write(msg)
                log_verbose.write(msg)

        if missing2:

            for sheet in sorted(missing2):

                msg = (
                    f"Missing in Workbook2: "
                    f"{sheet}\n"
                )

                log_normal.write(msg)
                log_verbose.write(msg)

        common = sorted(
            sheets1.intersection(sheets2)
        )

        if args.sheet:
            common = [
                s for s in common
                if s in args.sheet
            ]

        for sheet in common:

            diffs = compare_sheet(
                sheet,
                wb1,
                wb2,
                args,
                log_normal,
                log_verbose,
                html_report
            )

            total_diffs += diffs

            csv_rows.append(
                [sheet, diffs]
            )

    with open(
        csv_name,
        "w",
        newline="",
        encoding="utf-8"
    ) as f:

        writer = csv.writer(f)

        writer.writerow(
            ["Sheet", "Differences"]
        )

        for row in csv_rows:
            writer.writerow(row)

        writer.writerow(
            ["TOTAL", total_diffs]
        )

    html_report.write(
        f"""
<div class="summary">
<h2>Summary</h2>
<p>Total Differences: {total_diffs}</p>
</div>
"""
    )

    html_report.close()

    if not args.quiet:

        print()
        print("Comparison completed")
        print()

        print(normal_log_name)
        print(verbose_log_name)
        print(html_name)
        print(csv_name)

        print()
        print(
            f"Total differences: "
            f"{total_diffs}"
        )


if __name__ == "__main__":
    main()