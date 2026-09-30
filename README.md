# StructTester For MCBE
![Python](https://img.shields.io/badge/python-3.13-blue.svg)
![pygame](https://img.shields.io/badge/pygame-2.6-green.svg)

#### 基于Minecraft基岩版原版特性与社区相关研究，复刻原版机制的2D模拟器，用于基岩版红石树场架构设计

## 目录
- [功能特性](#功能特性)
- [界面与操作](#界面与操作)
- [注意事项](#注意事项)
- [参考](#参考)
- [下载](#下载)
## 功能特性

- 相比游戏内更便利的功能，支持单步/连续模拟，存档读档，mb可视化，充能特效等
- 复刻原版机制，包括游戏刻与更新流程，区块更新与优先级，计划刻，部分常用方块与红石原件的功能特性等
- 复刻了大部分的树苗生长，空间检测，主干/侧枝/树叶生成等特性，尚未有严谨反编译结果的，则在游戏内实测统计/使用近似方法实现相关特性
- 简化了机械运动以外的功能，使用可叠加的区域实现精确的充能控制，树苗生长，自动放置/破坏方块等
- 更多

---

## 界面与操作

| 输入            | 作用                         |
|---------------|----------------------------|
| 右键            | 放置方块（+Shift：配置区域 / 叠放粘性活塞） |
| 左键            | 移除方块                       |
| 中键            | 吸取光标所指方块类型                 |
| 滚轮            | 缩放视角                       |
| W / A / S / D | 移动视角                       |
| T             | 开关侧边栏                      |
| Esc           | 关闭弹窗                       |
| Enter         | 确认弹窗                       |
| Shift         | 切换侧边栏工具                    |

---

## 注意事项
机制复刻并未，也做不到严格遵照原版，存在很多用不严谨换取便利的地方(如并未实现方块实体)，精度也只精确到了游戏刻，不涉及更深层的方法调用乃至内存操作级别

使用ai辅助，实际代码水平弗如豆包，整体架构可以说一坨史，也难免会有不严谨，实现错误，恳请批评与指正，也很希望有更多直接的反编译资源与进一步优化的建议

**目前未实现** ：大橡树，巨型蘑菇，邻接表机制 后续会逐步更新

---
## 参考
[MinecraftWiki](https://www.bilibili.com/opus/1133540176957538311) 


[树苗机制](https://www.bilibili.com/opus/1133540176957538311)
by 8848yyds

[游戏机制-世界运行](https://www.bilibili.com/read/readlist/rl322068)
by hhhxiao_

[红石机制-活塞](https://www.bilibili.com/read/readlist/rl246316)
by origin0110 , hhhxiao_

[游戏与红石机制-观察者](https://www.bilibili.com/read/readlist/rl820632)
by 何以贯之

## 下载
仅支持windows-x64 : [点此下载](https://github.com/EndistD/StructTesterforMCBE/releases/download/v0.3/Simulator.zip)
，解压开盖即食