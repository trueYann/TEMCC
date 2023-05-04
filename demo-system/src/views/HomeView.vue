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
import type { node, station } from '@/utils/types'

const container = ref<string | HTMLDivElement>('')
const width = ref(1000)
const height = ref(600)
const stationCount = ref(3)
const nodeCount = ref(10)

const nodes = <node[]>[]

const stations = <station[]>[]

function init() {
  // 初始化数据
  nodes.length = 0
  stations.length = 0
  for (let i = 0; i < nodeCount.value; i++) {
    nodes.push({
      x: Math.floor(Math.random() * (width.value + 1)),
      y: Math.floor(Math.random() * (height.value + 1)),
      speed: 5
    })
  }
  for (let i = 0; i < stationCount.value; i++) {
    stations.push({
      x: Math.floor(Math.random() * (width.value + 1)),
      y: Math.floor(Math.random() * (height.value + 1))
    })
  }
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
  const nodeImg = new Image()
  const stationImg = new Image()
  nodeImg.src = nodeIcon
  stationImg.src = stationIcon

  // 监听图片加载完成的事件
  nodeImg.onload = () => {
    // 添加充电节点
    nodes.forEach((node) => {
      const nodeIcon = new Konva.Image({
        image: nodeImg, // 图片资源
        x: node.x - 10,
        y: node.y - 10,
        width: 20, // 宽度
        height: 20 // 高度
      })
      node.icon = nodeIcon
      layer.add(nodeIcon)
    })
  }

  stationImg.onload = () => {
    // 创建 Konva Image 对象
    stations.forEach((station) => {
      const stationIcon = new Konva.Image({
        image: stationImg, // 图片资源
        x: station.x - 15, // x 坐标
        y: station.y - 15, // y 坐标
        width: 30, // 宽度
        height: 30 // 高度
      })

      // 将节点图标添加到图层上
      layer.add(stationIcon)
    })
  }

  // 将图层添加到舞台
  stage.add(layer)

  // 绘制图层
  layer.draw()
}

function handleStart() {
  // TODO: generate elements and start simulation
  for (let node of nodes) {
    moveNode(node.icon as Konva.Image, stations[0], 2000)
    console.log(node)
  }
}

// 移动节点的动画函数
function moveNode(node: Konva.Image, baseStation: station, delay: number) {
  // 计算节点移动距离和角度
  const deltaX = baseStation.x - node.x()
  const deltaY = baseStation.y - node.y()
  const distance = Math.sqrt(deltaX ** 2 + deltaY ** 2)
  const oldX = node.x()
  const oldY = node.y()

  // 计算节点移动所需时间
  const speed = 500 // 5m/s(100x magnification)
  const time = distance / speed

  // 创建Tween动画
  const tween = new Konva.Tween({
    node: node,
    x: baseStation.x,
    y: baseStation.y,
    duration: time,
    easing: Konva.Easings.Linear,
    onFinish: function () {
      // 动画完成后添加延迟后再进行回到原位置的动画
      setTimeout(function () {
        const returnTween = new Konva.Tween({
          node: node,
          x: oldX,
          y: oldY,
          duration: time,
          easing: Konva.Easings.Linear
        })
        returnTween.play()
      }, delay)
    }
  })

  // 播放Tween动画
  tween.play()
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
