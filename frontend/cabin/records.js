import {api,empty,h} from '/base.js'
import {mast,link,select} from './common.js'
import {flowLines} from './bands.js'
import {roster,byShift} from './load.js'
import {minute,span} from './time.js'
import {editing} from './slice-form.js'

export async function records(root,user,selected){
  const list=await roster()
  const code=selected??list[0]?.code
  if(!code){root.innerHTML=empty('班表为空。');return}
  const shift=list.find(r=>r.code===code)
  const [rows,orders]=await Promise.all([byShift(code,'slices'),byShift(code,'orders')])
  root.innerHTML=mast('时段投入','同时处理几张工作单时，记录各自投入比例；同一人员在任一分钟的投入合计不能超过 100%。')
  +`<div class="cabin-layout"><section><h2>${h(shift.station)} · ${h(shift.team)} / ${span(shift.lo,shift.hi)}</h2>
    <ul class="spans">${flowLines(rows,shift)}</ul>${rows.length?'':empty('本班目前无工时。')}</section>
    <aside>${select(list,code)}${user.role==='operator'?editing(orders):''}</aside></div>`
  root.querySelector('#shift-choice').onchange=e=>records(root,user,e.target.value)
  link(root.querySelector('#slice'),data=>api('/api/cabin/slices','POST',{
    ...data,shift:code,lo:minute(data.lo),hi:minute(data.hi),weight:+data.weight}),()=>records(root,user,code))
}
