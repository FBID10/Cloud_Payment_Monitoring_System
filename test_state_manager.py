import unittest
import os
from StateManager import StateManager


class TestStateManager(unittest.TestCase):
    def setUp(self):
        """Set up a fresh database for each test."""
        self.test_db = "test_instance_state.db"
        self.state_manager = StateManager(db_path=self.test_db)

    def tearDown(self):
        """Clean up the test database after each test."""
        if os.path.exists(self.test_db):
            os.remove(self.test_db)

    def test_is_instance_seen_before_returns_false_for_new_instance(self):
        """Test that a new instance is not found in the database."""
        result = self.state_manager.is_instance_seen_before("i-99999")
        self.assertFalse(result)

    def test_is_instance_seen_before_returns_true_after_recording(self):
        """Test that an instance is found after being recorded."""
        instance_id = "i-12345"
        self.state_manager.record_flagged_instance(instance_id, ["Owner", "CostCenter"])
        
        result = self.state_manager.is_instance_seen_before(instance_id)
        self.assertTrue(result)

    def test_record_flagged_instance_stores_missing_tags(self):
        """Test that missing tags are properly stored."""
        instance_id = "i-54321"
        missing_tags = ["Owner", "CostCenter", "Project"]
        
        self.state_manager.record_flagged_instance(instance_id, missing_tags)
        history = self.state_manager.get_instance_history(instance_id)
        
        self.assertEqual(history["InstanceId"], instance_id)
        self.assertEqual(history["MissingTags"], missing_tags)
        self.assertTrue(history["IsActive"])

    def test_record_flagged_instance_updates_on_duplicate(self):
        """Test that recording the same instance updates its data."""
        instance_id = "i-11111"
        
        # First recording
        self.state_manager.record_flagged_instance(instance_id, ["Owner"])
        first_history = self.state_manager.get_instance_history(instance_id)
        
        # Second recording with different tags
        self.state_manager.record_flagged_instance(instance_id, ["Owner", "CostCenter"])
        second_history = self.state_manager.get_instance_history(instance_id)
        
        # Instance should still exist with updated tags
        self.assertEqual(first_history["InstanceId"], second_history["InstanceId"])
        self.assertEqual(second_history["MissingTags"], ["Owner", "CostCenter"])

    def test_mark_instance_resolved(self):
        """Test that an instance can be marked as resolved."""
        instance_id = "i-22222"
        self.state_manager.record_flagged_instance(instance_id, ["Owner"])
        
        self.state_manager.mark_instance_resolved(instance_id)
        history = self.state_manager.get_instance_history(instance_id)
        
        self.assertFalse(history["IsActive"])

    def test_get_all_flagged_instances_returns_active_only(self):
        """Test that only active instances are returned."""
        self.state_manager.record_flagged_instance("i-active-1", ["Owner"])
        self.state_manager.record_flagged_instance("i-active-2", ["CostCenter"])
        self.state_manager.record_flagged_instance("i-inactive", ["Project"])
        self.state_manager.mark_instance_resolved("i-inactive")
        
        flagged = self.state_manager.get_all_flagged_instances()
        
        self.assertEqual(len(flagged), 2)
        instance_ids = [inst["InstanceId"] for inst in flagged]
        self.assertIn("i-active-1", instance_ids)
        self.assertIn("i-active-2", instance_ids)
        self.assertNotIn("i-inactive", instance_ids)

    def test_get_instance_history_returns_none_for_unknown_instance(self):
        """Test that None is returned for unknown instances."""
        result = self.state_manager.get_instance_history("i-unknown")
        self.assertIsNone(result)

    def test_clear_database(self):
        """Test that the database can be cleared."""
        self.state_manager.record_flagged_instance("i-33333", ["Owner"])
        self.state_manager.record_flagged_instance("i-44444", ["CostCenter"])
        
        self.state_manager.clear_database()
        
        flagged = self.state_manager.get_all_flagged_instances()
        self.assertEqual(len(flagged), 0)


if __name__ == "__main__":
    unittest.main()
