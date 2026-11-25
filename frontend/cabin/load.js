import {api} from '/base.js'

export const roster=()=>api('/api/cabin/shifts')
export const byShift=(code,resource)=>api('/api/cabin/shifts/'+code+'/'+resource)
export const handoff=code=>api('/api/cabin/handoff/'+code)
