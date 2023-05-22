import type { node, plan, station } from './types'
import _ from 'lodash'

// function initSchedule()
function initSchedule(Station: station, Nodes: node[]): plan[] {
  const plan_set: plan[] = []
  let base: plan = { total: 0 } as plan

  // 找到baseline节点,初始化plan
  for (let node of Nodes) {
    let distance = Math.sqrt(Math.pow(node.x - Station.x, 2) + Math.pow(node.y - Station.y, 2))
    let move_time = distance / node.speed
    if (move_time * node.output_power < node.cur_power) {
      let charge_time =
        (node.target - node.cur_power + move_time * node.output_power) / Station.chargeing_power
      const td_max = node.ddl - 2 * move_time - charge_time
      if (td_max >= 0) {
        const plan: plan = { node, move_time, charge_time, total: move_time + charge_time, td_max }
        plan_set.push(plan)
        base.total = plan.total > base.total ? plan.total : base.total
      }
    }
  }

  // 计算每个节点 wait_time
  for (let plan of plan_set) {
    plan.dif_time = base.total - plan.total
    const D = Station.chargeing_power / plan.node.output_power
    const upper_OW =
      (plan.node.cur_power - plan.move_time * plan.node.output_power) / plan.node.output_power
    //  1. All wait at origin (plan.origin_wait + extra_charge_time <= △T)
    if ((D + 1) * plan.td_max <= plan.dif_time) {
      plan.origin_wait = D * plan.td_max > upper_OW ? upper_OW : D * plan.td_max
      plan.charge_time += plan.origin_wait / D
      plan.total = plan.origin_wait + plan.move_time + plan.charge_time
    }

    //  2. Origin wait + Station wait (ddl≤ △T < charging_power / node.ouput_power * ddl)
    else if (plan.dif_time >= plan.td_max && plan.dif_time < (D + 1) * plan.td_max) {
      plan.origin_wait =
        plan.dif_time - plan.td_max > upper_OW ? upper_OW : plan.dif_time - plan.td_max
      plan.charge_time += plan.origin_wait / D
      plan.station_wait = plan.td_max - plan.origin_wait / D
      plan.total = plan.origin_wait + plan.move_time + plan.station_wait + plan.charge_time
    }

    //  3. All wait at station  (ddl > △T)
    else if (plan.td_max > plan.dif_time) {
      plan.station_wait = plan.dif_time
      plan.total += plan.station_wait
    }
  }
  // console.log('plan_set', plan_set)

  return plan_set
}

function nodelaySchedule(Station: station, Nodes: node[]): plan[] {
  const plan_set: plan[] = []
  let base: plan = { total: 0 } as plan

  // 找到baseline节点,初始化plan
  for (let node of Nodes) {
    let distance = Math.sqrt(Math.pow(node.x - Station.x, 2) + Math.pow(node.y - Station.y, 2))
    let move_time = distance / node.speed
    if (move_time * node.output_power < node.cur_power) {
      let charge_time =
        (node.target - node.cur_power + move_time * node.output_power) / Station.chargeing_power
      const td_max = node.ddl - 2 * move_time - charge_time
      if (td_max >= 0) {
        const plan: plan = { node, move_time, charge_time, total: move_time + charge_time, td_max }
        plan_set.push(plan)
        base.total = plan.total > base.total ? plan.total : base.total
      }
    }
  }

  return plan_set
}

function findMinCostStation(
  node: node,
  stations: station[]
): { cost: number; minStation: station; start: number; end: number } {
  let ret: ReturnType<typeof findMinCostStation> = { cost: Infinity } as ReturnType<
    typeof findMinCostStation
  >

  for (let rs of node.reachable_stations) {
    const s = stations.find((station) => station.x === rs.x && station.y === rs.y)
    const distance = Math.sqrt(Math.pow(node.x - s.x, 2) + Math.pow(node.y - s.y, 2))
    const move_time = distance / node.speed
    const charge_time =
      (node.target - node.cur_power + move_time * node.output_power) / s.chargeing_power
    if (s.end_time === 0) {
      ret =
        charge_time < ret.cost
          ? { cost: charge_time, minStation: s, start: move_time, end: charge_time }
          : ret
    } else {
      let cost = 0
      if (move_time + charge_time > s.end_time) {
        if (move_time >= s.start_time) {
          cost = move_time + charge_time - s.end_time
        } else {
          cost = s.start_time + charge_time - s.end_time
        }
      } else {
        if (move_time < s.start_time) {
          cost = s.start_time - move_time
        } else {
          return { cost: 0, minStation: s, start: s.start_time, end: s.end_time }
        }
      }
      ret =
        cost < ret.cost
          ? { cost, minStation: s, start: move_time, end: move_time + charge_time }
          : ret
    }
  }
  return ret
}

export function reachable(node: node, stations: station[], reachableNum = 0): boolean {
  for (let s of stations) {
    let distance = Math.sqrt(Math.pow(node.x - s.x, 2) + Math.pow(node.y - s.y, 2))
    let move_time = distance / node.speed
    if (
      node.cur_power > move_time * node.output_power &&
      node.ddl >
        2 * move_time +
          (node.target - node.cur_power + node.output_power * move_time) / s.chargeing_power
    ) {
      node.reachable_stations.push(s)
    }
  }
  if (reachableNum !== 0) {
    if (node.reachable_stations.length !== reachableNum) {
      return false
    }
    return true
  }
  return Boolean(node.reachable_stations.length)
}

function min_margin_cost_schedule(
  schedules: plan[],
  base_start = Infinity,
  base_end = 0
): { min_radio: number; time_slot: { start: number; end: number }; node_set: node[] } {
  let min_radio = Infinity
  let time_slot = { start: base_start, end: base_end }
  let node_set = [] as node[]

  const S = schedules.filter(
    (plan) => plan.total - plan.charge_time < base_start || plan.total > base_end
  )

  if (S.length) {
    for (let start of S.map((p) => p.total - p.charge_time)) {
      for (let end of S.map((p) => p.total)) {
        if (end <= start) {
          continue
        } else {
          let radio = Infinity
          const temp = []
          for (let t of S) {
            if (start <= t.total - t.charge_time && end >= t.total) {
              temp.push(t.node)
            }
          }
          if (temp.length) {
            if (base_end !== 0) {
              if (base_end > end) {
                radio = base_start >= start ? (base_start - start) / temp.length : 0
              } else {
                radio =
                  base_start >= start
                    ? (end - base_end + base_start - start) / temp.length
                    : (end - base_end) / temp.length
              }
            } else {
              radio = (end - start) / temp.length
            }
            if (radio < min_radio) {
              min_radio = radio
              node_set = temp
              time_slot = { start, end }
            }
          }
        }
      }
    }
  }

  return { min_radio, time_slot, node_set }
}
type mmcs_ret = ReturnType<typeof min_margin_cost_schedule>

export function CSCO(Stations: station[], Nodes: node[]) {
  // console.log('Stations: ', Stations)
  // console.log('Node: ', Nodes, Nodes.length)
  while (Nodes.length > 0) {
    let temp_set: { mmcs: mmcs_ret; station: station; schedule: plan[] } = {
      mmcs: { min_radio: Infinity } as mmcs_ret,
      station: { node_set: [] as node[], start_time: Infinity, end_time: 0 } as station,
      schedule: [] as plan[]
    }
    for (let s of Stations) {
      let schedule, MMCS
      if (s.node_set?.length) {
        schedule = initSchedule(s, [...s.node_set, ...Nodes])
        MMCS = min_margin_cost_schedule(schedule, s.start_time, s.end_time)
      } else {
        schedule = initSchedule(s, [...Nodes])
        MMCS = min_margin_cost_schedule(schedule)
      }
      if (MMCS.min_radio < temp_set.mmcs.min_radio) {
        temp_set.mmcs = MMCS
        temp_set.station = s
        temp_set.schedule = schedule
      }
    }
    // console.log('temp set', temp_set)
    temp_set.station.schedule_set = temp_set.schedule
    if (
      temp_set.mmcs.time_slot?.start &&
      temp_set.mmcs.time_slot.start < temp_set.station.start_time
    ) {
      temp_set.station.start_time = temp_set.mmcs.time_slot.start
    }
    if (temp_set.mmcs.time_slot?.end && temp_set.mmcs.time_slot.end > temp_set.station.end_time) {
      temp_set.station.end_time = temp_set.mmcs.time_slot.end
    }
    if (temp_set.station.node_set?.length) {
      temp_set.station.node_set = temp_set.station.node_set.concat(temp_set.mmcs.node_set)
    } else {
      temp_set.station.node_set = temp_set.mmcs.node_set
    }
    if (temp_set.mmcs.node_set) {
      Nodes = Nodes.filter((n: node) => !temp_set.mmcs.node_set.includes(n))
    } else {
      Nodes = []
    }
  }
  let CSC = 0
  for (let s of Stations) {
    if (s.end_time !== 0) {
      CSC += s.end_time - s.start_time
    }
  }
  // console.log('CSCO Final:', Stations)
  return CSC
}

export function SCSCO(Stations: station[], Nodes: node[]) {
  const m_Stations = _.cloneDeep(Stations)
  let m_Nodes = _.cloneDeep(Nodes)
  // console.log('m_Stations: ', m_Stations)
  // console.log('m_Nodes: ', m_Nodes, m_Nodes.length)
  while (m_Nodes.length > 0) {
    let temp_set: { mmcs: mmcs_ret; station: station; schedule: plan[] } = {
      mmcs: { min_radio: Infinity } as mmcs_ret,
      station: { node_set: [] as node[], start_time: Infinity, end_time: 0 } as station,
      schedule: [] as plan[]
    }
    for (let s of m_Stations) {
      let schedule, MMCS
      if (s.node_set?.length) {
        schedule = nodelaySchedule(s, [...s.node_set, ...m_Nodes])
        MMCS = min_margin_cost_schedule(schedule, s.start_time, s.end_time)
      } else {
        schedule = nodelaySchedule(s, [...m_Nodes])
        MMCS = min_margin_cost_schedule(schedule)
      }
      if (MMCS.min_radio < temp_set.mmcs.min_radio) {
        temp_set = {
          mmcs: MMCS,
          station: s,
          schedule
        }
      }
    }
    temp_set.station.schedule_set = temp_set.schedule
    if (
      temp_set.mmcs.time_slot?.start &&
      temp_set.mmcs.time_slot.start < temp_set.station.start_time
    ) {
      temp_set.station.start_time = temp_set.mmcs.time_slot.start
    }
    if (temp_set.mmcs.time_slot?.end && temp_set.mmcs.time_slot.end > temp_set.station.end_time) {
      temp_set.station.end_time = temp_set.mmcs.time_slot.end
    }
    if (temp_set.station.node_set?.length) {
      temp_set.station.node_set = temp_set.station.node_set.concat(temp_set.mmcs.node_set)
    } else {
      temp_set.station.node_set = temp_set.mmcs.node_set
    }
    if (temp_set.mmcs.node_set) {
      m_Nodes = m_Nodes.filter((n: node) => !temp_set.mmcs.node_set.includes(n))
    } else {
      m_Nodes = []
    }
  }
  let CSC = 0
  for (let s of m_Stations) {
    if (s.end_time !== 0) {
      CSC += s.end_time - s.start_time
    }
  }
  // console.log('SCSCO Final:', m_Stations)
  return CSC
}

export function NCSA(Stations: station[], Nodes: node[]) {
  const m_Stations = _.cloneDeep(Stations)
  let m_Nodes = _.cloneDeep(Nodes)
  let CSC = 0
  for (let n of m_Nodes) {
    const s = n.nearestStation()
    const ms = m_Stations.find((fs: station) => fs.x === s.x && fs.y === s.y)

    ms.node_set.push(n)
  }
  for (let s of m_Stations) {
    if (s.node_set.length === 0) {
      continue
    }
    const plan_set = initSchedule(s, s.node_set)
    for (let p of plan_set) {
      s.start_time = p.total - p.charge_time < s.start_time ? p.total - p.charge_time : s.start_time
      s.end_time = p.total > s.end_time ? p.total : s.end_time
    }
    CSC += s.end_time - s.start_time
  }
  return CSC
}

export function SOA(Stations: station[], Nodes: node[]) {
  const m_Stations = _.cloneDeep(Stations)
  let m_Nodes = _.cloneDeep(Nodes)
  let CSC = 0

  while (m_Nodes.length) {
    let flag: { mc: ReturnType<typeof findMinCostStation>; index: number } = {
      mc: { cost: Infinity } as ReturnType<typeof findMinCostStation>,
      index: null
    }
    for (let [index, n] of m_Nodes.entries()) {
      const ret = findMinCostStation(n, m_Stations)
      if (ret.cost < flag.mc.cost) {
        flag = { mc: ret, index }
      }
    }
    const minStation = flag.mc.minStation
    minStation.node_set.push(m_Nodes[flag.index])
    minStation.start_time =
      flag.mc.start < minStation.start_time ? flag.mc.start : minStation.start_time
    minStation.end_time = flag.mc.end > minStation.end_time ? flag.mc.end : minStation.end_time
    m_Nodes.splice(flag.index, 1)
  }

  for (let s of m_Stations) {
    if (s.node_set.length === 0) {
      continue
    }
    const plan_set = initSchedule(s, s.node_set)
    for (let p of plan_set) {
      s.start_time = p.total - p.charge_time < s.start_time ? p.total - p.charge_time : s.start_time
      s.end_time = p.total > s.end_time ? p.total : s.end_time
    }
    CSC += s.end_time - s.start_time
  }
  return CSC
}
