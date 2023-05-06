<template>
  <div class="App">
    <div class="SimulationArea" style="width: 1050px; padding: 20px">
      <!-- TODO: render elements -->
      <div ref="container"></div>
    </div>
    <div class="StatusBar">
      <div class="Legend">
        <div class="StationText">
          <font-awesome-icon :icon="['fas', 'tower-cell']" style="margin-right: 10px" />
          Charging Station
        </div>
        <div class="NodeText">
          <font-awesome-icon :icon="['fas', 'satellite']" style="margin-right: 10px" />
          Rechargable Node
        </div>
      </div>
      <div class="Params">
        <label>
          Test Area Width:
          <input type="number" v-model="width" />
        </label>
        <label>
          Test Area Height:
          <input type="number" v-model="height" />
        </label>
        <label>
          Station Count:
          <input type="number" v-model="stationCount" />
        </label>
        <label>
          Node Count:
          <input type="number" v-model="nodeCount" />
        </label>
        <div style="display: flex; width: 250px; justify-content: space-around">
          <button style="width: 100px" @click="init">Init</button>
          <button style="width: 100px" @click="handleStart">Start</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import Konva from 'konva'
import nodeIcon from '@/assets/satellite-solid.svg'
import stationIcon from '@/assets/tower-cell-solid.svg'
import { Device, Station, type node, type plan, type station } from '@/utils/types'
import { CSCO, reachable } from '@/utils/funcs'

const container = ref<string | HTMLDivElement>('')
const width = ref(1000)
const height = ref(600)
const stationCount = ref(3)
const nodeCount = ref(10)

const nodes = <node[]>[]

const stations = <station[]>[]

function init() {
  // 初始化Konva画布
  const canvasWidth = width.value + 50
  const canvasHeight = height.value + 50
  const xMin = 0,
    xMax = canvasWidth,
    yMin = 0,
    yMax = canvasHeight
  const gridSize = 50
  const stage = new Konva.Stage({
    container: container.value,
    width: canvasWidth,
    height: canvasHeight
  })

  const layer = new Konva.Layer()
  stage.add(layer)

  // draw grid
  for (let x = xMin; x <= xMax; x += gridSize) {
    layer.add(
      new Konva.Line({
        points: [x, yMin, x, yMax],
        stroke: 'gray',
        strokeWidth: 0.5,
        opacity: 0.5
      })
    )
  }
  for (let y = yMin; y <= yMax; y += gridSize) {
    layer.add(
      new Konva.Line({
        points: [xMin, y, xMax, y],
        stroke: 'gray',
        strokeWidth: 0.5,
        opacity: 0.5
      })
    )
  }

  // draw axis
  const axis = new Konva.Group()
  layer.add(axis)

  for (let x = xMin + gridSize; x < xMax; x += gridSize) {
    axis.add(
      new Konva.Line({
        points: [x, -5, x, 5],
        stroke: 'black',
        strokeWidth: 2
      })
    )
    axis.add(
      new Konva.Text({
        text: x.toString(),
        x: x - 5,
        y: 8,
        fontSize: 12,
        fontFamily: 'Calibri',
        fill: 'black'
      })
    )
  }

  for (let y = yMin + gridSize; y < yMax; y += gridSize) {
    axis.add(
      new Konva.Line({
        points: [-5, y, 5, y],
        stroke: 'black',
        strokeWidth: 2
      })
    )
    axis.add(
      new Konva.Text({
        text: y.toString(),
        x: 8,
        y: y - 5,
        fontSize: 12,
        fontFamily: 'Calibri',
        fill: 'black'
      })
    )
  }

  // 加载充电节点图片
  let mulitImg = [nodeIcon, stationIcon]
  let promiseAll = [],
    img: HTMLImageElement[] = []
  for (let i = 0; i < mulitImg.length; i++) {
    promiseAll[i] = new Promise((resolve, reject) => {
      img[i] = new Image()
      img[i].src = mulitImg[i]
      img[i].onload = function () {
        //第i张加载完成
        resolve(img[i])
      }
    })
  }
  Promise.all(promiseAll).then((p) => {
    //全部加载完成
    stations.length = 0
    nodes.length = 0

    for (let i = 0; i < stationCount.value; i++) {
      stations.push(new Station(width.value, height.value))
    }
    // 创建 Konva Image 对象
    stations.forEach((station) => {
      const stationIcon = new Konva.Image({
        image: img[0], // 图片资源
        x: station.x - 15, // x 坐标
        y: station.y - 15, // y 坐标
        width: 30, // 宽度
        height: 30 // 高度
      })

      // 将节点图标添加到图层上
      layer.add(stationIcon)
    })
    let i = 0
    while (i < nodeCount.value) {
      const x = Math.floor(Math.random() * (width.value + 1))
      const y = Math.floor(Math.random() * (height.value + 1))
      const nodeIcon = new Konva.Image({
        image: img[1], // 图片资源
        x: x - 10,
        y: y - 10,
        width: 20, // 宽度
        height: 20 // 高度
      })

      // 添加充电节点
      const device = new Device(x, y, nodeIcon)
      if (reachable(device, stations)) {
        i++
        nodes.push(device)
        layer.add(nodeIcon)
      }
    }
  })
  // 将图层添加到舞台
  stage.add(layer)

  // 绘制图层
  layer.draw()
}

function handleStart() {
  // TODO: generate elements and start simulation
  let flag = false
  for (const s of stations) {
    if (s.schedule_set?.length) {
      flag = true
      console.log(s)
    }
  }
  if (!flag) {
    CSCO(stations, nodes)
  }
  for (let s of stations) {
    if (s.schedule_set?.length) {
      for (let p of s.schedule_set) {
        moveNode(p, s)
      }
    }
  }
}

// 移动节点的动画函数
function moveNode(plan: plan, baseStation: station) {
  const oldX = plan.node.iconObj.x()
  const oldY = plan.node.iconObj.y()

  // 创建Tween动画
  const tween = new Konva.Tween({
    node: plan.node.iconObj,
    x: baseStation.x,
    y: baseStation.y,
    duration: plan.move_time / 1000,
    easing: Konva.Easings.Linear,
    onFinish: function () {
      // 动画完成后添加延迟后再进行回到原位置的动画
      setTimeout(function () {
        const returnTween = new Konva.Tween({
          node: plan.node.iconObj,
          x: oldX,
          y: oldY,
          duration: plan.move_time / 1000,
          easing: Konva.Easings.Linear
        })
        returnTween.play()
      }, plan.charge_time)
    }
  })

  // 播放Tween动画
  setTimeout(() => {
    tween.play()
  }, plan.origin_wait)
}
</script>

<style scoped>
.App {
  display: flex;
}
.StatusBar,
.Legend,
.Params {
  padding: 1rem;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: space-around;
}
.StatusBar {
  width: 25vw;
  height: 90vh;
}
.Legend {
  height: 20vh;
  margin-bottom: -100px;
  align-items: baseline;
}
.Params {
  height: 50vh;
  align-items: baseline;
}
</style>
