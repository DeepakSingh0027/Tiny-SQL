def print_table(rows):
    if not rows:
        print("No results found.")
        return
    headers = rows[0].keys()
    print(" | ".join(headers))
    print("-" * (len(headers) * 10))
    for row in rows:
        print(" | ".join(str(row[h]) for h in headers))
