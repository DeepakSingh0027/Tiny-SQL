def print_table(rows):
    if not rows:
        print("No results found.")
        return

    headers = rows[0].keys()
    # Calculate max width per column for neat alignment
    col_widths = {h: max(len(str(h)), max(len(str(row[h])) for row in rows)) for h in headers}

    # Print headers
    header_line = " | ".join(f"{h.ljust(col_widths[h])}" for h in headers)
    print(header_line)

    # Print separator
    separator_line = "-+-".join('-' * col_widths[h] for h in headers)
    print(separator_line)

    # Print each row
    for row in rows:
        row_line = " | ".join(f"{str(row[h]).ljust(col_widths[h])}" for h in headers)
        print(row_line)
