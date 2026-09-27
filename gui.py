import copy
import pygame as pg
import types
import simulation
import config
import functions as fun

class KeyBinding:
    def __init__(self, key, action, repeat_protect=True):
        self.key = key
        self.action = action
        self.repeat_protect = repeat_protect
        self.pressed = False

class Button:
    # 空间
    pos = [0, 0]
    size = [0, 0]
    # 图像
    image = 0
    image_selected = 0
    image_disabled = 0
    # 状态
    is_selected = False
    is_shift_selected = False
    box = pg.Rect(pos[0],pos[1],size[0],size[1])
    # 函数
    def __init__(self,pos,size=(0,0)):
        self.pos = pos
        self.size = size
        self.box = pg.Rect(pos[0], pos[1], size[0], size[1])
        self.image = pg.transform.smoothscale(pg.image.load(config.resource_path("files/gui/button.png")).convert_alpha(), self.size)
        self.image_selected = pg.transform.smoothscale(pg.image.load(config.resource_path("files/gui/button_selected.png")).convert_alpha(),
                                                       self.size)
        self.image_disabled = pg.transform.smoothscale(pg.image.load(config.resource_path("files/gui/button_disabled.png")).convert_alpha(),
                                                       self.size)
        self.function = lambda: None
    def draw(self,window):
        if self.is_selected:
            window.blit(self.image_selected,self.box)
        else:
            window.blit(self.image,self.box)
    def check(self,mpos):
        if self.box.collidepoint(mpos):
            self.is_selected = True
        else:
            self.is_selected = False
    def check_shift(self,mpos):
        pass
    def execute(self):
        pass

class GUIButton(Button):
    fathergui = None
    icon = 0

    def __init__(self, pos, gui, size=(0, 0)):
        super().__init__(pos, size)
        self.fathergui = gui
        gui.guibuttonlist.append(self)
    def draw(self,window):
        if self.fathergui.active == True:
            if self.is_selected:
                window.blit(self.image_selected,self.box)
            else:
                window.blit(self.image,self.box)
            if self.icon != 0:
                window.blit(self.icon,[self.pos[0]+self.size[0]*0.02,self.pos[1]-self.size[1]*0.01])
class ExitButton(GUIButton):
    def __init__(self, pos, gui, size=(0, 0)):
        super().__init__(pos,gui,size)
        self.icon = pg.transform.smoothscale(pg.image.load(config.resource_path("files/gui/cancel.png")).convert_alpha(),self.size)
    def execute(self):
        self.fathergui.active = False
        if isinstance(self.fathergui, ZoneGUI):
            ZoneGUI.resetguis(config.state.ZoneGUIList)
class TextInButton(GUIButton):
    def __init__(self, pos, gui, size=(0, 0),maxlength = 10,fontcolor="white"):
        super().__init__(pos,gui,size)
        self.maxlength = maxlength
        self.image = pg.transform.smoothscale(pg.image.load(config.resource_path("files/gui/text.png")).convert_alpha(), self.size)
        self.image_selected = pg.transform.smoothscale(pg.image.load(config.resource_path("files/gui/text_selected.png")).convert_alpha(),self.size)
        self.textin = ""
        self.textsaved = ""
        self.font = pg.font.Font(config.resource_path("files/font/Pixel AE.ttf"),int(self.size[1]*0.6))
        self.fontcolor = fontcolor
        self.fathergui.textbuttonlist.append(self)
    def draw(self,window):
        super().draw(window)
        if self.fathergui.active == True:
            text = self.font.render(self.textin,True,self.fontcolor)
            window.blit(text,[self.pos[0]+self.size[0]*0.02,self.pos[1]+self.size[1]*0.2])
    def check(self,mpos):
        if self.box.collidepoint(mpos):
            # 取消所有GUI中其他输入框的选中状态
            for gui in config.state.GUIList:
                for tb in getattr(gui, 'textbuttonlist', []):
                    if tb is not self and tb.is_selected:
                        tb.textsaved = tb.textin
                        tb.fontcolor = "Grey"
                        tb.is_selected = False
            self.fontcolor = "white"
            self.is_selected = True
        else:
            self.textsaved = self.textin
            self.fontcolor = "Grey"
            self.is_selected = False
    def execute(self):
        pass
    def event_handle(self,events):
        if self.fathergui.active and self.is_selected:
            if events.type == pg.KEYDOWN:
                if events.key == pg.K_BACKSPACE:
                    self.textin = self.textin[:-1]
                elif events.key == pg.K_RETURN:
                    self.textsaved = self.textin
                    # 只退出编辑状态，保留 confirm 计算出的校验色（合法绿/非法红），不置灰
                    self.is_selected = False
                else:
                    inputkey = events.unicode
                    if len(self.textin) < self.maxlength and (inputkey == ' ' or inputkey == '-' or inputkey.isdigit()):
                        self.textin += inputkey
class TextButton(GUIButton):
    def __init__(self, pos, gui, size, text="", fontcolor="white"):
        super().__init__(pos, gui, size)
        self.label = text
        self.font = pg.font.Font(config.resource_path("files/font/Pixel AE.ttf"), int(self.size[1] * 0.5))
        self.fontcolor = fontcolor

    def draw(self, window):
        if self.fathergui.active == True:
            if self.is_selected:
                window.blit(self.image_selected, self.box)
            else:
                window.blit(self.image, self.box)
            if self.label:
                surf = self.font.render(self.label, True, self.fontcolor)
                tx = self.pos[0] + (self.size[0] - surf.get_width()) / 2
                ty = self.pos[1] + (self.size[1] - surf.get_height()) / 2
                window.blit(surf, [tx, ty])
class ShowButton(GUIButton):
    def draw(self, window):
        if self.fathergui.active == True:
            if self.icon != 0:
                window.blit(self.icon, [self.pos[0] + self.size[0] * 0.02, self.pos[1] - self.size[1] * 0.01])
class TextShow(GUIButton):
    def __init__(self, pos, gui, size=(0, 0),fontcolor="white"):
        super().__init__(pos, gui, size)
        self.textshow = ""
        self.font = pg.font.Font(config.resource_path("files/font/Pixel AE.ttf"), int(self.size[1] * 0.6))
        self.fontcolor = fontcolor
    def draw(self,window):
        if self.fathergui.active == True:
            text = self.font.render(self.textshow,True,self.fontcolor)
            window.blit(text,[self.pos[0]+self.size[0]*0.01,self.pos[1]+self.size[1]*0.2])
class SwichButton(GUIButton):
    def __init__(self, pos, gui, size=(0, 0),fontcolor="white"):
        super().__init__(pos, gui, size)
        self.font = pg.font.Font(config.resource_path("files/font/Pixel AE.ttf"), int(self.size[1] * 0.6))
        self.fontcolor = fontcolor
        self.locate = 1
        self.dict = {1:""}
    def draw(self,window):
        if self.fathergui.active == True:
            if self.is_selected:
                window.blit(self.image_selected,self.box)
            else:
                window.blit(self.image,self.box)
            if self.icon != 0:
                window.blit(self.icon,[self.pos[0]+self.size[0]*0.02,self.pos[1]-self.size[1]*0.01])
            text = self.font.render(self.dict[self.locate], True, self.fontcolor)
            window.blit(text, [self.pos[0] + self.size[0] * 0.15, self.pos[1] + self.size[1] * 0.2])
    def execute(self):
        if self.fathergui.active == True:
            if self.locate < len(self.dict):
                self.locate += 1
            else:
                self.locate = min(self.dict)

class BlockChoose(Button):
    # 目标
    target = None
    # 图像
    icon = None
    # 状态
    has_sub = False
    subbuttonlist = []
    is_selecting = False
    # 函数
    def __init__(self,pos,target):
        super().__init__(pos,size=[config.state.MenuWidth/6 ,config.state.MenuWidth/6])
        self.target = target
        if target.icon is not None:
            self.icon = target.icon
        if len(target.sub) != 0:
            self.has_sub = True
    def draw(self,window):
        if self.is_selecting == True:
            window.blit(self.image_disabled,self.box)
        elif self.is_selected == True:
            window.blit(self.image_selected,self.box)
        else:
            window.blit(self.image,self.box)
        window.blit(self.target.icon,(self.box.left+config.state.MenuWidth*0.05/6,self.box.top+config.state.MenuWidth*0.05/6))
        if hasattr(self.target, 'badge') and self.target.badge is not None:
            b = self.target.badge
            window.blit(b, (self.box.right - b.get_width() - 2, self.box.bottom - b.get_height() - 2))
    def check(self, mpos):
        if self.has_sub == False:
            if self.box.collidepoint(mpos) == True:
                self.is_selected = True
                hassubbuttonlist = [butss for butss in config.state.buttonlist if getattr(butss, 'has_sub', False) == True]
                for butss in hassubbuttonlist:
                    butss.is_selecting = False
            else:
                self.is_selected = False
        else:
            if self.box.collidepoint(mpos) == True:
                self.is_selecting = not self.is_selecting
                self.is_selected = True
                hassubbuttonlist = [butss for butss in config.state.buttonlist if getattr(butss, 'has_sub', False) == True]
                for butss in hassubbuttonlist:
                    if butss.is_selecting == True and butss != self:
                        butss.is_selecting = False
            else:
                self.is_selected = False
    def execute(self):
        config.state.Trigger = self.target
        config.state.icrosshair = update_crosshair(config.state.Trigger)
class SubBlockChoose(BlockChoose):
    fatherbutton = None
    def __init__(self,pos,target,fatherbutton):
        super().__init__(pos,target)
        self.pos = pos
        self.target = target
        self.fatherbutton = fatherbutton
    def check(self,mpos):
        if self.box.collidepoint(mpos) == True:

            self.is_selected = True
        else:
            self.is_selected = False
    def execute(self):
        config.state.Trigger = self.target
        self.fatherbutton.target = self.target
        self.fatherbutton.icon = self.icon
        config.state.icrosshair = update_crosshair(config.state.Trigger)

class Functional(Button):
    icon = 0
    icon_normal = 0
    icon_shift = 0
    def __init__(self,pos,size):
        super().__init__(pos,size)
    def draw(self,window):
        if self.is_selected or self.is_shift_selected:
            window.blit(self.image_selected,self.box)
        else:
            window.blit(self.image,self.box)
        window.blit(self.icon, (self.box.left + config.state.MenuWidth * 0.05 / 6, self.box.top + config.state.MenuWidth * 0.05 / 6))
    def check(self,mpos):
        super().check(mpos)
    def check_shift(self,mpos):
        if self.box.collidepoint(mpos):
            self.is_shift_selected = True
        else:
            self.is_shift_selected = False
    def execute(self):
        pass
    def execute_shift(self):
        pass
class Start(Functional):
    icon = 0
    icon_normal = 0
    icon_shift = 0
    icon_pause = 0
    icon_reset = 0
    icon_redplan = 0
    ticktext = None
    text = None

    save = []
    zonesave = []

    def __init__(self, pos, size):
        super().__init__(pos, size)
        self.icon_normal = pg.transform.scale(pg.image.load(config.resource_path("files/gui/run.png")).convert_alpha(),
                                           (config.state.MenuWidth * 1.2 / 6, config.state.MenuWidth * 1.2 / 6))
        self.icon_shift = pg.transform.scale(pg.image.load(config.resource_path("files/gui/runonce.png")).convert_alpha(),
                                               (config.state.MenuWidth * 1.2 / 6, config.state.MenuWidth * 1.2 / 6))
        self.icon_pause = pg.transform.scale(pg.image.load(config.resource_path("files/gui/pause.png")).convert_alpha(),
                                             (config.state.MenuWidth * 1.2 / 6, config.state.MenuWidth * 1.2 / 6))
        self.icon_reset = pg.transform.scale(pg.image.load(config.resource_path("files/gui/reset.png")).convert_alpha(),
                                             (config.state.MenuWidth * 1.2 / 6, config.state.MenuWidth * 1.2 / 6))
        self.icon_redplan = pg.transform.scale(pg.image.load(config.resource_path("files/icon/redplan.png")).convert_alpha(),
                                               (config.state.MenuWidth * 0.45 / 6, config.state.MenuWidth * 0.45 / 6))
        import blocks
        self.save = [[blocks.Air(fun.cidturnc(c), fun.bidturnub(b)) for b in range(config.state.SubChunkSize * config.state.SubChunkSize)] for c in
                     range(config.state.ChunkSize * config.state.ChunkSize)]
        self.icon = self.icon_normal
    def draw(self, window):
        if self.is_selected or self.is_shift_selected:
            window.blit(self.image_selected, self.box)
        else:
            window.blit(self.image, self.box)
        window.blit(self.icon, (self.box.left - config.state.MenuWidth * 0.05 / 6, self.box.top - config.state.MenuWidth * 0.1 / 6))
        self.ticktext = config.state.Text.render("tick : %d" % config.state.tick, False, "Grey", )
        window.blit(self.ticktext, (self.box.left + config.state.MenuWidth * 1 / 6, self.box.top + config.state.MenuWidth * 0.55 / 6))
        # 状态文本
        if config.state.simulating:
            label = "重置" if config.state.shiftdown else "暂停"
        else:
            label = "步进" if config.state.shiftdown else "启动"
        self.text = config.state.Text.render(label, False, "Grey", )
        window.blit(self.text,
                    (self.box.left + config.state.MenuWidth * 1 / 6, self.box.top + config.state.MenuWidth * 0.14 / 6))
        if config.state.tick % 2 == 1:
            window.blit(self.icon_redplan, (self.box.left + config.state.MenuWidth * 1 / 6 + self.text.get_width()
                                            + config.state.MenuWidth * 0.08 / 6,
                                            self.box.top + config.state.MenuWidth * 0.08 / 6))
    def execute(self):
        import blocks
        config.state.Trigger = blocks.Void
        config.state.icrosshair = config.state.crosshair
        if config.state.simulating == False:
            config.state.simulating = True
            if config.state.tick == 0:
                self.save = copy.deepcopy(config.state.ChunkList)
                self.zonesave = copy.deepcopy(config.state.ZoneList)
            self.icon = self.icon_pause
        else:
            config.state.simulating = False
            self.icon = self.icon_normal
    def execute_shift(self):
        import blocks
        config.state.Trigger = blocks.Void
        config.state.icrosshair = config.state.crosshair
        if config.state.simulating == False:
            if config.state.tick == 0:
                self.save = copy.deepcopy(config.state.ChunkList)
                self.zonesave = copy.deepcopy(config.state.ZoneList)
            simulation.runonce()
        else:
            config.state.simulating = False
            # 回溯到 tick=0 时保留当前视角（reset_world 会重置 Vpos，故先备份再恢复）
            old_vpos = list(config.state.Vpos)
            config.state.tick = 0
            fun.reset_world()
            config.state.ChunkList = copy.deepcopy(self.save)
            config.state.ZoneList = copy.deepcopy(self.zonesave)
            config.state.Vpos = old_vpos
            Vmax = config.state.Vsize
            config.state.Vpos[0] = max(0, min(config.state.Vpos[0], Vmax))
            config.state.Vpos[1] = max(0, min(config.state.Vpos[1], Vmax))
            self.icon = self.icon_normal
class Save(Functional):
    icon = 0
    id = 0
    icon_normal = 0
    icon_shift = 0
    icon_number = 0

    save = []
    zonesave = []

    def __init__(self, pos, size,ID):
        super().__init__(pos, size)
        self.id = ID
        self.icon_normal = pg.transform.scale(pg.image.load(config.resource_path("files/gui/save.png")).convert_alpha(),
                                            (config.state.MenuWidth * 0.9 / 6, config.state.MenuWidth * 0.9 / 6))
        self.icon_shift = pg.transform.scale(pg.image.load(config.resource_path("files/gui/load.png")).convert_alpha(),
                                            (config.state.MenuWidth * 0.9 / 6, config.state.MenuWidth * 0.9 / 6))
        import blocks
        self.save = [[blocks.Air(fun.cidturnc(c), fun.bidturnub(b)) for b in range(config.state.SubChunkSize * config.state.SubChunkSize)] for c in
             range(config.state.ChunkSize * config.state.ChunkSize)]
        self.zonesave = [[[] for b in range(config.state.SubChunkSize * config.state.SubChunkSize)] for c in
                        range(config.state.ChunkSize * config.state.ChunkSize)]
        match self.id:
            case 0:
                self.icon_number = pg.transform.scale(pg.image.load(config.resource_path("files/gui/token_1.png")).convert_alpha(),
                                                    (config.state.MenuWidth * 0.9 / 9, config.state.MenuWidth * 0.9 / 9))
            case 1:
                self.icon_number = pg.transform.scale(pg.image.load(config.resource_path("files/gui/token_2.png")).convert_alpha(),
                                                    (config.state.MenuWidth * 0.9 / 9, config.state.MenuWidth * 0.9 / 9))
            case 2:
                self.icon_number = pg.transform.scale(pg.image.load(config.resource_path("files/gui/token_3.png")).convert_alpha(),
                                                    (config.state.MenuWidth * 0.9 / 9, config.state.MenuWidth * 0.9 / 9))
        self.icon = self.icon_normal
    def draw(self, window):
        if config.state.simulating == True:
            window.blit(self.image_disabled, self.box)
        elif self.is_selected or self.is_shift_selected:
            window.blit(self.image_selected, self.box)
        else:
            window.blit(self.image, self.box)
        window.blit(self.icon, (self.box.left + config.state.MenuWidth * 0.05 / 6, self.box.top + config.state.MenuWidth * 0.05 / 6))
        window.blit(self.icon_number, (self.box.left + config.state.MenuWidth * 0.4 / 6, self.box.top + config.state.MenuWidth * 0.45 / 6))
    def execute(self):
        if config.state.simulating == False:
            slot = self.id + 1
            btn = self
            def do_save():
                btn.save = copy.deepcopy(config.state.ChunkList)
                btn.zonesave = copy.deepcopy(config.state.ZoneList)
            show_popup("保存?", do_save, f"存档{slot}将被覆盖")
    def execute_shift(self):
        if config.state.simulating == False:
            slot = self.id + 1
            btn = self
            def do_load():
                saved_size = int(len(btn.save) ** 0.5)
                # 备份视角，载入后保留；若新地图变小导致视角越界则限制到边界
                old_vpos = list(config.state.Vpos)
                if saved_size != config.state.ChunkSize:
                    fun.reset_world(saved_size)
                config.state.ChunkList = copy.deepcopy(btn.save)
                config.state.ZoneList = copy.deepcopy(btn.zonesave)
                # 恢复视角并做边界限制（0 ≤ Vpos ≤ Vsize）
                config.state.Vpos = old_vpos
                Vmax = config.state.Vsize
                config.state.Vpos[0] = max(0, min(config.state.Vpos[0], Vmax))
                config.state.Vpos[1] = max(0, min(config.state.Vpos[1], Vmax))
            show_popup(f"读取存档{slot}?", do_load, "你目前的工作将会丢失")
class Setting(Functional):
    def __init__(self, pos, size):
        super().__init__(pos, size)
        self.icon_img = pg.transform.scale(
            pg.image.load(config.resource_path("files/gui/setting.png")).convert_alpha(),
            (config.state.MenuWidth * 0.9 / 6, config.state.MenuWidth * 0.9 / 6))

    def draw(self, window):
        if self.is_selected or self.is_shift_selected:
            window.blit(self.image_selected, self.box)
        else:
            window.blit(self.image, self.box)
        window.blit(self.icon_img, (self.box.left + config.state.MenuWidth * 0.05 / 6,
                                     self.box.top + config.state.MenuWidth * 0.05 / 6))

    def execute(self):
        # 预填当前数值
        settingsgui.chunksize_textin.textin = str(config.state.ChunkSize)
        settingsgui.chunksize_textin.textsaved = str(config.state.ChunkSize)
        settingsgui.chunksize_textin.fontcolor = "white"
        settingsgui.speed_textin.textin = str(config.state.Oneticktime)
        settingsgui.speed_textin.textsaved = str(config.state.Oneticktime)
        settingsgui.speed_textin.fontcolor = "white"
        settingsgui.bg_switch.locate = 1 if config.state.show_background else 2
        settingsgui.active = True


def update_crosshair(trigger, towards=None):
    base = pg.transform.smoothscale(trigger.icon, (30, 30))
    # 方向角标
    if towards is not None:
        arrows = {1: "→", 2: "↓", 3: "←"}
        arrow = arrows.get(towards, "↑")
        font = pg.font.Font(config.resource_path("files/font/Pixel AE.ttf"), 28)
        ab = font.render(arrow, True, "black")
        canvas = pg.Surface((max(30, 30 - ab.get_width() + 5 + ab.get_width()),
                             max(30, 30 - ab.get_height() + 15 + ab.get_height())), pg.SRCALPHA)
        canvas.blit(base, (0, 0))
        canvas.blit(ab, (30 - ab.get_width() + 5, 30 - ab.get_height() + 15))
        return canvas
    # M 角标
    if hasattr(trigger, 'badge') and trigger.badge is not None:
        b = trigger.badge
        scale = 12 / max(b.get_width(), b.get_height())
        bs = pg.transform.smoothscale(b, (int(b.get_width() * scale), int(b.get_height() * scale)))
        canvas = pg.Surface((max(30, 30 - bs.get_width() + 5 + bs.get_width()),
                             max(30, 30 - bs.get_height() + 5 + bs.get_height())), pg.SRCALPHA)
        canvas.blit(base, (0, 0))
        canvas.blit(bs, (30 - bs.get_width() + 5, 30 - bs.get_height() + 5))
        return canvas
    return base

# 以类列表创建按钮
def gen_blockchoose(classlist,startpos,fatherbutton=0):
    startposv = [startpos[0],startpos[1]]
    step = 0
    lst = []
    for cls in classlist:
        if cls.hidden == False:
            if step % 6 != 0 and step != 0:
                startposv[0] = startposv[0] + config.state.MenuWidth/6+2
            elif step != 0:
                startposv[0] = startpos[0]
                startposv[1] = startposv[1] + config.state.MenuWidth/6
            col = step % 6
            row = step // 6
            if fatherbutton == 0:
                btn = BlockChoose(startposv,cls)
            else:
                btn = SubBlockChoose(startposv,cls,fatherbutton)
            btn.grid_col = col
            btn.grid_row = row
            lst.append(btn)
            step = step + 1
    return lst

class GUI:
    active = False
    # 图像
    background = None
    movemode = "none"
    downmode = "none"
    transmode = "none"

    def __init__(self,pos,size,movemode = "none",downmode = "none",transmode = "none", priority=0, modal=False):
        self.pos = pos
        self.size = size
        self.box = pg.Rect(pos[0], pos[1], size[0], size[1])
        self.background = pg.transform.smoothscale(pg.image.load(config.resource_path("files/gui/guibackground.png")).convert_alpha(), self.size)
        self.movemode = movemode
        self.downmode = downmode
        self.transmode = transmode
        self.guibuttonlist = []
        self.priority = priority
        self.modal = modal
        self.exitbut = ExitButton([pos[0] + size[0] - size[0] * 0.06, pos[1] + size[1] * 0.025], self,[size[0] * 0.05, size[0] * 0.05])

    def move(self,PreSsizes,Ssizes):
        if self.movemode == "right":
            self.pos[0] = Ssizes[0]*0.996-self.size[0]
            self.box.left = self.pos[0]
        elif self.movemode == "left":
            self.pos[0] = 1
            self.box.left = 1
        else:
            pass
        if self.downmode == "up":
            self.pos[1] = 1
            self.box.top = 1
        elif self.downmode == "down":
            self.pos[1] = Ssizes[1]-self.size[1]
            self.box.top = self.pos[1]
        else:
            pass
        if self.transmode == "followx":
            self.size[0] = self.size[0]+Ssizes[0]-PreSsizes[0]
            self.box.width = self.size[0]
        elif self.transmode == "followy":
            self.size[1] = Ssizes[1]
            self.box.height = self.size[1]
        elif self.transmode == "follow":
            self.size[0] = self.size[0] + Ssizes[0] - PreSsizes[0]
            self.size[1] = Ssizes[1]
            self.box.width = self.size[0]
            self.box.height = self.size[1]
        else:
            pass
        self.background = pg.transform.smoothscale(self.background, self.size)
    def draw(self, window):
        if self.active == True:
            window.blit(self.background, self.box)
            for butss in self.guibuttonlist:
                butss.draw(window)

class SidebarGUI(GUI):
    def __init__(self, pos, size, movemode="none", downmode="none", transmode="none"):
        super().__init__(pos, size, movemode, downmode, transmode)
        self.guibuttonlist.clear()

    def move(self, PreSsizes, Ssizes):
        self.pos[0] = Ssizes[0] - self.size[0]
        self.box.left = self.pos[0]
        self.pos[1] = 1
        self.box.top = 1
        if self.transmode == "followy":
            self.size[1] = Ssizes[1]
            self.box.height = self.size[1]
        self.background = pg.transform.smoothscale(self.background, self.size)
        start_x = Ssizes[0] - 379
        for buts in self.guibuttonlist:
            if hasattr(buts, 'grid_col'):
                buts.pos[0] = start_x + buts.grid_col * (config.state.MenuWidth / 6 + 2)
                if hasattr(buts, 'fatherbutton') and buts.fatherbutton is not None:
                    buts.pos[1] = Ssizes[1] * 0.5 + buts.grid_row * (config.state.MenuWidth / 6)
                else:
                    buts.pos[1] = 10 + buts.grid_row * (config.state.MenuWidth / 6)
            elif type(buts) is Setting:
                buts.pos[0] = start_x + 2
                buts.pos[1] = Ssizes[1] * 0.985 - config.state.MenuWidth / 6 * 2 - 5
            elif type(buts) is Start:
                buts.pos[0] = start_x + 2
                buts.pos[1] = Ssizes[1] * 0.985 - config.state.MenuWidth / 6
            elif type(buts) is Save:
                buts.pos[0] = start_x + config.state.MenuWidth * 3 / 6 + 3 + buts.id * (config.state.MenuWidth / 6 + 3) + 2
                buts.pos[1] = Ssizes[1] * 0.985 - config.state.MenuWidth / 6
            buts.box.left = buts.pos[0]
            buts.box.top = buts.pos[1]
            if hasattr(buts, 'has_sub') and buts.has_sub:
                sub_start_x = start_x
                sub_start_y = Ssizes[1] * 0.5
                for subbuts in buts.subbuttonlist:
                    if hasattr(subbuts, 'grid_col'):
                        subbuts.pos[0] = sub_start_x + subbuts.grid_col * (config.state.MenuWidth / 6 + 2)
                        subbuts.pos[1] = sub_start_y + subbuts.grid_row * (config.state.MenuWidth / 6)
                        subbuts.box.left = subbuts.pos[0]
                        subbuts.box.top = subbuts.pos[1]

    def draw(self, window):
        if self.active == True:
            window.blit(self.background, self.box)
            for buts in self.guibuttonlist:
                buts.draw(window)
                if hasattr(buts, 'has_sub') and buts.has_sub and buts.is_selecting:
                    for subbuts in buts.subbuttonlist:
                        subbuts.draw(window)

class ZoneGUI(GUI):
    target = None
    def __init__(self, pos, size, movemode="none", downmode="none", transmode="none"):
        super().__init__(pos, size, movemode, downmode, transmode)
        self.textbuttonlist = []
        # 图标
        self.iconbut = ShowButton([pos[0]+size[0]*0.01,pos[1]+size[1]*0.01], self,[size[0] * 0.3, size[0] * 0.3])
        # 对应坐标
        self.posshowbut = TextShow([pos[0] + size[0] * 0.16, pos[1] + size[1] * 0.01], self, [size[0] * 0.14, size[0] * 0.14])
        self.posshowbut.textshow = "[0,0]"
        # 确认
        self.confrimbut = GUIButton([pos[0] + size[0] * 0.86, pos[1] + size[1] - size[0] * 0.135], self,[size[0] * 0.125, size[0] * 0.125])
        self.confrimbut.icon = pg.transform.smoothscale(pg.image.load(config.resource_path("files/gui/confirm.png")).convert_alpha(),self.confrimbut.size)

        self.column = 0
        self.posdefault = pos
        self.boxdefault = pg.Rect(pos[0], pos[1], size[0], size[1])
        for butss in self.guibuttonlist:
            butss.posdefault = butss.pos[:]
            butss.boxdefault = pg.Rect(butss.pos[0], butss.pos[1], butss.size[0], butss.size[1])
    @staticmethod
    def resetguis(guilist):
        for gui in guilist:
            gui.column = 0
        for gui in [g for g in guilist if g.active]:
            gui.pos[1] = gui.posdefault[1]
            gui.box.top = gui.boxdefault.top
            for butss in gui.guibuttonlist:
                butss.pos[1] = butss.posdefault[1]
                butss.box.top = butss.boxdefault.top
        offset_y = 0
        for gui in [g for g in guilist if g.active]:
            gui.pos[1] = gui.posdefault[1] + offset_y
            gui.box.top = gui.boxdefault.top + offset_y
            for butss in gui.guibuttonlist:
                butss.pos[1] = butss.posdefault[1] + offset_y
                butss.box.top = butss.boxdefault.top + offset_y
            offset_y += gui.size[1]
class RedplanGUI(ZoneGUI):
    @staticmethod
    def _parse_command(text, clock):
        fl = lambda n: n if n == 0 or n % 2 == 1 else n - 1  # 偶数向下取整为最近较小奇数，0 不变
        ans = []
        for part in text.split():
            nums = [num for num in part.split("-") if num.isdigit()]
            if len(nums) == 1:
                n = int(nums[0])
                a = 0 if n == 0 else fl(n)     # 起点：0 不改；否则向下取奇数
                b = 1 if n == 0 else a + 2     # 终点：扩展到下一个奇数
                ans.append((a, b))
            elif len(nums) == 2:
                a = fl(int(nums[0]))
                b = int(nums[1])
                # 终点：等于周期时原样保留(以支持跨周期)，否则向下取奇数
                if b != clock:
                    b = fl(b)
                ans.append((a, b))
            else:
                return [], False
        for a, b in ans:
            if a > b:
                return [], False
            if 0 < clock < b:
                return [], False
        ans.sort()
        merged = []
        for a, b in ans:
            if not merged or a > merged[-1][1]:
                merged.append([a, b])
            else:
                merged[-1][1] = max(merged[-1][1], b)
        return merged, True

    def __init__(self, pos, size, movemode="none", downmode="none", transmode="none"):
        super().__init__(pos, size, movemode, downmode, transmode)
        # 指令
        self.commandtextbut = TextInButton([pos[0]+size[0]*0.03,pos[1]+size[1]*0.4 + 15], self,[size[0] * 0.9, size[0] * 0.05],41)
        self.cmd_text = TextShow(
            [pos[0] + size[0] * 0.032, pos[1] + size[1] * 0.3], self,
            [size[0] * 0.3, size[0] * 0.07], [100, 100, 100])
        self.cmd_text.textshow = "配置:"
        # 循环时间
        self.clockiconbut = ShowButton([pos[0] + size[0] * 0.6, pos[1] + size[1] * 0.05 + 25], self,[size[0] * 0.1, size[0] * 0.1])
        self.clockiconbut.icon = pg.transform.smoothscale(pg.image.load(config.resource_path("files/gui/clock.png")).convert_alpha(),self.clockiconbut.size)
        self.clocktextbut = TextInButton([pos[0] + size[0] * 0.73, pos[1] + size[1] * 0.05 + 25], self,[size[0] * 0.18, size[0] * 0.1], 4)
        self.clock_text = TextShow(
            [pos[0] + size[0] * 0.61, pos[1]+ 5], self,
            [size[0] * 0.3, size[0] * 0.07], [100, 100, 100])
        self.clock_text.textshow = "周期:"
        # 确认
        def redcfunction(self):
            text2 = self.fathergui.clocktextbut.textsaved
            clock_ok = text2.isdigit()
            fl = lambda n: n if n == 0 or n % 2 == 1 else n - 1  # 周期同样向下取整为奇数
            clock_val = fl(int(text2)) if clock_ok else 0
            ans, cmd_ok = RedplanGUI._parse_command(
                self.fathergui.commandtextbut.textsaved, clock_val if clock_ok else 0)
            if cmd_ok:
                self.fathergui.target.command = ans
                self.fathergui.commandtextbut.fontcolor = "green"
            else:
                self.fathergui.commandtextbut.fontcolor = "red"
            # 时钟
            if clock_ok:
                self.fathergui.target.clock = clock_val
                self.fathergui.clocktextbut.fontcolor = "green"
            else:
                self.fathergui.clocktextbut.fontcolor = "red"
        self.confrimbut.execute = types.MethodType(redcfunction, self.confrimbut)

        for butss in self.guibuttonlist:
            butss.posdefault = butss.pos[:]
            butss.boxdefault = pg.Rect(butss.pos[0], butss.pos[1], butss.size[0], butss.size[1])
class MovingplanGUI(ZoneGUI):
    @staticmethod
    def _parse_command(text, clock):
        fl = lambda n: n if n == 0 or n % 2 == 1 else n - 1  # 偶数向下取整为最近较小奇数，0 不变
        ans = []
        for part in text.split():
            nums = [num for num in part.split("-") if num.isdigit()]
            if len(nums) == 1:
                n = int(nums[0])
                a = 0 if n == 0 else fl(n)     # 起点：0 不改；否则向下取奇数
                b = 1 if n == 0 else a + 2     # 终点：扩展到下一个奇数
                ans.append((a, b))
            elif len(nums) == 2:
                a = fl(int(nums[0]))
                b = int(nums[1])
                # 终点：等于周期时原样保留(以支持跨周期)，否则向下取奇数
                if b != clock:
                    b = fl(b)
                ans.append((a, b))
            else:
                return [], False
        for a, b in ans:
            if a > b:
                return [], False
            if 0 < clock < b:
                return [], False
        ans.sort()
        merged = []
        for a, b in ans:
            if not merged or a > merged[-1][1]:
                merged.append([a, b])
            else:
                merged[-1][1] = max(merged[-1][1],b)
        return merged, True

    def __init__(self, pos, size, movemode="none", downmode="none", transmode="none"):
        super().__init__(pos, size, movemode, downmode, transmode)
        # 指令
        self.commandtextbut = TextInButton([pos[0]+size[0]*0.03,pos[1]+size[1]*0.4 + 15], self,[size[0] * 0.9, size[0] * 0.05],41)
        self.cmd_text = TextShow(
            [pos[0] + size[0] * 0.032, pos[1] + size[1] * 0.3], self,
            [size[0] * 0.3, size[0] * 0.07], [100, 100, 100])
        self.cmd_text.textshow = "配置:"
        # 循环时间
        self.clockiconbut = ShowButton([pos[0] + size[0] * 0.6, pos[1] + size[1] * 0.05 + 25], self,[size[0] * 0.1, size[0] * 0.1])
        self.clockiconbut.icon = pg.transform.smoothscale(pg.image.load(config.resource_path("files/gui/clock.png")).convert_alpha(),self.clockiconbut.size)
        self.clocktextbut = TextInButton([pos[0] + size[0] * 0.73, pos[1] + size[1] * 0.05 + 25], self,[size[0] * 0.18, size[0] * 0.1], 4)
        self.clock_text = TextShow(
            [pos[0] + size[0] * 0.61, pos[1]+ 5], self,
            [size[0] * 0.3, size[0] * 0.07], [100, 100, 100])
        self.clock_text.textshow = "周期:"
        # 确认
        def movecfunction(self):
            text2 = self.fathergui.clocktextbut.textsaved
            clock_ok = text2.isdigit()
            fl = lambda n: n if n == 0 or n % 2 == 1 else n - 1  # 周期同样向下取整为奇数
            clock_val = fl(int(text2)) if clock_ok else 0
            ans, cmd_ok = MovingplanGUI._parse_command(
                self.fathergui.commandtextbut.textsaved, clock_val if clock_ok else 0)
            if cmd_ok:
                self.fathergui.target.command = ans
                self.fathergui.commandtextbut.fontcolor = "green"
            else:
                self.fathergui.commandtextbut.fontcolor = "red"
            # 时钟
            if clock_ok:
                self.fathergui.target.clock = clock_val
                self.fathergui.clocktextbut.fontcolor = "green"
            else:
                self.fathergui.clocktextbut.fontcolor = "red"
        self.confrimbut.execute = types.MethodType(movecfunction, self.confrimbut)

        for butss in self.guibuttonlist:
            butss.posdefault = butss.pos[:]
            butss.boxdefault = pg.Rect(butss.pos[0], butss.pos[1], butss.size[0], butss.size[1])
class GrowplanGUI(ZoneGUI):
    def __init__(self, pos, size, movemode="none", downmode="none", transmode="none"):
        super().__init__(pos, size, movemode, downmode, transmode)
        # 循环时间输入框
        self.clockiconbut = ShowButton([pos[0] + size[0] * 0.6, pos[1] + size[1] * 0.05 + 21], self,[size[0] * 0.1, size[0] * 0.1])
        self.clockiconbut.icon = pg.transform.smoothscale(pg.image.load(config.resource_path("files/gui/clock.png")).convert_alpha(),self.clockiconbut.size)
        self.clocktextbut = TextInButton([pos[0] + size[0] * 0.73, pos[1] + size[1] * 0.05 + 21], self,[size[0] * 0.18, size[0] * 0.1], 4)
        self.clock_text = TextShow(
            [pos[0] + size[0] * 0.61, pos[1] + 5], self,
            [size[0] * 0.3, size[0] * 0.07], [100, 100, 100])
        self.clock_text.textshow = "周期:"
        # 高度输入框
        self.rangeiconbut = ShowButton([pos[0] + size[0] * 0.595, pos[1] + size[1] * 0.35 + 21], self,[size[0] * 0.1, size[0] * 0.1])
        self.rangeiconbut.icon = pg.transform.smoothscale(pg.image.load(config.resource_path("files/gui/layer.png")).convert_alpha(),self.rangeiconbut.size)
        self.heightswichbut = TextInButton([pos[0] + size[0] * 0.71, pos[1] + size[1] * 0.35 + 21], self,[size[0] * 0.18, size[0] * 0.1], 2)
        self.range_text = TextShow(
            [pos[0] + size[0] * 0.6,  pos[1] + size[1] * 0.315], self,
            [size[0] * 0.3, size[0] * 0.07], [100, 100, 100])
        self.range_text.textshow = "高度层:"
        # 树叶生成切换框
        self.leaficonbut = ShowButton([pos[0] + size[0] * 0.305, pos[1] + size[1] * 0.35 + 21], self,[size[0] * 0.1, size[0] * 0.1])
        self.leaficonbut.icon = pg.transform.smoothscale(pg.image.load(config.resource_path("files/icon/oak_leaves.png")).convert_alpha(),self.leaficonbut.size)
        self.leafswichbut = SwichButton([pos[0] + size[0] * 0.41, pos[1] + size[1] * 0.35 + 21], self,[size[0] * 0.18, size[0] * 0.1])
        self.leaf_text = TextShow(
            [pos[0] + size[0] * 0.31, pos[1] + size[1] * 0.315], self,
            [size[0] * 0.3, size[0] * 0.07], [100, 100, 100])
        self.leaf_text.textshow = "生成树叶:"
        # 模式切换框
        self.modeiconbut = ShowButton([pos[0] + size[0] * 0.01, pos[1] + size[1] * 0.35 + 21], self,[size[0] * 0.1, size[0] * 0.1])
        self.modeiconbut.icon = pg.transform.smoothscale(pg.image.load(config.resource_path("files/gui/detect.png")).convert_alpha(),self.modeiconbut.size)
        self.modeswichbut = SwichButton([pos[0] + size[0] * 0.12, pos[1] + size[1] * 0.35 + 21], self,[size[0] * 0.18, size[0] * 0.1])
        self.mode_text = TextShow(
            [pos[0] + size[0] * 0.02, pos[1] + size[1] * 0.315], self,
            [size[0] * 0.3, size[0] * 0.07], [100, 100, 100])
        self.mode_text.textshow = "模式:"
        # 确认按钮
        def growcfunction(self):
            self.fathergui.target.gen_leaves = bool(self.fathergui.leafswichbut.locate-1)
            self.fathergui.target.mode = self.fathergui.modeswichbut.locate
            right = False
            text2 = self.fathergui.clocktextbut.textsaved
            ans2 = 0
            try:
                if text2.isdigit():
                    ans2 = int(text2)
                    right = True
                else:
                    pass
            except ValueError:
                pass
            if right:
                self.fathergui.target.clock = ans2
                self.fathergui.clocktextbut.fontcolor = "green"
            else:
                self.fathergui.clocktextbut.fontcolor = "red"

            right1 = False
            text3 = self.fathergui.heightswichbut.textsaved
            ans3 = 0
            try:
                if text2.isdigit() and self.fathergui.target.heightrange[0] <= int(text3) <= self.fathergui.target.heightrange[1]:
                    ans3 = int(text3)
                    right1 = True
                else:
                    pass
            except ValueError:
                pass
            if right1:
                self.fathergui.target.height = ans3
                self.fathergui.heightswichbut.fontcolor = "green"
            else:
                self.fathergui.heightswichbut.fontcolor = "red"
        self.confrimbut.execute = types.MethodType(growcfunction, self.confrimbut)

        for butss in self.guibuttonlist:
            butss.posdefault = butss.pos[:]
            butss.boxdefault = pg.Rect(butss.pos[0], butss.pos[1], butss.size[0], butss.size[1])
class BreakplanGUI(ZoneGUI):
    def __init__(self, pos, size, movemode="none", downmode="none", transmode="none"):
        super().__init__(pos, size, movemode, downmode, transmode)
        # 循环时间输入框
        self.clockiconbut = ShowButton([pos[0] + size[0] * 0.6, pos[1] + size[1] * 0.05 + 24], self, [size[0] * 0.1, size[0] * 0.1])
        self.clockiconbut.icon = pg.transform.smoothscale(
            pg.image.load(config.resource_path("files/gui/clock.png")).convert_alpha(), self.clockiconbut.size)
        self.clocktextbut = TextInButton([pos[0] + size[0] * 0.73, pos[1] + size[1] * 0.05 + 24], self, [size[0] * 0.18, size[0] * 0.1], 4)
        self.clock_text = TextShow(
            [pos[0] + size[0] * 0.61, pos[1] + 5], self,
            [size[0] * 0.3, size[0] * 0.07], [100, 100, 100])
        self.clock_text.textshow = "周期:"
        # 范围输入框
        self.rangeiconbut = ShowButton([pos[0] + size[0] * 0.01, pos[1] + size[1] * 0.35 + 21], self, [size[0] * 0.1, size[0] * 0.1])
        self.rangeiconbut.icon = pg.transform.smoothscale(
            pg.image.load(config.resource_path("files/gui/range.png")).convert_alpha(), self.rangeiconbut.size)
        self.rangetextbut = TextInButton([pos[0] + size[0] * 0.12, pos[1] + size[1] * 0.35 + 21], self, [size[0] * 0.18, size[0] * 0.1], 2)
        self.range_text = TextShow(
            [pos[0] + size[0] * 0.02, pos[1] + size[1] * 0.315], self,
            [size[0] * 0.3, size[0] * 0.07], [100, 100, 100])
        self.range_text.textshow = "范围:"

        # 确认按钮
        def breakcfunction(self):
            gui = self.fathergui
            # 时钟
            right = False
            text2 = gui.clocktextbut.textsaved
            ans2 = 0
            try:
                if text2.isdigit():
                    ans2 = int(text2)
                    right = True
            except ValueError:
                pass
            if right:
                gui.target.clock = ans2
                gui.clocktextbut.fontcolor = "green"
            else:
                gui.clocktextbut.fontcolor = "red"
            # 范围
            right1 = False
            text3 = gui.rangetextbut.textsaved
            ans3 = 0
            try:
                if text3.isdigit() and 1 <= int(text3) <= 99:
                    ans3 = int(text3)
                    right1 = True
            except ValueError:
                pass
            if right1:
                gui.target.range = ans3
                gui.rangetextbut.fontcolor = "green"
            else:
                gui.rangetextbut.fontcolor = "red"
        self.confrimbut.execute = types.MethodType(breakcfunction, self.confrimbut)

        for butss in self.guibuttonlist:
            butss.posdefault = butss.pos[:]
            butss.boxdefault = pg.Rect(butss.pos[0], butss.pos[1], butss.size[0], butss.size[1])
class SetplanGUI(ZoneGUI):
    def __init__(self, pos, size, movemode="none", downmode="none", transmode="none"):
        super().__init__(pos, size, movemode, downmode, transmode)
        # 时钟
        self.clockiconbut = ShowButton([pos[0] + size[0] * 0.6, pos[1] + size[1] * 0.05 + 21], self, [size[0] * 0.1, size[0] * 0.1])
        self.clockiconbut.icon = pg.transform.smoothscale(
            pg.image.load(config.resource_path("files/gui/clock.png")).convert_alpha(), self.clockiconbut.size)
        self.clocktextbut = TextInButton([pos[0] + size[0] * 0.73, pos[1] + size[1] * 0.05 + 21], self, [size[0] * 0.18, size[0] * 0.1], 4)
        self.clock_text = TextShow(
            [pos[0] + size[0] * 0.61, pos[1] + 5], self,
            [size[0] * 0.3, size[0] * 0.07], [100, 100, 100])
        self.clock_text.textshow = "周期:"
        # 放置方块
        self.placeicon = ShowButton([pos[0] + size[0] * 0.03, pos[1] + size[1] * 0.35 + 21], self, [size[0] * 0.1, size[0] * 0.1])
        stone_icon = pg.transform.smoothscale(
            pg.image.load(config.resource_path("files/icon/stone.png")).convert_alpha(),
            (self.placeicon.size[0] - 4, self.placeicon.size[1] - 4))
        self.placeicon.icon = stone_icon
        self.place_text = TextShow(
            [pos[0] + size[0] * 0.02, pos[1] + size[1] * 0.315], self,
            [size[0] * 0.3, size[0] * 0.07], [100, 100, 100])
        self.place_text.textshow = "放置:"

        # 确认按钮
        def setcfunction(self):
            gui = self.fathergui
            # 时钟
            right = False
            text2 = gui.clocktextbut.textsaved
            ans2 = 0
            try:
                if text2.isdigit():
                    ans2 = int(text2)
                    right = True
            except ValueError:
                pass
            if right:
                gui.target.clock = ans2
                gui.clocktextbut.fontcolor = "green"
            else:
                gui.clocktextbut.fontcolor = "red"
        self.confrimbut.execute = types.MethodType(setcfunction, self.confrimbut)

        for butss in self.guibuttonlist:
            butss.posdefault = butss.pos[:]
            butss.boxdefault = pg.Rect(butss.pos[0], butss.pos[1], butss.size[0], butss.size[1])

class SettingsGUI(GUI):
    def __init__(self, pos, size, movemode="none", downmode="none", transmode="none"):
        super().__init__(pos, size, movemode, downmode, transmode)
        self.textbuttonlist = []

        icon_sz_main = [size[0] * 0.12, size[0] * 0.12]
        icon_sz = [size[0] * 0.06, size[0] * 0.06]
        text_sz = [size[0] * 0.12, size[0] * 0.06]
        switch_sz = [size[0] * 0.12, size[0] * 0.06]

        # 图标
        self.title_icon = ShowButton(
            [pos[0] + size[0]*0.02, pos[1] + size[1] * 0.02], self, icon_sz_main)
        self.title_icon.icon = pg.transform.smoothscale(
                pg.image.load(config.resource_path("files/gui/setting.png")).convert_alpha(), icon_sz_main)

        # 标题
        self.setting_text = TextShow(
            [pos[0] + size[0] * 0.155, pos[1] + size[1] * 0.03], self,
            [size[0] * 0.3, size[0] * 0.1],[25,25,25])
        self.setting_text.textshow = "设置[未完成]"

        self.map_text = TextShow(
            [pos[0] + size[0] * 0.02, pos[1] + size[1] * 0.157], self,
            [size[0] * 0.3, size[0] * 0.06],[50,50,50])
        self.map_text.textshow = "# 地图"
        # 区块阵列边长
        self.chunksize_icon = ShowButton(
            [pos[0] + size[0] * 0.04, pos[1] + size[1] * 0.25], self, icon_sz)
        self.chunksize_icon.icon = pg.transform.smoothscale(
                pg.image.load(config.resource_path("files/gui/setting_chunks.png")).convert_alpha(), icon_sz)
        self.chunksize_textin = TextInButton(
            [pos[0] + size[0] * 0.11, pos[1] + size[1] * 0.252], self, text_sz, 2)
        self.chunksize_text = TextShow(
            [pos[0] + size[0] * 0.038, pos[1] + size[1] * 0.207], self,
            [size[0] * 0.23, size[0] * 0.04], [100, 100, 100])
        self.chunksize_text.textshow = "地图边长(区块)"

        self.simulation_text = TextShow(
            [pos[0] + size[0] * 0.02, pos[1] + size[1] * 0.307], self,
            [size[0] * 0.3, size[0] * 0.06], [50, 50, 50])
        self.simulation_text.textshow = "# 模拟"
        # 模拟速度
        self.speed_icon = ShowButton(
            [pos[0] + size[0] * 0.04, pos[1] + size[1] * 0.40], self, icon_sz)
        self.speed_icon.icon = pg.transform.smoothscale(
                pg.image.load(config.resource_path("files/gui/setting_simspeed.png")).convert_alpha(), icon_sz)
        self.speed_textin = TextInButton(
            [pos[0] + size[0] * 0.11, pos[1] + size[1] * 0.402], self, text_sz, 4)
        self.speed_text = TextShow(
            [pos[0] + size[0] * 0.038, pos[1] + size[1] * 0.357], self,
            [size[0] * 0.23, size[0] * 0.04], [100, 100, 100])
        self.speed_text.textshow = "模拟速度(ms)"

        self.show_text = TextShow(
            [pos[0] + size[0] * 0.02, pos[1] + size[1] * 0.457], self,
            [size[0] * 0.3, size[0] * 0.06], [50, 50, 50])
        self.show_text.textshow = "# 视觉"
        # 背景开关
        self.bg_icon = ShowButton(
            [pos[0] + size[0] * 0.04, pos[1] + size[1] * 0.55], self, icon_sz)
        self.bg_icon.icon = pg.transform.smoothscale(
                pg.image.load(config.resource_path("files/gui/setting_background.png")).convert_alpha(), icon_sz)
        self.bg_switch = SwichButton(
            [pos[0] + size[0] * 0.11, pos[1] + size[1] * 0.551], self, switch_sz)
        self.bg_switch.dict = {1: "ON", 2: "OFF"}
        self.bg_text = TextShow(
            [pos[0] + size[0] * 0.038, pos[1] + size[1] * 0.507], self,
            [size[0] * 0.23, size[0] * 0.04], [100, 100, 100])
        self.bg_text.textshow = "背景显示"
        # 确认
        self.confrimbut = GUIButton(
            [pos[0] + size[0] * 0.896, pos[1] + size[1] * 0.885], self,
            [size[0] * 0.09, size[0] * 0.09])
        self.confrimbut.icon = pg.transform.smoothscale(
            pg.image.load(config.resource_path("files/gui/confirm.png")).convert_alpha(),
            self.confrimbut.size)

        # 语法
        def settings_confirm(self):
            gui = self.fathergui
            all_right = True
            # 区块边长验证：纯数字且1~16
            cs_text = gui.chunksize_textin.textsaved
            if cs_text.isdigit() and 1 <= int(cs_text) <= 16:
                gui.chunksize_textin.fontcolor = "white"
            else:
                gui.chunksize_textin.fontcolor = "red"
                all_right = False
            sp_text = gui.speed_textin.textsaved
            if sp_text.isdigit():
                sp_val = int(sp_text)
                if 10 <= sp_val <= 9999:
                    gui.speed_textin.fontcolor = "white"
                else:
                    gui.speed_textin.fontcolor = "red"
                    all_right = False
            else:
                gui.speed_textin.fontcolor = "red"
                all_right = False
            if all_right:
                config.state.show_background = (gui.bg_switch.locate == 1)

                cs_val = int(cs_text)
                sp_val = int(sp_text)
                cs_changed = cs_val != config.state.ChunkSize
                sp_changed = sp_val != config.state.Oneticktime

                if cs_changed:
                    def on_reload():
                        config.state.Oneticktime = sp_val
                        fun.reset_world(cs_val)
                        gui.active = False
                    show_popup("应用设置?", on_reload, "你目前的工作将会丢失")
                elif sp_changed:
                    config.state.Oneticktime = sp_val
                    gui.active = False
                else:
                    gui.active = False

        self.confrimbut.execute = types.MethodType(settings_confirm, self.confrimbut)

class PopupGUI(GUI):
    def __init__(self, pos, size, message="", subtitle="",
                 movemode="none", downmode="none", transmode="none"):
        super().__init__(pos, size, movemode, downmode, transmode, modal=True)
        self.guibuttonlist.clear()
        # 图标
        ico_sz = [int(size[0] * 0.15), int(size[0] * 0.15)]
        self.warning_icon = ShowButton(
            [int(pos[0] + size[0] * 0.04), int(pos[1] + size[1] * 0.04)], self, ico_sz)
        self.warning_icon.icon = pg.transform.smoothscale(
            pg.image.load(config.resource_path("files/gui/warning.png")).convert_alpha(), ico_sz)
        # 主标题
        self.msg_text = TextShow(
            [int(pos[0] + size[0] * 0.15), int(pos[1] + size[1] * 0.05)], self,
            [int(size[0] * 0.7), int(size[0] * 0.13)],[50,50,50])
        self.msg_text.textshow = message
        # 副标题
        self.subtitle_text = TextShow(
            [int(pos[0] + size[0] * 0.15), int(pos[1] + size[1] * 0.35)], self,
            [int(size[0] * 0.7), int(size[0] * 0.09)],[50,50,50])
        self.subtitle_text.textshow = subtitle
        btn_w = int(size[0] * 0.28)
        btn_h = int(size[0] * 0.1)
        btn_y = int(pos[1] + size[1] * 0.625)
        # 取消
        self.cancel_but = TextButton(
            [int(pos[0] + size[0] * 0.1), btn_y], self, [btn_w, btn_h], "取消")
        def cancel_action(self):
            self.fathergui.active = False
        self.cancel_but.execute = types.MethodType(cancel_action, self.cancel_but)
        # 确认
        self.confirm_but = TextButton(
            [int(pos[0] + size[0] * 0.6), btn_y], self, [btn_w, btn_h], "确认")

    def move(self, PreSsizes, Ssizes):
        # 大小固定
        w, h = self.size
        new_pos = [int((Ssizes[0] - w) / 2), int((Ssizes[1] - h) / 2)]
        dx = new_pos[0] - self.pos[0]
        dy = new_pos[1] - self.pos[1]
        self.pos = new_pos
        self.box.left = new_pos[0]
        self.box.top = new_pos[1]
        for but in self.guibuttonlist:
            but.pos[0] += dx
            but.pos[1] += dy
            but.box.left = but.pos[0]
            but.box.top = but.pos[1]
def show_popup(message, on_confirm, subtitle=""):
    for g in config.state.GUIList:
        if isinstance(g, PopupGUI) and g.active:
            return
    w = int(config.state.DefaultSsize[0] * 0.4)
    h = int(config.state.DefaultSsize[1] * 0.2)
    popup = PopupGUI(
        [int((config.state.Ssize[0] - w) / 2), int((config.state.Ssize[1] - h) / 2)],
        [w, h], message, subtitle)
    popup.priority = 114514

    def confirm_action(self):
        on_confirm()
        self.fathergui.active = False

    popup.confirm_but.execute = types.MethodType(confirm_action, popup.confirm_but)
    config.state.GUIList.append(popup)
    popup.active = True

class HelpGUI(GUI):
    def __init__(self, pos, size, movemode="none", downmode="none", transmode="none"):
        super().__init__(pos, size, movemode, downmode, transmode, modal=True)
        self.help_text = "1"
        self.font = pg.font.Font(config.resource_path("files/font/Pixel AE.ttf"), int(size[1] * 0.055))

    def draw(self, window):
        if self.active:
            window.blit(self.background, self.box)
            for buts in self.guibuttonlist:
                buts.draw(window)
            lines = self.help_text.split("\n")
            line_h = self.font.get_linesize()
            start_y = self.pos[1] + self.size[1] * 0.08
            for i, line in enumerate(lines):
                surf = self.font.render(line, True, [50, 50, 50])
                window.blit(surf, [self.pos[0] + self.size[0] * 0.05, start_y + i * line_h])
def show_help(text=None):
    if text is None:
        text = "1"
    for g in config.state.GUIList:
        if isinstance(g, HelpGUI) and g.active:
            return
    w = int(config.state.Ssize[0] * 0.5)
    h = int(config.state.Ssize[1] * 0.4)
    help_gui = HelpGUI(
        [int((config.state.Ssize[0] - w) / 2), int((config.state.Ssize[1] - h) / 2)],
        [w, h])
    help_gui.priority = 114514
    help_gui.help_text = text
    config.state.GUIList.append(help_gui)
    help_gui.active = True
def add_help_button(gui, text=None):
    btn_sz = gui.exitbut.size[:]
    btn_pos = [gui.exitbut.pos[0], gui.exitbut.pos[1] + btn_sz[1] + 3]
    btn = GUIButton(btn_pos, gui, btn_sz)
    btn.posdefault = btn.pos[:]
    btn.boxdefault = pg.Rect(btn.pos[0], btn.pos[1], btn.size[0], btn.size[1])
    btn.icon = pg.transform.smoothscale(
        pg.image.load(config.resource_path("files/gui/help.png")).convert_alpha(), btn_sz)
    def help_action(self):
        show_help(text)
    btn.execute = types.MethodType(help_action, btn)
    gui.guibuttonlist.append(btn)


# 初始化gui
sidebar = SidebarGUI([config.state.Ssize[0]-385, 1],[385, config.state.Ssize[1]],"right","up","followy")
sidebar.active = True

red = RedplanGUI([0,0],[config.state.Ssize[0]*0.4,config.state.Ssize[1]*0.25],"left")
red.priority = 1
moving = MovingplanGUI([0,0],[config.state.Ssize[0]*0.4,config.state.Ssize[1]*0.25],"left")
moving.priority = 1
grow = GrowplanGUI([0,0],[config.state.Ssize[0]*0.4,config.state.Ssize[1]*0.35],"left")
grow.priority = 1
breakplan = BreakplanGUI([0,0],[config.state.Ssize[0]*0.4,config.state.Ssize[1]*0.25],"left")
breakplan.priority = 1
setplan = SetplanGUI([0,0],[config.state.Ssize[0]*0.4,config.state.Ssize[1]*0.25],"left")
setplan.priority = 1
# 设置
settingsgui = SettingsGUI(
    [config.state.Ssize[0] * 0.2, config.state.Ssize[1] * 0.1],
    [config.state.Ssize[0] * 0.6, config.state.Ssize[1] * 0.8])
settingsgui.priority = 2
settingsgui.modal = True
settingsgui.exitbut.pos[0] -= 2
settingsgui.exitbut.box.left = settingsgui.exitbut.pos[0]
settingsgui.exitbut.pos[1] -= 5
settingsgui.exitbut.box.top = settingsgui.exitbut.pos[1]

#帮助文本
red_help = (
    "帮助 :\n"
    "区域的激活时间可自由配置, 允许键入数字与短横杠\'-\'\n"
    "若可能,配置输入会向下取整到红石刻(奇数)\'-\'\n"
    "输入n : 在 tick n 开始激活, n+2 终止激活\n"
    "输入a-b : 在 tick a 开始激活, b 终止激活\n"
    "当周期设置为0时, 不循环\n"
    "当周期设置非0时, 将tick / 周期的余数视为当前tick数实现循环\n"
    "例：周期=20 配置= 0 5-10 → 自动整理为 0-1 5-9 \n"
    "在 tick0 激活, tick1 取消, tick2 激活, tick4 取消\n"
)
add_help_button(red, red_help)
add_help_button(grow)
add_help_button(breakplan)
add_help_button(setplan)
add_help_button(settingsgui)

# 初始化GUI列表
config.state.ZoneGUIList = [red,moving,grow,breakplan,setplan]
config.state.GUIList = [sidebar]
config.state.GUIList.extend(config.state.ZoneGUIList)
config.state.GUIList.append(settingsgui)

# gui检测
def guisrect(guilist,mpos):
    active_guis = [g for g in guilist if g.active]
    if not active_guis:
        return None
    modal_guis = [g for g in active_guis if g.modal]
    if modal_guis:
        top = max(modal_guis, key=lambda g: g.priority)
        return top if top.box.collidepoint(mpos) else None
    #返回鼠标位置处优先级最高的gui
    top_gui = None
    for gui in active_guis:
        if gui.box.collidepoint(mpos):
            if top_gui is None or gui.priority > top_gui.priority:
                top_gui = gui
    return top_gui