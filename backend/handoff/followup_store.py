from fastapi import HTTPException

DETAIL="""SELECT f.*,
  h.team AS holder_team, h.lo AS holder_lo, h.hi AS holder_hi,
  o.team AS origin_team, o.lo AS origin_lo, o.hi AS origin_hi,
  n.team AS next_team, d.team AS delivered_team
FROM followups f
JOIN cabin_shifts h ON h.code=f.shift
JOIN cabin_shifts o ON o.code=f.origin
LEFT JOIN cabin_shifts n ON n.code=f.next_shift
LEFT JOIN cabin_shifts d ON d.code=f.delivered_to
"""

ORDER=""" ORDER BY CASE f.status WHEN 'open' THEN 0 WHEN 'held' THEN 1
  WHEN 'ack' THEN 2 ELSE 3 END,f.id"""

def entries(cx,code):
    return cx.execute(DETAIL+" WHERE f.shift=%s"+ORDER,(code,)).fetchall()

def incoming(cx,code):
    """Signed off to this shift but not yet delivered by the previous shift."""
    return cx.execute(DETAIL+" WHERE f.status='ack' AND f.next_shift=%s ORDER BY f.id",(code,)).fetchall()

def everything(cx):
    return cx.execute(DETAIL+ORDER).fetchall()

def lookup(cx,code):
    row=cx.execute("SELECT * FROM followups WHERE id=%s",(code,)).fetchone()
    if not row: raise HTTPException(404,"续办条未找到")
    return row

def log(cx,body):
    return cx.execute("""
      INSERT INTO followups(id,origin,shift,work,matter)
      VALUES (%(id)s,%(shift)s,%(shift)s,%(work)s,%(matter)s) RETURNING *
    """,body.model_dump()).fetchone()

def sign(cx,code,holder,actor,body,target):
    """Sign a followup off to a later same-station shift.

    The followup stays with its current holder (status ack) until that holder's
    handoff is actually delivered; only then does it move to the target.  The
    holder must still be the row's shift, otherwise a concurrent delivery has
    already moved it elsewhere.
    """
    result=cx.execute("""
      UPDATE followups SET status='ack',next_shift=%s,receiver=%s,initials=%s,signed_at=now()
      WHERE id=%s AND shift=%s AND status IN ('open','held') RETURNING *
    """,(target,actor,body.initials,code,holder)).fetchone()
    if not result: raise HTTPException(409,"此续办条已签收或已移交，请刷新后重试")
    return result

def close(cx,code,holder,actor,body):
    result=cx.execute("""
      UPDATE followups SET status='done',closed_by=%s,closed_initials=%s,closed_at=now()
      WHERE id=%s AND shift=%s AND status='held' RETURNING *
    """,(actor,body.initials,code,holder)).fetchone()
    if not result: raise HTTPException(409,"只有已送达本班的续办条可以办结")
    return result

def release(cx,code):
    """Delivery moves every followup signed off by this shift into the target.

    The receiving shift rows are locked first, in roster order, for the same
    reason sealing locks its own row: a followup signed off to a shift that is
    sealing right now must make one side wait, not slip past the check.  Taking
    all target rows before touching followups keeps the lock order identical to
    sealing (shift rows, then followup rows) so the two cannot deadlock.
    """
    targets=[row["next_shift"] for row in cx.execute("""
      SELECT DISTINCT f.next_shift, s.roster_day, s.lo
      FROM followups f JOIN cabin_shifts s ON s.code=f.next_shift
      WHERE f.shift=%s AND f.status='ack' AND f.next_shift IS NOT NULL
      ORDER BY s.roster_day,s.lo,f.next_shift
    """,(code,)).fetchall()]
    if not targets: return []
    # Lock in roster order, the same order sign-off walks (holder, then the
    # later target), so the two paths can never take each other's locks in
    # opposite order.
    cx.execute("""
      SELECT code FROM cabin_shifts WHERE code=ANY(%s) ORDER BY roster_day,lo,code FOR UPDATE
    """,(targets,)).fetchall()
    sealed=[row["code"] for row in cx.execute(
        "SELECT shift AS code FROM handoffs WHERE shift=ANY(%s) ORDER BY shift",(targets,)).fetchall()]
    if sealed:
        raise HTTPException(409,f"接手班 {sealed[0]} 已封口，续办条无法送达")
    ids=[row["id"] for row in cx.execute("""
      SELECT id FROM followups WHERE shift=%s AND status='ack' AND next_shift IS NOT NULL
      ORDER BY id FOR UPDATE
    """,(code,)).fetchall()]
    if not ids: return []
    return cx.execute("""
      UPDATE followups SET shift=next_shift,delivered_to=next_shift,delivered_at=now(),
        next_shift=NULL,status='held'
      WHERE id=ANY(%s) RETURNING id
    """,(ids,)).fetchall()
