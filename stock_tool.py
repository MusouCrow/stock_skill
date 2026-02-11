#!/usr/bin/env python3
"""
OpenBB 股票分析工具脚本
供 Claude Code/Codex 使用，封装 OpenBB 库功能
"""

import argparse
import json
import sys
from datetime import datetime, timedelta
from typing import Any, Optional


def get_obb():
    """延迟导入 OpenBB 以加快脚本启动"""
    from openbb import obb
    return obb


def find_indicator_key(data: dict, pattern: str) -> Optional[str]:
    """查找包含指定模式的 key（OpenBB 返回的 key 可能有前缀如 close_RSI_14）"""
    for key in data.keys():
        if pattern in key:
            return key
    return None


def get_indicator_value(data: dict, pattern: str) -> Optional[float]:
    """获取指标值"""
    key = find_indicator_key(data, pattern)
    return data.get(key) if key else None


def format_output(data: Any, fmt: str = "json") -> str:
    """格式化输出数据"""
    if fmt == "json":
        return json.dumps(data, indent=2, default=str, ensure_ascii=False)
    elif fmt == "table":
        if isinstance(data, list) and data:
            headers = list(data[0].keys())
            rows = [[str(row.get(h, "")) for h in headers] for row in data]
            col_widths = [max(len(h), max((len(r[i]) for r in rows), default=0)) for i, h in enumerate(headers)]
            header_line = " | ".join(h.ljust(col_widths[i]) for i, h in enumerate(headers))
            separator = "-+-".join("-" * w for w in col_widths)
            data_lines = [" | ".join(r[i].ljust(col_widths[i]) for i in range(len(headers))) for r in rows]
            return "\n".join([header_line, separator] + data_lines)
        return str(data)
    return str(data)


def cmd_quote(args):
    """获取股票实时报价"""
    obb = get_obb()
    try:
        result = obb.equity.price.quote(args.symbol, provider=args.provider)
        if result.results:
            data = result.to_dict(orient="records") if hasattr(result, 'to_dict') else [vars(r) for r in result.results]
            print(format_output(data, args.format))
        else:
            print(json.dumps({"error": "No data returned", "symbol": args.symbol}))
            sys.exit(1)
    except Exception as e:
        print(json.dumps({"error": str(e), "symbol": args.symbol}))
        sys.exit(1)


def cmd_history(args):
    """获取历史价格数据"""
    obb = get_obb()
    try:
        kwargs = {
            "symbol": args.symbol,
            "provider": args.provider,
        }
        if args.start:
            kwargs["start_date"] = args.start
        if args.end:
            kwargs["end_date"] = args.end
        if args.interval:
            kwargs["interval"] = args.interval

        result = obb.equity.price.historical(**kwargs)
        if result.results:
            data = result.to_dict(orient="records") if hasattr(result, 'to_dict') else [vars(r) for r in result.results]
            print(format_output(data, args.format))
        else:
            print(json.dumps({"error": "No data returned", "symbol": args.symbol}))
            sys.exit(1)
    except Exception as e:
        print(json.dumps({"error": str(e), "symbol": args.symbol}))
        sys.exit(1)


def cmd_news(args):
    """获取股票相关新闻"""
    obb = get_obb()
    try:
        kwargs = {
            "symbol": args.symbol,
            "provider": args.provider,
        }
        if args.limit:
            kwargs["limit"] = args.limit
        if args.start:
            kwargs["start_date"] = args.start
        if args.end:
            kwargs["end_date"] = args.end

        result = obb.news.company(**kwargs)
        if result.results:
            data = result.to_dict(orient="records") if hasattr(result, 'to_dict') else [vars(r) for r in result.results]
            print(format_output(data, args.format))
        else:
            print(json.dumps({"error": "No news found", "symbol": args.symbol}))
            sys.exit(1)
    except Exception as e:
        print(json.dumps({"error": str(e), "symbol": args.symbol}))
        sys.exit(1)


def cmd_technical(args):
    """技术分析指标计算"""
    obb = get_obb()
    try:
        # 先获取历史数据
        hist_kwargs = {
            "symbol": args.symbol,
            "provider": args.provider,
        }
        if args.start:
            hist_kwargs["start_date"] = args.start
        else:
            # 默认获取过去一年数据用于技术分析
            hist_kwargs["start_date"] = (datetime.now() - timedelta(days=365)).strftime("%Y-%m-%d")

        history = obb.equity.price.historical(**hist_kwargs)
        if not history.results:
            print(json.dumps({"error": "No historical data for technical analysis", "symbol": args.symbol}))
            sys.exit(1)

        indicators = [ind.strip().lower() for ind in args.indicators.split(",")]
        results = {"symbol": args.symbol, "indicators": {}}

        for indicator in indicators:
            try:
                if indicator == "rsi":
                    ind_result = obb.technical.rsi(data=history.results, length=args.period)
                    if ind_result.results:
                        data = ind_result.to_dict(orient="records")[-10:]  # 最近10条
                        latest = data[-1] if data else {}
                        rsi_val = get_indicator_value(latest, f"RSI_{args.period}")
                        results["indicators"]["rsi"] = {
                            "latest": rsi_val,
                            "period": args.period,
                            "recent_data": data,
                            "interpretation": interpret_rsi(rsi_val)
                        }

                elif indicator == "macd":
                    ind_result = obb.technical.macd(data=history.results)
                    if ind_result.results:
                        data = ind_result.to_dict(orient="records")[-10:]
                        latest = data[-1] if data else {}
                        macd_val = get_indicator_value(latest, "MACD_12_26_9")
                        signal_val = get_indicator_value(latest, "MACDs_12_26_9")
                        hist_val = get_indicator_value(latest, "MACDh_12_26_9")
                        results["indicators"]["macd"] = {
                            "latest_macd": macd_val,
                            "latest_signal": signal_val,
                            "latest_histogram": hist_val,
                            "recent_data": data,
                            "interpretation": interpret_macd({"macd": macd_val, "signal": signal_val, "histogram": hist_val})
                        }

                elif indicator == "sma":
                    ind_result = obb.technical.sma(data=history.results, length=args.period)
                    if ind_result.results:
                        data = ind_result.to_dict(orient="records")[-10:]
                        latest = data[-1] if data else {}
                        sma_val = get_indicator_value(latest, f"SMA_{args.period}")
                        results["indicators"]["sma"] = {
                            "latest": sma_val,
                            "period": args.period,
                            "recent_data": data
                        }

                elif indicator == "ema":
                    ind_result = obb.technical.ema(data=history.results, length=args.period)
                    if ind_result.results:
                        data = ind_result.to_dict(orient="records")[-10:]
                        latest = data[-1] if data else {}
                        ema_val = get_indicator_value(latest, f"EMA_{args.period}")
                        results["indicators"]["ema"] = {
                            "latest": ema_val,
                            "period": args.period,
                            "recent_data": data
                        }

                elif indicator == "bbands":
                    ind_result = obb.technical.bbands(data=history.results, length=args.period)
                    if ind_result.results:
                        data = ind_result.to_dict(orient="records")[-10:]
                        latest = data[-1] if data else {}
                        results["indicators"]["bbands"] = {
                            "upper": get_indicator_value(latest, f"BBU_{args.period}"),
                            "middle": get_indicator_value(latest, f"BBM_{args.period}"),
                            "lower": get_indicator_value(latest, f"BBL_{args.period}"),
                            "period": args.period,
                            "recent_data": data
                        }

                elif indicator == "adx":
                    ind_result = obb.technical.adx(data=history.results, length=args.period)
                    if ind_result.results:
                        data = ind_result.to_dict(orient="records")[-10:]
                        latest = data[-1] if data else {}
                        adx_val = get_indicator_value(latest, f"ADX_{args.period}")
                        results["indicators"]["adx"] = {
                            "latest": adx_val,
                            "period": args.period,
                            "recent_data": data,
                            "interpretation": interpret_adx(adx_val)
                        }

                elif indicator == "stoch":
                    ind_result = obb.technical.stoch(data=history.results)
                    if ind_result.results:
                        data = ind_result.to_dict(orient="records")[-10:]
                        latest = data[-1] if data else {}
                        k_val = get_indicator_value(latest, "STOCHk_14_3_3")
                        d_val = get_indicator_value(latest, "STOCHd_14_3_3")
                        results["indicators"]["stoch"] = {
                            "k": k_val,
                            "d": d_val,
                            "recent_data": data,
                            "interpretation": interpret_stoch({"k": k_val, "d": d_val})
                        }

                else:
                    results["indicators"][indicator] = {"error": f"Unsupported indicator: {indicator}"}

            except Exception as e:
                results["indicators"][indicator] = {"error": str(e)}

        print(format_output(results, args.format))

    except Exception as e:
        print(json.dumps({"error": str(e), "symbol": args.symbol}))
        sys.exit(1)


def interpret_rsi(value: Optional[float]) -> str:
    """解读 RSI 指标"""
    if value is None:
        return "无法计算"
    if value >= 70:
        return "超买区域，可能面临回调压力"
    elif value <= 30:
        return "超卖区域，可能存在反弹机会"
    elif value >= 50:
        return "偏强势，多头占优"
    else:
        return "偏弱势，空头占优"


def interpret_macd(data: dict) -> str:
    """解读 MACD 指标"""
    macd = data.get("macd")
    signal = data.get("signal")
    histogram = data.get("histogram")

    if macd is None or signal is None:
        return "无法计算"

    if histogram is None:
        histogram = macd - signal

    if macd > signal and histogram > 0:
        return "金叉形态，多头信号"
    elif macd < signal and histogram < 0:
        return "死叉形态，空头信号"
    elif macd > 0:
        return "MACD 在零轴上方，整体偏多"
    else:
        return "MACD 在零轴下方，整体偏空"


def interpret_adx(value: Optional[float]) -> str:
    """解读 ADX 指标"""
    if value is None:
        return "无法计算"
    if value >= 25:
        return "趋势明显，适合趋势跟踪策略"
    else:
        return "趋势不明显，市场可能处于震荡"


def interpret_stoch(data: dict) -> str:
    """解读随机指标"""
    k = data.get("k")
    d = data.get("d")

    if k is None or d is None:
        return "无法计算"

    if k >= 80 and d >= 80:
        return "超买区域，注意回调风险"
    elif k <= 20 and d <= 20:
        return "超卖区域，可能存在反弹机会"
    elif k > d:
        return "K线上穿D线，短期偏多"
    else:
        return "K线下穿D线，短期偏空"


def main():
    parser = argparse.ArgumentParser(
        description="OpenBB 股票分析工具 - 供 Claude Code/Codex 使用",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  python stock_tool.py quote AAPL
  python stock_tool.py history AAPL --start 2024-01-01 --end 2024-12-31
  python stock_tool.py news AAPL --limit 10
  python stock_tool.py technical AAPL --indicators rsi,macd,sma --period 14
        """
    )
    parser.add_argument("--format", "-f", choices=["json", "table"], default="json",
                        help="输出格式 (默认: json)")

    subparsers = parser.add_subparsers(dest="command", help="可用命令")

    # quote 子命令
    quote_parser = subparsers.add_parser("quote", help="获取股票实时报价")
    quote_parser.add_argument("symbol", help="股票代码")
    quote_parser.add_argument("--provider", "-p", default="yfinance",
                              help="数据提供商 (默认: yfinance)")
    quote_parser.set_defaults(func=cmd_quote)

    # history 子命令
    history_parser = subparsers.add_parser("history", help="获取历史价格数据")
    history_parser.add_argument("symbol", help="股票代码")
    history_parser.add_argument("--start", "-s", help="开始日期 (YYYY-MM-DD)")
    history_parser.add_argument("--end", "-e", help="结束日期 (YYYY-MM-DD)")
    history_parser.add_argument("--interval", "-i", default="1d",
                                help="时间间隔 (1m, 5m, 15m, 30m, 1h, 1d, 1wk, 1mo)")
    history_parser.add_argument("--provider", "-p", default="yfinance",
                                help="数据提供商 (默认: yfinance)")
    history_parser.set_defaults(func=cmd_history)

    # news 子命令
    news_parser = subparsers.add_parser("news", help="获取股票相关新闻")
    news_parser.add_argument("symbol", help="股票代码")
    news_parser.add_argument("--limit", "-l", type=int, default=10,
                             help="返回新闻数量 (默认: 10)")
    news_parser.add_argument("--start", "-s", help="开始日期 (YYYY-MM-DD)")
    news_parser.add_argument("--end", "-e", help="结束日期 (YYYY-MM-DD)")
    news_parser.add_argument("--provider", "-p", default="yfinance",
                             help="数据提供商 (默认: yfinance)")
    news_parser.set_defaults(func=cmd_news)

    # technical 子命令
    tech_parser = subparsers.add_parser("technical", help="技术分析指标")
    tech_parser.add_argument("symbol", help="股票代码")
    tech_parser.add_argument("--indicators", "-i", default="rsi,macd,sma",
                             help="指标列表，逗号分隔 (rsi,macd,sma,ema,bbands,adx,stoch)")
    tech_parser.add_argument("--period", "-n", type=int, default=14,
                             help="指标周期 (默认: 14)")
    tech_parser.add_argument("--start", "-s", help="历史数据开始日期 (YYYY-MM-DD)")
    tech_parser.add_argument("--provider", "-p", default="yfinance",
                             help="数据提供商 (默认: yfinance)")
    tech_parser.set_defaults(func=cmd_technical)

    args = parser.parse_args()

    if args.command is None:
        parser.print_help()
        sys.exit(1)

    args.func(args)


if __name__ == "__main__":
    main()
