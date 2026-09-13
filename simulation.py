import random
import config
import functions as fun
import blocks


def runonce():
    # 打乱更新顺序
    if config.state.tick % 10 == 0:
        random.shuffle(config.state.ChunkOrder)
    random.shuffle(config.state.BlockOrder)
    config.state.tick += 1

    # 遍历区域
    for chu in [config.state.ZoneList[x1] for x1 in config.state.ChunkOrder]:
        for blks in [chu[x2] for x2 in config.state.BlockOrder]:
            for zons in blks:
                zons.function()

    # 充能重置
    for chu in [config.state.ChunkList[x1] for x1 in config.state.ChunkOrder]:
        for blks in [chu[x2] for x2 in config.state.BlockOrder]:
            blks.actived = False
            blks.powered = False

    # 充能执行
    for chu in [config.state.ChunkList[x1] for x1 in config.state.ChunkOrder]:
        for blks in [chu[x2] for x2 in config.state.BlockOrder]:
            # 能量源充能
            if blks.has_generate == True:
                blks.generate()
            # 区域充能
            if blks.zone_powered == True and blks.can_powered == True and blks.moving_time == 0:
                blks.powered = True
            elif blks.zone_powered == True and blks.can_powered != True and blks.has_function == True and blks.moving_time == 0:
                blks.actived = True

    for chu in [config.state.ChunkList[x1] for x1 in config.state.ChunkOrder]:
        for blks in [chu[x2] for x2 in config.state.BlockOrder]:
            # 激活
            if blks.powered == True and blks.moving_time == 0:
                if blks.has_function == True:
                    blks.actived = True
                for towards in range(4):
                    if (config.state.ChunkList[fun.bturnid(blks.abpos, 1, towards)[0]][
                            fun.bturnid(blks.abpos, 1, towards)[1]].has_function == True
                        and config.state.ChunkList[fun.bturnid(blks.abpos, 1, towards)[0]][
                            fun.bturnid(blks.abpos, 1, towards)[1]].moving_time == 0) \
                            and not (config.state.ChunkList[fun.bturnid(blks.abpos, 1, towards)[0]][
                                         fun.bturnid(blks.abpos, 1, towards)[1]].target_generate
                                     and config.state.ChunkList[fun.bturnid(blks.abpos, 1, towards)[0]][
                                         fun.bturnid(blks.abpos, 1, towards)[1]].towards == fun.reverse(towards)):
                        config.state.ChunkList[fun.bturnid(blks.abpos, 1, towards)[0]][
                            fun.bturnid(blks.abpos, 1, towards)[1]].actived = True

    # 侦测器记录
    for chu in [config.state.ChunkList[x1] for x1 in config.state.ChunkOrder]:
        for blks in [chu[x2] for x2 in config.state.BlockOrder]:
            if type(blks) == blocks.Obsever:
                blks.check()

    # 功能执行
    for chu in [config.state.ChunkList[x1] for x1 in config.state.ChunkOrder]:
        for blks in [chu[x2] for x2 in config.state.BlockOrder]:
            if blks.has_function == True:
                blks.function()


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

