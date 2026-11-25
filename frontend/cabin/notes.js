import {api,empty} from '/base.js'
import {link,mast,options,select} from './common.js'
import {roster,byShift} from './load.js'
import {line} from './note-line.js'

export async function notes(root,user,selected){
  const list=await roster()
  const code=selected??list[0]?.code
  if(!code){root.innerHTML=empty('班表为空。');return}
  const [rows,orders]=await Promise.all([byShift(code,'followups'),byShift(code,'orders')])
  root.innerHTML=mast('续办接棒','即使当前班未全部处理，也须记录需继续跟进的事项并由接班人签收。')
    +`<div class="cabin-layout"><section>${rows.length?rows.map(item=>line(item,user.role==='reviewer')).join(''):empty('本班没有续办事项。')}</section>
    <aside>${select(list,code)}${user.role==='operator'?`<form id="follow"><label>续办条编号<input name="id" required pattern="[A-Z0-9-]{3,24}"></label>
    <label>关联工作单<select name="work">${options(orders,x=>x.title)}</select></label>
    <label>续办事项<textarea name="matter" minlength="5" maxlength="240" required></textarea></label><button>创建续办条</button><p role="status"></p></form>`:''}</aside></div>`
  root.querySelector('#shift-choice').onchange=e=>notes(root,user,e.target.value)
  for(const form of root.querySelectorAll('[data-note]'))link(form,data=>api('/api/cabin/followups/'+form.dataset.note,'PUT',data),()=>notes(root,user,code))
  link(root.querySelector('#follow'),data=>api('/api/cabin/followups','POST',{...data,shift:code}),()=>notes(root,user,code))
}
