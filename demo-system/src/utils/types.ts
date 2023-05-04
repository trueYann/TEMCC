import type Konva from "konva"

export type station = {
  x: number
  y: number
}
export type node = {
  x: number
  y: number
  speed: number
  icon?: Konva.Image
  station?: station
}