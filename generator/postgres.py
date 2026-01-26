from io import StringIO

def copy_rows(conn, table, columns, rows):
    buffer = StringIO()
    for row in rows:
        buffer.write("\t".join(map(str, row)) + "\n")
    buffer.seek(0)

    with conn.cursor() as cur:
        cur.copy_from(
            buffer,
            table,
            sep="\t",
            columns=columns,
        )
    conn.commit()
