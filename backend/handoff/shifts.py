from fastapi import HTTPException

def shift_for(cx,code,lock=False):
    row=cx.execute("SELECT * FROM cabin_shifts WHERE code=%s"+(" FOR UPDATE" if lock else ""),(code,)).fetchone()
    if not row: raise HTTPException(404,"交班班次不存在")
    return row

def orders(cx,shift):
    return cx.execute("SELECT * FROM work_orders WHERE station=%s ORDER BY family,code",(shift["station"],)).fetchall()

def sealed(cx,code,for_update=True):
    """The handoff row is the answer to 'has this shift been closed out'."""
    return cx.execute("SELECT * FROM handoffs WHERE shift=%s"+(" FOR UPDATE" if for_update else ""),(code,)).fetchone()

def writable(cx,code):
    """Lock the shift row; sealing takes the same lock, so the two serialize.

    The handoff row itself is only read for existence here: delivery locks it
    later, and taking that lock in this order could deadlock with release().
    """
    shift=shift_for(cx,code,True)
    if sealed(cx,code,False):
        raise HTTPException(409,"此班交接已封口")
    return shift

def compatible(cx,shift,work):
    if not any(row["code"]==work for row in orders(cx,shift)):
        raise HTTPException(409,"工作单归属另一个站点")

def later_shift(cx,shift,code):
    """Resolve the follow-up target and make sure it is a later shift here.

    The target row is locked so that signing a followup off and the receiver
    sealing its own handoff cannot both succeed: whoever gets the lock first
    wins, and the other side sees the committed outcome.
    """
    if not code:
        raise HTTPException(409,"请指定同站后续班次作为续办接收班")
    target=shift_for(cx,code,True)
    if target["station"]!=shift["station"]:
        raise HTTPException(409,"续办只能交给同站后续班次")
    if (target["roster_day"],target["lo"])<=(shift["roster_day"],shift["lo"]):
        raise HTTPException(409,"续办只能交给本班之后仍会接班的同站班次")
    # Read the target's handoff without locking it: the target shift row above
    # is already locked and sealing holds that same row, so a seal either
    # happened before this check or is waiting behind it.  Locking the handoff
    # row too would deadlock against a delivery that is moving work backwards.
    if sealed(cx,target["code"],False):
        raise HTTPException(409,"接手班已封口，无法再接收此续办条")
    return target
