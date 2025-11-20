import sqlite3
import os
DB = os.path.join(os.path.dirname(__file__), '..', 'db.sqlite3')
DB = os.path.abspath(DB)
print('DB path:', DB)
conn = sqlite3.connect(DB)
c = conn.cursor()
print('Updating token_number to id for all rows...')
c.execute("UPDATE queues_queue SET token_number = id;")
conn.commit()
print('Done. Rows affected:', c.rowcount)
conn.close()
