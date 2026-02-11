---
name: analyzing-stocks
description: 分析股票的技术面和消息面，获取实时报价、历史价格、新闻资讯和技术指标（RSI、MACD、布林带等），生成交易建议。当用户询问股票分析、股价走势、技术指标或交易建议时使用。
---

# 股票分析工具

基于 OpenBB 的股票分析工具，提供技术面和消息面分析能力。

## 快速开始

```bash
# 获取实时报价
python stock_tool.py quote AAPL

# 获取历史数据
python stock_tool.py history AAPL --start 2024-01-01

# 获取新闻
python stock_tool.py news AAPL --limit 10

# 技术分析
python stock_tool.py technical AAPL --indicators rsi,macd,bbands
```

## 命令详解

### quote - 实时报价

```bash
python stock_tool.py quote <股票代码> [--provider yfinance]
```

### history - 历史数据

```bash
python stock_tool.py history <股票代码> \
  --start YYYY-MM-DD \
  --end YYYY-MM-DD \
  --interval 1d  # 可选: 1m, 5m, 15m, 30m, 1h, 1d, 1wk, 1mo
```

### news - 新闻资讯

```bash
python stock_tool.py news <股票代码> --limit 10
```

### technical - 技术指标

```bash
python stock_tool.py technical <股票代码> \
  --indicators rsi,macd,sma,ema,bbands,adx,stoch \
  --period 14
```

支持的指标：
- **RSI**: 相对强弱指数，判断超买超卖
- **MACD**: 趋势跟踪指标，识别金叉死叉
- **SMA/EMA**: 移动平均线
- **BBands**: 布林带，判断价格波动区间
- **ADX**: 趋势强度指标
- **Stoch**: 随机指标

## 分析工作流

1. 获取实时报价了解当前价格
2. 获取历史数据观察价格走势
3. 计算技术指标判断买卖信号
4. 获取新闻了解消息面影响
5. 综合技术面和消息面给出交易建议

## 指标解读

| 指标 | 超买信号 | 超卖信号 |
|------|----------|----------|
| RSI | > 70 | < 30 |
| Stoch K/D | > 80 | < 20 |
| MACD | 金叉（MACD > Signal） | 死叉（MACD < Signal） |
| ADX | > 25 趋势明显 | < 25 震荡市 |

## 输出格式

默认 JSON 格式，可用 `--format table` 切换表格输出。
