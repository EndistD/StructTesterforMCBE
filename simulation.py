import random
import config
import heapq
import gui
import functions as fun
import blocks

class PendingTick:
    def __init__(self, due, owner, callback, *args):
        self.due = due      # 该区块时间轴上的到期刻
        self.owner = owner  # 创建该计划刻的方块实例
        self.callback = callback  # 函数引用
        self.args = args
        self.cancelled = False  # 删除标记


class PendingTickQueue:

    def __init__(self):
        self.timer = 0             # 队列独立时间轴
        self.heap = []             # 最小堆
        self._seq = 0
        self._due = []             # 正在执行的刻
        self.cid = None            # 队列索引

    def schedule(self, delay, owner, callback, *args):
        self._seq += 1
        item = PendingTick(self.timer + delay, owner, callback, *args)
        heapq.heappush(self.heap, (item.due, self._seq, item))

    def cancel(self, owner):
        for _, _, item in self.heap:
            if item.owner is owner:
                item.cancelled = True

    def has_pending(self, owner, strict=True):
        if strict and any(it.owner is owner for it in self._due):
            return True
        return any(not it.cancelled for _, _, it in self.heap if it.owner is owner)

    def update(self, limit=100):
        self.timer += 1
        if self.cid is None:
            self.cid = config.state.PendingTickList.index(self)
        due = []
        while self.heap and self.heap[0][0] <= self.timer:
            item = heapq.heappop(self.heap)[2]
            if item.cancelled or not item.owner.is_alive():
                continue
            if fun.cturncid(item.owner.cpos) != self.cid:
                continue
            due.append(item)
            if len(due) >= limit:
                break
        self._due = due
        for item in due:
            item.callback(*item.args)
        self._due = []


def runonce():
    for _ in range(config.state.simulate_scale):
        # 更新区块优先级
        if config.state.tick % 20 == 0:  # 跨区块顺序
            random.shuffle(config.state.ChunkOrder)
        random.shuffle(config.state.BlockOrder)  # 区块内顺序

        # 预热
        if config.state.tick == 0:
            redstonetick()

        config.state.tick += 1
        is_rt = config.state.tick % 2 == 1

        # 区块更新
        for chunkid in config.state.ChunkOrder:
            # 计划刻
            config.state.PendingTickList[chunkid].update()
            # 区域
            for blks in [config.state.ZoneList[chunkid][x2] for x2 in config.state.BlockOrder]:
                for zons in blks:
                    if not zons.is_redstone:
                        zons.function()
            # 方块功能
            for blks in [config.state.ChunkList[chunkid][x2] for x2 in config.state.BlockOrder]:
                if blks.has_function:
                    blks.function()
        # 红石刻
        if is_rt:
            redstonetick()


def redstonetick():
    # 充能重置
    for chu in [config.state.ChunkList[x1] for x1 in config.state.ChunkOrder]:
        for blks in [chu[x2] for x2 in config.state.BlockOrder]:
            blks.actived = False
            blks.powered = False
    # 区域充能
    for chu in [config.state.ZoneList[x1] for x1 in config.state.ChunkOrder]:
        for blks in [chu[x2] for x2 in config.state.BlockOrder]:
            for zons in blks:
                if zons.is_redstone:
                    zons.function()
    # 方块充能
    for chu in [config.state.ChunkList[x1] for x1 in config.state.ChunkOrder]:
        for blks in [chu[x2] for x2 in config.state.BlockOrder]:
            if blks.has_generate:
                blks.generate()
            if blks.zone_powered and blks.can_powered and blks.is_moving == 0:
                blks.powered = True
            elif blks.zone_powered and blks.can_powered != True and blks.has_function and blks.is_moving == 0:
                blks.actived = True
    # 3c 激活传播
    for chu in [config.state.ChunkList[x1] for x1 in config.state.ChunkOrder]:
        for blks in [chu[x2] for x2 in config.state.BlockOrder]:
            if blks.powered and blks.is_moving == 0:
                if blks.has_function:
                    blks.actived = True
                for towards in range(4):
                    npos = config.state.ChunkList[fun.bturnid(blks.abpos, 1, towards)[0]][
                        fun.bturnid(blks.abpos, 1, towards)[1]]
                    if (npos.has_function and npos.is_moving == 0
                            and not (npos.target_generate and npos.towards == fun.reverse(towards))):
                        npos.actived = True


def createbarrier(chunklist):
    cs = config.state.ChunkSize
    ss = config.state.SubChunkSize
    total_chunks = cs * cs
    blocks_per_chunk = ss * ss

    for chu in range(cs):
        for blks in range(ss):
            chunklist[chu][blks].set(blocks.Barrier)
    for chu in range(0, total_chunks, cs):
        for blks in range(0, blocks_per_chunk, ss):
            chunklist[chu][blks].set(blocks.Barrier)
    for chu in range(cs - 1, total_chunks, cs):
        for blks in range(ss - 1, blocks_per_chunk, ss):
            chunklist[chu][blks].set(blocks.Barrier)
    for chu in range(total_chunks - cs, total_chunks):
        for blks in range(blocks_per_chunk - ss, blocks_per_chunk):
            chunklist[chu][blks].set(blocks.Barrier)

def reset_world(chunk_size=None):
    #重置
    if chunk_size is not None:
        config.state.ChunkSize = chunk_size
        config.state.Vsize = config.state.BaseBlockSize * config.state.SubChunkSize * chunk_size

    cs = config.state.ChunkSize
    ss = config.state.SubChunkSize

    # 镜头复位
    config.state.Vpos = [config.state.Vsize / 2, config.state.Vsize / 2]

    # 重建数据结构
    import blocks
    config.state.ChunkList = [[blocks.Air(fun.cidturnc(c), fun.bidturnub(b)) for b in range(ss * ss)]
                              for c in range(cs * cs)]
    config.state.ZoneList = [[[] for b in range(ss * ss)]
                             for c in range(cs * cs)]
    config.state.ChunkOrder = list(range(cs * cs))
    config.state.BlockOrder = list(range(ss * ss))
    config.state.PendingTickList = [PendingTickQueue() for _ in range(cs * cs)]
    createbarrier(config.state.ChunkList)

def reset_simulation():
    import blocks
    config.state.tick = 0
    config.state.simulating = False
    for buts in config.state.buttonlist:
        if isinstance(buts, gui.Start):
            buts.save = [[blocks.Air(fun.cidturnc(c), fun.bidturnub(u))
                          for u in range(config.state.SubChunkSize * config.state.SubChunkSize)]
                         for c in range(config.state.ChunkSize * config.state.ChunkSize)]
            buts.zonesave = [[[] for _ in range(config.state.SubChunkSize * config.state.SubChunkSize)]
                             for _ in range(config.state.ChunkSize * config.state.ChunkSize)]
            buts.icon = buts.icon_normal