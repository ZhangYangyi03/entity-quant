"""全市场截面信号：按交易日推进，O(股票数 × 调仓次数)。

为什么这么写：沙箱进程内存上限约 490MB（实测 MemoryError），
1897 只股票 × 4130 天装不进内存，所以走 mmap + 行游标。
"""
import math


def series_metrics(bars, code, end_idx, n_ret):
    """用第 end_idx 行往前 n_ret 个收益，返回 (波动率, 累计涨幅, 平均成交额)。"""
    if end_idx < n_ret + 1: return None
    rets = []
    prev = bars.row_i(code, end_idx - n_ret)
    if prev is None: return None
    for k in range(end_idx - n_ret + 1, end_idx + 1):
        r = bars.row_i(code, k)
        if r is None: return None
        if prev[1] <= 0 or r[4] <= 0: return None    # 收盘价<=0 或停牌
        rets.append(r[1] / prev[1] - 1)
        prev = r
    if len(rets) < n_ret - 2: return None
    m = sum(rets) / len(rets)
    var = sum((x - m) ** 2 for x in rets) / (len(rets) - 1)
    vol = math.sqrt(var)
    cum = 1.0
    for x in rets: cum *= (1 + x)
    adv = 0.0; cnt = 0
    for k in range(max(0, end_idx - 19), end_idx + 1):
        r = bars.row_i(code, k)
        if r: adv += r[5]; cnt += 1
    return vol, cum - 1.0, (adv / cnt if cnt else 0.0), rets


def cross_section(bars, date, kind, n, min_price=2.0, min_adv=3e7):
    """返回 {code: score}，只用 date 及更早的数据（date 当行 = 当日收盘）。"""
    out = {}
    target = date.encode()
    for code in bars.meta:
        j = bars.bisect_abs(code, date)
        if j is None: continue
        m = series_metrics(bars, code, j, n)
        if m is None: continue
        vol, cum, adv, _ = m
        px = bars.row_i(code, j)[1]
        if px < min_price or adv < min_adv: continue
        if kind == "lowvol":
            if vol <= 0: continue
            out[code] = -vol
        elif kind == "mom":
            out[code] = cum
        elif kind == "momvol":
            if vol <= 0: continue
            out[code] = cum / vol
        elif kind == "rev":
            out[code] = -cum
        elif kind == "lowvol_mom":
            if vol <= 0: continue
            out[code] = -vol + 0.5 * cum
    return out
