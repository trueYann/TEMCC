import type { node, plan, station } from './types'

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
        (node.target - node.cur_power - move_time * node.output_power) / Station.chargeing_power
      const plan: plan = { node, move_time, charge_time, total: move_time + charge_time }
      plan_set.push(plan)
      base.total = plan.total > base.total ? plan.total : base.total
    }
  }

  // 计算每个节点 wait_time
  for (let plan of plan_set) {
    plan.dif_time = base.total - plan.total
    const D = Station.chargeing_power / plan.node.output_power

    //  1. All wait at origin (plan.origin_wait + extra_charge_time <= △T)
    if ((D + 1) * plan.node!.ddl <= plan.dif_time) {
      plan.origin_wait = D * plan.node.ddl
      plan.charge_time += plan.node.ddl
      plan.total = plan.origin_wait + plan.move_time + plan.charge_time
    }

    //  2. Origin wait + Station wait (ddl≤ △T < charging_power / node.ouput_power * ddl)
    else if (plan.dif_time >= plan.node.ddl && plan.dif_time < (D + 1) * plan.node.ddl) {
      plan.origin_wait = plan.dif_time - plan.node.ddl
      plan.charge_time += plan.origin_wait / D
      plan.station_wait = plan.node.ddl - plan.origin_wait / D
      plan.total = plan.origin_wait + plan.move_time + plan.station_wait + plan.charge_time
    }

    //  3. All wait at station  (ddl > △T)
    else if (plan.node.ddl > plan.dif_time) {
      plan.station_wait = plan.dif_time
      plan.total += plan.station_wait
    }
  }
  // console.log('plan_set', plan_set)

  return plan_set
}

export function reachable(node: node, stations: station[]): boolean {
  for (let s of stations) {
    let distance = Math.sqrt(Math.pow(node.x - s.x, 2) + Math.pow(node.y - s.y, 2))
    let move_time = distance / node.speed
    if (move_time * node.output_power < node.cur_power) {
      node.reachable_stations.push(s)
    }
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
  console.log('Stations: ', Stations)
  console.log('Node: ', Nodes, Nodes.length)
  while (Nodes.length > 0) {
    let temp_set: { mmcs: mmcs_ret; station: station; schdule: plan[] } = {
      mmcs: { min_radio: Infinity } as mmcs_ret,
      station: { node_set: [] as node[], start_time: Infinity, end_time: 0 } as station,
      schdule: [] as plan[]
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
        temp_set.schdule = schedule
      }
    }
    // console.log('temp set', temp_set)
    temp_set.station.schedule_set = temp_set.schdule
    temp_set.station.start_time =
      temp_set.mmcs.time_slot.start < temp_set.station.start_time
        ? temp_set.mmcs.time_slot.start
        : temp_set.station.start_time
    temp_set.station.end_time =
      temp_set.mmcs.time_slot.end > temp_set.station.end_time
        ? temp_set.mmcs.time_slot.end
        : temp_set.station.end_time
    if (temp_set.station.node_set?.length) {
      temp_set.station.node_set = temp_set.station.node_set.concat(temp_set.mmcs.node_set)
    } else {
      temp_set.station.node_set = temp_set.mmcs.node_set
    }

    //  temp_set.station.node_set?.length
    //   ? temp_set.station.node_set.concat(temp_set.mmcs.node_set)
    //   : temp_set.mmcs.node_set
    Nodes = Nodes.filter((n) => !temp_set.mmcs.node_set.includes(n))
  }
  // console.log('Final:', Stations)
}
