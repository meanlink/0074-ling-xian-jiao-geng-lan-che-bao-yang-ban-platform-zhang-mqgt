export const clock=n=>[Math.floor(n/60)%24,n%60].map(v=>String(v).padStart(2,'0')).join(':')
export const minute=s=>s.split(':').map(Number).reduce((h,m)=>h*60+m)
export const span=(a,b)=>clock(a)+'—'+clock(b)
export const units={retained:'保养登记',inspection:'清点校核',documentation:'资料归档'}
export const states={open:'未接班',ack:'已接班'}
export const inbox={lead:'保养领班',desk:'服务台值班室'}
