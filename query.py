import sqlite3
conn = sqlite3.connect('backend/demo.db')
c = conn.cursor()
t = c.execute('SELECT COUNT(*) FROM companies').fetchone()[0]
s = c.execute('SELECT COUNT(*) FROM (SELECT DISTINCT sector FROM companies)').fetchone()[0]
print('Tickers: ' + str(t))
print('Sectors: ' + str(s))
conn.close()
