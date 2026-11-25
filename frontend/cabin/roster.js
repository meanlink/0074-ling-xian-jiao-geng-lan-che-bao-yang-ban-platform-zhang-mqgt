import {api,h} from '/base.js'
import {mast} from './common.js'
import {span} from './time.js'

export async function roster(root){
  const list=await api('/api/cabin/shifts')
  const stations=[...new Set(list.map(row=>row.station))]
  root.innerHTML=mast('站点班表','按站点及班次准备保养登记和接班工作。班表给出允许登记的时间边界。')
    +`<div class="roster-track">${stations.map(station=>`<section><h2>${h(station)}</h2><ul>
      ${list.filter(row=>row.station===station).map(row=>`<li><b>${h(row.team)}</b><time>${span(row.lo,row.hi)}</time>
      <small>${h(row.roster_day)} · ${h(row.code)}</small></li>`).join('')}</ul></section>`).join('')}</div>`
}
