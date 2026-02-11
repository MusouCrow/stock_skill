#!/usr/bin/env python3
"""
OpenBB 股票分析工具单元测试
使用 mock 模拟 OpenBB API 响应
"""

import json
import sys
import unittest
from datetime import datetime
from io import StringIO
from unittest.mock import MagicMock, patch


class MockOBBResult:
    """模拟 OpenBB 返回结果"""
    def __init__(self, data):
        self.results = data

    def to_dict(self, orient="records"):
        if orient == "records":
            return self.results if isinstance(self.results, list) else [self.results]
        return self.results


class TestQuote(unittest.TestCase):
    """报价功能测试"""

    @patch('stock_tool.get_obb')
    def test_quote_single_symbol(self, mock_get_obb):
        """测试单个股票报价"""
        mock_obb = MagicMock()
        mock_get_obb.return_value = mock_obb

        mock_quote_data = [{
            "symbol": "AAPL",
            "name": "Apple Inc.",
            "price": 185.50,
            "change": 2.30,
            "change_percent": 1.25,
            "volume": 50000000,
            "day_high": 186.00,
            "day_low": 183.00,
        }]
        mock_obb.equity.price.quote.return_value = MockOBBResult(mock_quote_data)

        from stock_tool import cmd_quote
        import argparse
        args = argparse.Namespace(symbol="AAPL", provider="yfinance", format="json")

        captured_output = StringIO()
        sys.stdout = captured_output
        cmd_quote(args)
        sys.stdout = sys.__stdout__

        output = json.loads(captured_output.getvalue())
        self.assertEqual(len(output), 1)
        self.assertEqual(output[0]["symbol"], "AAPL")
        self.assertEqual(output[0]["price"], 185.50)

    @patch('stock_tool.get_obb')
    def test_quote_invalid_symbol(self, mock_get_obb):
        """测试无效股票代码处理"""
        mock_obb = MagicMock()
        mock_get_obb.return_value = mock_obb
        mock_obb.equity.price.quote.return_value = MockOBBResult([])

        from stock_tool import cmd_quote
        import argparse
        args = argparse.Namespace(symbol="INVALID123", provider="yfinance", format="json")

        captured_output = StringIO()
        sys.stdout = captured_output
        with self.assertRaises(SystemExit) as context:
            cmd_quote(args)
        sys.stdout = sys.__stdout__

        self.assertEqual(context.exception.code, 1)


class TestHistory(unittest.TestCase):
    """历史数据测试"""

    @patch('stock_tool.get_obb')
    def test_history_with_dates(self, mock_get_obb):
        """测试指定日期范围"""
        mock_obb = MagicMock()
        mock_get_obb.return_value = mock_obb

        mock_history_data = [
            {"date": "2024-01-02", "open": 180.0, "high": 182.0, "low": 179.0, "close": 181.5, "volume": 40000000},
            {"date": "2024-01-03", "open": 181.5, "high": 183.0, "low": 180.0, "close": 182.0, "volume": 45000000},
        ]
        mock_obb.equity.price.historical.return_value = MockOBBResult(mock_history_data)

        from stock_tool import cmd_history
        import argparse
        args = argparse.Namespace(
            symbol="AAPL", provider="yfinance", format="json",
            start="2024-01-01", end="2024-01-31", interval="1d"
        )

        captured_output = StringIO()
        sys.stdout = captured_output
        cmd_history(args)
        sys.stdout = sys.__stdout__

        output = json.loads(captured_output.getvalue())
        self.assertEqual(len(output), 2)
        self.assertIn("open", output[0])
        self.assertIn("close", output[0])

    @patch('stock_tool.get_obb')
    def test_history_with_interval(self, mock_get_obb):
        """测试不同时间间隔"""
        mock_obb = MagicMock()
        mock_get_obb.return_value = mock_obb

        mock_history_data = [
            {"date": "2024-01-02 09:30", "open": 180.0, "high": 180.5, "low": 179.5, "close": 180.2, "volume": 1000000},
        ]
        mock_obb.equity.price.historical.return_value = MockOBBResult(mock_history_data)

        from stock_tool import cmd_history
        import argparse
        args = argparse.Namespace(
            symbol="AAPL", provider="yfinance", format="json",
            start="2024-01-02", end="2024-01-02", interval="1h"
        )

        captured_output = StringIO()
        sys.stdout = captured_output
        cmd_history(args)
        sys.stdout = sys.__stdout__

        output = json.loads(captured_output.getvalue())
        self.assertIsInstance(output, list)
        mock_obb.equity.price.historical.assert_called_once()


class TestNews(unittest.TestCase):
    """新闻功能测试"""

    @patch('stock_tool.get_obb')
    def test_news_with_limit(self, mock_get_obb):
        """测试限制返回数量"""
        mock_obb = MagicMock()
        mock_get_obb.return_value = mock_obb

        mock_news_data = [
            {"title": "Apple announces new product", "date": "2024-01-15", "source": "Reuters", "url": "https://example.com/1"},
            {"title": "Apple stock rises", "date": "2024-01-14", "source": "Bloomberg", "url": "https://example.com/2"},
        ]
        mock_obb.news.company.return_value = MockOBBResult(mock_news_data)

        from stock_tool import cmd_news
        import argparse
        args = argparse.Namespace(
            symbol="AAPL", provider="yfinance", format="json",
            limit=5, start=None, end=None
        )

        captured_output = StringIO()
        sys.stdout = captured_output
        cmd_news(args)
        sys.stdout = sys.__stdout__

        output = json.loads(captured_output.getvalue())
        self.assertEqual(len(output), 2)
        self.assertIn("title", output[0])

    @patch('stock_tool.get_obb')
    def test_news_default(self, mock_get_obb):
        """测试默认参数"""
        mock_obb = MagicMock()
        mock_get_obb.return_value = mock_obb

        mock_news_data = [{"title": "Test news", "date": "2024-01-15"}]
        mock_obb.news.company.return_value = MockOBBResult(mock_news_data)

        from stock_tool import cmd_news
        import argparse
        args = argparse.Namespace(
            symbol="AAPL", provider="yfinance", format="json",
            limit=10, start=None, end=None
        )

        captured_output = StringIO()
        sys.stdout = captured_output
        cmd_news(args)
        sys.stdout = sys.__stdout__

        output = json.loads(captured_output.getvalue())
        self.assertIsInstance(output, list)


class TestTechnical(unittest.TestCase):
    """技术分析测试"""

    @patch('stock_tool.get_obb')
    def test_technical_rsi(self, mock_get_obb):
        """测试 RSI 指标"""
        mock_obb = MagicMock()
        mock_get_obb.return_value = mock_obb

        # 模拟历史数据
        mock_history = [{"date": f"2024-01-{i:02d}", "close": 180 + i} for i in range(1, 31)]
        mock_obb.equity.price.historical.return_value = MockOBBResult(mock_history)

        # 模拟 RSI 结果
        mock_rsi_data = [{"date": f"2024-01-{i:02d}", "RSI_14": 50 + i} for i in range(20, 31)]
        mock_obb.technical.rsi.return_value = MockOBBResult(mock_rsi_data)

        from stock_tool import cmd_technical
        import argparse
        args = argparse.Namespace(
            symbol="AAPL", provider="yfinance", format="json",
            indicators="rsi", period=14, start=None
        )

        captured_output = StringIO()
        sys.stdout = captured_output
        cmd_technical(args)
        sys.stdout = sys.__stdout__

        output = json.loads(captured_output.getvalue())
        self.assertEqual(output["symbol"], "AAPL")
        self.assertIn("rsi", output["indicators"])

    @patch('stock_tool.get_obb')
    def test_technical_macd(self, mock_get_obb):
        """测试 MACD 指标"""
        mock_obb = MagicMock()
        mock_get_obb.return_value = mock_obb

        mock_history = [{"date": f"2024-01-{i:02d}", "close": 180 + i} for i in range(1, 31)]
        mock_obb.equity.price.historical.return_value = MockOBBResult(mock_history)

        mock_macd_data = [{
            "date": "2024-01-30",
            "MACD_12_26_9": 1.5,
            "MACDs_12_26_9": 1.2,
            "MACDh_12_26_9": 0.3
        }]
        mock_obb.technical.macd.return_value = MockOBBResult(mock_macd_data)

        from stock_tool import cmd_technical
        import argparse
        args = argparse.Namespace(
            symbol="AAPL", provider="yfinance", format="json",
            indicators="macd", period=14, start=None
        )

        captured_output = StringIO()
        sys.stdout = captured_output
        cmd_technical(args)
        sys.stdout = sys.__stdout__

        output = json.loads(captured_output.getvalue())
        self.assertIn("macd", output["indicators"])

    @patch('stock_tool.get_obb')
    def test_technical_multiple(self, mock_get_obb):
        """测试多指标组合"""
        mock_obb = MagicMock()
        mock_get_obb.return_value = mock_obb

        mock_history = [{"date": f"2024-01-{i:02d}", "close": 180 + i} for i in range(1, 31)]
        mock_obb.equity.price.historical.return_value = MockOBBResult(mock_history)

        mock_obb.technical.rsi.return_value = MockOBBResult([{"RSI_14": 55}])
        mock_obb.technical.macd.return_value = MockOBBResult([{"MACD_12_26_9": 1.5, "MACDs_12_26_9": 1.2, "MACDh_12_26_9": 0.3}])
        mock_obb.technical.sma.return_value = MockOBBResult([{"SMA_14": 182.5}])

        from stock_tool import cmd_technical
        import argparse
        args = argparse.Namespace(
            symbol="AAPL", provider="yfinance", format="json",
            indicators="rsi,macd,sma", period=14, start=None
        )

        captured_output = StringIO()
        sys.stdout = captured_output
        cmd_technical(args)
        sys.stdout = sys.__stdout__

        output = json.loads(captured_output.getvalue())
        self.assertIn("rsi", output["indicators"])
        self.assertIn("macd", output["indicators"])
        self.assertIn("sma", output["indicators"])


class TestInterpretations(unittest.TestCase):
    """指标解读测试"""

    def test_interpret_rsi(self):
        """测试 RSI 解读"""
        from stock_tool import interpret_rsi

        self.assertIn("超买", interpret_rsi(75))
        self.assertIn("超卖", interpret_rsi(25))
        self.assertIn("多头", interpret_rsi(60))
        self.assertIn("空头", interpret_rsi(40))
        self.assertIn("无法计算", interpret_rsi(None))

    def test_interpret_macd(self):
        """测试 MACD 解读"""
        from stock_tool import interpret_macd

        self.assertIn("金叉", interpret_macd({"macd": 1.5, "signal": 1.0, "histogram": 0.5}))
        self.assertIn("死叉", interpret_macd({"macd": -1.5, "signal": -1.0, "histogram": -0.5}))
        self.assertIn("无法计算", interpret_macd({}))

    def test_interpret_adx(self):
        """测试 ADX 解读"""
        from stock_tool import interpret_adx

        self.assertIn("趋势明显", interpret_adx(30))
        self.assertIn("震荡", interpret_adx(20))
        self.assertIn("无法计算", interpret_adx(None))

    def test_interpret_stoch(self):
        """测试随机指标解读"""
        from stock_tool import interpret_stoch

        self.assertIn("超买", interpret_stoch({"k": 85, "d": 82}))
        self.assertIn("超卖", interpret_stoch({"k": 15, "d": 18}))
        self.assertIn("无法计算", interpret_stoch({}))


class TestFormatOutput(unittest.TestCase):
    """输出格式测试"""

    def test_json_format(self):
        """测试 JSON 格式输出"""
        from stock_tool import format_output

        data = [{"a": 1, "b": 2}]
        output = format_output(data, "json")
        parsed = json.loads(output)
        self.assertEqual(parsed, data)

    def test_table_format(self):
        """测试表格格式输出"""
        from stock_tool import format_output

        data = [{"name": "AAPL", "price": 185.5}, {"name": "GOOGL", "price": 140.0}]
        output = format_output(data, "table")
        self.assertIn("name", output)
        self.assertIn("price", output)
        self.assertIn("AAPL", output)


if __name__ == "__main__":
    unittest.main()
