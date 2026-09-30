#蘑菇
#下界蘑菇
import ctypes
from ctypes import wintypes
import pygame as pg
import config
import functions as fun
import blocks
import zones
import gui
import simulation
import effects

zones.RedPlan.gui = gui.red
zones.MovingPlan.gui = gui.moving
zones.GrowPlan.gui = gui.grow
zones.BreakPlan.gui = gui.breakplan
zones.SetPlan.gui = gui.setplan

config.state.screen = pg.display.get_surface()
pg.display.set_caption("Struct Tester")
config.state.clock = pg.time.Clock()
config.state.pasttime = pg.time.get_ticks()
pg.key.stop_text_input()
config.state.windowicon = pg.image.load(config.resource_path("files/icon/piston.png")).convert_alpha()
pg.display.set_icon(config.state.windowicon)

_wndproc_cb = None

class _MINMAXINFO(ctypes.Structure):
    _fields_ = [("ptReserved", wintypes.POINT),
                ("ptMaxSize", wintypes.POINT),
                ("ptMaxPosition", wintypes.POINT),
                ("ptMinTrackSize", wintypes.POINT),
                ("ptMaxTrackSize", wintypes.POINT)]

_user32 = ctypes.WinDLL('user32', use_last_error=True)
_WNDPROCTYPE = ctypes.WINFUNCTYPE(ctypes.c_ssize_t, wintypes.HWND, wintypes.UINT,
                                  wintypes.WPARAM, wintypes.LPARAM)
_setwndproc = getattr(_user32, 'SetWindowLongPtrW', None) or _user32.SetWindowLongW
_setwndproc.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_void_p]
_setwndproc.restype = ctypes.c_void_p
_user32.CallWindowProcW.argtypes = [ctypes.c_void_p, wintypes.HWND, wintypes.UINT,
                                    wintypes.WPARAM, wintypes.LPARAM]
_user32.CallWindowProcW.restype = ctypes.c_ssize_t


def _minmax_wndproc(hwnd, msg, wparam, lparam):
    if msg == 0x0024:  # WM_GETMINMAXINFO
        info = _MINMAXINFO.from_address(lparam)
        info.ptMinTrackSize.x = config.state.Minsize[0]
        info.ptMinTrackSize.y = config.state.Minsize[1]
        return 0
    return _user32.CallWindowProcW(_orig_wndproc, hwnd, msg, wparam, lparam)


_wndproc_cb = _WNDPROCTYPE(_minmax_wndproc)
_orig_wndproc = _setwndproc(wintypes.HWND(pg.display.get_wm_info()['window']), -4, _wndproc_cb)


# 资源加载
config.state.background_orig = pg.image.load(config.resource_path("files/pictures/background.jpg"))
config.state.ibackground = pg.transform.smoothscale(
    config.state.background_orig, (config.state.Ssize[0], config.state.Ssize[1]))
config.state.ibackground_size = list(config.state.Ssize)
config.state.crosshair = pg.transform.smoothscale(
    pg.image.load(config.resource_path("files/gui/crosshair.png")).convert_alpha(), (30, 30))
config.state.icrosshair = config.state.crosshair
config.state.Text = pg.font.Font(config.resource_path("files/font/Pixel AE.ttf"), 20)

# 网格初始化
config.state.ChunkList = [[blocks.Air(fun.cidturnc(c), fun.bidturnub(b)) for b in range(config.state.SubChunkSize * config.state.SubChunkSize)]
                   for c in range(config.state.ChunkSize * config.state.ChunkSize)]
config.state.ZoneList = [[[] for b in range(config.state.SubChunkSize * config.state.SubChunkSize)]
                  for c in range(config.state.ChunkSize * config.state.ChunkSize)]
config.state.PromptList = []
config.state.ChunkOrder = list(range(config.state.ChunkSize * config.state.ChunkSize))
config.state.PendingTickList = [simulation.PendingTickQueue() for _ in config.state.ChunkOrder]
config.state.BlockOrder = list(range(config.state.SubChunkSize * config.state.SubChunkSize))
simulation.createbarrier(config.state.ChunkList)

config.state.simulating = False
config.state.tick = 0
config.state.Trigger = blocks.Void

# 按钮初始化
Allclass = []
Allclass.extend(blocks.Blockclass)
Allclass.extend(zones.Zoneclass)

sidebar_buttons = gui.gen_blockchoose(Allclass, ((config.state.Ssize[0] - config.state.MenuWidth + 3) - 22, 10))
for buts in sidebar_buttons:
    if buts.has_sub == True:
        buts.subbuttonlist = gui.gen_blockchoose(
            buts.target.sub,
            ((config.state.Ssize[0] - config.state.MenuWidth + 3) - 22, config.state.Ssize[1] * 0.5),
            buts)
    gui.sidebar.guibuttonlist.append(buts)

# 设置按钮
settingbutton = gui.Setting(
    [(config.state.Ssize[0] - config.state.MenuWidth + 3) - 20,
     config.state.Ssize[1] * 0.985 - config.state.MenuWidth / 6 - config.state.MenuWidth / 6 - 5],
    [config.state.MenuWidth / 6, config.state.MenuWidth / 6])
gui.sidebar.guibuttonlist.append(settingbutton)
startbutton = gui.Start([(config.state.Ssize[0] - config.state.MenuWidth + 3) - 20, config.state.Ssize[1] * 0.985 - config.state.MenuWidth / 6],
                    [config.state.MenuWidth * 3 / 6, config.state.MenuWidth / 6])
gui.sidebar.guibuttonlist.append(startbutton)
savebutton1 = gui.Save([(config.state.Ssize[0] - config.state.MenuWidth * 3 / 6 + 3) - 20 + 3, config.state.Ssize[1] * 0.985 - config.state.MenuWidth / 6],
                   [config.state.MenuWidth / 6, config.state.MenuWidth / 6], 0)
savebutton2 = gui.Save([(config.state.Ssize[0] - config.state.MenuWidth * 2 / 6 + 3) - 20 + 6, config.state.Ssize[1] * 0.985 - config.state.MenuWidth / 6],
                   [config.state.MenuWidth / 6, config.state.MenuWidth / 6], 1)
savebutton3 = gui.Save([(config.state.Ssize[0] - config.state.MenuWidth / 6 + 3) - 20 + 9, config.state.Ssize[1] * 0.985 - config.state.MenuWidth / 6],
                   [config.state.MenuWidth / 6, config.state.MenuWidth / 6], 2)
gui.sidebar.guibuttonlist.append(savebutton1)
gui.sidebar.guibuttonlist.append(savebutton2)
gui.sidebar.guibuttonlist.append(savebutton3)

config.state.buttonlist = gui.sidebar.guibuttonlist

# 快捷键
def toggle_sidebar():
    gui.sidebar.active = not gui.sidebar.active
def close_top_gui():
    top_guis = [g for g in config.state.GUIList if g.active and g is not gui.sidebar]
    if top_guis:
        max_pri = max(g.priority for g in top_guis)
        for g in top_guis:
            if g.priority == max_pri:
                g.active = False
def confirm_top_gui():
    for g in config.state.GUIList:
        if g.active:
            for tb in getattr(g, 'textbuttonlist', []):
                tb.textsaved = tb.textin
    top_guis = [g for g in config.state.GUIList if g.active and g is not gui.sidebar]
    if top_guis:
        max_pri = max(g.priority for g in top_guis)
        for g in top_guis:
            if g.priority == max_pri:
                confirm = getattr(g, 'confirm_but', None) or getattr(g, 'confrimbut', None)
                if confirm is not None:
                    confirm.execute()

# 快捷键注册
config.state.keybindings = [
    gui.KeyBinding(pg.K_t, lambda: toggle_sidebar()),
    gui.KeyBinding(pg.K_ESCAPE, close_top_gui),
    gui.KeyBinding(pg.K_RETURN, confirm_top_gui),
]

# 主循环
running = True

while running:
    config.state.clock.tick(60)
    config.state.Spos = [(config.state.Ssize[0] - config.state.MenuWidth) / 2, config.state.Ssize[1] / 2]
    nowtime = pg.time.get_ticks()

    # 事件
    keys = pg.key.get_pressed()
    Mpos = pg.mouse.get_pos()
    pending_resize = None
    for event in pg.event.get():
        # 窗口大小
        if event.type == pg.VIDEORESIZE:
            pending_resize = [max(config.state.Minsize[0], event.size[0]),
                              max(config.state.Minsize[1], event.size[1])]

        # 视角移动
        if config.state.Zoom <= 24:
            if keys[pg.K_w] and config.state.Vpos[1] > 0:
                config.state.Vpos[1] -= config.state.Zoom * 2
            if keys[pg.K_s] and config.state.Vpos[1] < config.state.Vsize:
                config.state.Vpos[1] += config.state.Zoom * 2
            if keys[pg.K_a] and config.state.Vpos[0] > 0:
                config.state.Vpos[0] -= config.state.Zoom * 2
            if keys[pg.K_d] and config.state.Vpos[0] < config.state.Vsize:
                config.state.Vpos[0] += config.state.Zoom * 2

        # shift
        if event.type == pg.KEYDOWN:
            if event.key == pg.K_LSHIFT:
                if config.state.simulating == False:
                    for buts in gui.sidebar.guibuttonlist:
                        if hasattr(buts, 'icon_shift'):
                            buts.icon = buts.icon_shift
                else:
                    for buts in gui.sidebar.guibuttonlist:
                        if type(buts) == gui.Start:
                            buts.icon = buts.icon_reset
                config.state.shiftdown = True
            else:
                # 通用
                for kb in config.state.keybindings:
                    if event.key == kb.key:
                        if kb.repeat_protect and kb.pressed:
                            continue
                        kb.pressed = True
                        kb.action()
        if event.type == pg.KEYUP:
            if event.key == pg.K_LSHIFT:
                if config.state.simulating == False:
                    for buts in gui.sidebar.guibuttonlist:
                        if hasattr(buts, 'icon_normal'):
                            buts.icon = buts.icon_normal
                else:
                    for buts in gui.sidebar.guibuttonlist:
                        if type(buts) == gui.Start:
                            buts.icon = buts.icon_pause
                config.state.shiftdown = False
            else:
                # 释放
                for kb in config.state.keybindings:
                    if event.key == kb.key:
                        kb.pressed = False

        # 鼠标
        if event.type == pg.MOUSEBUTTONDOWN:
            hit_gui = gui.guisrect(config.state.GUIList, Mpos)
            if hit_gui is None:
                if event.button == 4:  # 上滚轮
                    if config.state.Zoom < 24:
                        config.state.Zoom += 0.5
                if event.button == 5:  # 下滚轮
                    if config.state.Zoom > 0.5:
                        config.state.Zoom -= 0.5
                if 15 >= fun.cturncid(fun.vturnc(fun.sturnv(Mpos))) >= 0 and 255 >= fun.ubturnbid(fun.vturnub(fun.sturnv(Mpos))) >= 0:
                    if event.button == 3:  # 右键
                        if config.state.Zoom <= 4 and (config.state.simulating == False or config.state.put_when_simulating == True):
                            if config.state.shiftdown == False:
                                if config.state.Trigger is not None and config.state.Trigger.is_zone == True:
                                    zones.Zone.set((fun.vturnc(fun.sturnv(Mpos))), (fun.vturnub(fun.sturnv(Mpos))), config.state.Trigger)
                                    effects.create_fade(
                                        fun.idturnb(fun.cturncid(fun.vturnc(fun.sturnv(Mpos))), fun.ubturnbid(fun.vturnub(fun.sturnv(Mpos)))),
                                        (255, 255, 255), 300)
                                else:
                                    block = config.state.ChunkList[fun.cturncid(fun.vturnc(fun.sturnv(Mpos)))][fun.ubturnbid(fun.vturnub(fun.sturnv(Mpos)))]
                                    rotated = False
                                    if block.can_rotate_byhand == True:
                                        block.rotate()
                                        rotated = True
                                    if config.state.Trigger != blocks.Void:
                                        was_air = type(block) == blocks.Air
                                        block.set(config.state.Trigger, config.state.Towards)
                                        if not rotated:
                                            if was_air:
                                                effects.create_fade(block.abpos, (255, 255, 255), 150)
                                            else:
                                                effects.create_fade(block.abpos, (180, 0, 0), 100)
                            else:
                                # 活塞叠放
                                block = config.state.ChunkList[fun.cturncid(fun.vturnc(fun.sturnv(Mpos)))][fun.ubturnbid(fun.vturnub(fun.sturnv(Mpos)))]
                                if config.state.Trigger == blocks.StickyPiston and type(block) == blocks.StickyPiston and not block.stacked:
                                    block.stacked = True
                                    block.stacked_piston_type = config.state.Trigger
                                    effects.create_fade(block.abpos, (255, 255, 255), 150)
                                else:
                                    # 放置区域
                                    hit_zone_list = config.state.ZoneList[fun.cturncid(fun.vturnc(fun.sturnv(Mpos)))][fun.ubturnbid(fun.vturnub(fun.sturnv(Mpos)))]
                                    setplan_set = False
                                    for zon in hit_zone_list:
                                        if isinstance(zon, zones.SetPlan):
                                            is_block = (config.state.Trigger is not None
                                                        and config.state.Trigger != blocks.Void
                                                        and not getattr(config.state.Trigger, 'is_zone', False))
                                            if is_block and config.state.Trigger != zon.settrigger:
                                                zon.settrigger = config.state.Trigger
                                                setplan_set = True
                                                if hasattr(zon.settrigger, 'icon') and zon.settrigger.icon is not None:
                                                    ico = pg.transform.smoothscale(zon.settrigger.icon,
                                                        (zon.gui.placeicon.size[0] - 4, zon.gui.placeicon.size[1] - 4))
                                                    zon.gui.placeicon.icon = ico
                                                effects.create_fade(zon.abpos, (139, 90, 43), 300)
                                            break
                                    if not setplan_set:
                                        for guis in config.state.ZoneGUIList:
                                            guis.active = False
                                        if len(config.state.ZoneList[fun.cturncid(fun.vturnc(fun.sturnv(Mpos)))][fun.ubturnbid(fun.vturnub(fun.sturnv(Mpos)))]) != 0:
                                            for zoness in config.state.ZoneList[fun.cturncid(fun.vturnc(fun.sturnv(Mpos)))][fun.ubturnbid(fun.vturnub(fun.sturnv(Mpos)))]:
                                                zoness.opengui()

                    if event.button == 2:  # 中键
                        if config.state.Zoom <= 4 and (config.state.simulating == False or config.state.put_when_simulating == True):
                            if config.state.ChunkList[fun.cturncid(fun.vturnc(fun.sturnv(Mpos)))][fun.ubturnbid(fun.vturnub(fun.sturnv(Mpos)))].hidden == False:
                                config.state.Trigger = type(config.state.ChunkList[fun.cturncid(fun.vturnc(fun.sturnv(Mpos)))][fun.ubturnbid(fun.vturnub(fun.sturnv(Mpos)))])
                                config.state.Towards = config.state.ChunkList[fun.cturncid(fun.vturnc(fun.sturnv(Mpos)))][fun.ubturnbid(fun.vturnub(fun.sturnv(Mpos)))].towards
                                config.state.icrosshair = gui.update_crosshair(config.state.Trigger, config.state.Towards)
                    if event.button == 1:  # 左键
                        if config.state.shiftdown == False:
                            if config.state.Zoom <= 4 and (config.state.simulating == False or config.state.put_when_simulating == True):
                                block = config.state.ChunkList[fun.cturncid(fun.vturnc(fun.sturnv(Mpos)))][fun.ubturnbid(fun.vturnub(fun.sturnv(Mpos)))]
                                if block.hidden == False:
                                    effects.create_fade(block.abpos, (255, 255, 255), 300)
                                block.remove()
                        else:
                            if config.state.Zoom <= 4 and (config.state.simulating == False or config.state.put_when_simulating == True):
                                zone_list = config.state.ZoneList[fun.cturncid(fun.vturnc(fun.sturnv(Mpos)))][fun.ubturnbid(fun.vturnub(fun.sturnv(Mpos)))]
                                if zone_list:
                                    effects.create_fade(zone_list[0].abpos, (255, 255, 255), 300)
                                zone_list.clear()
                                config.state.ChunkList[fun.cturncid(fun.vturnc(fun.sturnv(Mpos)))][fun.ubturnbid(fun.vturnub(fun.sturnv(Mpos)))].zone_powered = False
            else:
                if event.button == 1:
                    for buts in hit_gui.guibuttonlist:
                        if config.state.shiftdown and isinstance(buts, gui.Functional):
                            buts.is_selected = False
                        else:
                            buts.check(Mpos)
                        # 子菜单
                        if hasattr(buts, 'has_sub') and buts.has_sub and buts.is_selecting:
                            for subbuts in buts.subbuttonlist:
                                subbuts.check(Mpos)
                    if hit_gui is gui.sidebar and config.state.shiftdown:
                        for buts in hit_gui.guibuttonlist:
                            if isinstance(buts, gui.Functional):
                                buts.check_shift(Mpos)

                    if hit_gui in config.state.ZoneGUIList:
                        gui.ZoneGUI.resetguis(config.state.ZoneGUIList)

        if event.type == pg.MOUSEBUTTONUP:
            if gui.sidebar.active:
                for buts in gui.sidebar.guibuttonlist:
                    if buts.is_selected:
                        buts.execute()
                    if hasattr(buts, 'is_shift_selected') and buts.is_shift_selected:
                        buts.execute_shift()
                    if hasattr(buts, 'has_sub') and buts.has_sub and buts.is_selecting:
                        for subbuts in buts.subbuttonlist:
                            if subbuts.is_selected:
                                subbuts.execute()
            for guis2 in config.state.GUIList:
                if guis2 is gui.sidebar:
                    continue
                for buts in guis2.guibuttonlist:
                    if type(buts).__name__ != 'TextInButton' and buts.is_selected:
                        buts.execute()
            # 重置
            if gui.sidebar.active:
                for buts in gui.sidebar.guibuttonlist:
                    buts.is_selected = False
                    if hasattr(buts, 'is_shift_selected'):
                        buts.is_shift_selected = False
                    if hasattr(buts, 'has_sub') and buts.has_sub:
                        for subbuts in buts.subbuttonlist:
                            subbuts.is_selected = False
            for guis2 in config.state.GUIList:
                for buts in guis2.guibuttonlist:
                    if type(buts).__name__ != 'TextInButton':
                        buts.is_selected = False

        # gui按钮
        for guis in config.state.GUIList:
            for buts in guis.guibuttonlist:
                if hasattr(buts, 'event_handle'):
                    buts.event_handle(event)

        if event.type == pg.QUIT:
            running = False

    # 防重复
    any_gui_active = any(g.active for g in config.state.GUIList if g is not gui.sidebar)
    if any_gui_active and not config.state.key_repeat_slow:
        pg.key.set_repeat(500, 100)
        config.state.key_repeat_slow = True
    elif not any_gui_active and config.state.key_repeat_slow:
        pg.key.set_repeat(1, 1)
        config.state.key_repeat_slow = False

    # 机制
    if nowtime - config.state.pasttime >= config.state.Oneticktime:
        if config.state.simulating == True:
            simulation.runonce()
        config.state.pasttime = nowtime

    # 窗口缩放更新
    if pending_resize is not None:
        PreSsize = list(config.state.Ssize)
        config.state.Ssize = pending_resize
        config.state.Spos = [(config.state.Ssize[0] - config.state.MenuWidth) / 2, config.state.Ssize[1] / 2]
        config.state.screen = pg.display.set_mode(config.state.Ssize, pg.RESIZABLE)
        # gui更新
        for guis in config.state.GUIList:
            guis.move(PreSsize, config.state.Ssize)

    # 绘制
    if config.state.show_background:
        if config.state.ibackground_size != list(config.state.Ssize):
            config.state.ibackground = pg.transform.smoothscale(
                config.state.background_orig, (config.state.Ssize[0], config.state.Ssize[1]))
            config.state.ibackground_size = list(config.state.Ssize)
        config.state.screen.blit(config.state.ibackground, (0, 0))
    else:
        config.state.screen.fill((20, 20, 40))

    # 绘制方块
    for chunk in config.state.ChunkList:
        for block in chunk:
            block.draw()

    # 绘制区域
    for chunksz in config.state.ZoneList:
        for blocksz in chunksz:
            if len(blocksz) != 0:
                for zon in blocksz:
                    zon.draw()

    # 绘制特效
    effects.draw_effects(config.state.screen)

    # 绘制提示方块
    TargetBlock = pg.Surface((config.state.BaseBlockSize / config.state.Zoom, config.state.BaseBlockSize / config.state.Zoom), pg.SRCALPHA)
    TargetBlock.fill((255, 255, 255, 64))
    if config.state.Zoom <= 4:
        if 0 <= fun.vturnc(fun.sturnv(Mpos))[0] < config.state.ChunkSize and 0 <= fun.vturnc(fun.sturnv(Mpos))[1] < config.state.ChunkSize and gui.guisrect(
                config.state.GUIList, Mpos) is None:
            config.state.screen.blit(TargetBlock, fun.vturns(fun.bturnv(fun.vturnb(fun.sturnv(Mpos)))))
    # 绘制背景网格

    line_color = "white" if not config.state.show_background else "black"
    if config.state.Zoom >= 4 and config.state.draw_structs == True:
        for x in range(0, config.state.ChunkSize + 1):
            pg.draw.line(config.state.screen, line_color, (fun.vturns(fun.cturnv([x, 0]))), (fun.vturns(fun.cturnv([x, config.state.ChunkSize]))), width=3)
        for y in range(0, config.state.ChunkSize + 1):
            pg.draw.line(config.state.screen, line_color, (fun.vturns(fun.cturnv([0, y]))), (fun.vturns(fun.cturnv([config.state.ChunkSize, y]))), width=3)
    if config.state.Zoom <= 4:
        for x in range(0, config.state.ChunkSize * config.state.SubChunkSize):
            pg.draw.line(config.state.screen, line_color, (fun.vturns(fun.bturnv([x, 0]))),
                         (fun.vturns(fun.bturnv([x, config.state.ChunkSize * config.state.SubChunkSize]))), width=1)
        for y in range(0, config.state.ChunkSize * config.state.SubChunkSize):
            pg.draw.line(config.state.screen, line_color, (fun.vturns(fun.bturnv([0, y]))),
                         (fun.vturns(fun.bturnv([config.state.ChunkSize * config.state.SubChunkSize, y]))), width=1)
        for x in range(0, config.state.ChunkSize + 1):
            pg.draw.line(config.state.screen, line_color, (fun.vturns(fun.cturnv([x, 0]))), (fun.vturns(fun.cturnv([x, config.state.ChunkSize]))), width=3)
        for y in range(0, config.state.ChunkSize + 1):
            pg.draw.line(config.state.screen, line_color, (fun.vturns(fun.cturnv([0, y]))), (fun.vturns(fun.cturnv([config.state.ChunkSize, y]))), width=3)

    # 绘制gui
    for guis2 in sorted(config.state.GUIList, key=lambda g: g.priority):
        guis2.draw(config.state.screen)

    # 绘制准星
    config.state.screen.blit(config.state.icrosshair, (Mpos[0] - 15, Mpos[1] - 15))
    pg.display.update()
    pg.display.flip()