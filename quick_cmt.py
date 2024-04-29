#!/usr/bin/python3

# quick_cmt.db schema:
# create table entry_comment (entry text, comment text);
# create index idx_entry_cmt on entry_comment(entry);

import sqlite3
import sys

def query_comments(db_path:str, entries:list):
    con_quick_cmt = sqlite3.connect(db_path)
    cur = con_quick_cmt.cursor()
    entries_str = ','.join([f'"{entry}"' for entry in entries])
    cur.execute(f'select ec.comment from entry_comment ec where ec.entry in ({entries_str});')
    for item in cur.fetchall():
        print(item[0])

if __name__ == '__main__':
    db_path = sys.argv[1]
    entries = sys.argv[1:]
    if db_path:
        query_comments(db_path, entries)
