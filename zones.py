import copy
import random
import math
import pygame as pg
import config
import functions as fun
import blocks
import effects



class Zone:
    is_zone = True
    is_redstone = False
    # 空间
    cpos = [0, 0]  # 区块坐标
    bpos = [0, 0]  # 相对坐标
    abpos = fun.idturnb(fun.cturncid(cpos), fun.ubturnbid(bpos))  # 绝对坐标
    target = None
    # 结构
    sub = []
    hidden = True  # 隐藏于方块列表中
    unseen = False  # 不可见
    cantrepeat = False  # 重复放置
    # 图片
    imageway = config.resource_path("files/blocks/redplan.png")
    iconway = config.resource_path("files/icon/redplan.png")
    image = pg.image.load(imageway)
    image_load = image
    icon = pg.transform.scale(pg.image.load(iconway).convert_alpha(), (config.state.MenuWidth * 0.9 / 6, config.state.MenuWidth * 0.9 / 6))
    gui = None

    # 变换缓存
    _last_zoom = None
    _last_image = None

    def __init__(self, cpos, bpos):
        self.cpos = cpos
        self.bpos = bpos
        self.abpos = fun.idturnb(fun.cturncid(cpos), fun.ubturnbid(bpos))
        self.target = config.state.ChunkList[fun.cturncid(cpos)][fun.ubturnbid(bpos)]

    def __deepcopy__(self, memo):
        if id(self) in memo:
            return memo[id(self)]
        newobj = object.__new__(type(self))
        memo[id(self)] = newobj
        uncopyablename = {"image", "icon", "image_load", "gui", "_last_zoom", "_last_image"}
        copytarget = {key: value for key, value in self.__dict__.items() if key not in uncopyablename}
        newobj.__dict__ = copy.deepcopy(copytarget, memo)
        newobj.image = pg.image.load(newobj.imageway)
        newobj.image_load = newobj.image
        newobj.icon = pg.transform.scale(pg.image.load(newobj.iconway).convert_alpha(), (config.state.MenuWidth * 0.9 / 6, config.state.MenuWidth * 0.9 / 6))
        newobj.gui = None
        return newobj

    def draw(self):
        if self.unseen == False:
            if (-config.state.BaseBlockSize / config.state.Zoom <= fun.vturns(fun.bturnv(self.abpos))[0] <= config.state.Ssize[0]
                    and -config.state.BaseBlockSize / config.state.Zoom <= fun.vturns(fun.bturnv(self.abpos))[1] <= config.state.Ssize[1]):
                zoom = config.state.BaseBlockSize / config.state.Zoom
                if self._last_zoom != zoom or self._last_image is not self.image:
                    self.image_load = pg.transform.scale(self.image, (zoom, zoom))
                    self._last_zoom = zoom
                    self._last_image = self.image
                config.state.screen.blit(self.image_load, (fun.vturns(fun.bturnv(self.abpos))))

    @staticmethod
    def set(cposin, bposin, trigger):
        if len(config.state.ZoneList[fun.cturncid(cposin)][fun.ubturnbid(bposin)]) != 0:
            for zones in config.state.ZoneList[fun.cturncid(cposin)][fun.ubturnbid(bposin)]:
                if zones.gui == trigger.gui:
                    return
        if config.state.ChunkList[fun.cturncid(cposin)][fun.ubturnbid(bposin)].iconway != config.resource_path("files/blocks/barrier.png"):
            config.state.ZoneList[fun.cturncid(cposin)][fun.ubturnbid(bposin)].append(trigger(cposin, bposin))

    def opengui(self):
        self.gui.target = self
        self.gui.active = True
        self.gui.iconbut.icon = self.gui.target.icon
        self.gui.posshowbut.textshow = f"[{self.abpos[0]},{self.abpos[1]}]"
        import gui
        gui.ZoneGUI.resetguis(config.state.ZoneGUIList)

    def function(self):
        self.target = config.state.ChunkList[fun.cturncid(self.cpos)][fun.ubturnbid(self.bpos)]


class RedPlan(Zone):
    hidden = False
    gui = None
    is_redstone = True

    def __init__(self, cpos, bpos):
        super().__init__(cpos, bpos)
        self.clock = 0  # 周期
        self.command = []  # 指令

    def __deepcopy__(self, memo):
        if id(self) in memo:
            return memo[id(self)]
        newobj = object.__new__(type(self))
        memo[id(self)] = newobj
        uncopyablename = {"image", "icon", "image_load", "gui", "_last_zoom", "_last_image"}
        copytarget = {key: value for key, value in self.__dict__.items() if key not in uncopyablename}
        newobj.__dict__ = copy.deepcopy(copytarget, memo)
        newobj.image = pg.image.load(newobj.imageway)
        newobj.image_load = newobj.image
        newobj.icon = pg.transform.scale(pg.image.load(newobj.iconway).convert_alpha(), (config.state.MenuWidth * 0.9 / 6, config.state.MenuWidth * 0.9 / 6))
        newobj.gui = type(self).gui
        return newobj

    def opengui(self):
        super().opengui()
        self.gui.commandtextbut.fontcolor = "white"
        self.gui.clocktextbut.fontcolor = "white"
        if len(self.command) != 0:
            self.gui.commandtextbut.textin = " ".join(f"{x[0]}-{x[1]}" for x in self.command)
        else:
            self.gui.commandtextbut.textin = ""
        self.gui.clocktextbut.textin = f"{self.clock}"

    def function(self):
        super().function()
        if self.clock != 0:
            cur = config.state.tick % self.clock
            on = any(
                (a == b and cur == (a % self.clock))
                or (a < b and a <= cur < b)
                for a, b in self.command
            )
        else:
            on = any(
                (a == b and config.state.tick == a)
                or (a < b and a <= config.state.tick < b)
                for a, b in self.command
            )
        if on and not self.target.zone_powered:
            dur = max(fun.active_ticks(self.clock, self.command, cur if self.clock != 0 else config.state.tick), 1) * config.state.Oneticktime * 2
            effects.create_fade(self.target.abpos, (255, 0, 0), dur)
        self.target.zone_powered = on


class MovingPlan(Zone):
    hidden = False
    gui = None
    is_redstone = True

    imageway = config.resource_path("files/blocks/movingplan.png")
    iconway = config.resource_path("files/icon/movingplan.png")
    image = pg.image.load(imageway)
    image_load = image
    icon = pg.transform.scale(pg.image.load(iconway).convert_alpha(), (config.state.MenuWidth * 0.9 / 6, config.state.MenuWidth * 0.9 / 6))

    def __init__(self, cpos, bpos):
        super().__init__(cpos, bpos)
        self.clock = 0  # 周期
        self.command = []  # 指令

    def __deepcopy__(self, memo):
        if id(self) in memo:
            return memo[id(self)]
        newobj = object.__new__(type(self))
        memo[id(self)] = newobj
        uncopyablename = {"image", "icon", "image_load", "gui", "_last_zoom", "_last_image"}
        copytarget = {key: value for key, value in self.__dict__.items() if key not in uncopyablename}
        newobj.__dict__ = copy.deepcopy(copytarget, memo)
        newobj.image = pg.image.load(newobj.imageway)
        newobj.image_load = newobj.image
        newobj.icon = pg.transform.scale(pg.image.load(newobj.iconway).convert_alpha(), (config.state.MenuWidth * 0.9 / 6, config.state.MenuWidth * 0.9 / 6))
        newobj.gui = type(self).gui
        return newobj

    def opengui(self):
        super().opengui()
        self.gui.commandtextbut.fontcolor = "white"
        self.gui.clocktextbut.fontcolor = "white"
        if len(self.command) != 0:
            self.gui.commandtextbut.textin = " ".join(f"{x[0]}-{x[1]}" for x in self.command)
        else:
            self.gui.commandtextbut.textin = ""
        self.gui.clocktextbut.textin = f"{self.clock}"

    def function(self):
        super().function()
        if self.clock != 0:
            cur = config.state.tick % self.clock
            on = any(
                (a == b and cur == (a % self.clock))
                or (a < b and a <= cur < b)
                for a, b in self.command
            )
        else:
            on = any(
                (a == b and config.state.tick == a)
                or (a < b and a <= config.state.tick < b)
                for a, b in self.command
            )
        if on and self.target.is_moving == 0:
            dur = max(fun.active_ticks(self.clock, self.command, cur if self.clock != 0 else config.state.tick), 1) * config.state.Oneticktime * 2
            effects.create_fade(self.target.abpos, (255, 165, 0), dur)
        self.target.is_moving = 1 if on else 0


class GrowPlan(Zone):
    hidden = False
    gui = None

    heightrange = (1, 7)  # 高度切片取值
    logheightrange = (4, 6)  # 树干高度取值
    woodtype = blocks.Oak
    leavestype = blocks.Oakleaves

    imageway = config.resource_path("files/blocks/growplan.png")
    iconway = config.resource_path("files/icon/oaksapling.png")
    image = pg.image.load(imageway)
    image_load = image
    icon = pg.transform.scale(pg.image.load(iconway).convert_alpha(), (config.state.MenuWidth * 0.9 / 6, config.state.MenuWidth * 0.9 / 6))

    def __init__(self, cpos, bpos):
        super().__init__(cpos, bpos)
        self.clock = 0  # 周期
        self.height = 1  # 目标高度
        self.testrange = 1  # 检测范围
        self.gen_leaves = True
        self.mode = 1  #（1时钟，2检测，3强制时钟）

    def __deepcopy__(self, memo):
        if id(self) in memo:
            return memo[id(self)]
        newobj = object.__new__(type(self))
        memo[id(self)] = newobj
        uncopyablename = {"image", "icon", "image_load", "gui", "_last_zoom", "_last_image"}
        copytarget = {key: value for key, value in self.__dict__.items() if key not in uncopyablename}
        newobj.__dict__ = copy.deepcopy(copytarget, memo)
        newobj.image = pg.image.load(newobj.imageway)
        newobj.image_load = newobj.image
        newobj.icon = pg.transform.scale(pg.image.load(newobj.iconway).convert_alpha(), (config.state.MenuWidth * 0.9 / 6, config.state.MenuWidth * 0.9 / 6))
        newobj.gui = type(self).gui
        return newobj

    def draw(self):
        super().draw()
        topleft = fun.vturns(fun.bturnv(fun.bposmove(fun.bposmove(self.abpos, 0, self.testrange - 1), 3, self.testrange - 1)))
        downright = fun.vturns(fun.bturnv(fun.bposmove(fun.bposmove(self.abpos, 2, self.testrange), 1, self.testrange)))
        rect = (topleft[0] + 1, topleft[1] + 1, downright[0] - topleft[0], downright[1] - topleft[1])
        if config.state.Zoom <= 4:
            pg.draw.rect(config.state.screen, "green", rect, 2)

    def opengui(self):
        super().opengui()
        self.gui.clocktextbut.fontcolor = "white"
        self.gui.clocktextbut.textin = f"{self.clock}"
        self.gui.heightswichbut.fontcolor = "white"
        self.gui.heightswichbut.textin = f"{self.height}"
        self.gui.leafswichbut.locate = int(self.gen_leaves) + 1
        self.gui.leafswichbut.dict = {1: "NO", 2: "YES"}
        self.gui.modeswichbut.locate = self.mode
        self.gui.modeswichbut.dict = {1: "CLO", 2: "DEC", 3: "STR"}

    # 实际空间检测
    @staticmethod
    def test(pos, maxwidth):
        if not fun.testmatrix(pos, 0):
            return 0
        bestw = 1  # 中心通过 = 1×1
        for w in range(1, maxwidth + 1):
            if fun.testmatrix(pos, w):
                bestw = w + 1
            else:
                break
        return bestw

    # 理论检测范围
    def testrangeset(self, height):
        ans = [0, 1]
        ans += [3] * (self.heightrange[1])
        for x in range(2, 2 + height - 1):
            ans[x] = 2
        return ans

    def summonwood(self, treeheight, pos):
        if fun.bturnblock(pos).push_destroyed and self.height <= treeheight:
            fun.bturnblock(pos).set(self.woodtype, 0, "grow")

    def summonleaves(self, treeheight, pos):
        match self.height:
            case a if a == treeheight + 1:
                fun.bturnblock(pos).set(self.leavestype, 0, "grow")
                for twd in range(0, 4):
                    fun.bturnblock(fun.bposmove(pos, twd, 1)).set(self.leavestype, 0, "grow")
            case a if a == treeheight:
                for dx in (-1, 0, 1):
                    for dy in (-1, 0, 1):
                        if (dx, dy) in [(-1, -1), (-1, 1), (1, -1), (1, 1)]:
                            continue
                        fun.bturnblock([pos[0] + dx, pos[1] + dy]).set(self.leavestype, 0, "grow")
                corners = [[pos[0] - 1, pos[1] - 1],
                           [pos[0] + 1, pos[1] - 1],
                           [pos[0] + 1, pos[1] + 1],
                           [pos[0] - 1, pos[1] + 1]]
                selected = [p for p in corners if random.random() <= 0.25]
                if not selected:
                    selected = [random.choice(corners)]
                for p in selected:
                    fun.bturnblock(p).set(self.leavestype, 0, "grow")
            case a if a == treeheight - 1 or a == treeheight - 2:
                for dx in (-2, -1, 0, 1, 2):
                    for dy in (-2, -1, 0, 1, 2):
                        if (dx, dy) in [(-2, -2), (-2, 2), (2, -2), (2, 2)]:
                            continue
                        fun.bturnblock([pos[0] + dx, pos[1] + dy]).set(self.leavestype, 0, "grow")
                corners = [[pos[0] - 2, pos[1] - 2],
                           [pos[0] + 2, pos[1] - 2],
                           [pos[0] + 2, pos[1] + 2],
                           [pos[0] - 2, pos[1] + 2]]
                selected = [p for p in corners if random.random() <= 0.5]
                if not selected:
                    selected = [random.choice(corners)]
                for p in selected:
                    fun.bturnblock(p).set(self.leavestype, 0, "grow")
            case _:
                pass

    def summontree(self, mode=0):
        treeheight = random.randint(self.logheightrange[0], self.logheightrange[1])  # 随机树干高度，决定检测范围
        self.testrange = self.testrangeset(treeheight)[self.height]  # 设置检测范围
        width = self.test(self.abpos, 3)  # 检测实际空间大小
        cangrow = False
        if self.testrange <= width or mode != 0:
            cangrow = True  # 检测结果判定
        if cangrow:
            if self.gen_leaves:
                self.summonleaves(treeheight, self.abpos)
            self.summonwood(treeheight, self.abpos)

    def function(self):
        super().function()
        match self.mode:
            case 1:  # 时钟
                if self.clock != 0:
                    if config.state.tick % self.clock == 0:
                        self.summontree()
                        effects.create_fade(self.abpos, (144, 238, 144), config.state.Oneticktime)
            case 2:  # 检测
                self.summontree()
                effects.create_fade(self.abpos, (144, 238, 144), config.state.Oneticktime)
            case 3:  # 强制时钟
                if self.clock != 0:
                    if config.state.tick % self.clock == 0:
                        self.summontree(1)
                        effects.create_fade(self.abpos, (144, 238, 144), config.state.Oneticktime)

class OakPlan(GrowPlan):
    pass
class BrichPlan(GrowPlan):
    heightrange = (1, 8)  # 高度切片取值
    logheightrange = (5, 7)  # 树干高度取值
    woodtype = blocks.Brich
    leavestype = blocks.Brichleaves

    iconway = config.resource_path("files/icon/birchsapling.png")
    icon = pg.transform.scale(pg.image.load(iconway).convert_alpha(), (config.state.MenuWidth * 0.9 / 6, config.state.MenuWidth * 0.9 / 6))
class SprucePlan(GrowPlan):
    heightrange = (1, 10)  # 高度切片取值
    logheightrange = (6, 9)  # 树干高度取值
    woodtype = blocks.Spruce
    leavestype = blocks.Spruceleaves

    iconway = config.resource_path("files/icon/sprucesapling.png")
    icon = pg.transform.scale(pg.image.load(iconway).convert_alpha(), (config.state.MenuWidth * 0.9 / 6, config.state.MenuWidth * 0.9 / 6))

    def summonleaves(self, treeheight, pos):
        def getleavesshape(height):
            if height == 6:
                 return random.choice([[0,0,0,0,0,0,2,1,2,0],[0,0,0,0,0,0,1,2,0,0]])
            tall = random.choice([height, height - 1])
            res = []
            part1 = random.choice([[1, 2], [2]])
            res += part1
            part2 = [1, 2, 3]
            if res[-1] == part2[0]:
                part2 = part2[1:]
            res += part2
            current = len(res)
            remaining = tall - current
            if remaining < 2:
                if len(res) == tall - 1:
                    res.append(2)
                if tall == height - 1:
                    res.append(0)
                res.append(0)
                res = [0] * (10 - len(res)) + res
                return res
            canuselong = (remaining >= 3)
            uselong = canuselong and (random.random() < 0.5)
            lastlen = 3 if uselong else 2
            fill = remaining - lastlen
            k = fill // 2
            for _ in range(k):
                res += [2, 3]
            if lastlen == 3:
                res += [2, 3, 4]
            else:
                res += [2, 3]
            if len(res) == tall - 1:
                res.append(2)
            if tall == height - 1:
                res.append(0)
            res.append(0)
            res = [0] * (10 - len(res)) + res
            return res

        shape = getleavesshape(treeheight)[::-1]
        listx = []
        listy = []
        delta = 0
        match shape[self.height - 1]:
            case 1:
                listx = [0]
                listy = [0]
            case 2:
                listx = [-1, 0, 1]
                listy = [-1, 0, 1]
                delta = 1
            case 3:
                listx = [-2, -1, 0, 1, 2]
                listy = [-2, -1, 0, 1, 2]
                delta = 2
            case 4:
                listx = [-3, -2, -1, 0, 1, 2, 3]
                listy = [-3, -2, -1, 0, 1, 2, 3]
                delta = 3
            case _:
                pass
        for dx in listx:
            for dy in listy:
                if (dx, dy) in [(-delta, -delta), (-delta, delta), (delta, -delta), (delta, delta)]:
                    continue
                fun.bturnblock([pos[0] + dx, pos[1] + dy]).set(self.leavestype, 0, "grow")

    def summonwood(self, treeheight, pos):
        if fun.bturnblock(pos).push_destroyed and self.height <= treeheight - (random.randint(0, 2)):
            fun.bturnblock(pos).set(self.woodtype, 0, "strong")
class MegaSprucePlan(GrowPlan):
    heightrange = (1, 30)  # 高度切片取值
    logheightrange = (13, 29)  # 树干高度取值
    woodtype = blocks.Spruce
    leavestype = blocks.Spruceleaves

    iconway = config.resource_path("files/icon/sprucesapling.png")
    icon = pg.transform.scale(pg.image.load(iconway).convert_alpha(), (config.state.MenuWidth * 0.9 / 6, config.state.MenuWidth * 0.9 / 6))
    badge = pg.font.Font(config.resource_path("files/font/Pixel AE.ttf"), 14).render("M", True, "black")

    def draw(self):
        super().draw()
        topleft2 = fun.vturns(fun.bturnv(self.abpos))
        downright2 = fun.vturns(fun.bturnv(fun.bposmove(fun.bposmove(self.abpos, 2, 2), 1, 2)))
        rect2 = (topleft2[0] + 1, topleft2[1] + 1, downright2[0] - topleft2[0] - 1, downright2[1] - topleft2[1] - 1)
        if config.state.Zoom <= 4:
            pg.draw.rect(config.state.screen, (0, 139, 69), rect2, 3)
    def testrangeset(self, height):
        ans = [0, 2]
        ans += [3] * self.logheightrange[1]
        return ans

    def getleavesdata(self):
        pattern = [1]
        l1 = random.randint(1, 2)
        l2 = random.randint(1, 2)
        for _ in range(l1):
            pattern.append(2)
            pattern.append(1)
        for _ in range(l2):
            pattern.append(3)
            pattern.append(2)
        for _ in range(l2):
            pattern.append(4)
            pattern.append(3)
        i = len(pattern) - 2
        while i >= 2:
            if pattern[i] < pattern[i - 1] and pattern[i] < pattern[i + 1] and random.random() < 0.3:
                pattern.insert(i + 1, pattern[i])
            i -= 1
        pattern.append(5)
        pattern.append(4)
        if random.random() < 0.5:
            pattern.append(4)
        fill_count = 0
        while len(pattern) < 14 and fill_count < 2:
            try:
                idx3 = pattern.index(3)
            except ValueError:
                idx3 = len(pattern) - 3
            pattern[idx3:idx3] = [2, 1]
            fill_count += 1
        return pattern
    def summonleaves(self, abpos, width):
        rows=[]
        if width == 0:
            return
        if width == 1:
            rows = [(0, 0, 1), (1, 0, 1)]
        elif width == 2:
            rows = [(-1, 0, 1), (0, -1, 2), (1, -1, 2), (2, 0, 1)]
        elif width == 3:
            rows = [(-2, 0, 1), (-1, -1, 2), (0, -2, 3), (1, -2, 3), (2, -1, 2), (3, 0, 1)]
        elif width == 4:
            rows = [(-3, 0, 1), (-2, -2, 3), (-1, -2, 3), (0, -3, 4), (1, -3, 4), (2, -2, 3), (3, -2, 3), (4, 0, 1)]
        elif width == 5:
            rows = [(-4, 0, 1), (-3, -2, 3), (-2, -3, 4), (-1, -3, 4),
                    (0, -4, 5), (1, -4, 5), (2, -3, 4), (3, -3, 4),
                    (4, -2, 3), (5, 0, 1)]
        elif width == 6:
            rows = [(-5, 0, 1), (-4, -3, 4), (-3, -4, 5), (-2, -4, 5),
                    (-1, -4, 5), (0, -5, 6), (1, -5, 6), (2, -4, 5),
                    (3, -4, 5), (4, -4, 5), (5, -3, 4), (6, 0, 1)]
        for dy, x_start, x_end in rows:
            for dx in range(x_start, x_end + 1):
                pos = [abpos[0] + dx, abpos[1] + dy]
                fun.bturnblock(pos).set(self.leavestype, 0, "grow")
    def summontree(self, mode=0):
        treeheight = 13 + random.randint(0, 2) + random.randint(0, 14)  # 随机树干高度，决定检测范围
        self.testrange = self.testrangeset(treeheight)[self.height]  # 设置检测范围
        width = self.test(self.abpos, 3)  # 检测实际空间大小
        cangrow = False
        if self.testrange <= width or mode != 0:
            cangrow = True  # 检测结果判定
        if cangrow:
            if self.height < treeheight:
                fun.bturnblock(self.abpos).set(self.woodtype, 0, "grow")
                fun.bturnblock(fun.bposmove(self.abpos, 1)).set(self.woodtype, 0, "grow")
                fun.bturnblock(fun.bposmove(self.abpos, 2)).set(self.woodtype, 0, "grow")
                fun.bturnblock(fun.bposmove(fun.bposmove(self.abpos, 2), 1)).set(self.woodtype, 0, "grow")
            if self.height == treeheight:
                fun.bturnblock(self.abpos).set(self.woodtype, 0, "grow")
            if self.gen_leaves:
                shape = self.getleavesdata()
                idx = treeheight + 1 - self.height
                if 0 <= idx < len(shape):
                    w = shape[idx]
                    if w > 0:
                        self.summonleaves(self.abpos, w)
class JunglePlan(GrowPlan):
    heightrange = (1, 11)  # 高度切片取值
    logheightrange = (4, 10)  # 树干高度取值
    woodtype = blocks.Jungle
    leavestype = blocks.Jungleleaves

    iconway = config.resource_path("files/icon/junglesapling.png")
    icon = pg.transform.scale(pg.image.load(iconway).convert_alpha(), (config.state.MenuWidth * 0.9 / 6, config.state.MenuWidth * 0.9 / 6))
class MegaJunglePlan(GrowPlan):
    heightrange = (1, 32)  # 高度切片取值
    logheightrange = (10, 31)  # 树干高度取值
    woodtype = blocks.Jungle
    leavestype = blocks.Jungleleaves

    iconway = config.resource_path("files/icon/junglesapling.png")
    icon = pg.transform.scale(pg.image.load(iconway).convert_alpha(), (config.state.MenuWidth * 0.9 / 6, config.state.MenuWidth * 0.9 / 6))
    badge = pg.font.Font(config.resource_path("files/font/Pixel AE.ttf"), 14).render("M", True, "black")

    def draw(self):
        super().draw()
        topleft2 = fun.vturns(fun.bturnv(self.abpos))
        downright2 = fun.vturns(fun.bturnv(fun.bposmove(fun.bposmove(self.abpos, 2, 2), 1, 2)))
        rect2 = (topleft2[0] + 1, topleft2[1] + 1, downright2[0] - topleft2[0] - 1, downright2[1] - topleft2[1] - 1)
        if config.state.Zoom <= 4:
            pg.draw.rect(config.state.screen, (0, 139, 69), rect2, 3)
    def testrangeset(self, height):
        ans = [0, 2]
        ans += [3] * self.logheightrange[1]
        return ans

    def summonleaves(self, abpos, width):
        rows=[]
        if width == 0:
            return
        if width == 1:
            rows = [(0, 0, 1), (1, 0, 1)]
        elif width == 2:
            rows = [(-1, 0, 1), (0, -1, 2), (1, -1, 2), (2, 0, 1)]
        elif width == 3:
            rows = [(-2, 0, 1), (-1, -1, 2), (0, -2, 3), (1, -2, 3), (2, -1, 2), (3, 0, 1)]
        elif width == 4:
            rows = [(-3, 0, 1), (-2, -2, 3), (-1, -2, 3), (0, -3, 4), (1, -3, 4), (2, -2, 3), (3, -2, 3), (4, 0, 1)]
        elif width == 5:
            rows = [(-4, 0, 1), (-3, -2, 3), (-2, -3, 4), (-1, -3, 4),
                    (0, -4, 5), (1, -4, 5), (2, -3, 4), (3, -3, 4),
                    (4, -2, 3), (5, 0, 1)]
        elif width == 6:
            rows = [(-5, 0, 1), (-4, -3, 4), (-3, -4, 5), (-2, -4, 5),
                    (-1, -4, 5), (0, -5, 6), (1, -5, 6), (2, -4, 5),
                    (3, -4, 5), (4, -4, 5), (5, -3, 4), (6, 0, 1)]
        for dy, x_start, x_end in rows:
            for dx in range(x_start, x_end + 1):
                pos = [abpos[0] + dx, abpos[1] + dy]
                fun.bturnblock(pos).set(self.leavestype, 0, "grow")
    def getbranchesdata(self, treeheight):
        branchdata = []
        branch_ends = []
        pos = treeheight
        while True:
            delta = random.randint(2, 5)
            nextpos = pos - delta
            if nextpos <= 0.5 * treeheight:
                break
            pos = nextpos
            angle = random.uniform(0, 2 * math.pi)
            for i in range(5):
                dx = int(math.floor(math.cos(angle) * i + 1.5))
                dy = int(math.floor(math.sin(angle) * i + 1.5))
                z = int(pos - 1 - (4 - i) * 0.5)
                entry = [dx, dy, z]
                branchdata.append(entry)
                if i == 4:
                    branch_ends.append(entry)
        return branchdata, branch_ends
    def summontree(self, mode=0):
        treeheight = 10 + random.randint(0,19) + random.randint(0,2) # 随机树干高度，决定检测范围
        branchdata, branch_ends = self.getbranchesdata(treeheight)

        self.testrange = self.testrangeset(treeheight)[self.height]  # 设置检测范围
        width = self.test(self.abpos, 3)  # 检测实际空间大小
        cangrow = False
        if self.testrange <= width or mode != 0:
            cangrow = True  # 检测结果判定
        if cangrow:
            # 2×2树干
            if self.height < treeheight:
                fun.bturnblock(self.abpos).set(self.woodtype, 0, "grow")
                fun.bturnblock(fun.bposmove(self.abpos, 1)).set(self.woodtype, 0, "grow")
                fun.bturnblock(fun.bposmove(self.abpos, 2)).set(self.woodtype, 0, "grow")
                fun.bturnblock(fun.bposmove(fun.bposmove(self.abpos, 2), 1)).set(self.woodtype, 0, "grow")
            if self.height == treeheight:
                fun.bturnblock(self.abpos).set(self.woodtype, 0, "grow")
            # 侧枝木头
            for entry in branchdata:
                if entry[2] == self.height:
                    pos = [self.abpos[0] + entry[0], self.abpos[1] + entry[1]]
                    fun.bturnblock(pos).set(self.woodtype, 0, "grow")
            # 树叶
            if self.gen_leaves:
                # 主树冠
                if self.height == treeheight+1:
                    self.summonleaves(self.abpos, 4)
                if self.height == treeheight:
                    self.summonleaves(self.abpos, 5)
                if self.height == treeheight-1:
                    self.summonleaves(self.abpos, 6)
                for end in branch_ends:
                    edx, edy, ez = end
                    base = [self.abpos[0] + edx, self.abpos[1] + edy]
                    if self.height == ez + 1:
                        for dx in range(-1, 2):
                            for dy in range(-1, 2):
                                if abs(dx) + abs(dy) <= 1:
                                    pos = [base[0] + dx, base[1] + dy]
                                    fun.bturnblock(pos).set(self.leavestype, 0, "grow")
                    elif self.height == ez:
                        for dx in range(-2, 3):
                            for dy in range(-2, 3):
                                if abs(dx) + abs(dy) <= 2:
                                    pos = [base[0] + dx, base[1] + dy]
                                    fun.bturnblock(pos).set(self.leavestype, 0, "grow")
                    elif self.height == ez - 1 and random.random() < 0.5:
                        for dx in range(-3, 4):
                            for dy in range(-3, 4):
                                if abs(dx) <= 2 and abs(dy) <= 2 or abs(dx) + abs(dy) <= 3:
                                    pos = [base[0] + dx, base[1] + dy]
                                    fun.bturnblock(pos).set(self.leavestype, 0, "grow")
class AcaciaPlan(GrowPlan):
    heightrange = (1, 10)  # 高度切片取值
    logheightrange = (5, 9)  # 树干高度取值
    woodtype = blocks.Acacia
    leavestype = blocks.Acacialeaves

    iconway = config.resource_path("files/icon/acaciasapling.png")
    icon = pg.transform.scale(pg.image.load(iconway).convert_alpha(), (config.state.MenuWidth * 0.9 / 6, config.state.MenuWidth * 0.9 / 6))

    def summonwoods(self, height, data, pos):
        offset = data[height - 1]
        if offset != []:
            nx = pos[0] + offset[0]
            ny = pos[1] + offset[1]
            fun.bturnblock([nx, ny]).set(self.woodtype, 0, "grow")

    def summonleavesmain(self, height, pos):
        match self.height:
            case a if a == height + 1:
                for dx in (-2, -1, 0, 1, 2):
                    for dy in (-2, -1, 0, 1, 2):
                        if (dx, dy) in [(-2, -2), (-2, 2), (2, -2), (2, 2), (1, 2), (-1, 2), (1, -2), (-1, -2), (2, 1), (2, -1), (-2, 1), (-2, -1)]:
                            continue
                        fun.bturnblock([pos[0] + dx, pos[1] + dy]).set(self.leavestype, 0, "grow")
            case a if a == height:
                for dx in (-3, -2, -1, 0, 1, 2, 3):
                    for dy in (-3, -2, -1, 0, 1, 2, 3):
                        if (dx, dy) in [(-3, -3), (-3, 3), (3, -3), (3, 3)]:
                            continue
                        fun.bturnblock([pos[0] + dx, pos[1] + dy]).set(self.leavestype, 0, "grow")
            case _:
                pass

    def summonleavesbranch(self, height, pos):
        match self.height:
            case a if a == height + 1:
                for dx in (-1, 0, 1):
                    for dy in (-1, 0, 1):
                        fun.bturnblock([pos[0] + dx, pos[1] + dy]).set(self.leavestype, 0, "grow")
            case a if a == height:
                for dx in (-2, -1, 0, 1, 2):
                    for dy in (-2, -1, 0, 1, 2):
                        if (dx, dy) in [(-2, -2), (-2, 2), (2, -2), (2, 2)]:
                            continue
                        fun.bturnblock([pos[0] + dx, pos[1] + dy]).set(self.leavestype, 0, "grow")
            case _:
                pass

    def summontree(self, mode=0):
        treeheight = random.randint(0, 2) + random.randint(0, 2) + 5  # 随机树干高度，决定检测范围
        leanheight = treeheight - random.randint(1, 4)  # 主干弯曲起始高度确定
        bendheight = treeheight - leanheight  # 主干弯曲部分高度
        bendwidth = random.randint(1, 3)  # 主干弯曲部分宽度
        maintoward = random.randint(0, 3)  # 主干朝向
        branchtoward = random.randint(0, 3)  # 侧枝朝向
        branchwidth = random.randint(1, 3)  # 侧枝宽度
        branchstartheight = leanheight - random.randint(1, 2)  # 侧枝开始生成高度
        while branchstartheight < 1:
            branchwidth -= 1
            branchstartheight += 1
            if branchwidth == 0:
                break
        maindata = []
        # region 主干生成
        offsets = [(0, -1), (1, 0), (0, 1), (-1, 0)]
        dx, dy = offsets[maintoward]
        nx, ny = 0, 0
        for i in range(leanheight):
            maindata.append([0, 0])
        offsetsteps = 0
        while len(maindata) < treeheight:
            if offsetsteps < bendwidth:
                nx += dx
                ny += dy
                offsetsteps += 1
            maindata.append([nx, ny])
        while len(maindata) < 10:
            maindata.append([])
        # endregion
        mainpos = [self.abpos[0] + maindata[treeheight - 1][0], self.abpos[1] + maindata[treeheight - 1][1]]  # 主干末端坐标
        branchdata = []
        # region 侧枝生成
        offsets_branch = [(0, -1), (1, 0), (0, 1), (-1, 0)]
        dx2, dy2 = offsets_branch[branchtoward]
        nx2, ny2 = 0, 0
        for i in range(1, 11):
            if i <= branchstartheight:
                branchdata.append([])
            else:
                if i - branchstartheight <= branchwidth and i <= treeheight:
                    nx2 += dx2
                    ny2 += dy2
                    branchdata.append([nx2, ny2])
                else:
                    branchdata.append([])
        # endregion
        branchheight = fun.findlastelement(branchdata, [])  # 侧枝高度
        if branchheight != 0:
            branchheight += 1
        branchpos = [self.abpos[0] + (branchdata[branchheight - 1][0] if branchdata[branchheight - 1] else 0), self.abpos[1] + (branchdata[branchheight - 1][1] if branchdata[branchheight - 1] else 0)]  # 侧枝末端坐标
        self.testrange = self.testrangeset(treeheight)[self.height]  # 设置检测范围
        width = self.test(self.abpos, 3)  # 检测实际空间大小
        cangrow = False
        if self.testrange <= width or mode != 0:
            cangrow = True  # 检测结果判定
        if cangrow:
            if self.gen_leaves:
                self.summonleavesmain(treeheight, mainpos)
            self.summonwoods(treeheight, maindata, self.abpos)
            if branchtoward != maintoward and branchheight != 1:
                if self.gen_leaves:
                    self.summonleavesbranch(branchheight, branchpos)
                self.summonwoods(treeheight, branchdata, self.abpos)
class DarkOakPlan(GrowPlan):
    heightrange = (1, 11)  # 高度切片取值
    logheightrange = (6, 9)  # 树干高度取值
    woodtype = blocks.Darkoak
    leavestype = blocks.Oakleaves

    iconway = config.resource_path("files/icon/darkoaksapling.png")
    icon = pg.transform.scale(pg.image.load(iconway).convert_alpha(), (config.state.MenuWidth * 0.9 / 6, config.state.MenuWidth * 0.9 / 6))

    def draw(self):
        super().draw()
        topleft2 = fun.vturns(fun.bturnv(self.abpos))
        downright2 = fun.vturns(fun.bturnv(fun.bposmove(fun.bposmove(self.abpos, 2, 2), 1, 2)))
        rect2 = (topleft2[0] + 1, topleft2[1] + 1, downright2[0] - topleft2[0] - 1, downright2[1] - topleft2[1] - 1)
        if config.state.Zoom <= 4:
            pg.draw.rect(config.state.screen, (0, 139, 69), rect2, 3)

    def summonwoods(self, treeheight, data, pos):
        if self.height <= treeheight:
            fun.bturnblock(pos).set(self.woodtype, 0, "grow")
            fun.bturnblock(fun.bposmove(pos, 1)).set(self.woodtype, 0, "grow")
            fun.bturnblock(fun.bposmove(pos, 2)).set(self.woodtype, 0, "grow")
            fun.bturnblock(fun.bposmove(fun.bposmove(pos, 2), 1)).set(self.woodtype, 0, "grow")
        offsets = [(-1, -1), (0, -1), (1, -1), (2, -1),
                   (-1, 0), (2, 0),
                   (-1, 1), (2, 1),
                   (-1, 2), (0, 2), (1, 2), (2, 2)]
        for step in range(12):
            if treeheight - 1 - data[step] < self.height < treeheight and data[step] != 0:
                dx = offsets[step][0]
                dy = offsets[step][1]
                fun.bturnblock([pos[0] + dx, pos[1] + dy]).set(self.woodtype, 0, "grow")

    def summonleaves2(self, treeheight, data, pos):
        match self.height:
            case a if a == treeheight + 2 and random.random() < 1 / 5:
                for dx in (0, 1):
                    for dy in (0, 1):
                        fun.bturnblock([pos[0] + dx, pos[1] + dy]).set(self.leavestype, 0, "grow")
            case a if a == treeheight + 1:
                for dx in (-2, -1, 0, 1, 2, 3):
                    for dy in (-2, -1, 0, 1, 2, 3):
                        if (dx, dy) in [(-2, -2), (-2, 3), (3, -2), (3, 3), (2, 3), (-1, 3), (2, -2), (-1, -2), (3, 2),
                                        (3, -1), (-2, 2), (-2, -1)]:
                            continue
                        fun.bturnblock([pos[0] + dx, pos[1] + dy]).set(self.leavestype, 0, "grow")
            case a if a == treeheight:
                for dx in (-3, -2, -1, 0, 1, 2, 3, 4):
                    for dy in (-3, -2, -1, 0, 1, 2, 3, 4):
                        if (dx, dy) in [(-3, -3), (-3, -2), (-2, -3), (-2, -2),
                                        (-3, 4), (-3, 3), (-2, 4), (-2, 3),
                                        (4, -3), (4, -2), (3, -3), (3, -2),
                                        (4, 4), (4, 3), (3, 4), (3, 3), ]:
                            continue
                        fun.bturnblock([pos[0] + dx, pos[1] + dy]).set(self.leavestype, 0, "grow")

                offset2 = [(-3, -2), (-2, -3), (-2, -2),
                           (-3, 3), (-2, 4), (-2, 3),
                           (4, -2), (3, -3), (3, -2),
                           (4, 3), (3, 4), (3, 3), ]
                for g in range(4):
                    sub = offset2[g * 3:g * 3 + 3]
                    mainoffset = sub[2]
                    otheroffset = [sub[0], sub[1]]
                    rand = random.randint(0, 3)
                    match rand:
                        case 0:
                            continue
                        case 1:
                            x = pos[0] + mainoffset[0]
                            y = pos[1] + mainoffset[1]
                            fun.bturnblock([x, y]).set(self.leavestype, 0, "grow")
                        case 2:
                            x = pos[0] + mainoffset[0]
                            y = pos[1] + mainoffset[1]
                            fun.bturnblock([x, y]).set(self.leavestype, 0, "grow")
                            randos = random.choice(otheroffset)
                            x2 = pos[0] + randos[0]
                            y2 = pos[1] + randos[1]
                            fun.bturnblock([x2, y2]).set(self.leavestype, 0, "grow")
                        case 3:
                            for os in sub:
                                x = pos[0] + os[0]
                                y = pos[1] + os[1]
                                fun.bturnblock([x, y]).set(self.leavestype, 0, "grow")
                offsets = [(-1, -1), (0, -1), (1, -1), (2, -1),
                           (-1, 0), (2, 0),
                           (-1, 1), (2, 1),
                           (-1, 2), (0, 2), (1, 2), (2, 2)]
                for step in range(12):
                    if data[step] != 0:
                        for dx2 in (-1, 0, 1):
                            for dy2 in (-1, 0, 1):
                                fun.bturnblock([pos[0] + offsets[step][0] + dx2, pos[1] + offsets[step][1] + dy2]).set(self.leavestype, 0, "grow")
            case a if a == treeheight - 1:
                for dx in (-3, -2, -1, 0, 1, 2, 3):
                    for dy in (-3, -2, -1, 0, 1, 2, 3):
                        fun.bturnblock([pos[0] + dx, pos[1] + dy]).set(self.leavestype, 0, "grow")
                offsets = [(-1, -1), (0, -1), (1, -1), (2, -1),
                           (-1, 0), (2, 0),
                           (-1, 1), (2, 1),
                           (-1, 2), (0, 2), (1, 2), (2, 2)]
                for step in range(12):
                    if data[step] != 0:
                        for dx2 in (-2, -1, 0, 1, 2):
                            for dy2 in (-2, -1, 0, 1, 2):
                                if (dx2, dy2) in [(-2, -2), (-2, 2), (2, -2), (2, 2)]:
                                    continue
                                fun.bturnblock([pos[0] + offsets[step][0] + dx2, pos[1] + offsets[step][1] + dy2]).set(self.leavestype, 0, "grow")
            case _:
                pass

    def summontree(self, mode=0):
        treeheight = random.randint(self.logheightrange[0], self.logheightrange[1])  # 随机树干高度，决定检测范围
        branchdata = []
        for _ in range(12):
            if random.random() < 1 / 3:
                branchdata.append(random.randint(2, 4))
            else:
                branchdata.append(0)
        self.testrange = self.testrangeset(treeheight)[self.height]  # 设置检测范围
        width = self.test(self.abpos, 3)  # 检测实际空间大小
        cangrow = False
        if self.testrange <= width or mode != 0:
            cangrow = True  # 检测结果判定
        if cangrow:
            if self.gen_leaves:
                self.summonleaves2(treeheight, branchdata, fun.bposmove(fun.bposmove(self.abpos, 2), 1))
            self.summonwoods(treeheight, branchdata, self.abpos)
class PaleOakPlan(GrowPlan):
    heightrange = (1, 11)  # 高度切片取值
    logheightrange = (6, 9)  # 树干高度取值
    woodtype = blocks.Paleoak
    leavestype = blocks.Paleoakleaves

    iconway = config.resource_path("files/icon/paleoaksapling.png")
    icon = pg.transform.scale(pg.image.load(iconway).convert_alpha(), (config.state.MenuWidth * 0.9 / 6, config.state.MenuWidth * 0.9 / 6))

    def draw(self):
        super().draw()
        topleft2 = fun.vturns(fun.bturnv(self.abpos))
        downright2 = fun.vturns(fun.bturnv(fun.bposmove(fun.bposmove(self.abpos, 2, 2), 1, 2)))
        rect2 = (topleft2[0] + 1, topleft2[1] + 1, downright2[0] - topleft2[0] - 1, downright2[1] - topleft2[1] - 1)
        if config.state.Zoom <= 4:
            pg.draw.rect(config.state.screen, (0, 139, 69), rect2, 3)

    def summonwoods(self, treeheight, data, pos):
        if self.height <= treeheight:
            fun.bturnblock(pos).set(self.woodtype, 0, "grow")
            fun.bturnblock(fun.bposmove(pos, 1)).set(self.woodtype, 0, "grow")
            fun.bturnblock(fun.bposmove(pos, 2)).set(self.woodtype, 0, "grow")
            fun.bturnblock(fun.bposmove(fun.bposmove(pos, 2), 1)).set(self.woodtype, 0, "grow")
        offsets = [(-1, -1), (0, -1), (1, -1), (2, -1),
                   (-1, 0), (2, 0),
                   (-1, 1), (2, 1),
                   (-1, 2), (0, 2), (1, 2), (2, 2)]
        for step in range(12):
            if treeheight - 1 - data[step] < self.height < treeheight and data[step] != 0:
                dx = offsets[step][0]
                dy = offsets[step][1]
                fun.bturnblock([pos[0] + dx, pos[1] + dy]).set(self.woodtype, 0, "grow")

    def summonleaves2(self, treeheight, data, pos):
        match self.height:
            case a if a == treeheight + 2 and random.random() < 1 / 5:
                for dx in (0, 1):
                    for dy in (0, 1):
                        fun.bturnblock([pos[0] + dx, pos[1] + dy]).set(self.leavestype, 0, "grow")
            case a if a == treeheight + 1:
                for dx in (-2, -1, 0, 1, 2, 3):
                    for dy in (-2, -1, 0, 1, 2, 3):
                        if (dx, dy) in [(-2, -2), (-2, 3), (3, -2), (3, 3), (2, 3), (-1, 3), (2, -2), (-1, -2), (3, 2),
                                        (3, -1), (-2, 2), (-2, -1)]:
                            continue
                        fun.bturnblock([pos[0] + dx, pos[1] + dy]).set(self.leavestype, 0, "grow")
            case a if a == treeheight:
                for dx in (-3, -2, -1, 0, 1, 2, 3, 4):
                    for dy in (-3, -2, -1, 0, 1, 2, 3, 4):
                        if (dx, dy) in [(-3, -3), (-3, -2), (-2, -3), (-2, -2),
                                        (-3, 4), (-3, 3), (-2, 4), (-2, 3),
                                        (4, -3), (4, -2), (3, -3), (3, -2),
                                        (4, 4), (4, 3), (3, 4), (3, 3), ]:
                            continue
                        fun.bturnblock([pos[0] + dx, pos[1] + dy]).set(self.leavestype, 0, "grow")

                offset2 = [(-3, -2), (-2, -3), (-2, -2),
                           (-3, 3), (-2, 4), (-2, 3),
                           (4, -2), (3, -3), (3, -2),
                           (4, 3), (3, 4), (3, 3), ]
                for g in range(4):
                    sub = offset2[g * 3:g * 3 + 3]
                    mainoffset = sub[2]
                    otheroffset = [sub[0], sub[1]]
                    rand = random.randint(0, 3)
                    match rand:
                        case 0:
                            continue
                        case 1:
                            x = pos[0] + mainoffset[0]
                            y = pos[1] + mainoffset[1]
                            fun.bturnblock([x, y]).set(self.leavestype, 0, "grow")
                        case 2:
                            x = pos[0] + mainoffset[0]
                            y = pos[1] + mainoffset[1]
                            fun.bturnblock([x, y]).set(self.leavestype, 0, "grow")
                            randos = random.choice(otheroffset)
                            x2 = pos[0] + randos[0]
                            y2 = pos[1] + randos[1]
                            fun.bturnblock([x2, y2]).set(self.leavestype, 0, "grow")
                        case 3:
                            for os in sub:
                                x = pos[0] + os[0]
                                y = pos[1] + os[1]
                                fun.bturnblock([x, y]).set(self.leavestype, 0, "grow")
                offsets = [(-1, -1), (0, -1), (1, -1), (2, -1),
                           (-1, 0), (2, 0),
                           (-1, 1), (2, 1),
                           (-1, 2), (0, 2), (1, 2), (2, 2)]
                for step in range(12):
                    if data[step] != 0:
                        for dx2 in (-1, 0, 1):
                            for dy2 in (-1, 0, 1):
                                fun.bturnblock([pos[0] + offsets[step][0] + dx2, pos[1] + offsets[step][1] + dy2]).set(self.leavestype, 0, "grow")
            case a if a == treeheight - 1:
                for dx in (-3, -2, -1, 0, 1, 2, 3):
                    for dy in (-3, -2, -1, 0, 1, 2, 3):
                        fun.bturnblock([pos[0] + dx, pos[1] + dy]).set(self.leavestype, 0, "grow")
                offsets = [(-1, -1), (0, -1), (1, -1), (2, -1),
                           (-1, 0), (2, 0),
                           (-1, 1), (2, 1),
                           (-1, 2), (0, 2), (1, 2), (2, 2)]
                for step in range(12):
                    if data[step] != 0:
                        for dx2 in (-2, -1, 0, 1, 2):
                            for dy2 in (-2, -1, 0, 1, 2):
                                if (dx2, dy2) in [(-2, -2), (-2, 2), (2, -2), (2, 2)]:
                                    continue
                                fun.bturnblock([pos[0] + offsets[step][0] + dx2, pos[1] + offsets[step][1] + dy2]).set(self.leavestype, 0, "grow")
            case _:
                pass

    def summontree(self, mode=0):
        treeheight = random.randint(self.logheightrange[0], self.logheightrange[1])  # 随机树干高度，决定检测范围
        branchdata = []
        for _ in range(12):
            if random.random() < 1 / 3:
                branchdata.append(random.randint(2, 4))
            else:
                branchdata.append(0)
        self.testrange = self.testrangeset(treeheight)[self.height]  # 设置检测范围
        width = self.test(self.abpos, 3)  # 检测实际空间大小
        cangrow = False
        if self.testrange <= width or mode != 0:
            cangrow = True  # 检测结果判定
        if cangrow:
            if self.gen_leaves:
                self.summonleaves2(treeheight, branchdata, fun.bposmove(fun.bposmove(self.abpos, 2), 1))
            self.summonwoods(treeheight, branchdata, self.abpos)
class CherryPlan(GrowPlan):
    heightrange = (1, 11)  # 高度切片取值
    logheightrange = 0#special  # 树干高度取值
    woodtype = blocks.Cherry
    leavestype = blocks.Cherryleaves

    iconway = config.resource_path("files/icon/cherrysapling.png")
    icon = pg.transform.scale(pg.image.load(iconway).convert_alpha(), (config.state.MenuWidth * 0.9 / 6, config.state.MenuWidth * 0.9 / 6))

    def summonbranches(self, data, pos):
        offset = data[self.height - 1]
        if offset != []:
            nx = pos[0] + offset[0]
            ny = pos[1] + offset[1]
            fun.bturnblock([nx, ny]).set(self.woodtype, 0, "grow")

    def summonleaves(self, height, brpos):
            dz = self.height - height
            if abs(dz) > 2:
                return
            for dx in range(-2, 3):
                for dy in range(-2, 3):
                    pos = [brpos[0] + dx, brpos[1] + dy]
                    if abs(dx) == 2 or abs(dy) == 2:
                        if random.random() < 0.9:
                            fun.bturnblock(pos).set(self.leavestype, 0, "grow")
                    else:
                        fun.bturnblock(pos).set(self.leavestype, 0, "grow")

    def summontree(self, mode=0):
        treeheight = 7 + random.randint(0, 1)  # 随机树干高度
        branchnum = random.randint(1, 3)  # 侧枝数目
        branchtoward1 = random.randint(0, 3)  # 侧枝1朝向
        branchtoward2 = fun.reverse(branchtoward1)  # 侧枝2朝向
        branchstartheight1 = 0  # 侧枝1开始生成位置
        branchstartheight2 = 0  # 侧枝2开始生成位置
        leanheight = 0  # 主干竖直高度
        match branchnum:
            case 1:
                branchstartheight1 = treeheight - 3 - random.randint(0, 1)
                leanheight = branchstartheight1 + 1
            case 2:
                branchstartheight1 = treeheight - 4
                branchstartheight2 = treeheight - 3
                leanheight = treeheight - 3
            case 3:
                branchstartheight1 = treeheight - 4
                branchstartheight2 = treeheight - 3
                leanheight = treeheight
        maindata = []
        for i in range(leanheight):
            maindata.append([0, 0])
        while len(maindata) < 11:
            maindata.append([])
        mainpos = [self.abpos[0], self.abpos[1]]  # 主干末端坐标（直干，与根部同x,y）
        branchwidth1 = 0  # 侧枝1宽度
        branchwidth2 = 0  # 侧枝2宽度
        basebranchwidth1 = 0  # 基础侧枝1宽度
        basebranchwidth2 = 0  # 基础侧枝2宽度
        branchheight1 = 0  # 侧枝1高度
        branchheight2 = 0  # 侧枝2高度
        match branchnum:
            case 1:
                branchheight1 = treeheight - random.randint(0, 1)
                basebranchwidth1 = 1
                branchwidth1 = random.randint(2, 4)
            case 2:
                branchheight1 = treeheight - random.randint(0, 1)
                branchheight2 = treeheight - random.randint(0, 1)
                basebranchwidth1 = 2
                basebranchwidth2 = 1
                branchwidth1 = random.randint(2, 4) + 1
                branchwidth2 = random.randint(2, 4)
            case 3:
                branchheight1 = treeheight - random.randint(0, 1)
                branchheight2 = treeheight - random.randint(0, 1)
                basebranchwidth1 = 2
                basebranchwidth2 = 2
                branchwidth1 = random.randint(2, 4) + 1
                branchwidth2 = random.randint(2, 4) + 1
        # region 侧枝生成
        def genbranchdata(startheight, toward, basewidth, totalwidth, endheight):
            offsets = [(0, -1), (1, 0), (0, 1), (-1, 0)]
            dx, dy = offsets[toward]
            data = []
            # 起始空层
            for i in range(startheight):
                data.append([])
            nx, ny = 0, 0
            for step in range(basewidth):
                nx += dx
                ny += dy
                data.append([nx, ny])
            h_remain = totalwidth - basewidth  # 剩余水平步数
            v_remain = endheight - (startheight + basewidth)  # 剩余竖直步数
            while h_remain > 0 or v_remain > 0:
                total = h_remain + v_remain
                if v_remain > 0 and (h_remain == 0 or random.random() < v_remain / total):
                    # 竖直步进
                    data.append([nx, ny])
                    v_remain -= 1
                else:
                    # 水平步进
                    nx += dx
                    ny += dy
                    data.append([nx, ny])
                    h_remain -= 1
            # 补齐到11层
            while len(data) < 11:
                data.append([])
            return data

        branchdata1 = genbranchdata(branchstartheight1, branchtoward1, basebranchwidth1, branchwidth1, branchheight1)
        if branchnum >= 2:
            branchdata2 = genbranchdata(branchstartheight2, branchtoward2, basebranchwidth2, branchwidth2,
                                        branchheight2)
        else:
            branchdata2 = []
        # 侧枝末端坐标（绝对坐标，用于树叶生成）
        if branchheight1 != 0:
            branchpos1 = [self.abpos[0] + (branchdata1[branchheight1 - 1][0] if branchdata1[branchheight1 - 1] else 0),
                          self.abpos[1] + (branchdata1[branchheight1 - 1][1] if branchdata1[branchheight1 - 1] else 0)]
        else:
            branchpos1 = [0, 0]
        if branchnum >= 2 and branchheight2 != 0:
            branchpos2 = [self.abpos[0] + (branchdata2[branchheight2 - 1][0] if branchdata2[branchheight2 - 1] else 0),
                          self.abpos[1] + (branchdata2[branchheight2 - 1][1] if branchdata2[branchheight2 - 1] else 0)]
        else:
            branchpos2 = [0, 0]
        # endregion
        self.testrange = self.testrangeset(treeheight)[self.height]  # 设置检测范围
        width = self.test(self.abpos, 3)  # 检测实际空间大小
        cangrow = False
        if self.testrange <= width or mode != 0:
            cangrow = True  # 检测结果判定
        if cangrow:
            if self.gen_leaves:
                self.summonleaves(treeheight, mainpos)
            self.summonbranches(maindata, self.abpos)
            if branchnum >= 1:
                if self.gen_leaves:
                    self.summonleaves(branchheight1, branchpos1)
                self.summonbranches(branchdata1, self.abpos)
            if branchnum >= 2:
                if self.gen_leaves:
                    self.summonleaves(branchheight2, branchpos2)
                self.summonbranches(branchdata2, self.abpos)
class MangrovePlan(GrowPlan):
    heightrange = (1, 25)  # 高度切片取值
    logheightrange = (7, 8)  # 树干高度取值
    woodtype = blocks.Mangrove
    leavestype = blocks.Mangroveleaves
    roottype= blocks.Mangroveroot

    iconway = config.resource_path("files/icon/mangrovesapling.png")
    icon = pg.transform.scale(pg.image.load(iconway).convert_alpha(), (config.state.MenuWidth * 0.9 / 6, config.state.MenuWidth * 0.9 / 6))

    def getrootdata(self,startheight, status):
        offsets = [(0, -1), (1, 0), (0, 1), (-1, 0)]
        data = []
        for toward in range(4):
            dx, dy = offsets[toward]
            # 随机宽度
            rootwidth = random.randint(1, 5)
            if status == 0 and 3 <= rootwidth <= 5:
                if random.random() < 0.5:
                    rootwidth -= 1
            if status == 1:
                if 1 <= rootwidth <= 3 and random.random() < 0.5:
                    rootwidth += 1
                if rootwidth == 5 and random.random() < 0.2:
                    rootwidth += 1
            # 搜索附近方块
            nearby = 0
            for dist in range(1, rootwidth + 1):
                checkpos = fun.bposmove(self.abpos, toward, dist)
                if fun.bturnblock(checkpos).pretend:
                    nearby = dist
                    break
            # 生成树根路径
            nx, ny = dx, dy
            currz = startheight
            hdist = 1
            data.append([nx, ny, currz])
            while currz > 1:
                hremain = rootwidth - hdist
                vremain = currz - 1
                if nearby != 0 and hdist >= nearby:
                    break
                if hremain <= 0:
                    currz -= 1
                    data.append([nx, ny, currz])
                    continue
                total = hremain + vremain
                if total == 0:
                    break
                if random.random() < hremain / total:
                    currz -= 1
                else:
                    nx += dx
                    ny += dy
                    hdist += 1
                data.append([nx, ny, currz])
        return data

    def getbranchdata(self, startheight, status):
        if random.random() >= 0.4:
            return []
        if status == 0:
            width = random.randint(1, 3)
        else:
            width = random.randint(1, 5)
        offsets = [(0, -1), (1, 0), (0, 1), (-1, 0)]
        toward = random.randint(0, 3)
        dx, dy = offsets[toward]
        data = []
        nx, ny = dx, dy
        currz = startheight
        hdist = 1
        data.append([nx, ny, currz])
        while hdist < width:
            nx += dx
            ny += dy
            currz += 1
            hdist += 1
            data.append([nx, ny, currz])
        return data

    def summonbranches(self, data, pos):
        offset = data[self.height - 1]
        if offset != []:
            nx = pos[0] + offset[0]
            ny = pos[1] + offset[1]
            fun.bturnblock([nx, ny]).set(self.woodtype, 0, "grow")

    def summonleaves(self, trunk_end, branch_ends):
        for ep in [trunk_end] + branch_ends:
            dz = self.height - ep[2]
            if abs(dz) > 2:
                continue
            for dx in range(-2, 3):
                for dy in range(-2, 3):
                    pos = [ep[0] + dx, ep[1] + dy]
                    if abs(dx) == 2 or abs(dy) == 2:
                        if random.random() < 0.9:
                            fun.bturnblock(pos).set(self.leavestype, 0, "grow")
                    else:
                        fun.bturnblock(pos).set(self.leavestype, 0, "grow")

    def summontree(self, mode=0):
        status=0
        rootheight = random.randint(1, 3)
        treeheight = rootheight + random.randint(0, 5) + 2
        if random.randint(0,100)<=85:
            status=1
            rootheight=random.randint(5,7)
            treeheight=rootheight+random.randint(0,1)+random.randint(0,9)+4
        rootdata = self.getrootdata(rootheight+1,status)
        branchdata = []
        branch_ends = []
        for h in range(rootheight + 1, treeheight + 1):
            branch = self.getbranchdata(h, status)
            if branch:
                branch_ends.append([self.abpos[0] + branch[-1][0], self.abpos[1] + branch[-1][1], branch[-1][2]])
            branchdata.extend(branch)
        trunk_end = [self.abpos[0], self.abpos[1], treeheight]

        self.testrange = self.testrangeset(treeheight)[self.height]  # 设置检测范围
        width = self.test(self.abpos, 3)  # 检测实际空间大小
        cangrow = False
        if self.testrange <= width or mode != 0:
            cangrow = True  # 检测结果判定
        if cangrow:
            if self.gen_leaves:
                self.summonleaves(trunk_end, branch_ends)
            # 放置主干
            if self.height in range(rootheight + 1, treeheight + 1):
                fun.bturnblock(self.abpos).set(self.woodtype, 0, "grow")
            if self.height == rootheight:
                fun.bturnblock(self.abpos).set(self.roottype, 0, "grow")
            for entry in rootdata:
                if entry[2] == self.height:
                    abspos = [self.abpos[0] + entry[0], self.abpos[1] + entry[1]]
                    fun.bturnblock(abspos).set(self.roottype, 0, "grow")
            for entry in branchdata:
                if entry[2] == self.height:
                    abspos = [self.abpos[0] + entry[0], self.abpos[1] + entry[1]]
                    fun.bturnblock(abspos).set(self.woodtype, 0, "grow")
class PoplarPlan(GrowPlan):
    heightrange = (1, 12)  # 高度切片取值
    logheightrange = (7, 10)  # 树干高度取值
    woodtype = blocks.Poplar
    leavestype = [blocks.PoplarRedleaves,blocks.PoplarOrangeleaves,blocks.PoplarYellowleaves]

    iconway = config.resource_path("files/icon/poplarsapling.png")
    icon = pg.transform.scale(pg.image.load(iconway).convert_alpha(), (config.state.MenuWidth * 0.9 / 6, config.state.MenuWidth * 0.9 / 6))

    def getleavesdata(self, height, z1, z2, r, offset):
        data = []
        mode = None
        gen_r = r
        if height == z2:
            mode = 0
            gen_r = r
        elif height > z2:
            if height >= z2 + 4:
                return []
            gen_r = r - (height - z2)
            if gen_r <= 0:
                return []
            if gen_r == 1:
                mode = 1
            else:
                mode = 0
        elif height < z2:
            delta = z2 - height
            if z2 - z1 == 2:
                if delta == 1:
                    mode = 0
                    gen_r = r - 1
                elif delta == 2:
                    mode = 1
            elif z2 - z1 == 3:
                if delta == 1:
                    mode = 0
                    gen_r = r
                elif delta == 2:
                    mode = 0
                    gen_r = r - 1
                elif delta == 3:
                    mode = 1
        if mode is None:
            return []
        if mode == 0:
            for dx in range(-gen_r, gen_r + 1):
                for dy in range(-gen_r, gen_r + 1):
                    if abs(dx) + abs(dy) > gen_r:
                        continue
                    if abs(dx) + abs(dy) == gen_r and random.random() < 0.15:
                        continue
                    data.append([dx + offset[0], dy + offset[1], height])
        elif mode == 1:
            for dx in range(-1, 2):
                for dy in range(-1, 2):
                    if max(abs(dx), abs(dy)) == 1 and random.random() < 0.15:
                        continue
                    data.append([dx + offset[0], dy + offset[1], height])
        return data

    def summontree(self, mode=0):
        treeheight = random.randint(7, 10)  # 随机树干高度，决定检测范围
        branch1height = treeheight - 4  # 一层侧枝高度
        branch1num = random.randint(1, 4) #一层侧枝数量
        branch2height = branch1height + random.randint(1,2) # 二层侧枝高度
        branch2width = 0 # 二层侧枝宽度
        randomnum = random.randint(0, 200)
        if randomnum >= 100:
            if randomnum <= 200:
                branch2width = 3
            if randomnum <= 165:
                branch2width = 2
            if randomnum <= 145:
                branch2width = 1
        leaveswidth = 5  # 树叶厚度
        randomnum = random.randint(0, 120)
        if randomnum >= 50:
            if randomnum <= 120:
                leaveswidth = 8
            if randomnum <= 110:
                leaveswidth = 7
            if randomnum <= 100:
                leaveswidth = 6

        self.testrange = self.testrangeset(treeheight)[self.height]  # 设置检测范围
        width = self.test(self.abpos, 3)  # 检测实际空间大小
        cangrow = False
        if self.testrange <= width or mode != 0:
            cangrow = True  # 检测结果判定
        if cangrow:
            if self.height <= treeheight:
                fun.bturnblock(self.abpos).set(self.woodtype, 0, "grow")
            if self.height == branch1height:
                directions = random.sample(range(4), branch1num)
                for d in directions:
                    abspos = fun.bposmove(self.abpos, d)
                    fun.bturnblock(abspos).set(self.woodtype, 0, "grow")
            if branch2width > 0 and self.height == branch2height:
                for d in range(4):
                    for step in range(1, branch2width + 1):
                        abspos = fun.bposmove(self.abpos, d, step)
                        fun.bturnblock(abspos).set(self.woodtype, 0, "grow")
            if self.gen_leaves:
                leavesrepeat = 1
                if branch2width >= 2:
                    leavesrepeat += random.randint(0, 1)
                if branch2width == 0 and random.random() < 0.25:
                    leavesrepeat = 0
                diag = random.randint(0, 1)
                offsets = []
                for step in range(-leavesrepeat, leavesrepeat + 1):
                    if diag == 0:
                        offsets.append([step, step])
                    else:
                        offsets.append([step, -step])
                leavesdata = []
                for off in offsets:
                    leavesdata.extend(self.getleavesdata(self.height, branch1height, branch2height, leaveswidth, off))
                leavetype = random.choice(self.leavestype)
                for entry in leavesdata:
                    abspos = [self.abpos[0] + entry[0], self.abpos[1] + entry[1]]
                    fun.bturnblock(abspos).set(leavetype, 0, "grow")
class AzaleaPlan(GrowPlan):
    heightrange = (1, 6)  # 高度切片取值
    logheightrange = (4, 5)  # 树干高度取值
    woodtype = blocks.Oak
    leavestype = [blocks.Azalealeaves,blocks.AzaleaFloweringleaves]

    iconway = config.resource_path("files/icon/azaleasapling.png")
    icon = pg.transform.scale(pg.image.load(iconway).convert_alpha(), (config.state.MenuWidth * 0.9 / 6, config.state.MenuWidth * 0.9 / 6))

    def summonleaves(self, height, pos):
        match self.height:
            case a if a == height + 1:
                for dx in (-2, -1, 0, 1, 2):
                    for dy in (-2, -1, 0, 1, 2):
                        if (dx, dy) in [(-2, -2), (-2, 2), (2, -2), (2, 2), (1, 2), (-1, 2), (1, -2), (-1, -2), (2, 1), (2, -1), (-2, 1), (-2, -1)]:
                            continue
                        fun.bturnblock([pos[0] + dx, pos[1] + dy]).set(self.leavestype, 0, "grow")
            case a if a == height:
                for dx in (-3, -2, -1, 0, 1, 2, 3):
                    for dy in (-3, -2, -1, 0, 1, 2, 3):
                        if (dx, dy) in [(-3, -3), (-3, 3), (3, -3), (3, 3)]:
                            continue
                        fun.bturnblock([pos[0] + dx, pos[1] + dy]).set(self.leavestype, 0, "grow")
            case _:
                pass

    def summontree(self, mode=0):
        treeheight = random.randint(4, 5)  # 随机树干高度，决定检测范围
        leanheight = treeheight - 2  # 主干弯曲起始高度确定
        toward = random.randint(0, 3)  # 朝向
        branchstartheight = leanheight - random.randint(1, 2)  # 侧枝开始生成高度

        offsets = [(0, -1), (1, 0), (0, 1), (-1, 0)]
        dx, dy = offsets[toward]

        self.testrange = self.testrangeset(treeheight)[self.height]  # 设置检测范围
        width = self.test(self.abpos, 3)  # 检测实际空间大小
        cangrow = False
        if self.testrange <= width or mode != 0:
            cangrow = True  # 检测结果判定
        if cangrow:
            # 竖直树干部分
            if self.height <= leanheight:
                fun.bturnblock(self.abpos).set(self.woodtype, 0, "grow")
            if self.height == treeheight - 1:
                abspos = fun.bposmove(self.abpos, toward)
                fun.bturnblock(abspos).set(self.woodtype, 0, "grow")
            if self.height == treeheight:
                abspos = fun.bposmove(self.abpos, toward, 2)
                fun.bturnblock(abspos).set(self.woodtype, 0, "grow")
                abspos = fun.bposmove(self.abpos, toward, 3)
                fun.bturnblock(abspos).set(self.woodtype, 0, "grow")
            if self.gen_leaves:
                base_abspos = fun.bposmove(self.abpos, toward, 2)
                base_z = treeheight
                axis_dx, axis_dy = [(0, -1), (1, 0), (0, 1), (-1, 0)][toward]
                perp_dx, perp_dy = [(1, 0), (0, 1), (1, 0), (0, 1)][toward]
                if base_z - 2 <= self.height <= base_z + 1:
                    for along in range(-3, 4):
                        for perp in range(-2, 3):
                            pos = [base_abspos[0] + along * axis_dx + perp * perp_dx,
                                   base_abspos[1] + along * axis_dy + perp * perp_dy]
                            dist = abs(along) + abs(perp) + abs(self.height - base_z)
                            if random.random() < max(0.15, 1.0 - dist / 7):
                                leavetype = blocks.AzaleaFloweringleaves if random.random() < 0.15 else blocks.Azalealeaves
                                fun.bturnblock(pos).set(leavetype, 0, "grow")

class BreakPlan(Zone):
    hidden = False
    gui = None

    imageway = config.resource_path("files/blocks/breakplan.png")
    iconway = config.resource_path("files/icon/breakplan.png")
    image = pg.image.load(imageway)
    image_load = image
    icon = pg.transform.scale(pg.image.load(iconway).convert_alpha(), (config.state.MenuWidth * 0.9 / 6, config.state.MenuWidth * 0.9 / 6))

    def __init__(self, cpos, bpos):
        super().__init__(cpos, bpos)
        self.clock = 0      # 周期
        self.range = 4      # 边长

    def __deepcopy__(self, memo):
        if id(self) in memo:
            return memo[id(self)]
        newobj = object.__new__(type(self))
        memo[id(self)] = newobj
        uncopyablename = {"image", "icon", "image_load", "gui", "_last_zoom", "_last_image"}
        copytarget = {key: value for key, value in self.__dict__.items() if key not in uncopyablename}
        newobj.__dict__ = copy.deepcopy(copytarget, memo)
        newobj.image = pg.image.load(newobj.imageway)
        newobj.image_load = newobj.image
        newobj.icon = pg.transform.scale(pg.image.load(newobj.iconway).convert_alpha(), (config.state.MenuWidth * 0.9 / 6, config.state.MenuWidth * 0.9 / 6))
        newobj.gui = type(self).gui
        return newobj

    def opengui(self):
        super().opengui()
        self.gui.clocktextbut.fontcolor = "white"
        self.gui.clocktextbut.textin = f"{self.clock}"
        self.gui.clocktextbut.textsaved = f"{self.clock}"
        self.gui.rangetextbut.fontcolor = "white"
        self.gui.rangetextbut.textin = f"{self.range}"
        self.gui.rangetextbut.textsaved = f"{self.range}"

    def draw(self):
        super().draw()
        if config.state.Zoom <= 4:
            half = self.range // 2
            if self.range % 2 == 1:
                x1 = self.abpos[0] - half
                y1 = self.abpos[1] - half
            else:
                x1 = self.abpos[0] - half + 1
                y1 = self.abpos[1] - half + 1
            x2 = x1 + self.range
            y2 = y1 + self.range
            topleft = fun.vturns(fun.bturnv([x1, y1]))
            downright = fun.vturns(fun.bturnv([x2, y2]))
            rect = (topleft[0] + 1, topleft[1] + 1, downright[0] - topleft[0] - 1, downright[1] - topleft[1] - 1)
            pg.draw.rect(config.state.screen, (128, 128, 128), rect, 3)

    def function(self):
        super().function()
        if self.clock == 0:
            return
        if config.state.tick % self.clock != 0:
            return

        half = self.range // 2
        if self.range % 2 == 1:
            x1 = self.abpos[0] - half
            x2 = self.abpos[0] + half
            y1 = self.abpos[1] - half
            y2 = self.abpos[1] + half
        else:
            x1 = self.abpos[0] - half + 1
            x2 = self.abpos[0] + half
            y1 = self.abpos[1] - half + 1
            y2 = self.abpos[1] + half

        cs = config.state.ChunkSize
        ss = config.state.SubChunkSize
        limit = cs * ss
        for x in range(max(0, x1), min(limit, x2 + 1)):
            for y in range(max(0, y1), min(limit, y2 + 1)):
                cid = fun.cturncid(fun.vturnc(fun.bturnv([x, y])))
                bid = fun.ubturnbid(fun.vturnub(fun.bturnv([x, y])))
                block = config.state.ChunkList[cid][bid]
                if not block.hidden:
                    effects.create_fade(block.abpos, (128, 128, 128), config.state.Oneticktime)
                    block.remove()

        effects.create_fade(self.abpos, (128, 128, 128), config.state.Oneticktime)

class SetPlan(Zone):
    hidden = False
    gui = None

    imageway = config.resource_path("files/blocks/setplan.png")
    iconway = config.resource_path("files/icon/setplan.png")
    image = pg.image.load(imageway)
    image_load = image
    icon = pg.transform.scale(pg.image.load(iconway).convert_alpha(), (config.state.MenuWidth * 0.9 / 6, config.state.MenuWidth * 0.9 / 6))

    def __init__(self, cpos, bpos):
        super().__init__(cpos, bpos)
        self.clock = 0
        self.settrigger = blocks.Stone

    def __deepcopy__(self, memo):
        if id(self) in memo:
            return memo[id(self)]
        newobj = object.__new__(type(self))
        memo[id(self)] = newobj
        uncopyablename = {"image", "icon", "image_load", "gui", "_last_zoom", "_last_image"}
        copytarget = {key: value for key, value in self.__dict__.items() if key not in uncopyablename}
        newobj.__dict__ = copy.deepcopy(copytarget, memo)
        newobj.image = pg.image.load(newobj.imageway)
        newobj.image_load = newobj.image
        newobj.icon = pg.transform.scale(pg.image.load(newobj.iconway).convert_alpha(), (config.state.MenuWidth * 0.9 / 6, config.state.MenuWidth * 0.9 / 6))
        newobj.gui = type(self).gui
        return newobj

    def opengui(self):
        super().opengui()
        self.gui.clocktextbut.fontcolor = "white"
        self.gui.clocktextbut.textin = f"{self.clock}"
        self.gui.clocktextbut.textsaved = f"{self.clock}"
        # 更新放置方块icon
        if self.settrigger is not None and hasattr(self.settrigger, 'icon') and self.settrigger.icon is not None:
            ico = pg.transform.smoothscale(self.settrigger.icon,
                (self.gui.placeicon.size[0] - 4, self.gui.placeicon.size[1] - 4))
            self.gui.placeicon.icon = ico

    def function(self):
        super().function()
        if self.clock == 0:
            return
        if config.state.tick % self.clock != 0:
            return
        cid = fun.cturncid(self.cpos)
        bid = fun.ubturnbid(self.bpos)
        block = config.state.ChunkList[cid][bid]
        if type(block) != blocks.Barrier and self.settrigger is not None:
            block.set(self.settrigger, 0, "strong")
            effects.create_fade(self.abpos, (139, 90, 43), config.state.Oneticktime)

# 创建区域列表与子列表
Zoneclass = fun.subclass(Zone)
for zon in Zoneclass:
    if len(fun.subclass(zon)) != 0:
        zon.sub = fun.subclass(zon)

__all__ = [
    "Zone", "RedPlan", "MovingPlan", "GrowPlan", "OakPlan", "BrichPlan", "SprucePlan","MegaSprucePlan",
    "JunglePlan","MegaJunglePlan", "AcaciaPlan", "DarkOakPlan", "PaleOakPlan", "CherryPlan","MangrovePlan","AzaleaPlan",
    "BreakPlan", "SetPlan", "Zoneclass"
]