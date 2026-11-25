import {api,empty,h,waitJob} from '/base.js'
import {mast,link,select} from './common.js'
import {roster,handoff} from './load.js'
import {workTable} from './work-table.js'
import {inbox} from './time.js'

export async function report(root,user,selected){
  const list=await roster()
  const code=selected??list[0]?.code
  if(!code){root.innerHTML=empty('班表为空。');return}
  const {board,packet}=await handoff(code)
  root.innerHTML=mast('交接汇总','投入分钟由工作持续时间乘人员参与比例，汇总交接单与续办签名。')
  +`<div class="cabin-layout"><section>${workTable(board)}
    <p>投入合计 ${board.total_minutes} 人分钟 · 待接棒 ${board.pending} 项</p>
    ${board.accepted.map(note=>`<p>续办 ${h(note.id)} · ${h(note.initials)} 已接收</p>`).join('')}</section>
    <aside>${select(list,code)}${packet?`<h2>${packet.delivery==='sent'?'站内已送达':'站内待分发'}</h2><p>${inbox[packet.destination]}</p>`:
    user.role==='reviewer'?`<form><label>交班收件台<select name="destination"><option value="lead">保养领班</option><option value="desk">服务台值班室</option></select></label>
    <button>封口并分发</button><p role="status"></p></form>`:''}</aside></div>`
  root.querySelector('#shift-choice').onchange=e=>report(root,user,e.target.value)
  link(root.querySelector('form'),async data=>{
    const packet=await api('/api/cabin/handoff/'+code,'POST',data)
    await waitJob(packet.job_id)
  },()=>report(root,user,code))
}
