#!/usr/bin/env python3
# -*- coding: utf-8 -*-

###############################################################################
#
# Script Name
#   xlsb_compare.py
#
# Purpose
#   Compare two XLSB workbooks.
#
# Features
#   - Compare sheet names
#   - Compare cell contents
#   - Non-verbose log
#   - Verbose log
#   - HTML report
#   - CSV summary
#
# Requirements
#
#   py -m pip install pandas pyxlsb
#
# Usage
#
#   py xlsb_compare.py file1.xlsb file2.xlsb
#
###############################################################################

import csv
import html
import os
import sys

from datetime import datetime

import pandas as pd


###############################################################################
# Helpers
###############################################################################

def excel_col(col_num):

    result = ""

    while col_num > 0:
        col_num, rem = divmod(col_num - 1, 26)
        result = chr(65 + rem) + result

    return result


def excel_address(row, col):

    return f"{excel_col(col)}{row}"


def get_sheet_names(filename):

    xls = pd.ExcelFile(
        filename,
        engine="pyxlsb"
    )

    return xls.sheet_names


def load_sheet(filename, sheet_name):

    try:

        return pd.read_excel(
            filename,
            sheet_name=sheet_name,
            header=None,
            engine="pyxlsb",
            dtype=str
        )

    except Exception:

        return pd.DataFrame()


def normalize(value):

    if pd.isna(value):
        return ""

    return str(value).strip()


###############################################################################
# HTML
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
<meta charset="utf-8"/>

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
 padding:5px;
}

td{
 border:1px solid #cccccc;
 padding:4px;
}

.diff{
 background:#ffd0d0;
}

</style>

</head>

<body>

<h1>XLSB Comparison Report</h1>
""")

    def write(self, text):
        self.f.write(text)

    def close(self):
        self.f.write("</body></html>")
        self.f.close()


###############################################################################
# Main
###############################################################################

def main():

    if len(sys.argv) != 3:

        print(
            "Usage: "
            "xlsb_compare.py file1.xlsb file2.xlsb"
        )

        sys.exit(1)

    file1 = sys.argv[1]
    file2 = sys.argv[2]

    timestamp = datetime.now().strftime(
        "%Y%m%d_%H%M%S"
    )

    base_dir = os.path.dirname(
        os.path.abspath(__file__)
    )

    log_dir = os.path.join(
        base_dir,
        "logs"
    )

    os.makedirs(
        log_dir,
        exist_ok=True
    )

    normal_log = os.path.join(
        log_dir,
        f"{timestamp}_xlsbcompare.log"
    )

    verbose_log = os.path.join(
        log_dir,
        f"{timestamp}_xlsbcompare_verbose.log"
    )

    html_report_name = os.path.join(
        log_dir,
        f"{timestamp}_xlsbcompare.html"
    )

    csv_summary = os.path.join(
        log_dir,
        f"{timestamp}_xlsbcompare_summary.csv"
    )

    sheets1 = set(
        get_sheet_names(file1)
    )

    sheets2 = set(
        get_sheet_names(file2)
    )

    html_report = HtmlReport(
        html_report_name
    )

    total_diffs = 0

    csv_rows = []

    with open(
        normal_log,
        "w",
        encoding="utf-8"
    ) as log1, open(
        verbose_log,
        "w",
        encoding="utf-8"
    ) as log2:

        log1.write(f"FILE1={file1}\n")
        log1.write(f"FILE2={file2}\n")

        log2.write(f"FILE1={file1}\n")
        log2.write(f"FILE2={file2}\n")

        missing1 = sheets2 - sheets1
        missing2 = sheets1 - sheets2

        for sheet in sorted(missing1):

            msg = (
                f"Missing in workbook1: "
                f"{sheet}\n"
            )

            log1.write(msg)
            log2.write(msg)

        for sheet in sorted(missing2):

            msg = (
                f"Missing in workbook2: "
                f"{sheet}\n"
            )

            log1.write(msg)
            log2.write(msg)

        common = sorted(
            sheets1.intersection(
                sheets2
            )
        )

        for sheet in common:

            df1 = load_sheet(
                file1,
                sheet
            )

            df2 = load_sheet(
                file2,
                sheet
            )

            rows = max(
                len(df1.index),
                len(df2.index)
            )

            cols = max(
                len(df1.columns),
                len(df2.columns)
            )

            sheet_diffs = 0

            html_report.write(
                f"<h2>{html.escape(sheet)}</h2>"
            )

            html_report.write("""
<table>
<tr>
<th>Cell</th>
<th>Workbook 1</th>
<th>Workbook 2</th>
</tr>
""")

            for r in range(rows):

                for c in range(cols):

                    try:
                        v1 = normalize(
                            df1.iat[r, c]
                        )
                    except Exception:
                        v1 = ""

                    try:
                        v2 = normalize(
                            df2.iat[r, c]
                        )
                    except Exception:
                        v2 = ""

                    if v1 != v2:

                        addr = excel_address(
                            r + 1,
                            c + 1
                        )

                        msg = (
                            f"{sheet} "
                            f"{addr}: "
                            f"'{v1}' != '{v2}'\n"
                        )

                        log2.write(msg)

                        if not (
                            (v1 == "" and v2 == "")
                        ):
                            log1.write(msg)

                        html_report.write(
                            "<tr class='diff'>"
                            f"<td>{addr}</td>"
                            f"<td>{html.escape(v1)}</td>"
                            f"<td>{html.escape(v2)}</td>"
                            "</tr>"
                        )

                        sheet_diffs += 1
                        total_diffs += 1

            html_report.write("</table>")

            csv_rows.append(
                [sheet, sheet_diffs]
            )

        log1.write(
            f"\nTOTAL DIFFERENCES="
            f"{total_diffs}\n"
        )

        log2.write(
            f"\nTOTAL DIFFERENCES="
            f"{total_diffs}\n"
        )

    with open(
        csv_summary,
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
<h2>Summary</h2>
<p>Total Differences:
{total_diffs}</p>
"""
    )

    html_report.close()

    print()
    print("Comparison complete")
    print()

    print(
        f"Normal Log : {normal_log}"
    )

    print(
        f"Verbose Log: {verbose_log}"
    )

    print(
        f"HTML Report: {html_report_name}"
    )

    print(
        f"CSV Summary: {csv_summary}"
    )

    print()
    print(
        f"Total Differences: "
        f"{total_diffs}"
    )


if __name__ == "__main__":
    main()