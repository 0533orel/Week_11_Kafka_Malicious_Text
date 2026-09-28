import os
import unittest
from unittest.mock import patch, MagicMock
from common.demo_source import load_demo, publish_demo
from services.retriever import app


class SourceTests(unittest.TestCase):
    def setUp(self):
        guard = patch("socket.socket.connect", side_effect=AssertionError("Network forbidden"))
        guard.start()
        self.addCleanup(guard.stop)

    def test_demo_entrypoint_publishes_both_routes_without_mongo(self):
        with patch.dict(os.environ, {}, clear=True), patch.object(app, "MongoClient") as mongo, patch.object(app, "KafkaProducer") as factory:
            app.main()
            mongo.assert_not_called()
            producer = factory.return_value
            self.assertEqual(producer.send.call_count, 2)
            self.assertEqual({call.args[0] for call in producer.send.call_args_list}, {app.TOPIC_RAW_ANT, app.TOPIC_RAW_NOT})
            self.assertEqual(producer.send.return_value.get.call_count, 2)
            producer.close.assert_called_once()

    def test_mongo_mode_requires_uri_before_clients(self):
        for uri in ("", " "):
            with patch.dict(os.environ, {"SOURCE_MODE": "mongo", "ATLAS_URI": uri}, clear=True), patch.object(app, "MongoClient") as mongo, patch.object(app, "KafkaProducer") as kafka:
                with self.assertRaisesRegex(ValueError, "ATLAS_URI must be set"):
                    app.main()
                mongo.assert_not_called()
                kafka.assert_not_called()

    def test_invalid_mode_fails_without_clients(self):
        with patch.dict(os.environ, {"SOURCE_MODE": "typo"}, clear=True), patch.object(app, "MongoClient") as mongo:
            with self.assertRaisesRegex(ValueError, "SOURCE_MODE"):
                app.main()
            mongo.assert_not_called()

    def test_publish_failure_propagates_and_closes(self):
        with patch.dict(os.environ, {}, clear=True), patch.object(app, "KafkaProducer") as factory:
            factory.return_value.send.return_value.get.side_effect = TimeoutError("synthetic")
            with self.assertRaises(TimeoutError):
                app.main()
            factory.return_value.close.assert_called_once()

    def test_fixture_is_deterministic(self):
        self.assertEqual(load_demo(), load_demo())
        self.assertEqual(len({x["id"] for x in load_demo()}), 2)
