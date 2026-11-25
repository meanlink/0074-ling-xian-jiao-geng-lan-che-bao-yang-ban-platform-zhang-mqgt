from fastapi import HTTPException

def shift_for(cx,code,lock=False):
    row=cx.execute("SELECT * FROM cabin_shifts WHERE code=%s"+(" FOR UPDATE" if lock else ""),(code,)).fetchone()
    if not row: raise HTTPException(404,"交班班次不存在")
    return row

def orders(cx,shift):
    return cx.execute("SELECT * FROM work_orders WHERE station=%s ORDER BY family,code",(shift["station"],)).fetchall()

def writable(cx,code):
    shift=shift_for(cx,code,True)
    if cx.execute("SELECT 1 FROM handoffs WHERE shift=%s",(code,)).fetchone():
        raise HTTPException(409,"此班交接已封口")
    return shift

def compatible(cx,shift,work):
    if not any(row["code"]==work for row in orders(cx,shift)):
        raise HTTPException(409,"工作单归属另一个站点")
