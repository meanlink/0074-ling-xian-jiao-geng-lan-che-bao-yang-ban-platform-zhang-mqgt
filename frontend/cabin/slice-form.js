import {options} from './common.js'

export const editing=orders=>`<form id="slice"><label>工时单号<input name="code" required pattern="[A-Z0-9-]{3,24}"></label>
  <label>工作单<select name="work">${options(orders,o=>o.title)}</select></label><label>人员<input name="staff" required minlength="2"></label>
  <label>开始<input type="time" name="lo" required></label><label>结束<input type="time" name="hi" required></label>
  <label>投入比例<select name="weight"><option>100</option><option>75</option><option>50</option><option>25</option></select></label>
  <button>登记工时</button><p role="status"></p></form>`
