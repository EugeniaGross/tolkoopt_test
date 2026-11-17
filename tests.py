import asyncio
import unittest
from decimal import Decimal

from starter import recommend_price


class RecommendPriceTests(unittest.IsolatedAsyncioTestCase):

    async def test_normal_calculation(self):
        """Проверяем обычный расчёт цены."""

        async def fetch_offers():
            return {
                "status": "success",
                "offers": [
                    {
                        "seller": "myshop",
                        "price": Decimal("4300.00"),
                        "delivery_days": 2,
                    },
                    {
                        "seller": "PARTS",
                        "price": Decimal("4800.00"),
                        "delivery_days": 3,
                    },
                    {
                        "seller": "SLOW",
                        "price": Decimal("4700.00"),
                        "delivery_days": 8,
                    },
                ],
            }

        result = await recommend_price(
            fetch_offers,
            Decimal("4900.00"),
            Decimal("4500.00"),
        )

        self.assertEqual(result["price"], Decimal("4728.00"))
        self.assertEqual(result["decision"], "APPLY")

    async def test_no_suitable_offers(self):
        """Если подходящих предложений нет, возвращаем текущую цену."""

        async def fetch_offers():
            return {
                "status": "success",
                "offers": [
                    {
                        "seller": "MYSHOP",
                        "price": Decimal("4300.00"),
                        "delivery_days": 2,
                    },
                    {
                        "seller": "PARTS",
                        "price": Decimal("4700.00"),
                        "delivery_days": None,
                    },
                ],
            }

        result = await recommend_price(
            fetch_offers,
            Decimal("4000.00"),
            Decimal("4500.00"),
        )

        self.assertEqual(result["price"], Decimal("4000.00"))
        self.assertEqual(result["decision"], "HOLD")

    async def test_fetch_timeout(self):
        """При превышении времени ожидания возвращаем HOLD."""

        async def fetch_offers():
            await asyncio.sleep(1)

        result = await recommend_price(
            fetch_offers,
            Decimal("4900.00"),
            Decimal("4500.00"),
            timeout_s=0.01,
        )

        self.assertEqual(result["price"], Decimal("4900.00"))
        self.assertEqual(result["decision"], "HOLD")

    async def test_exactly_30_percent_deviation(self):
        """Отклонение ровно на 30% допускается."""

        async def fetch_offers():
            return {
                "status": "success",
                "offers": [
                    {
                        "seller": "PARTS",
                        "price": Decimal("131.98"),
                        "delivery_days": 2,
                    },
                ],
            }

        result = await recommend_price(
            fetch_offers,
            Decimal("100.00"),
            Decimal("1.00"),
        )

        self.assertEqual(result["price"], Decimal("130.00"))
        self.assertEqual(result["decision"], "APPLY")

    async def test_deviation_more_than_30_percent(self):
        """При отклонении больше 30% требуется ручная проверка."""

        async def fetch_offers():
            return {
                "status": "success",
                "offers": [
                    {
                        "seller": "PARTS",
                        "price": Decimal("132.00"),
                        "delivery_days": 2,
                    },
                ],
            }

        result = await recommend_price(
            fetch_offers,
            Decimal("100.00"),
            Decimal("1.00"),
        )

        self.assertEqual(result["price"], Decimal("130.02"))
        self.assertEqual(result["decision"], "REVIEW")


if __name__ == "__main__":
    unittest.main()
