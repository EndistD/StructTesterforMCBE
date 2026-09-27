import random
import config
import functions as fun
import blocks


def runonce():
    # S0 更新区块优先级
    if config.state.tick % 20 == 0:          # 跨区块顺序
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

