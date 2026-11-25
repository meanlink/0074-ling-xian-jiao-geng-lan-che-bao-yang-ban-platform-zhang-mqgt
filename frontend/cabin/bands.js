import {h} from '/base.js'
import {span} from './time.js'

function pill(row,shift){
  const extent=shift.hi-shift.lo
  return `<div class="track-bar"><span style="left:${100*(row.lo-shift.lo)/extent}%;
    width:${100*(row.hi-row.lo)/extent}%" title="${h(row.work)} / ${span(row.lo,row.hi)}"></span></div>`
}

export const flowLines=(rows,shift)=>rows.map(row=>`<li><b>${h(row.staff)} / ${h(row.work)}</b>
  ${pill(row,shift)}<time>${span(row.lo,row.hi)}</time><strong>${row.weight}%</strong></li>`).join('')
