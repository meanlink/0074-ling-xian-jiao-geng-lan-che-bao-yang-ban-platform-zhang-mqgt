import {h} from '/base.js'
import {units} from './time.js'

export function workTable(board) {
  return `<div class="manifest"><h2>工作单人力分布</h2>${board.work.map(row=>`<div>
     <p><b>${h(row.title)}</b><small>${units[row.family]} · ${h(row.code)}</small></p>
     <meter value="${row.minutes}" min="0" max="${board.total_minutes||1}"></meter>
     <b>${row.minutes} 分钟</b></div>`).join('')}</div>`
}
