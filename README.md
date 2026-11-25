# 岭线交更 · 缆车保养班台账

杉溪缆道站 9 位后勤班成员，在峰口上站和杉溪下站记录保养档案、备件标记和站房杂项。班表、人员投入记录与续办纸条原来分开留存，容易误把同一人的同时投入记成两倍、把工作单记错站点、未由接班人签收就关账。交接单给后勤领班和值班室。

| 角色 | 工作台职责 |
|---|---|
| operator | 登记工作时间和比例，创建续办条 |
| reviewer | 在交班前签收续办并分发快照 |
| viewer | 查阅班表、投入、续办和交接状态 |

1. 08:00 SHIFT-N1 杉溪下站开班。
2. 08:10—09:10 小杜为 M-042 登记 75% 投入，折 45 人分钟。
3. 08:20—09:00 小杜同时整理 M-043，25% 折 10 人分钟。
4. 08:55—09:50 小林处理 M-044 纸单盘点，100% 折 55 人分钟。
5. 11:50 续办条 NOTE-071 提请午班核对备件标签。
6. 12:00 复核员签收 NOTE-071 并指定同站后续班 SHIFT-N2，交接汇总首次分发 110 人分钟至保养领班。
7. 交接单送达后 NOTE-071 才离开 SHIFT-N1、归入 SHIFT-N2；值班人员据此追查续办现归哪班。

每人每分钟最多拥有 100% 的投入份额，扫描有序起止增量判断重叠。某工作单的计量是持续分钟乘投入占比后求和。输入均为记录工作，交接只作人员记录归档。含未签收续办或零工作量的班次不能发送，发出后冻结明细。

续办条签收时要写明同站后续班：签收只作预约，要等原班交接单真正送达才移交给接手班，接手班仍有待办或未送达的续办条时不能封口。接手班可以办结，也可以再交更晚的同站班次；已送达的交接单保留当时去向与快照。分发失败的工作可用同一张交接单重试，不会重复生成续办。工作台的交接汇总列出每张续办条现归哪班。

```sh
cp -n .env.example .env
docker compose up -d --build --wait
docker compose exec backend python -m scripts.seed_demo
docker compose down -v --remove-orphans
```

三个演示账号为 operator@demo.local、reviewer@demo.local、viewer@demo.local，密码 Demo2026!。FRONTEND_PORT、BACKEND_PORT、DB_PORT 决定宿主端口，SEED_DEMO 控制演示数据，DEMO_PASSWORD、JWT_SECRET、POSTGRES_PASSWORD 为本地配置。五服务分别为 Nginx 和原生 ES modules、FastAPI/Python、worker、PostgreSQL、Redis。后端本地安装 backend/requirements.txt，配置 DATABASE_URL、REDIS_URL、JWT_SECRET，再启动 `uvicorn app:app --reload` 与 `python worker.py`。backend/handoff 包含区间投入、续办及分发逻辑，frontend/cabin 是班组工作台。角色和任务枚举在 backend/core.py、frontend/base.js；分发去向和续办状态在 backend/schema.sql、backend/handoff/forms.py 和 frontend/cabin/time.js。MIT 许可证。

前端地址为 http://127.0.0.1:18468，API 为 http://127.0.0.1:19468，数据库本机映射端口为 17968。
