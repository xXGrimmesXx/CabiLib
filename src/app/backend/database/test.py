import sqlite3

con = sqlite3.connect("C:\\Users\\mloui\\Desktop\\CabiLib\\src\\app\\backend\\database\\CabiLib.db".replace('\\', '/'))
cur = con.cursor()
print(cur.execute("delete from rendez_vous where patient_id=56").fetchall())
print(cur.execute("select * from patient where id=56").fetchall())
con.commit()
con.close()

