import config


def vturns(vpos):
    sx = config.state.Spos[0] + (vpos[0] - config.state.Vpos[0]) / config.state.Zoom
    sy = config.state.Spos[1] + (vpos[1] - config.state.Vpos[1]) / config.state.Zoom
    return [sx, sy]


def sturnv(spos):
    vx = config.state.Vpos[0] + (spos[0] - config.state.Spos[0]) * config.state.Zoom
    vy = config.state.Vpos[1] + (spos[1] - config.state.Spos[1]) * config.state.Zoom
    return [vx, vy]


def vturnc(vpos):
    cx = vpos[0] // (config.state.BaseBlockSize * config.state.SubChunkSize)
    cy = vpos[1] // (config.state.BaseBlockSize * config.state.SubChunkSize)
    return [cx, cy]


def vturnb(vpos):
    xx = vpos[0] // config.state.BaseBlockSize
    yy = vpos[1] // config.state.BaseBlockSize
    return [xx, yy]


def vturnub(vpos):
    xx = vpos[0] // config.state.BaseBlockSize - vturnc(vpos)[0] * 16
    yy = vpos[1] // config.state.BaseBlockSize - vturnc(vpos)[1] * 16
    return [xx, yy]


def cturncid(cpos):
    cid = cpos[0] + cpos[1] * config.state.ChunkSize
    return int(cid)


def ubturnbid(ubpos):
    bid = ubpos[0] + ubpos[1] * 16
    return int(bid)


# ── id → 坐标 ──
def cidturnc(cid):
    cx = cid % config.state.ChunkSize
    cy = cid // config.state.ChunkSize
    return [cx, cy]


def bidturnub(bid):
    ubx = bid % 16
    uby = bid // 16
    return [ubx, uby]


def idturnb(cid, bid):
    bx = cidturnc(cid)[0] * 16 + bidturnub(bid)[0]
    cx = cidturnc(cid)[1] * 16 + bidturnub(bid)[1]
    return [bx, cx]


def cturnv(cpos):
    vx = cpos[0] * (config.state.BaseBlockSize * config.state.SubChunkSize)
    vy = cpos[1] * (config.state.BaseBlockSize * config.state.SubChunkSize)
    return [vx, vy]


def bturnv(bpos):
    vx = bpos[0] * config.state.BaseBlockSize
    vy = bpos[1] * config.state.BaseBlockSize
    return [vx, vy]


def subclass(upclass):
    classlist = [cls for cls in upclass.__subclasses__()]
    return classlist


def bturnid(bpos, move=0, towards=0):
    bpos2 = bpos[:]
    match towards:
        case 0:
            if 0 <= bpos2[1] - move < config.state.ChunkSize * 16 - 1:
                bpos2[1] -= move
        case 1:
            if 0 <= bpos2[0] + move < config.state.ChunkSize * 16:
                bpos2[0] += move
        case 2:
            if 0 <= bpos2[1] + move < config.state.ChunkSize * 16 - 1:
                bpos2[1] += move
        case 3:
            if 0 <= bpos2[0] - move < config.state.ChunkSize * 16:
                bpos2[0] -= move
    cid = cturncid(vturnc(bturnv(bpos2)))
    bid = ubturnbid(vturnub(bturnv(bpos2)))
    return cid, bid


def bturnblock(bpos):
    cid = cturncid(vturnc(bturnv(bpos)))
    bid = ubturnbid(vturnub(bturnv(bpos)))
    if 0 <= cid < len(config.state.ChunkList):
        sub_list = config.state.ChunkList[cid]
        if 0 <= bid < len(sub_list):
            return sub_list[bid]
    from blocks import NullBlock
    return NullBlock()


def bposmove(bpos, towards, step=1):
    deltax, deltay = 0, 0
    match towards:
        case 0:
            deltay = -1
        case 1:
            deltax = 1
        case 2:
            deltay = 1
        case 3:
            deltax = -1
    newposx = bpos[0] + deltax * step
    newposy = bpos[1] + deltay * step
    return [newposx, newposy]


def reverse(towards):
    match towards:
        case 0:
            return 2
        case 1:
            return 3
        case 2:
            return 0
        case 3:
            return 1
    return 0


def testmatrix(center, width):
    cx, cy = center[0], center[1]
    if width == 0:
        return not bturnblock([cx, cy]).pretend
    for x in range(cx - width, cx + width + 1):
        if bturnblock([x, cy - width]).pretend:
            return False
    for x in range(cx - width, cx + width + 1):
        if bturnblock([x, cy + width]).pretend:
            return False
    for y in range(cy - width + 1, cy + width):
        if bturnblock([cx - width, y]).pretend:
            return False
    for y in range(cy - width + 1, cy + width):
        if bturnblock([cx + width, y]).pretend:
            return False
    return True


def findlastelement(target, emptyvalue=0):
    for step in reversed(range(len(target))):
        if target[step] != emptyvalue:
            return step
    return -1


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
    config.state.ChunkList = [[blocks.Air(cidturnc(c), bidturnub(b)) for b in range(ss * ss)]
                              for c in range(cs * cs)]
    config.state.ZoneList = [[[] for b in range(ss * ss)]
                             for c in range(cs * cs)]
    config.state.ChunkOrder = list(range(cs * cs))
    config.state.BlockOrder = list(range(ss * ss))

    from simulation import createbarrier
    createbarrier(config.state.ChunkList)