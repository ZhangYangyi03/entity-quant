entity-quant —— 与 entity-graph 配套的量化研究栈（2026-11-02 重建）
========================================================================

它不是什么
  不是投资建议，不是实盘交易系统，也没有"能自动赚钱"的结论。
  这个仓库存在的理由只有一个：把每一个数字都算到能被证伪为止。

它和 entity-graph 的关系
  entity-graph（github.com/ZhangYangyi03/entity-graph）是实体层：公司、卫星、
  电网、时间图、传导链；它回答"谁是谁、谁连谁、什么时候变的"。
  这里是数字层：把同一批实体接到价格上，问"这个连接值不值得交易"。
  分工是单向的 —— 实体图提供标的池与标签（板块、行业、供应链邻接、持股人），
  这边只做信号、回测、统计校正，从不反过来改写实体图。

  build_store.py 会把 A 股代码挂回 entitygraph 的节点/板块/行业标签，
  产出 graph_links.json；没有 entity-graph 也能跑，只是少了那层标签。

三层结果（都可以在这个仓库里复跑）
  一、ETF 池（8 只，2007 起）
      最强的配置是 20 日动量 k=2/k=3，净 CAGR 15.26% / 13.90%，NW-t 2.47/2.50，
      但 Deflated Z 只有 0.60/0.65 —— 过不了多重检验这道门。
  二、全市场 1897 只（创业板+科创板，2010-2026）
      等权基准 CAGR 22.72%。四个策略全部跑输：lowvol60 +7.88%（alpha -4.9, t=-1.5）、
      mom60 -24.5%、rev20 -25.2%、momvol60 -1.6%（费用吃掉 19%）。
  三、结论
      ETF 上那个"低波有效"的结论在 1897 只股票池里不成立 —— 8 只 ETF 里的低波
      实际是在选"国债+沪深300"，是资产配置效应，不是选股 alpha。
      详见 UNIVERSE.md。

为什么这里的数字可以相信一半
  engine.py / perf.py 里做了：隔夜成交、涨跌停、停牌、容量上限、分向成本、
  Newey-West t、Deflated Sharpe、PBO、alpha/beta 分解。
  全市场那一轮修掉了四个会凭空造出收益或亏损的引擎 bug（行下标错位、
  停牌当 0 元、卖出前算 per、调仓日没对齐），写进 UNIVERSE.md 第四节。
  METHOD.md 列了已知的坑，包括哪些格子里的数不能用。

怎么跑
  python run_backtest.py      # ETF 池，约 40 秒，写 results_etf.json
  python run_daily.py         # 每日收盘后：刷 K 线 -> 信号 -> 纸面账 -> daily.log
  python fetch_stocks.py      # 抓全市场日线到 stockdata/（断点续抓）
  python build_store.py       # CSV -> 列式二进制 store/，并挂 entity-graph 标签
  python run_universe.py a    # 全市场单策略 a..e，写 universe_results.json
  环境变量 OPENBLAS_NUM_THREADS=1 / OMP_NUM_THREADS=1：本机不设会 MemoryError。

还没做的（按优先级，来自 UNIVERSE.md 第五节）
  1. 扩到全 A 5563 只 + 沪深主板，摊平"只有创业板"的 2015 年偏差
  2. 行业/市值中性：拆掉市值与行业暴露后还剩多少 alpha
  3. 换手约束（单次调仓换手 < 30%）后再比一次成本
  4. 成本模型从固定费率换成平方根冲击模型

边界
  没有券商接口，没有下单权限，从不自动交易。paper.py 连 1 元现金买不起都记
  affordable=false，不写假成交。任何"能赚钱"的说法必须先过 Deflated Sharpe 和 PBO。

许可：研究代码，无担保。
