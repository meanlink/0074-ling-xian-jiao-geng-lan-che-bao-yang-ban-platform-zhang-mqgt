export const clock=n=>[Math.floor(n/60)%24,n%60].map(v=>String(v).padStart(2,'0')).join(':')
export const minute=s=>s.split(':').map(Number).reduce((h,m)=>h*60+m)
export const span=(a,b)=>clock(a)+'—'+clock(b)
export const units={retained:'保养登记',inspection:'清点校核',documentation:'资料归档'}
export const states={open:'待签收',ack:'已签收 · 待原班送达',held:'已送达 · 待办',done:'已办结'}
export const inbox={lead:'保养领班',desk:'服务台值班室'}
export const deliveries={pending:'站内待分发',sent:'站内已送达'}

export function laterShifts(list,code){
  const here=list.find(row=>row.code===code)
  if(!here)return []
  return list.filter(row=>row.station===here.station&&
    (row.roster_day>here.roster_day||(row.roster_day===here.roster_day&&row.lo>here.lo)))
    .sort((a,b)=>a.roster_day.localeCompare(b.roster_day)||a.lo-b.lo)
}
