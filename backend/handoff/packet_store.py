from psycopg.types.json import Jsonb

def packet(cx,code):
    return cx.execute("SELECT * FROM handoffs WHERE shift=%s",(code,)).fetchone()

def save(cx,shift,dest,data,job):
    return cx.execute("""
      INSERT INTO handoffs(shift,destination,data,job_id) VALUES (%s,%s,%s,%s) RETURNING *
    """,(shift,dest,Jsonb(data),job)).fetchone()

def send(cx,shift):
    return cx.execute("""
      UPDATE handoffs SET delivery='sent',sent_at=now() WHERE shift=%s AND delivery='pending' RETURNING *
    """,(shift,)).fetchone()
