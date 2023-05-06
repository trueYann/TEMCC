import type Konva from 'konva'

export interface station {
  x: number
  y: number
  node_set?: node[]
  schedule_set?: plan[]
  start_time: number
  end_time: number
  base_node?: node
  chargeing_power: number
}
export interface node {
  iconObj: Konva.Image
  x: number
  y: number
  speed: number
  ddl: number
  cur_power: number
  target: number
  output_power: number
  reachable_stations: station[]
  free_time?: number
  station?: station
}
export type plan = {
  node: node
  move_time: number
  charge_time: number
  total: number
  origin_wait?: number
  station_wait?: number
  dif_time?: number
}

export class Device implements node {
  iconObj: Konva.Image
  x: number
  y: number
  speed: number
  ddl: number
  cur_power: number
  target: number
  output_power: number
  reachable_stations: station[]
  free_time?: number
  station?: station
  constructor(x: number, y: number, iconObj: Konva.Image) {
    this.x = x
    this.y = y
    this.iconObj = iconObj
    this.ddl = Math.floor(Math.random() * 290) + 10
    this.cur_power = Math.floor(Math.random() * 1500) + 200
    this.target = 10800
    this.output_power = 0.5
    this.speed = 0.5
    this.reachable_stations = []
  }
}

export class Station implements station {
  x: number
  y: number
  start_time: number
  end_time: number
  chargeing_power: number
  base_node?: node
  node_set?: node[]
  schedule_set?: plan[]
  constructor(x: number, y: number) {
    this.x = Math.floor(Math.random() * (x + 1))
    this.y = Math.floor(Math.random() * (y + 1))
    this.start_time = Infinity
    this.end_time = 0
    this.chargeing_power = 5
  }
}
