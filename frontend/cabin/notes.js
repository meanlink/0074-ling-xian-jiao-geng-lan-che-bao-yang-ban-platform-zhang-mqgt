import {api,empty,h,notice} from '/base.js'
import {link,mast,options,select} from './common.js'
import {roster,byShift} from './load.js'
import {line} from './note-line.js'
import {laterShifts} from './time.js'

function bind(root,user,code){
  const reload=()=>notes(root,user,code)
  for(const form of root.querySelectorAll('[data-note]')){
    form.onsubmit=async event=>{
      event.preventDefault()
      const button=event.submitter
      button.disabled=true
      try{await api('/api/cabin/followups/'+form.dataset.note,'PUT',Object.fromEntries(new FormData(form))); await reload()}
      catch(error){notice(form.querySelector('[role=status]'),error.message,true)}
      finally{button.disabled=false}
    }
  }
  for(const form of root.querySelectorAll('[data-close]')){
    form.onsubmit=async event=>{
      event.preventDefault()
      const button=event.submitter
      button.disabled=true
      try{await api('/api/cabin/followups/'+form.dataset.close+'/close','PUT',Object.fromEntries(new FormData(form))); await reload()}
      catch(error){notice(form.querySelector('[role=status]'),error.message,true)}
      finally{button.disabled=false}
    }
  }
  link(root.querySelector('#follow'),data=>api('/api/cabin/followups','POST',{...data,shift:code}),reload)
}

export async function notes(root,user,selected){
  const list=await roster()
  const code=selected??list[0]?.code
  if(!code){root.innerHTML=empty('班表为空。');return}
  const [rows,orders,waiting]=await Promise.all([byShift(code,'followups'),byShift(code,'orders'),byShift(code,'incoming')])
  const pick=row=>line(row,user,laterShifts(list,row.shift))
  root.innerHTML=mast('续办接棒','签收时指定同站后续班；原班送达后此条才归接手班，尚未办结的续办条会挡住封口。')
    +`<div class="cabin-layout"><section>
    ${rows.length?rows.map(pick).join(''):empty('本班目前没有现持的续办条。')}
    ${waiting.length?`<h2>上游已签收 · 尚未送达</h2>${waiting.map(row=>`<p class="waiting">${h(row.id)} · ${h(row.holder_team)} 签收，待其交接送达本班</p>`).join('')}`:''}
    </section>
    <aside>${select(list,code)}${user.role==='operator'?`<form id="follow"><label>续办条编号<input name="id" required pattern="[A-Z0-9-]{3,24}"></label>
    <label>关联工作单<select name="work">${options(orders,x=>x.title)}</select></label>
    <label>续办事项<textarea name="matter" minlength="5" maxlength="240" required></textarea></label><button>创建续办条</button><p role="status"></p></form>`:''}</aside></div>`
  root.querySelector('#shift-choice').onchange=e=>notes(root,user,e.target.value)
  bind(root,user,code)
}
