import {mount} from '/base.js'
import {roster} from './roster.js'
import {records} from './records.js'
import {notes} from './notes.js'
import {report} from './report.js'

const sections={roster,records,notes,report}
mount({title:'岭线交更 · 缆车保养班台账',kicker:'杉溪缆道站 / 保养班记录',
  pages:{roster:'站点班表',records:'时段投入',notes:'续办接棒',report:'交接汇总'},
  render:(slug,root,user)=>sections[slug](root,user)})
