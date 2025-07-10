from typing import List, Dict, Optional
from datetime import datetime
import json
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field, validator
import uvicorn


class ImagingActivityInput(BaseModel):
    """Input model for imaging activity data."""
    satellite_hw_id: str = Field(..., description="Unique satellite hardware identifier")
    start_time: str = Field(..., description="ISO 8601 timestamp with timezone (e.g., '2024-07-12T00:34:05Z')")
    end_time: str = Field(..., description="ISO 8601 timestamp with timezone")
    activity_state: Optional[str] = Field(None, description="Activity state: 'scheduled' or 'proposed'")
    
    @validator('start_time', 'end_time')
    def validate_iso_timestamp(cls, v):
        """Validate ISO 8601 format and timezone handling"""
        try:
            datetime.fromisoformat(v.replace("Z", "+00:00"))
            return v
        except ValueError:
            raise ValueError(f"Invalid ISO 8601 timestamp: {v}")
    
    @validator('activity_state')
    def validate_activity_state(cls, v):
        """Validate activity state values"""
        if v is not None and v not in ['scheduled', 'proposed']:
            raise ValueError("activity_state must be 'scheduled' or 'proposed'")
        return v


class ChronologicalWindowRequest(BaseModel):
    """Request model for chronological window endpoint"""
    activities: List[ImagingActivityInput] = Field(..., description="List of imaging activities to sort chronologically")


class StreamingWindowRequest(BaseModel):
    """Request model for streaming windows endpoint"""
    activities: List[ImagingActivityInput] = Field(..., description="List of imaging activities with activity_state")
    
    @validator('activities')
    def validate_activities_have_state(cls, v):
        """Ensure all activities have activity_state for streaming windows"""
        for activity in v:
            if activity.activity_state is None:
                raise ValueError("All activities must have 'activity_state' for streaming windows")
        return v


class ChronologicalWindowResponse(BaseModel):
    """Response model for chronological window endpoint"""
    window: List[Dict] = Field(..., description="Chronologically sorted imaging activities")
    count: int = Field(..., description="Total number of activities")


class StreamingWindowsResponse(BaseModel):
    """Response model for streaming windows endpoint"""
    windows: List[List[Dict]] = Field(..., description="List of activity windows grouped by state")
    window_count: int = Field(..., description="Total number of windows")
    total_activities: int = Field(..., description="Total number of activities across all windows")


class ImagingActivity:
    """Represents a single imaging activity by a satellite."""
    
    def __init__(self, satellite_hw_id: str, start_time: str, end_time: str, activity_state: Optional[str] = None):
        self.satellite_hw_id = satellite_hw_id
        self.start_time_str = start_time
        self.end_time_str = end_time
        self.start_time = datetime.fromisoformat(start_time.replace("Z", "+00:00"))
        self.end_time = datetime.fromisoformat(end_time.replace("Z", "+00:00"))
        self.activity_state = activity_state

    def to_dict(self) -> Dict:
        """Convert to dictionary format for JSON output."""
        data = {
            "satellite_hw_id": self.satellite_hw_id,
            "start_time": self.start_time_str,
            "end_time": self.end_time_str
        }
        if self.activity_state:
            data["activity_state"] = self.activity_state
        return data

    def __repr__(self):
        return json.dumps(self.to_dict(), indent=2)


class ImagingWindowBuilder:
    """Builds imaging windows for satellite imaging activities."""
    
    def __init__(self, activities: List[ImagingActivity]):
        self.activities = activities

    def build_chronological_window(self) -> List[Dict]:
        """Sort all imaging activities by start_time."""
        sorted_activities = sorted(self.activities, key=lambda a: a.start_time)
        return [activity.to_dict() for activity in sorted_activities]

    def build_streaming_windows_by_state(self) -> List[List[Dict]]:
        """
        Build streaming imaging windows grouped by consecutive activities with the same activity_state.
        Ensures that the start time of the next window does not overlap with the end time of the previous.
        """
        if any(activity.activity_state is None for activity in self.activities):
            raise ValueError("All activities must have 'activity_state' to build state windows.")

        sorted_activities = sorted(self.activities, key=lambda a: a.start_time)
        windows = []
        current_window = []
        last_state = None
        last_end_time = None

        for activity in sorted_activities:
            if (last_state is None) or \
               (activity.activity_state != last_state) or \
               (last_end_time and activity.start_time < last_end_time):
                
                if current_window:
                    windows.append(current_window)
                current_window = [activity.to_dict()]
            else:
                current_window.append(activity.to_dict())

            last_state = activity.activity_state
            last_end_time = activity.end_time

        if current_window:
            windows.append(current_window)

        return windows


app = FastAPI(
    title="Planet Labs Mission Awareness Service",
    description="Imaging Window Builder API for SkySat constellation management",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)


@app.get("/health")
async def health_check():
    """Health check endpoint for service monitoring."""
    return {"status": "healthy", "service": "mas-imaging-window-builder"}


@app.post(
    "/imaging-windows/chronological",
    response_model=ChronologicalWindowResponse,
    summary="Build Chronological Imaging Window",
    description="Sorts imaging activities chronologically by start time for basic customer visibility"
)
async def build_chronological_window(request: ChronologicalWindowRequest):
    """Build chronological imaging window."""
    try:
        activities = [
            ImagingActivity(
                satellite_hw_id=activity.satellite_hw_id,
                start_time=activity.start_time,
                end_time=activity.end_time,
                activity_state=activity.activity_state
            )
            for activity in request.activities
        ]
        
        builder = ImagingWindowBuilder(activities)
        window = builder.build_chronological_window()
        
        return ChronologicalWindowResponse(
            window=window,
            count=len(window)
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@app.post(
    "/imaging-windows/streaming",
    response_model=StreamingWindowsResponse,
    summary="Build Streaming Windows by Activity State",
    description="Groups activities by state with non-overlapping temporal constraint for advanced scheduling"
)
async def build_streaming_windows(request: StreamingWindowRequest):
    """Build streaming windows by activity state."""
    try:
        activities = [
            ImagingActivity(
                satellite_hw_id=activity.satellite_hw_id,
                start_time=activity.start_time,
                end_time=activity.end_time,
                activity_state=activity.activity_state
            )
            for activity in request.activities
        ]
        
        builder = ImagingWindowBuilder(activities)
        windows = builder.build_streaming_windows_by_state()
        
        total_activities = sum(len(window) for window in windows)
        
        return StreamingWindowsResponse(
            windows=windows,
            window_count=len(windows),
            total_activities=total_activities
        )
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Validation error: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


if __name__ == "__main__":
    print("API Documentation: http://localhost:8000/docs")
    print("\nAvailable Endpoints:")
    print("  POST /imaging-windows/chronological - Simple chronological ordering")
    print("  POST /imaging-windows/streaming - Streaming windows by activity state")
    
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
