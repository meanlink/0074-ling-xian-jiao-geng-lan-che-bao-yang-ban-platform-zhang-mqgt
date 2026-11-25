from collections import defaultdict

def overloaded(rows):
    deltas=defaultdict(lambda:defaultdict(int))
    for row in rows:
        deltas[row["staff"]][row["lo"]]+=row["weight"]
        deltas[row["staff"]][row["hi"]]-=row["weight"]
    offenders=[]
    for staff,events in deltas.items():
        weight=0
        for time,delta in sorted(events.items()):
            weight+=delta
            if weight>100:
                offenders.append({"staff":staff,"minute":time,"weight":weight})
                break
    return offenders

def allocated(rows,orders):
    totals=defaultdict(int)
    for row in rows:
        totals[row["work"]]+=(row["hi"]-row["lo"])*row["weight"]
    return [order | {"minutes":totals[order["code"]]/100} for order in orders]
