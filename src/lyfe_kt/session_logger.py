"""
Session Management and Logging for Lyfe Supertask Knowledge Generator.

This module provides session-based logging capabilities to track pipeline
execution and correlate logs with generated content for audit trails.
"""

import json
import uuid
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, asdict


# Set up logging
logger = logging.getLogger(__name__)


@dataclass
class SessionMetadata:
    """Session execution metadata."""
    session_id: str
    start_time: str
    end_time: Optional[str] = None
    duration_seconds: Optional[float] = None
    stages_executed: List[str] = None
    success: bool = True
    input_files: List[str] = None
    output_files: List[str] = None
    schema_version: str = "v1.1"
    total_api_calls: int = 0
    total_tokens: int = 0
    model: str = "gpt-4"
    success_rate: float = 1.0
    schema_compliance: float = 1.0
    mobile_optimization_score: float = 0.0
    ari_persona_consistency: float = 0.0

    def __post_init__(self):
        if self.stages_executed is None:
            self.stages_executed = []
        if self.input_files is None:
            self.input_files = []
        if self.output_files is None:
            self.output_files = []


def generate_session_id() -> str:
    """
    Generate unique session ID for pipeline execution.
    
    Returns:
        Unique session ID in format: sess_YYYY-MM-DD_HH-MM-SS_<8-char-uuid>
    """
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    unique_suffix = uuid.uuid4().hex[:8]
    return f"sess_{timestamp}_{unique_suffix}"


class SessionLogger:
    """
    Session-aware logger for tracking pipeline execution.
    
    This logger captures all pipeline events with session context,
    enabling correlation between logs and generated content.
    """
    
    def __init__(self, session_id: str):
        """
        Initialize session logger.
        
        Args:
            session_id: Unique session identifier.
        """
        self.session_id = session_id
        self.session_logs = []
        self.metadata = SessionMetadata(
            session_id=session_id,
            start_time=datetime.now().isoformat()
        )
        
        logger.info(f"Session logger initialized: {session_id}")
    
    def log_with_session(self, level: str, message: str, **kwargs):
        """
        Log message with session context.
        
        Args:
            level: Log level (INFO, DEBUG, WARNING, ERROR).
            message: Log message.
            **kwargs: Additional context data.
        """
        log_entry = {
            "session_id": self.session_id,
            "timestamp": datetime.now().isoformat(),
            "level": level.upper(),
            "message": message,
            **kwargs
        }
        
        self.session_logs.append(log_entry)
        
        # Also log to standard logger
        getattr(logger, level.lower())(f"[{self.session_id}] {message}")
    
    def log_stage_start(self, stage_name: str):
        """Log start of pipeline stage."""
        self.metadata.stages_executed.append(stage_name)
        self.log_with_session("INFO", f"Starting stage: {stage_name}", stage=stage_name)
    
    def log_stage_complete(self, stage_name: str, duration_seconds: float = None):
        """Log completion of pipeline stage."""
        self.log_with_session(
            "INFO", 
            f"Completed stage: {stage_name}", 
            stage=stage_name,
            duration_seconds=duration_seconds
        )
    
    def log_api_call(self, model: str, tokens_used: int, success: bool = True):
        """Log OpenAI API call details."""
        self.metadata.total_api_calls += 1
        self.metadata.total_tokens += tokens_used
        self.metadata.model = model
        
        if not success:
            self.metadata.success_rate = (
                self.metadata.success_rate * (self.metadata.total_api_calls - 1) / 
                self.metadata.total_api_calls
            )
        
        self.log_with_session(
            "DEBUG",
            f"API call: {model}, tokens: {tokens_used}, success: {success}",
            model=model,
            tokens_used=tokens_used,
            success=success
        )
    
    def log_input_file(self, file_path: str):
        """Log input file being processed."""
        if file_path not in self.metadata.input_files:
            self.metadata.input_files.append(file_path)
        self.log_with_session("INFO", f"Processing input file: {file_path}", input_file=file_path)
    
    def log_output_file(self, file_path: str):
        """Log output file generated."""
        if file_path not in self.metadata.output_files:
            self.metadata.output_files.append(file_path)
        self.log_with_session("INFO", f"Generated output file: {file_path}", output_file=file_path)
    
    def log_quality_metric(self, metric_name: str, value: float):
        """Log quality metric."""
        if hasattr(self.metadata, metric_name):
            setattr(self.metadata, metric_name, value)
        
        self.log_with_session(
            "INFO",
            f"Quality metric - {metric_name}: {value}",
            metric_name=metric_name,
            metric_value=value
        )
    
    def finalize_session(self, success: bool = True):
        """
        Finalize session and calculate final metrics.
        
        Args:
            success: Whether the overall session was successful.
        """
        self.metadata.end_time = datetime.now().isoformat()
        self.metadata.success = success
        
        # Calculate duration
        start_dt = datetime.fromisoformat(self.metadata.start_time.replace('Z', '+00:00'))
        end_dt = datetime.fromisoformat(self.metadata.end_time.replace('Z', '+00:00'))
        self.metadata.duration_seconds = (end_dt - start_dt).total_seconds()
        
        self.log_with_session(
            "INFO",
            f"Session finalized: success={success}, duration={self.metadata.duration_seconds:.2f}s",
            session_success=success,
            session_duration=self.metadata.duration_seconds
        )
    
    def get_session_logs(self) -> List[Dict[str, Any]]:
        """Get all session logs."""
        return self.session_logs.copy()
    
    def get_session_metadata(self) -> Dict[str, Any]:
        """Get session metadata as dictionary."""
        return asdict(self.metadata)
    
    def save_session_logs(self, output_path: Path):
        """
        Save session logs to file.
        
        Args:
            output_path: Path to save logs file.
        """
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            for log_entry in self.session_logs:
                timestamp = log_entry['timestamp']
                level = log_entry['level']
                message = log_entry['message']
                f.write(f"[{timestamp}] {level}: {message}\n")
        
        logger.info(f"Session logs saved to: {output_path}")
    
    def generate_execution_summary(self) -> str:
        """
        Generate human-readable execution summary in Markdown format.
        
        Returns:
            Markdown-formatted execution summary.
        """
        metadata = self.metadata
        
        # Format duration
        if metadata.duration_seconds:
            duration_mins = int(metadata.duration_seconds // 60)
            duration_secs = int(metadata.duration_seconds % 60)
            duration_str = f"{duration_mins} minutes, {duration_secs} seconds"
        else:
            duration_str = "Unknown"
        
        # Format timestamps
        start_time = datetime.fromisoformat(metadata.start_time.replace('Z', '+00:00')).strftime("%Y-%m-%d %H:%M:%S")
        end_time = "Unknown"
        if metadata.end_time:
            end_time = datetime.fromisoformat(metadata.end_time.replace('Z', '+00:00')).strftime("%Y-%m-%d %H:%M:%S")
        
        # Build summary
        summary = f"""# Pipeline Execution Summary

## Session Information
- **Session ID**: {metadata.session_id}
- **Start Time**: {start_time}
- **End Time**: {end_time}
- **Total Duration**: {duration_str}
- **Overall Success**: {'✅ Yes' if metadata.success else '❌ No'}

## Pipeline Stages Executed
"""
        
        for stage in metadata.stages_executed:
            summary += f"- ✅ **{stage.title()}**: Completed\n"
        
        summary += f"""
## Content Generated
- **Input Files**: {len(metadata.input_files)} files
"""
        for input_file in metadata.input_files:
            summary += f"  - {Path(input_file).name}\n"
        
        summary += f"- **Output Files**: {len(metadata.output_files)} files\n"
        for output_file in metadata.output_files:
            summary += f"  - {Path(output_file).name}\n"
        
        summary += f"- **Schema Version**: {metadata.schema_version}\n"
        
        summary += f"""
## AI Model Usage
- **Total API Calls**: {metadata.total_api_calls}
- **Total Tokens**: {metadata.total_tokens:,}
- **Model**: {metadata.model}
- **Success Rate**: {metadata.success_rate:.1%}

## Quality Metrics
- **Schema Compliance**: {metadata.schema_compliance:.1%}
- **Mobile Optimization Score**: {metadata.mobile_optimization_score:.2f}
- **Ari Persona Consistency**: {metadata.ari_persona_consistency:.1%}

## Session Logs
Total log entries: {len(self.session_logs)}

---
*Generated automatically by Lyfe Supertask Knowledge Generator*
"""
        
        return summary


# Global session registry for tracking active sessions
_active_sessions: Dict[str, SessionLogger] = {}


def create_session() -> SessionLogger:
    """
    Create new session logger.
    
    Returns:
        New SessionLogger instance.
    """
    session_id = generate_session_id()
    session_logger = SessionLogger(session_id)
    _active_sessions[session_id] = session_logger
    return session_logger


def get_session(session_id: str) -> Optional[SessionLogger]:
    """
    Get existing session logger by ID.
    
    Args:
        session_id: Session identifier.
        
    Returns:
        SessionLogger instance or None if not found.
    """
    return _active_sessions.get(session_id)


def finalize_session(session_id: str, success: bool = True) -> Optional[SessionLogger]:
    """
    Finalize and remove session from active registry.
    
    Args:
        session_id: Session identifier.
        success: Whether session was successful.
        
    Returns:
        Finalized SessionLogger instance or None if not found.
    """
    session_logger = _active_sessions.pop(session_id, None)
    if session_logger:
        session_logger.finalize_session(success)
    return session_logger


def get_active_sessions() -> Dict[str, SessionLogger]:
    """Get all active sessions."""
    return _active_sessions.copy()


def clear_all_sessions():
    """Clear all active sessions (mainly for testing)."""
    global _active_sessions
    _active_sessions = {} 