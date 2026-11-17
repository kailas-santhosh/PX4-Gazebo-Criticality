import os
import sys
import subprocess
import unittest

sys.path.insert(
    0,
    os.path.abspath(
        os.path.join(os.path.dirname(__file__), "..")
    )
)

from criticality_core.events.obstacle_event import ObstacleEvent


class AlwaysFireTrigger:

    def should_fire(self, context):
        return True


class MockCriticalityLogger:

    def __init__(self):
        self.started_events = []
        self.ended_events = []

    def start_event(self, **kwargs):
        self.started_events.append(kwargs)
        return "test_event_id"

    def end_event(self, **kwargs):
        self.ended_events.append(kwargs)


class TestObstacleEventLifecycle(unittest.TestCase):

    def create_event(self):

        criticality_logger = MockCriticalityLogger()

        event = ObstacleEvent(
            trigger=AlwaysFireTrigger(),
            model_file="critical_box.sdf",
            model_name="test_obstacle",
            x=5.0,
            y=5.0,
            z=0.5,
            criticality_logger=criticality_logger,
        )

        return event, criticality_logger

    def test_failed_activation_does_not_start_label(self):

        event, logger = self.create_event()

        event.on_enter = lambda: False

        event.update(
            x=0.0,
            y=0.0,
            z=0.0,
            timestamp=10.0,
        )

        self.assertFalse(event.active)
        self.assertFalse(event.completed)
        self.assertIsNone(event.event_id)
        self.assertEqual(len(logger.started_events), 0)

    def test_none_activation_preserves_existing_behaviour(self):

        event, logger = self.create_event()

        event.on_enter = lambda: None

        event.update(
            x=0.0,
            y=0.0,
            z=0.0,
            timestamp=10.0,
        )

        self.assertTrue(event.active)
        self.assertEqual(len(logger.started_events), 1)
        self.assertEqual(event.event_id, "test_event_id")

    def test_successful_activation_starts_label(self):

        event, logger = self.create_event()

        event.on_enter = lambda: True

        event.update(
            x=0.0,
            y=0.0,
            z=0.0,
            timestamp=10.0,
        )

        self.assertTrue(event.active)
        self.assertEqual(len(logger.started_events), 1)
        self.assertEqual(event.event_id, "test_event_id")

    def test_failed_activation_can_retry(self):

        event, logger = self.create_event()

        attempts = {"count": 0}

        def simulated_activation():

            attempts["count"] += 1

            if attempts["count"] == 1:
                return False

            return True

        event.on_enter = simulated_activation

        # First attempt fails.
        event.update(
            x=0.0,
            y=0.0,
            z=0.0,
            timestamp=10.0,
        )

        self.assertFalse(event.active)
        self.assertEqual(len(logger.started_events), 0)

        # Second attempt succeeds.
        event.update(
            x=0.0,
            y=0.0,
            z=0.0,
            timestamp=11.0,
        )

        self.assertTrue(event.active)
        self.assertEqual(attempts["count"], 2)
        self.assertEqual(len(logger.started_events), 1)

    def test_finalize_ends_label(self):

        event, logger = self.create_event()

        event.on_enter = lambda: True

        event.update(
            x=0.0,
            y=0.0,
            z=0.0,
            timestamp=10.0,
        )

        self.assertTrue(event.active)

        event.finalize(timestamp=20.0)

        self.assertFalse(event.active)
        self.assertTrue(event.completed)
        self.assertEqual(len(logger.ended_events), 1)
        self.assertEqual(
            logger.ended_events[0]["event_id"],
            "test_event_id",
        )
        self.assertEqual(
            logger.ended_events[0]["offset_ts"],
            20.0,
        )

    def test_finalize_does_not_call_on_exit(self):

        event, logger = self.create_event()

        event.on_enter = lambda: True

        event.on_exit = lambda: self.fail(
            "finalize() must not call on_exit()."
        )

        event.update(
            x=0.0,
            y=0.0,
            z=0.0,
            timestamp=10.0,
        )

        event.finalize(timestamp=20.0)

        self.assertFalse(event.active)
        self.assertTrue(event.completed)

    def test_finalize_does_not_change_inactive_event(self):

        event, logger = self.create_event()

        event.finalize(timestamp=20.0)

        self.assertFalse(event.active)
        self.assertFalse(event.completed)
        self.assertEqual(len(logger.started_events), 0)
        self.assertEqual(len(logger.ended_events), 0)


class TestGazeboSpawnResponse(unittest.TestCase):

    def make_result(
        self,
        returncode=0,
        stdout="data: true\n",
        stderr="",
    ):

        return subprocess.CompletedProcess(
            args=["gz", "service"],
            returncode=returncode,
            stdout=stdout,
            stderr=stderr,
        )

    def test_successful_response(self):

        result = self.make_result()

        self.assertTrue(
            ObstacleEvent._spawn_succeeded(result)
        )

    def test_false_response(self):

        result = self.make_result(
            stdout="data: false\n"
        )

        self.assertFalse(
            ObstacleEvent._spawn_succeeded(result)
        )

    def test_nonzero_return_code(self):

        result = self.make_result(
            returncode=1,
            stdout="data: true\n",
        )

        self.assertFalse(
            ObstacleEvent._spawn_succeeded(result)
        )

    def test_missing_response(self):

        result = self.make_result(stdout="")

        self.assertFalse(
            ObstacleEvent._spawn_succeeded(result)
        )

    def test_malformed_response(self):

        result = self.make_result(
            stdout="service call completed\n"
        )

        self.assertFalse(
            ObstacleEvent._spawn_succeeded(result)
        )

    def test_none_result(self):

        self.assertFalse(
            ObstacleEvent._spawn_succeeded(None)
        )


if __name__ == "__main__":

    unittest.main()
