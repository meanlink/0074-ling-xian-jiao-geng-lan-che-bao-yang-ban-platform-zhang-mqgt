import {badge,h} from '/base.js'
import {states} from './time.js'

export const line=(item,reviewer)=>`<article class="carry"><header><b>${h(item.id)} / ${h(item.work)}</b>${badge(states[item.status],item.status)}</header>
  <p>${h(item.matter)}</p>${item.initials?`<small>接班 ${h(item.initials)}</small>`:''}
  ${reviewer&&item.status==='open'?`<form data-note="${h(item.id)}"><label>接班签名<input name="initials" minlength="2" maxlength="24" required></label>
  <button>签收续办</button><p role="status"></p></form>`:''}</article>`
