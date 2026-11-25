def list_slices(cx,code):
    return cx.execute("SELECT * FROM shift_slices WHERE shift=%s ORDER BY lo,code",(code,)).fetchall()

def add(cx,body):
    return cx.execute("""
      INSERT INTO shift_slices(code,shift,work,lo,hi,staff,weight)
      VALUES (%(code)s,%(shift)s,%(work)s,%(lo)s,%(hi)s,%(staff)s,%(weight)s) RETURNING *
    """,body.model_dump()).fetchone()
