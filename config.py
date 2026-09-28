import sys
import os
import heapq
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


class PendingTick:
    def __init__(self, due, owner, callback, *args):
        self.due = due      # 该区块时间轴上的到期刻
        self.owner = owner  # 创建该计划刻的方块实例
        self.callback = callback  # 函数引用
        self.args = args
        self.cancelled = False  # 删除标记


class PendingTickQueue:

    def __init__(self):
        self.timer = 0             # 本队列独立时间轴（每次 update +1）
        self.heap = []             # 最小堆[(due, seq, PendingTick)]
        self._seq = 0
        self._due = []             # 本次 update 已弹出、正在执行的计划刻（供严格查询统计）
        self.cid = None            # 本队列在 PendingTickList 中的索引(区块id)，惰性确认

    def schedule(self, delay, owner, callback, *args):
        """为 owner 延迟 delay 刻执行 callback（按到期时刻压入堆）。"""
        self._seq += 1
        item = PendingTick(self.timer + delay, owner, callback, *args)
        heapq.heappush(self.heap, (item.due, self._seq, item))

    def cancel(self, owner):
        """将 owner 的全部计划刻标记为取消（惰性删除）。"""
        for _, _, item in self.heap:
            if item.owner is owner:
                item.cancelled = True

    def has_pending(self, owner, strict=True):
        """owner 是否已有未取消的未决计划刻。
        strict=True：外部来源（nc/被推）用，连同本次已弹出、正在执行的计划刻一起统计；
        strict=False：计划刻内部续接用，只看堆，从而允许自己紧接着添加下一个计划刻。"""
        if strict and any(it.owner is owner for it in self._due):
            return True
        return any(not it.cancelled for _, _, it in self.heap if it.owner is owner)

    def update(self, limit=100):
        """推进时间轴，弹出并依序执行全部到期计划刻。
        owner 已不在本队列对应区块(如被搬跨区)的残留计划刻，视为伪删除丢弃，不占执行名额。"""
        import functions as fun  # 延迟导入，避免循环依赖
        self.timer += 1
        if self.cid is None:
            self.cid = state.PendingTickList.index(self)
        due = []
        while self.heap and self.heap[0][0] <= self.timer:
            item = heapq.heappop(self.heap)[2]
            if item.cancelled or not item.owner.is_alive():
                continue  # 弹出即剔，不占执行名额
            if fun.cturncid(item.owner.cpos) != self.cid:
                continue  # owner 已迁出本区块，残留计划刻丢弃(同伪删除，不占名额)
            due.append(item)
            if len(due) >= limit:
                break
        self._due = due          # 执行期间对外可见，避免同批计划刻互相"看不见"
        for item in due:
            item.callback(*item.args)
        self._due = []


class GameState:
    def __init__(self):
        # 窗口
        self.Ssize = [1080, 720]       # 窗口大小
        self.Minsize = [540, 360]      # 最小窗口大小
        self.DefaultSsize = [1080, 720]  # 默认窗口大小
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
        self.PendingTickList = []      # 计划刻队列

        # 对象
        self.screen = None             # 窗口
        self.clock = None              # 时钟
        self.pasttime = 0              # 前一tick时间

        # 资源
        self.ibackground = None        # 背景图片
        self.background_orig = None    # 原始背景图
        self.ibackground_size = None   # 背景图对应的窗口尺寸
        self.crosshair = None          # 准星图片
        self.icrosshair = None         # 绘制准星
        self.Text = None               # 字体

state = GameState()