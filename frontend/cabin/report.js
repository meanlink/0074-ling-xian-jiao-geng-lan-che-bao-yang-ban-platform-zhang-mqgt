import {api,badge,empty,h,notice,waitJob} from '/base.js'
import {mast,select} from './common.js'
import {roster,handoff,allFollowups} from './load.js'
import {workTable} from './work-table.js'
import {inbox,span,states,deliveries} from './time.js'

function trace(code,all){
  const active=all.filter(item=>item.status!=='done')
  const done=all.filter(item=>item.status==='done')
  const mine=active.filter(item=>item.shift===code)
  const elsewhere=active.filter(item=>item.shift!==code)
  const block=item=>`<li><b>${h(item.id)}</b> ${badge(states[item.status],item.status)}
    <small>现归 ${h(item.holder_team??item.shift)} ${h(span(item.holder_lo,item.holder_hi))}
    ${item.next_team?` · 待交 ${h(item.next_team)}`:''}${item.delivered_team?` · 已送达 ${h(item.delivered_team)}`:''}</small></li>`
  const closed=item=>`<li><b>${h(item.id)}</b> ${badge(states.done,'done')}
    <small>原由 ${h(item.origin_team??item.origin)} 提请 · 送达 ${h(item.delivered_team??item.delivered_to)}
    ${item.closed_initials?` · 办结 ${h(item.closed_initials)}`:''}</small></li>`
  return `<div class="manifest"><h2>续办现归哪班</h2>
    ${mine.length?`<h3>本班现持</h3><ul class="trace">${mine.map(block).join('')}</ul>`:''}
    ${elsewhere.length?`<h3>其他班现持</h3><ul class="trace">${elsewhere.map(block).join('')}</ul>`:''}
    ${done.length?`<h3>已办结</h3><ul class="trace">${done.map(closed).join('')}</ul>`:''}
    ${all.length?'':empty('还没有续办条。')}</div>`
}

export async function report(root,user,selected){
  const list=await roster()
  const code=selected??list[0]?.code
  if(!code){root.innerHTML=empty('班表为空。');return}
  const [{board,packet,job,incoming},all]=await Promise.all([handoff(code),allFollowups()])
  const pending=packet?.delivery==='pending'
  const failed=pending&&job?.status==='failed'
  root.innerHTML=mast('交接汇总','投入分钟由工作持续时间乘人员参与比例。封口前须签收全部续办，接手班有待办的续办条时不能封口。')
  +`<div class="cabin-layout"><section>${workTable(board)}
    <p>投入合计 ${board.total_minutes} 人分钟 · 待签收 ${board.pending??0} 项 · 本班待办 ${board.unsettled??0} 项 · 待上游送达 ${board.incoming??incoming.length} 项</p>
    ${(board.accepted??[]).map(note=>`<p>续办 ${h(note.id)} · ${h(states[note.status]??'已签收')}${note.initials?` · ${h(note.initials)}`:''}${note.next_team?` → ${h(note.next_team)}`:''}</p>`).join('')}
    ${incoming.length?`<p>上游班次已签收但尚未送达：${incoming.map(row=>h(row.id)).join('、')}</p>`:''}
    ${trace(code,all)}</section>
    <aside>${select(list,code)}${packet?`<h2>${deliveries[packet.delivery]}</h2><p>${h(inbox[packet.destination])}</p>
      ${pending&&!failed?`<p>分发任务${job?`（${h(job.status)}）`:''}进行中，交接单已冻结。</p>`:''}
      ${failed?`<p data-type="error">分发失败：${h(job.error)}。重试沿用同一交接单，不会再生成续办。</p>
        <button type="button" data-retry>重新分发</button><p role="status"></p>`:''}`:
    user.role==='reviewer'?`<form><label>交班收件台<select name="destination"><option value="lead">保养领班</option><option value="desk">服务台值班室</option></select></label>
    <button>封口并分发</button><p role="status"></p></form>`:''}
    ${incoming.length?'<p>上游已签收的续办条尚未送达，暂不能封口。</p>':''}</aside></div>`
  root.querySelector('#shift-choice').onchange=e=>report(root,user,e.target.value)
  const form=root.querySelector('form')
  if(form)form.onsubmit=async event=>{
    event.preventDefault()
    const button=event.submitter
    button.disabled=true
    try{
      const created=await api('/api/cabin/handoff/'+code,'POST',Object.fromEntries(new FormData(form)))
      await waitJob(created.job_id)
      await report(root,user,code)
    }catch(error){notice(form.querySelector('[role=status]'),error.message,true);button.disabled=false}
  }
  const retry=root.querySelector('[data-retry]')
  if(retry)retry.onclick=async()=>{
    retry.disabled=true
    try{
      const {job_id}=await api('/api/cabin/handoff/'+code+'/retry','POST')
      await waitJob(job_id)
      await report(root,user,code)
    }catch(error){notice(retry.parentElement.querySelector('[role=status]'),error.message,true)}
    finally{retry.disabled=false}
  }
}
