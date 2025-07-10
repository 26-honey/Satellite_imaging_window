
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

import pytest
from mas_api.main import ImagingActivity, ImagingWindowBuilder


class TestMainFunctions:
    
    def test_chronological_window_pass(self):
        activities = [
            ImagingActivity("s112", "2024-07-12T01:03:49Z", "2024-07-12T01:04:08Z"),
            ImagingActivity("s112", "2024-07-12T00:34:05Z", "2024-07-12T00:34:08Z"),
        ]
        
        builder = ImagingWindowBuilder(activities)
        result = builder.build_chronological_window()
        
        assert result[0]["start_time"] == "2024-07-12T00:34:05Z"
        assert result[1]["start_time"] == "2024-07-12T01:03:49Z"
        assert len(result) == 2
    
    def test_streaming_windows_pass(self):
        activities = [
            ImagingActivity("s112", "2024-07-12T00:34:05Z", "2024-07-12T00:34:08Z", "scheduled"),
            ImagingActivity("s112", "2024-07-12T00:37:58Z", "2024-07-12T00:38:20Z", "proposed"),
        ]
        
        builder = ImagingWindowBuilder(activities)
        result = builder.build_streaming_windows_by_state()
        
        assert len(result) == 2
        assert result[0][0]["activity_state"] == "scheduled"
        assert result[1][0]["activity_state"] == "proposed"
    
    def test_streaming_windows_fail(self):
        activities = [
            ImagingActivity("s112", "2024-07-12T00:34:05Z", "2024-07-12T00:34:08Z")
        ]
        
        builder = ImagingWindowBuilder(activities)
        
        with pytest.raises(ValueError, match="All activities must have 'activity_state'"):
            builder.build_streaming_windows_by_state()


if __name__ == "__main__":
    pytest.main([__file__, "-v"]) 