from fastapi import HTTPException

def entries(cx,code):
    return cx.execute("SELECT * FROM followups WHERE shift=%s ORDER BY status DESC,id",(code,)).fetchall()

def lookup(cx,code):
    row=cx.execute("SELECT * FROM followups WHERE id=%s",(code,)).fetchone()
    if not row: raise HTTPException(404,"续办条未找到")
    return row

def log(cx,body):
    return cx.execute("""
      INSERT INTO followups(id,shift,work,matter) VALUES (%(id)s,%(shift)s,%(work)s,%(matter)s) RETURNING *
    """,body.model_dump()).fetchone()

def accept(cx,code,actor,body):
    result=cx.execute("""
      UPDATE followups SET status='ack',receiver=%s,initials=%s WHERE id=%s AND status='open' RETURNING *
    """,(actor,body.initials,code)).fetchone()
    if not result: raise HTTPException(409,"此续办条已签收")
    return result
