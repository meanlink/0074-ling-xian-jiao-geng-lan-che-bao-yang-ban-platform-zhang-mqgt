import {badge,h} from '/base.js'
import {states,span} from './time.js'

function history(item){
  const parts=[]
  if(item.origin!==item.shift&&item.origin_team)parts.push(`原由 ${h(item.origin_team)} 提请`)
  if(item.status==='ack')parts.push(`签收后仍留本班，待送达才移交`)
  return parts.join(' · ')
}

function signatures(item){
  const parts=[]
  if(item.initials)parts.push(`签收 ${h(item.initials)}${item.next_shift?` → ${h(item.next_team??item.next_shift)}`:''}`)
  if(item.delivered_team)parts.push(`送达 ${h(item.delivered_team)}`)
  if(item.closed_initials)parts.push(`办结 ${h(item.closed_initials)}`)
  else if(item.status==='done'&&item.initials)parts.push(`办结 ${h(item.initials)}`)
  return parts.join(' · ')
}

const targets=(later,withInitials)=>`${withInitials?`<label>接班签名<input name="initials" minlength="2" maxlength="24" required></label>`:''}
  <label>交给后续班<select name="next_shift" required>${later.map(row=>`<option value="${h(row.code)}">${h(row.team)} ${h(span(row.lo,row.hi))}</option>`).join('')}</select></label>
  <button ${later.length?'':'disabled'}>${withInitials?'签收并交班':'再交后续班'}</button>
  <p role="status">${later.length?'':'本班之后已无同站班次可接棒。'}</p>`

export const line=(item,user,later)=>`<article class="carry"><header><b>${h(item.id)} / ${h(item.work)}</b>${badge(states[item.status],item.status)}</header>
  <p>${h(item.matter)}</p><small>现归 ${h(item.holder_team??item.shift)} ${h(span(item.holder_lo,item.holder_hi))}${history(item)?' · '+history(item):''}</small>
  ${signatures(item)?`<small>${signatures(item)}</small>`:''}
  ${item.next_team&&item.status==='ack'?`<small>签收后仍留本班，待原班交接送达才移交 ${h(item.next_team)}</small>`:''}
  ${user.role==='reviewer'&&item.status==='open'?`<form data-note="${h(item.id)}">${targets(later,true)}</form>`:''}
  ${user.role==='reviewer'&&item.status==='held'?`<form data-close="${h(item.id)}"><label>办结签名<input name="initials" minlength="2" maxlength="24" required></label>
  <button>办结此条</button><p role="status"></p></form>
  <form data-note="${h(item.id)}">${targets(later,false)}</form>`:''}
  ${user.role!=='reviewer'&&item.status==='held'?`<small>等待复核员办结或再交后续班。</small>`:''}</article>`
