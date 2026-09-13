import sys
import os
import pygame as pg

pg.init()
pg.mixer.init()
pg.font.init()
pg.key.set_repeat(1, 1)
pg.mouse.set_visible(False)
pg.display.set_mode((1080, 720), pg.RESIZABLE)

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
#???
def resource_path(relative_path):
    if getattr(sys, 'frozen', False):
        return os.path.join(getattr(sys, '_MEIPASS', ''), relative_path)
    return os.path.join(ROOT_DIR, relative_path)

class GameState:
    def __init__(self):
        # 窗口
        self.Ssize = [1080, 720]       # 窗口大小
        self.Minsize = [540, 360]      # 最小窗口大小
        self.DefaultSsize = [1080, 720]  # 默认窗口大小（弹窗等固定布局的基准）
        self.MenuWidth = 360           # 菜单宽度

        # 世界
        self.ChunkSize = 4             # 区块阵列边长
        self.SubChunkSize = 16         # 区块边长
        self.BaseBlockSize = 256       # 单方块虚坐标边长
        self.Vsize = self.BaseBlockSize * self.SubChunkSize * self.ChunkSize  # 虚坐标边长
        self.Zoom = 2.0                # 缩放倍率（0.5-24）
        self.PistonMax = 12            # 最大推拉数量

        # 相机
        self.Vpos = [self.Vsize / 2, self.Vsize / 2]                           # 镜头虚坐标
        self.Spos = [(self.Ssize[0] - self.MenuWidth) / 2, self.Ssize[1] / 2]  # 镜头实坐标

        # 模拟
        self.Oneticktime = 250         # 单刻时间/ms
        self.simulating = False        # 模拟状态
        self.tick = 0                  # 当前 tick 计数

        # 设置
        self.put_when_simulating = True  # 允许运行时操作坏
        self.draw_structs = True         # 绘制区块线
        self.show_background = True      # 显示背景图片
        self.debug = False

        # 输入
        self.shiftdown = False         # shift标识
        self.key_repeat_slow = False   # 使用慢速重复
        self.keybindings = []          # 快捷键绑定列表

        # 方块选择器
        self.Trigger = None            # 当前选中的方块/区域类型
        self.Towards = 0               # 当前朝向

        # 区块数据
        self.ChunkList = []            # 区块列表
        self.ZoneList = []             # 区域列表
        self.PromptList = []           # 提示列表
        self.ChunkOrder = []           # 区块更新顺序
        self.BlockOrder = []           # 方块更新顺序

        # 对象
        self.screen = None             # 窗口
        self.clock = None              # 时钟
        self.pasttime = 0              # 前一tick时间

        # 资源
        self.ibackground = None        # 背景图片
        self.background_orig = None    # 原始背景图（仅窗口尺寸变化时重采样）
        self.ibackground_size = None   # 背景图对应的窗口尺寸
        self.crosshair = None          # 准星图片
        self.icrosshair = None         # 绘制准星
        self.Text = None               # 字体

state = GameState()