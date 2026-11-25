import {h,notice} from '/base.js'
import {span} from './time.js'

export const mast=(title,line)=>`<header class="cabin-head"><h1>${h(title)}</h1><p>${h(line)}</p></header>`
export const options=(rows,label,code)=>rows.map(row=>`<option value="${h(row.code)}" ${row.code===code?'selected':''}>${h(label(row))}</option>`).join('')
export const select=(rows,code)=>`<label>站点班次<select id="shift-choice">${options(rows,row=>row.station+' / '+row.team+' '+span(row.lo,row.hi),code)}</select></label>`
export function link(form,submit,reload){
  if(!form)return
  form.onsubmit=async event=>{
    event.preventDefault()
    const button=event.submitter
    button.disabled=true
    try{await submit(Object.fromEntries(new FormData(form))); await reload()}
    catch(error){notice(form.querySelector('[role=status]'),error.message,true)}
    finally{button.disabled=false}
  }
}
