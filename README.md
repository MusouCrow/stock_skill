# Stock Analysis Skill

基于 OpenBB 的股票分析工具，供 Claude Code/Codex 使用，提供股票交易数据获取、新闻数据获取和技术分析能力。

## 功能

- **实时报价** - 获取股票当前价格、涨跌幅、成交量等
- **历史数据** - 获取 OHLCV 历史价格数据
- **新闻资讯** - 获取股票相关新闻
- **技术分析** - RSI、MACD、SMA、EMA、布林带、ADX、随机指标

## 安装

```bash
pip install -r requirements.txt
```

## 快速开始

```bash
# 获取报价
python stock_tool.py quote AAPL

# 获取历史数据
python stock_tool.py history AAPL --start 2024-01-01

# 获取新闻
python stock_tool.py news AAPL --limit 5

# 技术分析
python stock_tool.py technical AAPL --indicators rsi,macd,sma
```

## 详细文档

参见 [SKILL.md](SKILL.md)

## 测试

```bash
python -m pytest test_stock_tool.py -v
```
