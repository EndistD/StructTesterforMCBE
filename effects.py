import pygame as pg
import config
import functions as fun


class FadeEffect:
    def __init__(self, abpos, color, duration):
        self.abpos = abpos          # 绝对坐标
        self.color = color          # RGB
        self.start_time = pg.time.get_ticks()
        self.duration = duration    # 持续时间

    def draw(self, screen):
        elapsed = pg.time.get_ticks() - self.start_time
        if elapsed >= self.duration:
            return
        alpha = int(255 * 0.8 * (1 - elapsed / self.duration))  # 初始透明度80%
        vpos = fun.bturnv(self.abpos)
        spos = fun.vturns(vpos)
        size = config.state.BaseBlockSize / config.state.Zoom
        surf = pg.Surface((size, size), pg.SRCALPHA)
        surf.fill((*self.color, alpha))
        screen.blit(surf, spos)


# 全局特效列表
effects_list = []

def create_fade(abpos, color, duration=500):
    effects_list.append(FadeEffect(abpos, color, duration))


def draw_effects(screen):
    alive = []
    for effect in effects_list:
        if pg.time.get_ticks() - effect.start_time < effect.duration:
            effect.draw(screen)
            alive.append(effect)
    effects_list.clear()
    effects_list.extend(alive)