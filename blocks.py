import copy
import pygame as pg
import config
import functions as fun
import effects


class Block:
    is_zone = False
    # 空间
    cpos = [0, 0]  # 区块坐标
    bpos = [0, 0]  # 方块坐标相对坐标
    abpos = fun.idturnb(fun.cturncid(cpos), fun.ubturnbid(bpos))  # 方块绝对坐标
    can_rotate = False  # 可旋转
    can_rotate_byhand = False  # 可手动旋转
    towards = 0  # 朝向，北0东1南2西3
    # 属性
    powered = False  # 被充能
    is_moving = 0  # 移动状态
    actived = False  # 被激活
    zone_powered = False  # 区域提供的充能
    special = 0  # 特殊值

    pretend = True  # 阻止生长
    can_powered = True  # 可以被强充能
    can_push = True  # 可以被推动
    can_slime = True  # 可以被粘液块粘
    can_honey = True  # 可以被蜂蜜块粘
    push_destroyed = False  # 推动时被摧毁
    grow_destoryed = False  # 生长时被摧毁
    show_moving = True  # 是否显示mb标识

    has_function = False  # 具有功能
    has_generate = False  # 可以提供充能
    target_generate = False  # 是否有充能指向性
    # 结构
    sub = []
    hidden = True  # 隐藏于方块列表中
    unseen = False  # 不可见

    # 图片
    imageway = config.resource_path("files/blocks/stone.png")
    iconway = config.resource_path("files/icon/stone.png")
    moving_imageway = config.resource_path("files/blocks/moving.png")
    image = pg.image.load(imageway)
    image_moving = pg.image.load(moving_imageway)
    image_load = image
    image_moving_load = image_moving
    icon = pg.transform.scale(pg.image.load(iconway).convert_alpha(),(config.state.MenuWidth * 0.9 / 6, config.state.MenuWidth * 0.9 / 6))

    # 缓存
    _last_zoom = None
    _last_towards = None
    _last_image = None
    _last_moving_zoom = None
    _last_moving_towards = None
    _last_moving_image = None

    # 函数
    def __init__(self, cpos, bpos, towards=0, mode="double", abpos=0):
        if mode == "double":
            self.cpos = cpos
            self.bpos = bpos
            if self.can_rotate == True:
                self.towards = towards
            self.abpos = fun.idturnb(fun.cturncid(cpos), fun.ubturnbid(bpos))
        else:
            self.abpos = abpos
            self.cpos = fun.vturnc(fun.bturnv(abpos))
            self.bpos = fun.vturnub(fun.bturnv(abpos))
            if self.can_rotate == True:
                self.towards = towards

    def __deepcopy__(self, memo):
        if id(self) in memo:
            return memo[id(self)]
        if type(self) != Air:
            newobj = object.__new__(type(self))
            memo[id(self)] = newobj
            uncopyablename = {"image", "icon", "image_load", "image_moving", "image_moving_load",
                              "_last_zoom", "_last_towards", "_last_image",
                              "_last_moving_zoom", "_last_moving_towards", "_last_moving_image"}
            copytarget = {key: value for key, value in self.__dict__.items() if key not in uncopyablename}
            newobj.__dict__ = copy.deepcopy(copytarget, memo)
            newobj.image = pg.image.load(newobj.imageway)
            newobj.image_moving = pg.image.load(newobj.moving_imageway)
            newobj.image_load = newobj.image
            newobj.image_moving_load = newobj.image_moving
            newobj.icon = pg.transform.scale(pg.image.load(newobj.iconway).convert_alpha(),
                                             (config.state.MenuWidth * 0.9 / 6, config.state.MenuWidth * 0.9 / 6))
            return newobj
        else:
            newobj = Air(self.cpos, self.bpos)
            return newobj

    def draw(self):
        if self.unseen == False:
            if (-config.state.BaseBlockSize / config.state.Zoom <= fun.vturns(fun.bturnv(self.abpos))[0] <= config.state.Ssize[0] and
                    -config.state.BaseBlockSize / config.state.Zoom <= fun.vturns(fun.bturnv(self.abpos))[1] <= config.state.Ssize[1]):
                zoom = config.state.BaseBlockSize / config.state.Zoom
                # 复用缓存
                if self._last_zoom != zoom or self._last_towards != self.towards or self._last_image is not self.image:
                    self.image_load = pg.transform.scale(
                        pg.transform.rotate(self.image, -90 * self.towards), (zoom, zoom))
                    self._last_zoom = zoom
                    self._last_towards = self.towards
                    self._last_image = self.image
                config.state.screen.blit(self.image_load, (fun.vturns(fun.bturnv(self.abpos))))
        if self.is_moving != 0 and self.show_moving:
            zoom = config.state.BaseBlockSize / config.state.Zoom
            if self._last_moving_zoom != zoom or self._last_moving_towards != self.towards or self._last_moving_image is not self.image_moving:
                self.image_moving_load = pg.transform.scale(
                    pg.transform.rotate(self.image_moving, -90 * self.towards), (zoom, zoom))
                self._last_moving_zoom = zoom
                self._last_moving_towards = self.towards
                self._last_moving_image = self.image_moving
            config.state.screen.blit(self.image_moving_load, (fun.vturns(fun.bturnv(self.abpos))))

    def set(self, trigger, toward=0, mode="normal"):
        match mode:
            case "normal":
                if type(config.state.ChunkList[fun.cturncid(self.cpos)][fun.ubturnbid(self.bpos)]) == Air:
                    newobj = trigger(self.cpos, self.bpos, toward)
                    config.state.ChunkList[fun.cturncid(self.cpos)][fun.ubturnbid(self.bpos)] = newobj
                    self.notify_neighbors()
                    newobj.after_set()
            case "strong":
                newobj = trigger(self.cpos, self.bpos, toward)
                config.state.ChunkList[fun.cturncid(self.cpos)][fun.ubturnbid(self.bpos)] = newobj
                self.notify_neighbors()
                newobj.after_set()
            case "grow":
                if config.state.ChunkList[fun.cturncid(self.cpos)][fun.ubturnbid(self.bpos)].grow_destoryed:
                    newobj = trigger(self.cpos, self.bpos, toward)
                    config.state.ChunkList[fun.cturncid(self.cpos)][fun.ubturnbid(self.bpos)] = newobj
                    self.notify_neighbors()
                    newobj.after_set()
            case _:
                pass

    def after_set(self):
        pass

    def remove(self):
        if type(config.state.ChunkList[fun.cturncid(self.cpos)][fun.ubturnbid(self.bpos)]) != Air and type(
                config.state.ChunkList[fun.cturncid(self.cpos)][fun.ubturnbid(self.bpos)]) != Barrier:
            self.notify_neighbors()
            config.state.ChunkList[fun.cturncid(self.cpos)][fun.ubturnbid(self.bpos)] = Air(self.cpos, self.bpos)

    def neighborchanged(self, towards):
        pass

    def is_alive(self):
        return fun.bturnblock(self.abpos) is self

    def notify_neighbors(self):
        for twd in (0, 1, 2, 3):
            fun.bturnblock(fun.bposmove(self.abpos, twd)).neighborchanged(twd)

    def bemoved(self):
        pass

    def rotate(self):
        if self.can_rotate == True:
            if self.towards != 3:
                self.towards += 1
            else:
                self.towards = 0

    def update(self, newbpos):
        self.cpos = fun.vturnc(fun.bturnv(newbpos))
        self.bpos = fun.vturnub(fun.bturnv(newbpos))
        self.abpos = newbpos

class NullBlock:
    def draw(self):
        pass

    def set(self, trigger, toward=0, mode="normal"):
        pass

    def remove(self):
        pass

    def neighborchanged(self, towards):
        pass

    def notify_neighbors(self):
        pass

    def rotate(self):
        pass

    def update(self, newbpos):
        pass
#子类
class Air(Block):
    pretend = False
    can_powered = False
    can_slime = False
    can_honey = False
    push_destroyed = True
    grow_destoryed = True
    unseen = True
class Solid(Block):
    hidden = False
class Stone(Solid):
    pass
class Brick(Solid):
    imageway = config.resource_path("files/blocks/brick.png")
    iconway = config.resource_path("files/icon/brick.png")
    image = pg.image.load(imageway)
    image_load = image
    icon = pg.transform.scale(pg.image.load(iconway).convert_alpha(),
                               (config.state.MenuWidth * 0.9 / 6, config.state.MenuWidth * 0.9 / 6))
class StoneBrick(Solid):
    imageway = config.resource_path("files/blocks/stone_brick.png")
    iconway = config.resource_path("files/icon/stone_brick.png")
    image = pg.image.load(imageway)
    image_load = image
    icon = pg.transform.scale(pg.image.load(iconway).convert_alpha(),
                               (config.state.MenuWidth * 0.9 / 6, config.state.MenuWidth * 0.9 / 6))
class PolishedAndesite(Solid):
    imageway = config.resource_path("files/blocks/polished_andesite.png")
    iconway = config.resource_path("files/icon/polished_andesite.png")
    image = pg.image.load(imageway)
    image_load = image
    icon = pg.transform.scale(pg.image.load(iconway).convert_alpha(),
                               (config.state.MenuWidth * 0.9 / 6, config.state.MenuWidth * 0.9 / 6))
class PolishedDeepslate(Solid):
    imageway = config.resource_path("files/blocks/polished_deepslate.png")
    iconway = config.resource_path("files/icon/polished_deepslate.png")
    image = pg.image.load(imageway)
    image_load = image
    icon = pg.transform.scale(pg.image.load(iconway).convert_alpha(),
                               (config.state.MenuWidth * 0.9 / 6, config.state.MenuWidth * 0.9 / 6))
class EndBrick(Solid):
    imageway = config.resource_path("files/blocks/end_stone_brick.png")
    iconway = config.resource_path("files/icon/end_stone_brick.png")
    image = pg.image.load(imageway)
    image_load = image
    icon = pg.transform.scale(pg.image.load(iconway).convert_alpha(),
                               (config.state.MenuWidth * 0.9 / 6, config.state.MenuWidth * 0.9 / 6))
class CutCopper(Solid):
    imageway = config.resource_path("files/blocks/cut_copper.png")
    iconway = config.resource_path("files/icon/cut_copper.png")
    image = pg.image.load(imageway)
    image_load = image
    icon = pg.transform.scale(pg.image.load(iconway).convert_alpha(),
                               (config.state.MenuWidth * 0.9 / 6, config.state.MenuWidth * 0.9 / 6))
class Purpur(Solid):
    imageway = config.resource_path("files/blocks/purpur_block.png")
    iconway = config.resource_path("files/icon/purpur_block.png")
    image = pg.image.load(imageway)
    image_load = image
    icon = pg.transform.scale(pg.image.load(iconway).convert_alpha(),
                               (config.state.MenuWidth * 0.9 / 6, config.state.MenuWidth * 0.9 / 6))
class Quartz(Solid):
    imageway = config.resource_path("files/blocks/quartz_block.png")
    iconway = config.resource_path("files/icon/quartz_block.png")
    image = pg.image.load(imageway)
    image_load = image
    icon = pg.transform.scale(pg.image.load(iconway).convert_alpha(),
                               (config.state.MenuWidth * 0.9 / 6, config.state.MenuWidth * 0.9 / 6))
class AndesiteCasing(Solid):
    imageway = config.resource_path("files/blocks/andesite_casing.png")
    iconway = config.resource_path("files/icon/andesite_casing.png")
    imageset = pg.image.load(imageway).convert_alpha()
    imagemap = None
    image = imageset.subsurface((0, 0, 16, 16))
    image_load = image
    icon = pg.transform.scale(pg.image.load(iconway).convert_alpha(),
                               (config.state.MenuWidth * 0.9 / 6, config.state.MenuWidth * 0.9 / 6))

    @classmethod
    def createmap(cls):
        if cls.imagemap is None:
            def compress(i):
                N  = (i >> 0) & 1; NE = (i >> 1) & 1; E = (i >> 2) & 1; SE = (i >> 3) & 1
                S  = (i >> 4) & 1; SW = (i >> 5) & 1; W = (i >> 6) & 1; NW = (i >> 7) & 1
                # 压缩：角位两侧两条边不全为1则清零
                NE = NE and N and E
                SE = SE and E and S
                SW = SW and S and W
                NW = NW and W and N
                return N | (NE << 1) | (E << 2) | (SE << 3) | (S << 4) | (SW << 5) | (W << 6) | (NW << 7)
            codes = sorted({compress(i) for i in range(256)})
            cls.imagemap = {c: idx for idx, c in enumerate(codes)}
        return cls.imagemap

    def updateimage(self):
        x, y = self.abpos
        b = fun.bturnblock
        same = lambda p: isinstance(b(p), AndesiteCasing)
        N  = same([x,   y - 1]); NE = same([x + 1, y - 1])
        E  = same([x + 1, y   ]); SE = same([x + 1, y + 1])
        S  = same([x,   y + 1]); SW = same([x - 1, y + 1])
        W  = same([x - 1, y   ]); NW = same([x - 1, y - 1])
        # 编码：正上N为最低位，顺时针绕一圈，左上NW为最高位；角位做压缩
        code = (N << 0) | ((NE and N and E) << 1) | (E << 2) | ((SE and E and S) << 3) \
             | (S << 4) | ((SW and S and W) << 5) | (W << 6) | ((NW and W and N) << 7)
        idx = self.createmap()[code]                    # 0..46
        tx, ty = (idx % 8) * 16, (idx // 8) * 16
        self.image = AndesiteCasing.imageset.subsurface((tx, ty, 16, 16))
        self.image_load = self.image

    def nearbyupdate(self):
        blk = fun.bturnblock(self.abpos)
        if isinstance(blk, AndesiteCasing):
            blk.updateimage()
        x, y = self.abpos
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx == 0 and dy == 0:
                    continue
                around = fun.bturnblock([x + dx, y + dy])
                if isinstance(around, AndesiteCasing):
                    around.updateimage()

    def after_set(self):
        self.nearbyupdate()

    def bemoved(self):
        self.nearbyupdate()

    def neighborchanged(self, towards):
        self.nearbyupdate()

    def remove(self):
        super().remove()
        self.nearbyupdate()

def refresh_connected_casings():
    for chunk in config.state.ChunkList:
        for blk in chunk:
            if isinstance(blk, AndesiteCasing):
                blk.updateimage()
class Concrete(Block):
    hidden = False
    imageway = config.resource_path("files/blocks/white_concrete.png")
    iconway = config.resource_path("files/icon/white_concrete.png")
    image = pg.image.load(imageway)
    image_load = image
    icon = pg.transform.scale(pg.image.load(iconway).convert_alpha(),
                               (config.state.MenuWidth * 0.9 / 6, config.state.MenuWidth * 0.9 / 6))
class ConcrateWhite(Concrete):
    pass
class ConcrateOrange(Concrete):
    imageway = config.resource_path("files/blocks/orange_concrete.png")
    iconway = config.resource_path("files/icon/orange_concrete.png")
    image = pg.image.load(imageway)
    image_load = image
    icon = pg.transform.scale(pg.image.load(iconway).convert_alpha(),
                               (config.state.MenuWidth * 0.9 / 6, config.state.MenuWidth * 0.9 / 6))
class ConcrateMagenta(Concrete):
    imageway = config.resource_path("files/blocks/magenta_concrete.png")
    iconway = config.resource_path("files/icon/magenta_concrete.png")
    image = pg.image.load(imageway)
    image_load = image
    icon = pg.transform.scale(pg.image.load(iconway).convert_alpha(),
                               (config.state.MenuWidth * 0.9 / 6, config.state.MenuWidth * 0.9 / 6))
class ConcrateLightBlue(Concrete):
    imageway = config.resource_path("files/blocks/light_blue_concrete.png")
    iconway = config.resource_path("files/icon/light_blue_concrete.png")
    image = pg.image.load(imageway)
    image_load = image
    icon = pg.transform.scale(pg.image.load(iconway).convert_alpha(),
                               (config.state.MenuWidth * 0.9 / 6, config.state.MenuWidth * 0.9 / 6))
class ConcrateYellow(Concrete):
    imageway = config.resource_path("files/blocks/yellow_concrete.png")
    iconway = config.resource_path("files/icon/yellow_concrete.png")
    image = pg.image.load(imageway)
    image_load = image
    icon = pg.transform.scale(pg.image.load(iconway).convert_alpha(),
                               (config.state.MenuWidth * 0.9 / 6, config.state.MenuWidth * 0.9 / 6))
class ConcrateLime(Concrete):
    imageway = config.resource_path("files/blocks/lime_concrete.png")
    iconway = config.resource_path("files/icon/lime_concrete.png")
    image = pg.image.load(imageway)
    image_load = image
    icon = pg.transform.scale(pg.image.load(iconway).convert_alpha(),
                               (config.state.MenuWidth * 0.9 / 6, config.state.MenuWidth * 0.9 / 6))
class ConcratePink(Concrete):
    imageway = config.resource_path("files/blocks/pink_concrete.png")
    iconway = config.resource_path("files/icon/pink_concrete.png")
    image = pg.image.load(imageway)
    image_load = image
    icon = pg.transform.scale(pg.image.load(iconway).convert_alpha(),
                               (config.state.MenuWidth * 0.9 / 6, config.state.MenuWidth * 0.9 / 6))
class ConcrateGray(Concrete):
    imageway = config.resource_path("files/blocks/gray_concrete.png")
    iconway = config.resource_path("files/icon/gray_concrete.png")
    image = pg.image.load(imageway)
    image_load = image
    icon = pg.transform.scale(pg.image.load(iconway).convert_alpha(),
                               (config.state.MenuWidth * 0.9 / 6, config.state.MenuWidth * 0.9 / 6))
class ConcrateLightGray(Concrete):
    imageway = config.resource_path("files/blocks/light_gray_concrete.png")
    iconway = config.resource_path("files/icon/light_gray_concrete.png")
    image = pg.image.load(imageway)
    image_load = image
    icon = pg.transform.scale(pg.image.load(iconway).convert_alpha(),
                               (config.state.MenuWidth * 0.9 / 6, config.state.MenuWidth * 0.9 / 6))
class ConcrateCyan(Concrete):
    imageway = config.resource_path("files/blocks/cyan_concrete.png")
    iconway = config.resource_path("files/icon/cyan_concrete.png")
    image = pg.image.load(imageway)
    image_load = image
    icon = pg.transform.scale(pg.image.load(iconway).convert_alpha(),
                               (config.state.MenuWidth * 0.9 / 6, config.state.MenuWidth * 0.9 / 6))
class ConcratePurple(Concrete):
    imageway = config.resource_path("files/blocks/purple_concrete.png")
    iconway = config.resource_path("files/icon/purple_concrete.png")
    image = pg.image.load(imageway)
    image_load = image
    icon = pg.transform.scale(pg.image.load(iconway).convert_alpha(),
                               (config.state.MenuWidth * 0.9 / 6, config.state.MenuWidth * 0.9 / 6))
class ConcrateBlue(Concrete):
    imageway = config.resource_path("files/blocks/blue_concrete.png")
    iconway = config.resource_path("files/icon/blue_concrete.png")
    image = pg.image.load(imageway)
    image_load = image
    icon = pg.transform.scale(pg.image.load(iconway).convert_alpha(),
                               (config.state.MenuWidth * 0.9 / 6, config.state.MenuWidth * 0.9 / 6))
class ConcrateBrown(Concrete):
    imageway = config.resource_path("files/blocks/brown_concrete.png")
    iconway = config.resource_path("files/icon/brown_concrete.png")
    image = pg.image.load(imageway)
    image_load = image
    icon = pg.transform.scale(pg.image.load(iconway).convert_alpha(),
                               (config.state.MenuWidth * 0.9 / 6, config.state.MenuWidth * 0.9 / 6))
class ConcrateGreen(Concrete):
    imageway = config.resource_path("files/blocks/green_concrete.png")
    iconway = config.resource_path("files/icon/green_concrete.png")
    image = pg.image.load(imageway)
    image_load = image
    icon = pg.transform.scale(pg.image.load(iconway).convert_alpha(),
                               (config.state.MenuWidth * 0.9 / 6, config.state.MenuWidth * 0.9 / 6))
class ConcrateRed(Concrete):
    imageway = config.resource_path("files/blocks/red_concrete.png")
    iconway = config.resource_path("files/icon/red_concrete.png")
    image = pg.image.load(imageway)
    image_load = image
    icon = pg.transform.scale(pg.image.load(iconway).convert_alpha(),
                               (config.state.MenuWidth * 0.9 / 6, config.state.MenuWidth * 0.9 / 6))
class ConcrateBlack(Concrete):
    imageway = config.resource_path("files/blocks/black_concrete.png")
    iconway = config.resource_path("files/icon/black_concrete.png")
    image = pg.image.load(imageway)
    image_load = image
    icon = pg.transform.scale(pg.image.load(iconway).convert_alpha(),
                               (config.state.MenuWidth * 0.9 / 6, config.state.MenuWidth * 0.9 / 6))
class Log(Block):
    hidden = False
    imageway = config.resource_path("files/blocks/oak.png")
    iconway = config.resource_path("files/icon/oak.png")
    image = pg.image.load(imageway)
    image_load = image
    icon = pg.transform.scale(pg.image.load(iconway).convert_alpha(),
                               (config.state.MenuWidth * 0.9 / 6, config.state.MenuWidth * 0.9 / 6))
class Oak(Log):
    pass
class Brich(Log):
    imageway = config.resource_path("files/blocks/birch.png")
    iconway = config.resource_path("files/icon/birch.png")
    image = pg.image.load(imageway)
    image_load = image
    icon = pg.transform.scale(pg.image.load(iconway).convert_alpha(),
                               (config.state.MenuWidth * 0.9 / 6, config.state.MenuWidth * 0.9 / 6))
class Spruce(Log):
    imageway = config.resource_path("files/blocks/spruce.png")
    iconway = config.resource_path("files/icon/spruce.png")
    image = pg.image.load(imageway)
    image_load = image
    icon = pg.transform.scale(pg.image.load(iconway).convert_alpha(),
                               (config.state.MenuWidth * 0.9 / 6, config.state.MenuWidth * 0.9 / 6))
class Jungle(Log):
    imageway = config.resource_path("files/blocks/jungle.png")
    iconway = config.resource_path("files/icon/jungle.png")
    image = pg.image.load(imageway)
    image_load = image
    icon = pg.transform.scale(pg.image.load(iconway).convert_alpha(),
                               (config.state.MenuWidth * 0.9 / 6, config.state.MenuWidth * 0.9 / 6))
class Acacia(Log):
    imageway = config.resource_path("files/blocks/acacia.png")
    iconway = config.resource_path("files/icon/acacia.png")
    image = pg.image.load(imageway)
    image_load = image
    icon = pg.transform.scale(pg.image.load(iconway).convert_alpha(),
                               (config.state.MenuWidth * 0.9 / 6, config.state.MenuWidth * 0.9 / 6))
class Mangrove(Log):
    imageway = config.resource_path("files/blocks/mangrove.png")
    iconway = config.resource_path("files/icon/mangrove.png")
    image = pg.image.load(imageway)
    image_load = image
    icon = pg.transform.scale(pg.image.load(iconway).convert_alpha(),
                               (config.state.MenuWidth * 0.9 / 6, config.state.MenuWidth * 0.9 / 6))
class Mangroveroot(Log):
    imageway = config.resource_path("files/blocks/mangrove_root.png")
    iconway = config.resource_path("files/icon/mangrove_root.png")
    image = pg.image.load(imageway)
    image_load = image
    icon = pg.transform.scale(pg.image.load(iconway).convert_alpha(),
                               (config.state.MenuWidth * 0.9 / 6, config.state.MenuWidth * 0.9 / 6))
class Darkoak(Log):
    imageway = config.resource_path("files/blocks/darkoak.png")
    iconway = config.resource_path("files/icon/darkoak.png")
    image = pg.image.load(imageway)
    image_load = image
    icon = pg.transform.scale(pg.image.load(iconway).convert_alpha(),
                               (config.state.MenuWidth * 0.9 / 6, config.state.MenuWidth * 0.9 / 6))
class Cherry(Log):
    imageway = config.resource_path("files/blocks/cherry.png")
    iconway = config.resource_path("files/icon/cherry.png")
    image = pg.image.load(imageway)
    image_load = image
    icon = pg.transform.scale(pg.image.load(iconway).convert_alpha(),
                               (config.state.MenuWidth * 0.9 / 6, config.state.MenuWidth * 0.9 / 6))
class Paleoak(Log):
    imageway = config.resource_path("files/blocks/paleoak.png")
    iconway = config.resource_path("files/icon/paleoak.png")
    image = pg.image.load(imageway)
    image_load = image
    icon = pg.transform.scale(pg.image.load(iconway).convert_alpha(),
                               (config.state.MenuWidth * 0.9 / 6, config.state.MenuWidth * 0.9 / 6))
class Poplar(Log):
    imageway = config.resource_path("files/blocks/poplar.png")
    iconway = config.resource_path("files/icon/poplar.png")
    image = pg.image.load(imageway)
    image_load = image
    icon = pg.transform.scale(pg.image.load(iconway).convert_alpha(),
                               (config.state.MenuWidth * 0.9 / 6, config.state.MenuWidth * 0.9 / 6))
class Leaves(Block):
    hidden = False
    can_slime = False
    can_honey = False
    push_destroyed = True
    grow_destoryed = True
    pretend = False
    imageway = config.resource_path("files/blocks/oak_leaves.png")
    iconway = config.resource_path("files/icon/oak_leaves.png")
    image = pg.image.load(imageway)
    image_load = image
    icon = pg.transform.scale(pg.image.load(iconway).convert_alpha(),
                               (config.state.MenuWidth * 0.9 / 6, config.state.MenuWidth * 0.9 / 6))
class Oakleaves(Leaves):
    pass
class Brichleaves(Leaves):
    imageway = config.resource_path("files/blocks/birch_leaves.png")
    iconway = config.resource_path("files/icon/birch_leaves.png")
    image = pg.image.load(imageway)
    image_load = image
    icon = pg.transform.scale(pg.image.load(iconway).convert_alpha(),
                               (config.state.MenuWidth * 0.9 / 6, config.state.MenuWidth * 0.9 / 6))
class Spruceleaves(Leaves):
    imageway = config.resource_path("files/blocks/spruce_leaves.png")
    iconway = config.resource_path("files/icon/spruce_leaves.png")
    image = pg.image.load(imageway)
    image_load = image
    icon = pg.transform.scale(pg.image.load(iconway).convert_alpha(),
                               (config.state.MenuWidth * 0.9 / 6, config.state.MenuWidth * 0.9 / 6))
class Jungleleaves(Leaves):
    imageway = config.resource_path("files/blocks/jungle_leaves.png")
    iconway = config.resource_path("files/icon/jungle_leaves.png")
    image = pg.image.load(imageway)
    image_load = image
    icon = pg.transform.scale(pg.image.load(iconway).convert_alpha(),
                               (config.state.MenuWidth * 0.9 / 6, config.state.MenuWidth * 0.9 / 6))
class Acacialeaves(Leaves):
    imageway = config.resource_path("files/blocks/acacia_leaves.png")
    iconway = config.resource_path("files/icon/acacia_leaves.png")
    image = pg.image.load(imageway)
    image_load = image
    icon = pg.transform.scale(pg.image.load(iconway).convert_alpha(),
                               (config.state.MenuWidth * 0.9 / 6, config.state.MenuWidth * 0.9 / 6))
class Mangroveleaves(Leaves):
    imageway = config.resource_path("files/blocks/mangrove_leaves.png")
    iconway = config.resource_path("files/icon/mangrove_leaves.png")
    image = pg.image.load(imageway)
    image_load = image
    icon = pg.transform.scale(pg.image.load(iconway).convert_alpha(),
                               (config.state.MenuWidth * 0.9 / 6, config.state.MenuWidth * 0.9 / 6))
class Azalealeaves(Leaves):
    imageway = config.resource_path("files/blocks/azalea_leaves.png")
    iconway = config.resource_path("files/icon/azalea_leaves.png")
    image = pg.image.load(imageway)
    image_load = image
    icon = pg.transform.scale(pg.image.load(iconway).convert_alpha(),
                               (config.state.MenuWidth * 0.9 / 6, config.state.MenuWidth * 0.9 / 6))
class AzaleaFloweringleaves(Leaves):
    imageway = config.resource_path("files/blocks/azalea_leaves_flowering.png")
    iconway = config.resource_path("files/icon/azalea_leaves_flowering.png")
    image = pg.image.load(imageway)
    image_load = image
    icon = pg.transform.scale(pg.image.load(iconway).convert_alpha(),
                               (config.state.MenuWidth * 0.9 / 6, config.state.MenuWidth * 0.9 / 6))
class Cherryleaves(Leaves):
    imageway = config.resource_path("files/blocks/cherry_leaves.png")
    iconway = config.resource_path("files/icon/cherry_leaves.png")
    image = pg.image.load(imageway)
    image_load = image
    icon = pg.transform.scale(pg.image.load(iconway).convert_alpha(),
                               (config.state.MenuWidth * 0.9 / 6, config.state.MenuWidth * 0.9 / 6))
class Paleoakleaves(Leaves):
    imageway = config.resource_path("files/blocks/pale_oak_leaves.png")
    iconway = config.resource_path("files/icon/pale_oak_leaves.png")
    image = pg.image.load(imageway)
    image_load = image
    icon = pg.transform.scale(pg.image.load(iconway).convert_alpha(),
                               (config.state.MenuWidth * 0.9 / 6, config.state.MenuWidth * 0.9 / 6))
class PoplarRedleaves(Leaves):
    imageway = config.resource_path("files/blocks/poplar_leaves_red.png")
    iconway = config.resource_path("files/icon/poplar_leaves_red.png")
    image = pg.image.load(imageway)
    image_load = image
    icon = pg.transform.scale(pg.image.load(iconway).convert_alpha(),
                               (config.state.MenuWidth * 0.9 / 6, config.state.MenuWidth * 0.9 / 6))
class PoplarOrangeleaves(Leaves):
    imageway = config.resource_path("files/blocks/poplar_leaves_orange.png")
    iconway = config.resource_path("files/icon/poplar_leaves_orange.png")
    image = pg.image.load(imageway)
    image_load = image
    icon = pg.transform.scale(pg.image.load(iconway).convert_alpha(),
                               (config.state.MenuWidth * 0.9 / 6, config.state.MenuWidth * 0.9 / 6))
class PoplarYellowleaves(Leaves):
    imageway = config.resource_path("files/blocks/poplar_leaves_yellow.png")
    iconway = config.resource_path("files/icon/poplar_leaves_yellow.png")
    image = pg.image.load(imageway)
    image_load = image
    icon = pg.transform.scale(pg.image.load(iconway).convert_alpha(),
                               (config.state.MenuWidth * 0.9 / 6, config.state.MenuWidth * 0.9 / 6))
class Glass(Block):
    can_powered = False
    hidden = False
    imageway = config.resource_path("files/blocks/glass.png")
    iconway = config.resource_path("files/icon/glass.png")
    image = pg.image.load(imageway)
    image_load = image
    icon = pg.transform.scale(pg.image.load(iconway).convert_alpha(),
                               (config.state.MenuWidth * 0.9 / 6, config.state.MenuWidth * 0.9 / 6))
class Dirts(Block):
    hidden = False
    pretend = False
    imageway = config.resource_path("files/blocks/dirt.png")
    iconway = config.resource_path("files/icon/dirt.png")
    image = pg.image.load(imageway)
    image_load = image
    icon = pg.transform.scale(pg.image.load(iconway).convert_alpha(),
                               (config.state.MenuWidth * 0.9 / 6, config.state.MenuWidth * 0.9 / 6))
class Dirt(Dirts):
    pass
class Mud(Dirts):
    imageway = config.resource_path("files/blocks/mud.png")
    iconway = config.resource_path("files/icon/mud.png")
    image = pg.image.load(imageway)
    image_load = image
    icon = pg.transform.scale(pg.image.load(iconway).convert_alpha(),
                               (config.state.MenuWidth * 0.9 / 6, config.state.MenuWidth * 0.9 / 6))
class Moss(Dirts):
    can_slime = False
    can_honey = False
    push_destroyed = True
    imageway = config.resource_path("files/blocks/moss.png")
    iconway = config.resource_path("files/icon/moss.png")
    image = pg.image.load(imageway)
    image_load = image
    icon = pg.transform.scale(pg.image.load(iconway).convert_alpha(),
                               (config.state.MenuWidth * 0.9 / 6, config.state.MenuWidth * 0.9 / 6))
class Obsidian(Block):
    hidden = False
    can_push = False
    can_slime = False
    can_honey = False
    imageway = config.resource_path("files/blocks/obsidian.png")
    iconway = config.resource_path("files/icon/obsidian.png")
    image = pg.image.load(imageway)
    image_load = image
    icon = pg.transform.scale(pg.image.load(iconway).convert_alpha(),
                               (config.state.MenuWidth * 0.9 / 6, config.state.MenuWidth * 0.9 / 6))
class Barrier(Block):
    hidden = True
    can_push = False
    can_slime = False
    can_honey = False
    can_rotate = False
    can_rotate_byhand = False
    imageway = config.resource_path("files/blocks/barrier.png")
    iconway = config.resource_path("files/blocks/barrier.png")
    image = pg.image.load(imageway)
    image_load = image
    icon = pg.transform.scale(pg.image.load(iconway).convert_alpha(),
                               (config.state.MenuWidth * 0.9 / 6, config.state.MenuWidth * 0.9 / 6))
class Terracotta(Block):
    hidden = False
    can_rotate = True
    can_rotate_byhand = True
    can_slime = False
    can_honey = False
    imageway = config.resource_path("files/blocks/white_glazed_terracotta.png")
    iconway = config.resource_path("files/icon/white_glazed_terracotta.png")
    image = pg.image.load(imageway)
    image_load = image
    icon = pg.transform.scale(pg.image.load(iconway).convert_alpha(),
                               (config.state.MenuWidth * 0.9 / 6, config.state.MenuWidth * 0.9 / 6))
class Redstone(Block):
    hidden = False
    has_generate = True
    imageway = config.resource_path("files/blocks/redstone.png")
    iconway = config.resource_path("files/icon/redstone.png")
    image = pg.image.load(imageway)
    image_load = image
    icon = pg.transform.scale(pg.image.load(iconway).convert_alpha(),
                               (config.state.MenuWidth * 0.9 / 6, config.state.MenuWidth * 0.9 / 6))

    def generate(self):
        if self.is_moving == 0:
            self.powered = True
class RedstoneLamp(Block):
    hidden = False
    has_function = True
    image1way = config.resource_path("files/blocks/redstone_lamp.png")
    image2way = config.resource_path("files/blocks/redstone_lamp_on.png")
    iconway = config.resource_path("files/icon/redstone_lamp.png")
    imageway = image1way
    image = pg.image.load(imageway)
    image_load = image
    icon = pg.transform.scale(pg.image.load(iconway).convert_alpha(),
                               (config.state.MenuWidth * 0.9 / 6, config.state.MenuWidth * 0.9 / 6))

    def function(self):
        if self.is_moving != 0:
            return
        if self.actived:
            if self.imageway == self.image1way:
                self.imageway = self.image2way
                self.image = pg.image.load(self.imageway)
                self.special = 1
                self.notify_neighbors()
        else:
            if self.imageway == self.image2way and not config.state.PendingTickList[
                    fun.cturncid(self.cpos)].has_pending(self):
                config.state.PendingTickList[fun.cturncid(self.cpos)].schedule(3, self, self.turn_off)

    def turn_off(self):
        if self.actived:
            return
        if self.imageway == self.image2way:
            self.imageway = self.image1way
            self.image = pg.image.load(self.imageway)
            self.special = 0
            self.notify_neighbors()
class CopperBulb(Block):
    hidden = False
    has_function = True
    image1way = config.resource_path("files/blocks/copper_bulb.png")
    image2way = config.resource_path("files/blocks/copper_bulb_on_powered.png")
    image3way = config.resource_path("files/blocks/copper_bulb_powered.png")
    image4way = config.resource_path("files/blocks/copper_bulb_on.png")
    iconway = config.resource_path("files/icon/copper_bulb.png")
    special = 0
    imageway = image1way
    image = pg.image.load(imageway)
    image_load = image
    icon = pg.transform.scale(pg.image.load(iconway).convert_alpha(),
                               (config.state.MenuWidth * 0.9 / 6, config.state.MenuWidth * 0.9 / 6))

    def function(self):
        if self.is_moving != 0:
            return
        if self.actived:
            if self.special not in (1, 2):
                q = config.state.PendingTickList[fun.cturncid(self.cpos)]
                if not q.has_pending(self):
                    q.schedule(1, self, self.change)
        else:
            if config.state.tick % 2 == 1 and self.special in (1, 2):
                self.special = 3 if self.special % 2 == 1 else 0
                self.imagechange()

    def imagechange(self):
        images = (self.image1way, self.image2way, self.image3way, self.image4way)
        self.imageway = images[self.special]
        self.image = pg.image.load(self.imageway)
        self.image_load = self.image

    def change(self):
        if self.actived:
            self.special = 1 if self.special % 2 == 0 else 2
            self.imagechange()
            self.notify_neighbors()
class Piston(Block):
    can_powered = False
    target_generate = True
    hidden = False
    has_function = True
    can_rotate = True
    can_rotate_byhand = True
    is_dynamical = False
    show_moving = False

    state = 0        # 0收回 1半推 2推出 3半收
    sticky = False   # 是否为粘性活塞
    pushlimit = config.state.PistonMax
    stacked = False
    stacked_piston_type = None

    image1way = config.resource_path("files/blocks/piston.png")
    image2way = config.resource_path("files/blocks/actived_piston.png")
    imageway = image1way
    iconway = config.resource_path("files/icon/piston.png")
    image = pg.image.load(imageway)
    image_load = image
    dual_image1 = pg.image.load(config.resource_path("files/blocks/dual_piston.png"))
    dual_image2 = pg.image.load(config.resource_path("files/blocks/dual_sticky_piston.png"))
    icon = pg.transform.scale(pg.image.load(iconway).convert_alpha(),
                               (config.state.MenuWidth * 0.9 / 6, config.state.MenuWidth * 0.9 / 6))

    def __init__(self, cpos, bpos, towards=0, mode="double", abpos=0, pushlimit=None):
        if pushlimit is None:
            pushlimit = config.state.PistonMax
        super().__init__(cpos, bpos, towards, mode, abpos)
        self.pushlimit = pushlimit
        self.movingblockposlist = []
        self.parent_abpos = None

    def draw(self):
        super().draw()
        if self.stacked and self.is_moving == 0:
            dual = self.dual_image2 if self.stacked_piston_type == StickyPiston else self.dual_image1
            scaled = pg.transform.scale(pg.transform.rotate(dual, -90 * self.towards),
                                        (config.state.BaseBlockSize / config.state.Zoom,
                                         config.state.BaseBlockSize / config.state.Zoom))
            config.state.screen.blit(scaled, fun.vturns(fun.bturnv(self.abpos)))

    @staticmethod
    def getlist(abpos, towards, mode="push", limit=None):
        if limit is None:
            limit = config.state.PistonMax
        startpos = abpos
        if type(fun.bturnblock(fun.bposmove(startpos, towards))) == PistonArm:
            armpos = fun.bposmove(startpos, towards)
        else:
            armpos = 0
        deque = dict()  # 处理黏附
        ans = set()  # 列表
        end = False
        complete = False

        # 推动搜索
        def searchpush(pos, towards):
            nonlocal end
            posx = pos
            while True:
                # 检查自身活塞臂
                if fun.bturnblock(posx).push_destroyed and fun.bturnblock(posx).can_push == False and posx == armpos:
                    end = True
                    return
                # 检查是否可推动
                if fun.bturnblock(posx).can_push == False or fun.bturnblock(posx).is_moving != 0 or posx == startpos:
                    end = True
                    return
                # 检查是否可推坏
                if fun.bturnblock(posx).push_destroyed:
                    break
                else:
                    ans.add(tuple(posx))
                posx = fun.bposmove(posx, towards)
            # 检查是否到达上限
            if len(ans) > limit:
                end = True
                return
            # 更新黏附表
            posx = pos
            while True:
                if fun.bturnblock(posx).push_destroyed:
                    break
                if type(fun.bturnblock(posx)) == Slime:
                    for tow in range(4):
                        if fun.bturnblock(fun.bposmove(posx, tow)).can_slime and fun.bturnblock(
                                fun.bposmove(posx, tow)).is_moving == 0 and fun.bposmove(posx, tow) != startpos and not (
                        tuple(fun.bposmove(posx, tow)) in ans):
                            deque[tuple((fun.bposmove(posx, tow)))] = False
                if type(fun.bturnblock(posx)) == Honey:
                    for tow in range(4):
                        if fun.bturnblock(fun.bposmove(posx, tow)).can_honey and fun.bturnblock(
                                fun.bposmove(posx, tow)).is_moving == 0 and fun.bposmove(posx, tow) != startpos and not (
                        tuple(fun.bposmove(posx, tow)) in ans):
                            deque[tuple((fun.bposmove(posx, tow)))] = False
                posx = fun.bposmove(posx, towards)
        # 拉动搜索
        def searchpull(pos, towards):
            nonlocal end
            posx = pos
            btype = type(fun.bturnblock(pos))
            dequelist = []
            if btype == Slime:
                while True:
                    if not fun.bturnblock(posx).can_slime or fun.bturnblock(posx).is_moving != 0 or posx == startpos:
                        break
                    if fun.bturnblock(posx).can_slime and fun.bturnblock(
                            posx).is_moving == 0 and posx != startpos and type(fun.bturnblock(posx)) != Slime:
                        ans.add(tuple(posx))
                        break
                    if type(fun.bturnblock(posx)) == Slime and fun.bturnblock(posx).is_moving == 0:
                        ans.add(tuple(posx))
                        dequelist.append(posx)
                        posx = fun.bposmove(posx, fun.reverse(towards))
                        continue
                for poss in dequelist:
                    for tow in range(4):
                        if fun.bturnblock(fun.bposmove(poss, tow)).can_slime and fun.bturnblock(
                                fun.bposmove(poss, tow)).is_moving == 0 and fun.bposmove(poss, tow) != startpos and not (
                        tuple(fun.bposmove(poss, tow)) in ans):
                            deque[tuple((fun.bposmove(poss, tow)))] = False
            elif btype == Honey:
                while True:
                    if not fun.bturnblock(posx).can_honey or fun.bturnblock(posx).is_moving != 0 or posx == startpos:
                        break
                    if fun.bturnblock(posx).can_honey and fun.bturnblock(
                            posx).is_moving == 0 and posx != startpos and type(fun.bturnblock(posx)) != Honey:
                        ans.add(tuple(posx))
                        break
                    if type(fun.bturnblock(posx)) == Honey and fun.bturnblock(posx).is_moving == 0:
                        ans.add(tuple(posx))
                        dequelist.append(posx)
                        posx = fun.bposmove(posx, fun.reverse(towards))
                        continue
                for poss in dequelist:
                    for tow in range(4):
                        if fun.bturnblock(fun.bposmove(poss, tow)).can_honey and fun.bturnblock(
                                fun.bposmove(poss, tow)).is_moving == 0 and fun.bposmove(poss, tow) != startpos and not (
                        tuple(fun.bposmove(poss, tow)) in ans):
                            deque[tuple((fun.bposmove(poss, tow)))] = False
            else:
                if (fun.bturnblock(posx).can_slime or fun.bturnblock(posx).can_honey) and fun.bturnblock(
                        posx).is_moving == 0 and posx != startpos:
                    ans.add(tuple(posx))

        match mode:
            case "push":
                searchpush(fun.bposmove(startpos, towards), towards)
                if len(ans) > limit:
                    return 0
                while True:
                    if len(ans) > limit:
                        return 0
                    if end:
                        return 0
                    if len(deque) > 0:
                        if all(deque.values()):
                            complete = True
                    else:
                        complete = True
                    if complete:
                        return list(ans)
                    else:
                        for slimepos in deque.copy():
                            if type(fun.bturnblock(list(slimepos))) == Slime or Honey:
                                searchpull(list(slimepos), towards)
                                searchpush(list(slimepos), towards)
                                deque[slimepos] = True
            case "pull":
                searchpull(fun.bposmove(startpos, towards, 2), fun.reverse(towards))
                if len(ans) > limit:
                    return 0
                while True:
                    if len(ans) > limit:
                        return 0
                    if end:
                        return 0
                    if len(deque) > 0:
                        if all(deque.values()):
                            complete = True
                    else:
                        complete = True
                    if complete:
                        return list(ans)
                    else:
                        for slimepos in deque.copy():
                            if type(fun.bturnblock(list(slimepos))) == Slime or Honey:
                                searchpull(list(slimepos), fun.reverse(towards))
                                searchpush(list(slimepos), fun.reverse(towards))
                                deque[slimepos] = True
                    if end:
                        return 0
                    if complete:
                        return list(ans)
        return []

    def function(self):
        if config.state.tick % 2 != 1:
            return
        old = self.state
        S = self.actived
        if old == 0:
            new = 1 if S else 0
        elif old == 1:
            new = 2
        elif old == 2:
            new = 3 if not S else 2
        else:  # old == 3
            new = 0
        self.state = new
        if new != old:
            self._transition(old, new)

    def _transition(self, old, new):
        if old == 0 and new == 1:
            self._extend()
        elif old == 1 and new == 2:
            self._settle()      # 推出完成：取消 MB
        elif old == 2 and new == 3:
            self._retract()
        elif old == 3 and new == 0:
            self._settle()      # 收回完成：取消 MB

    def _settle(self):
        for blk in self.movingblockposlist:
            blk.is_moving = 0
        self.movingblockposlist.clear()
        if self.state == 0:
            self.can_push = True
            self.can_slime = True
            self.can_honey = True
            self.can_rotate_byhand = True

    def _extend(self):
        limit = self.pushlimit - 2 if self.stacked else self.pushlimit
        blocklist = self.getlist(self.abpos, self.towards, "push", limit)
        if blocklist != 0:
            self.imageway = self.image2way
            self.image = pg.image.load(self.imageway)
            self.can_push = False
            self.can_slime = False
            self.can_honey = False
            self.can_rotate_byhand = False
            self.special = 1
            if len(blocklist) > 0:
                movedblocklist = dict()
                for pos in blocklist:
                    movedblocklist[tuple(fun.bposmove(pos, self.towards))] = fun.bturnblock(pos)
                    movedblocklist[tuple(fun.bposmove(pos, self.towards))].update(
                        list(fun.bposmove(pos, self.towards)))
                for pos in blocklist:
                    config.state.ChunkList[fun.bturnid(list(pos))[0]][fun.bturnid(list(pos))[1]] = Air(0, 0, self.towards,
                                                                                             "single", pos)
                    effects.create_fade(fun.bposmove(pos, self.towards), (255, 255, 255), 150)
                    fun.bturnblock(list(pos)).notify_neighbors()
                for pos in movedblocklist:
                    config.state.ChunkList[fun.bturnid(list(pos))[0]][fun.bturnid(list(pos))[1]] = movedblocklist[pos]
                    self.movingblockposlist.append(fun.bturnblock(pos))
                    config.state.ChunkList[fun.bturnid(list(pos))[0]][fun.bturnid(list(pos))[1]].notify_neighbors()
                for blk in self.movingblockposlist:
                    blk.is_moving = 1
                    blk.bemoved()
            armpos = fun.bposmove(self.abpos, self.towards)
            has_slime_or_honey = len(blocklist) > 0 and any(type(blk) in (Slime, Honey) for blk in movedblocklist.values())
            if self.stacked and self.stacked_piston_type is not None and has_slime_or_honey:
                child = self.stacked_piston_type(0, 0, self.towards, "single", armpos,
                                                 pushlimit=self.pushlimit - 1)
                child.stacked = False
                child.parent_abpos = self.abpos
                config.state.ChunkList[fun.bturnid(armpos)[0]][fun.bturnid(armpos)[1]] = child
                fun.bturnblock(armpos).notify_neighbors()
                child.actived = True
                self.movingblockposlist.append(child)
            else:
                config.state.ChunkList[fun.bturnid(armpos)[0]][fun.bturnid(armpos)[1]] \
                    = PistonArm(0, 0, self.towards, "single", armpos)
                fun.bturnblock(armpos).notify_neighbors()
                armblk = config.state.ChunkList[fun.bturnid(armpos)[0]][fun.bturnid(armpos)[1]]
                armblk.imageway = armblk.image2way if self.sticky else armblk.image1way
                armblk.image = pg.image.load(armblk.imageway)
        else:
            self.movingblockposlist.clear()

    def _retract(self):
        self.imageway = self.image1way
        self.image = pg.image.load(self.imageway)
        self.special = 0
        config.state.ChunkList[fun.bturnid(fun.bposmove(self.abpos, self.towards))[0]][
            fun.bturnid(fun.bposmove(self.abpos, self.towards))[1]] = \
            Air(0, 0, self.towards, "single", fun.bposmove(self.abpos, self.towards))
        fun.bturnblock(fun.bposmove(self.abpos, self.towards)).notify_neighbors()
        if self.sticky:
            self._pull_blocks()

    def _pull_blocks(self):
        pass

    def remove(self):
        if self.state != 0:
            config.state.ChunkList[fun.bturnid(self.abpos, 1, self.towards)[0]][
                fun.bturnid(self.abpos, 1, self.towards)[1]] = Air(0, 0, self.towards, "single",
                                                                fun.bposmove(self.abpos, self.towards))
            fun.bturnblock(fun.bposmove(self.abpos, self.towards)).notify_neighbors()
        if self.parent_abpos is not None:
            parent_block = fun.bturnblock(self.parent_abpos)
            if type(parent_block) != Air:
                parent_block.remove()
        super().remove()
class NormalPiston(Piston):
    pass
class StickyPiston(Piston):
    image1way = config.resource_path("files/blocks/sticky_piston.png")
    image2way = config.resource_path("files/blocks/actived_sticky_piston.png")
    imageway = image1way
    iconway = config.resource_path("files/icon/sticky_piston.png")
    image = pg.image.load(imageway)
    image_load = image
    icon = pg.transform.scale(pg.image.load(iconway).convert_alpha(),
                               (config.state.MenuWidth * 0.9 / 6, config.state.MenuWidth * 0.9 / 6))
    sticky = True

    def _pull_blocks(self):
        blocklist = self.getlist(self.abpos, self.towards, "pull")
        if blocklist != 0:
            if len(blocklist) > 0:
                movedblocklist = dict()
                for pos in blocklist:
                    movedblocklist[tuple(fun.bposmove(pos, fun.reverse(self.towards)))] = fun.bturnblock(pos)
                    movedblocklist[tuple(fun.bposmove(pos, fun.reverse(self.towards)))].update(
                        list(fun.bposmove(pos, fun.reverse(self.towards))))
                for pos in blocklist:
                    config.state.ChunkList[fun.bturnid(list(pos))[0]][fun.bturnid(list(pos))[1]] = Air(0, 0, 0, "single", pos)
                    effects.create_fade(fun.bposmove(pos, fun.reverse(self.towards)), (255, 255, 255), 150)
                    fun.bturnblock(list(pos)).notify_neighbors()
                for pos in movedblocklist:
                    config.state.ChunkList[fun.bturnid(list(pos))[0]][fun.bturnid(list(pos))[1]] = movedblocklist[pos]
                    self.movingblockposlist.append(fun.bturnblock(pos))
                    config.state.ChunkList[fun.bturnid(list(pos))[0]][fun.bturnid(list(pos))[1]].notify_neighbors()
                for blk in self.movingblockposlist:
                    blk.is_moving = 1
                    blk.bemoved()
        else:
            self.movingblockposlist.clear()

class PistonArm(Block):
    can_push = False
    push_destroyed = True
    can_slime = False
    can_honey = False
    can_rotate = True
    show_moving = False

    image1way = config.resource_path("files/blocks/piston_arm.png")
    image2way = config.resource_path("files/blocks/sticky_piston_arm.png")
    imageway = image1way
    iconway = config.resource_path("files/blocks/piston_arm.png")
    image = pg.image.load(imageway)
    image_load = image
    icon = pg.transform.scale(pg.image.load(iconway).convert_alpha(),
                               (config.state.MenuWidth * 0.9 / 6, config.state.MenuWidth * 0.9 / 6))

    def remove(self):
        config.state.ChunkList[fun.bturnid(self.abpos, 1, fun.reverse(self.towards))[0]][
            fun.bturnid(self.abpos, 1, fun.reverse(self.towards))[1]].remove()
class Slime(Block):
    hidden = False
    can_honey = False

    imageway = config.resource_path("files/blocks/slime.png")
    iconway = config.resource_path("files/icon/slime.png")
    image = pg.image.load(imageway)
    image_load = image
    icon = pg.transform.scale(pg.image.load(iconway).convert_alpha(),
                               (config.state.MenuWidth * 0.9 / 6, config.state.MenuWidth * 0.9 / 6))
class Honey(Block):
    hidden = False
    can_slime = False

    imageway = config.resource_path("files/blocks/honey.png")
    iconway = config.resource_path("files/icon/honey.png")
    image = pg.image.load(imageway)
    image_load = image
    icon = pg.transform.scale(pg.image.load(iconway).convert_alpha(),
                               (config.state.MenuWidth * 0.9 / 6, config.state.MenuWidth * 0.9 / 6))
class Obsever(Block):
    can_powered = False
    hidden = False
    has_generate = True
    can_rotate = True
    can_rotate_byhand = True

    def __init__(self, cpos, bpos, towards=0, mode="double", abpos=0):
        super().__init__(cpos, bpos, towards, mode, abpos)
        self.state = 0

    image1way = config.resource_path("files/blocks/observer.png")
    image2way = config.resource_path("files/blocks/actived_observer.png")
    imageway = image1way
    iconway = config.resource_path("files/icon/observer.png")
    image = pg.image.load(imageway)
    image_load = image
    icon = pg.transform.scale(pg.image.load(iconway).convert_alpha(),
                               (config.state.MenuWidth * 0.9 / 6, config.state.MenuWidth * 0.9 / 6))

    def _set_state(self, newstate):
        if newstate == self.state:
            return
        self.state = newstate
        self.imageway = self.image2way if newstate == 1 else self.image1way
        self.image = pg.image.load(self.imageway)
        self.notify_neighbors()

    def _q(self):
        return config.state.PendingTickList[fun.cturncid(self.cpos)]

    def _maybe_schedule(self, delay, cb, strict=True):

        if not self._q().has_pending(self, strict):
            self._q().schedule(delay, self, cb)

    def neighborchanged(self, towards):
        if self.is_moving != 0:
            return
        self._maybe_schedule(2, self._on_update)

    def _on_update(self):
        if config.state.tick % 2 != 1:
            self._maybe_schedule(1, self._on_update, strict=False)
            return
        self._set_state(1)          # 亮起
        self._maybe_schedule(2, self._turn_off, strict=False)

    def _turn_off(self):
        if config.state.tick % 2 != 1:
            self._maybe_schedule(1, self._turn_off, strict=False)
            return
        self._set_state(0)

    def generate(self):
        if self.is_moving != 0 or self.state == 0:
            return
        front = fun.bturnblock(fun.bposmove(self.abpos, self.towards))
        if front.can_powered:
            front.powered = True
        elif front.has_function:
            front.actived = True

    def bemoved(self):
        self._q().cancel(self)
        self.state = 0
        self.imageway = self.image1way
        self.image = pg.image.load(self.imageway)
        self._maybe_schedule(2, self._on_update)
class Void(Block):
    pass

# 方块列表初始化
Blockclass = fun.subclass(Block)
for blk in Blockclass:
    if len(fun.subclass(blk)) != 0:
        blk.sub = fun.subclass(blk)
Trigger = Void
Towards = 0