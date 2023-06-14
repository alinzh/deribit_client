from aiounittest import AsyncTestCase
from database_and_requests import RequestDerebit


class TestRequestDerebit(AsyncTestCase):
    """
    Test `RequestDerebit.request` method if received from the exchange data is correct.
    """

    async def check_result(self, data):
        """
        Check if `result` key is present in the data dictionary.
        Returns True if present, False otherwise.
        """
        return "result" in data

    async def test_request(self):
        """
        Test on request by APT to Deribit.
        Func is checks if the answer is a dict, or not. If not - no response received.
        """
        message_btc = {
            "jsonrpc": "2.0",
            "id": 8106,
            "method": "public/ticker",
            "params": {
                "instrument_name": "BTC-PERPETUAL"
            }
        }
        message_eth = {
            "jsonrpc": "2.0",
            "id": 8107,
            "method": "public/ticker",
            "params": {
                "instrument_name": "ETH-PERPETUAL"
            }
        }
        answer_btc = await RequestDerebit().request(message_btc)
        answer_eth = await RequestDerebit().request(message_eth)

        self.assertIsInstance(answer_btc, dict)
        self.assertIsInstance(answer_eth, dict)

        # Check if result in response or not
        result_btc = await self.check_result(answer_btc)
        result_eth = await self.check_result(answer_eth)

        self.assertTrue(result_btc)
        self.assertTrue(result_eth)


if __name__ == '__main__':
    TestRequestDerebit().run_async()
