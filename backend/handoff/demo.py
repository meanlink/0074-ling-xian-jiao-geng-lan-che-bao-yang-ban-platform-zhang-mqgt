def seed(cx):
    cx.execute("""
      INSERT INTO cabin_shifts VALUES ('SHIFT-N1','2026-11-19','杉溪下站','白班',480,720),
        ('SHIFT-N2','2026-11-19','杉溪下站','午班',720,960),
        ('SHIFT-A1','2026-11-19','峰口上站','白班',480,720) ON CONFLICT DO NOTHING;
      INSERT INTO work_orders VALUES ('M-042','站房保养登记','杉溪下站','retained'),
        ('M-043','备件标签复核','杉溪下站','inspection'),
        ('M-044','交班纸单清点','杉溪下站','documentation'),
        ('M-062','上站材料归档','峰口上站','documentation') ON CONFLICT DO NOTHING;
      INSERT INTO shift_slices VALUES ('D-01','SHIFT-N1','M-042',490,550,'小杜',75),
        ('D-02','SHIFT-N1','M-043',500,540,'小杜',25),
        ('D-03','SHIFT-N1','M-044',535,590,'小林',100),
        ('D-04','SHIFT-A1','M-062',560,615,'小伍',100) ON CONFLICT DO NOTHING;
      INSERT INTO followups(id,shift,work,matter) VALUES
        ('NOTE-071','SHIFT-N1','M-043','请午班核对缺少流水编号的备件标签。') ON CONFLICT DO NOTHING;
    """)
