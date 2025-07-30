# Package Execution Logging - Simple Implementation PRD

**Feature Name**: Package Execution Logging Integration  
**Version**: 1.0.0  
**Priority**: MEDIUM  
**Target Release**: Q1 2025 (1-2 days)  
**Owner**: Engineering Team  

## 📋 Problem Statement

Currently, when we package pipeline content using the `package` command, we lose the execution context:
- **Prompt audits** remain in global `logs/prompts/` directory
- **Processing logs** stay in global `logs/lyfe-kt.log`
- **No execution traceability** for specific pipeline runs
- **Debugging difficulty** when issues arise with packaged content

This makes it impossible to:
- Understand exactly how specific content was generated
- Debug issues with particular supertasks after packaging
- Maintain audit trails for content generation decisions
- Correlate prompts with their resulting outputs

## 🎯 Proposed Solution

Enhance the content packaging system to **capture and include all execution logs** within each package, creating a complete audit trail for every pipeline run.

### Core Enhancement
When `package` command runs, copy relevant logs into the package under a `logs/` directory, providing complete execution documentation.

## 📋 Functional Requirements

### 1. Enhanced Package Structure
```
packages/
  └── naval_supertask-2025-01-18-17-30/
      ├── 01_raw/              # Source content
      ├── 02_preprocessed/     # Templates and analysis  
      ├── 03_output/           # Generated supertasks
      ├── reports/             # Processing reports
      └── logs/                # 🆕 EXECUTION LOGS
          ├── prompts_audit.log    # All prompts used in this run
          ├── processing.log       # Pipeline execution log
          ├── execution_summary.md # Human-readable summary
          └── metadata.json        # Execution metadata
```

### 2. Log Capture Strategy

#### 2.1 Session-Based Logging
- **Track pipeline sessions** with unique session IDs
- **Capture session-specific logs** during execution
- **Filter logs by session** when packaging

#### 2.2 Log Types to Capture
1. **Prompt Audits**: All OpenAI API calls with system/user messages
2. **Processing Logs**: Pipeline execution, errors, timings
3. **Validation Results**: Schema validation, quality checks
4. **Performance Metrics**: Processing times, token usage

### 3. Execution Documentation

#### 3.1 Execution Summary (Markdown)
```markdown
# Pipeline Execution Summary

## Session Information
- **Session ID**: sess_2025-01-18_17-30-45
- **Start Time**: 2025-01-18 17:30:45
- **End Time**: 2025-01-18 17:35:12
- **Total Duration**: 4 minutes, 27 seconds

## Pipeline Stages Executed
- ✅ **Stage 1 (Preprocessing)**: 1 file processed
- ✅ **Stage 3 (Generation)**: 2 supertasks generated

## Content Generated
- **Source**: test_ari_persona.md
- **Output**: 2 supertasks (1 beginner, 1 advanced)
- **Schema Version**: v1.1 (mobile-optimized)

## AI Model Usage
- **Total API Calls**: 3
- **Total Tokens**: 4,250
- **Model**: gpt-4
- **Success Rate**: 100%

## Quality Metrics
- **Schema Compliance**: 100%
- **Mobile Optimization Score**: 0.92
- **Ari Persona Consistency**: 85%
```

#### 3.2 Execution Metadata (JSON)
```json
{
  "session_id": "sess_2025-01-18_17-30-45",
  "execution": {
    "start_time": "2025-01-18T17:30:45Z",
    "end_time": "2025-01-18T17:35:12Z",
    "duration_seconds": 267,
    "stages_executed": ["preprocessing", "generation"],
    "success": true
  },
  "content": {
    "input_files": ["test_ari_persona.md"],
    "output_files": ["test_ari_persona_beginner.json", "test_ari_persona_advanced.json"],
    "schema_version": "v1.1"
  },
  "ai_usage": {
    "total_api_calls": 3,
    "total_tokens": 4250,
    "model": "gpt-4",
    "success_rate": 1.0
  },
  "quality_metrics": {
    "schema_compliance": 1.0,
    "mobile_optimization_score": 0.92,
    "ari_persona_consistency": 0.85
  }
}
```

## 🔧 Technical Requirements

### 1. Session Management

#### 1.1 Session ID Generation
```python
import uuid
from datetime import datetime

def generate_session_id() -> str:
    """Generate unique session ID for pipeline execution."""
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    return f"sess_{timestamp}_{uuid.uuid4().hex[:8]}"
```

#### 1.2 Session Context Integration
- **Pipeline Initialization**: Generate session ID at start
- **Log Tagging**: Tag all logs with session ID
- **Context Passing**: Pass session through all pipeline stages

### 2. Enhanced Logging System

#### 2.1 Session-Aware Logger
```python
class SessionLogger:
    def __init__(self, session_id: str):
        self.session_id = session_id
        self.session_logs = []
        
    def log_with_session(self, level: str, message: str):
        """Log message with session context."""
        log_entry = {
            "session_id": self.session_id,
            "timestamp": datetime.now().isoformat(),
            "level": level,
            "message": message
        }
        self.session_logs.append(log_entry)
```

#### 2.2 Prompt Auditing Enhancement
- **Session-tagged prompts**: Include session ID in prompt logs
- **Session filtering**: Extract prompts for specific sessions
- **Correlation**: Link prompts to their generated outputs

### 3. Package Integration

#### 3.1 Enhanced ContentPackager
```python
class ContentPackager:
    def package_content(self, title: str, session_id: str = None):
        """Package content with execution logs."""
        # ... existing packaging logic ...
        
        # 🆕 NEW: Copy execution logs
        self._copy_execution_logs(package_path, session_id)
        self._generate_execution_summary(package_path, session_id)
        self._create_execution_metadata(package_path, session_id)
    
    def _copy_execution_logs(self, package_path: Path, session_id: str):
        """Copy session-specific logs to package."""
        pass
    
    def _generate_execution_summary(self, package_path: Path, session_id: str):
        """Generate human-readable execution summary."""
        pass
```

## 📊 Success Metrics

### 1. Technical Metrics
- **✅ Complete Audit Trail**: Every package contains full execution logs
- **✅ Session Correlation**: 100% correlation between logs and outputs
- **✅ Log Completeness**: All prompts, processing steps, and results captured
- **✅ Performance**: < 5% overhead for log capture and packaging

### 2. User Experience Metrics
- **✅ Debugging Efficiency**: 80% reduction in time to debug packaged content
- **✅ Audit Compliance**: Complete traceability for all generated content
- **✅ Documentation Quality**: Clear, readable execution summaries

## 🚧 Implementation Plan

### Day 1: Session Management
- [ ] Implement session ID generation and context passing
- [ ] Enhance logging system with session awareness
- [ ] Update pipeline initialization to create sessions

### Day 2: Package Integration
- [ ] Enhance ContentPackager with log capture
- [ ] Implement execution summary generation
- [ ] Create execution metadata collection
- [ ] Test with existing Naval content

## 🎯 Acceptance Criteria

### Must Have
- [ ] Every package contains `logs/` directory with execution logs
- [ ] Session-based log filtering works correctly
- [ ] Execution summary provides clear overview of pipeline run
- [ ] Prompt audits are correlated with their outputs

### Should Have
- [ ] Execution metadata includes performance and quality metrics
- [ ] Log capture adds minimal performance overhead
- [ ] Human-readable summaries for non-technical users

### Could Have
- [ ] Log compression for large packages
- [ ] Interactive log viewer for complex debugging
- [ ] Automated quality issue detection in logs

## 🔄 Example Usage

### Before (Current)
```bash
python -m src.lyfe_kt.cli preprocess file content.md work/02_preprocessed
python -m src.lyfe_kt.cli generate file template.md work/03_output
python -m src.lyfe_kt.cli package

# Logs scattered in global logs/ directory
# No connection between logs and packaged content
```

### After (Enhanced)
```bash
python -m src.lyfe_kt.cli preprocess file content.md work/02_preprocessed
python -m src.lyfe_kt.cli generate file template.md work/03_output
python -m src.lyfe_kt.cli package

# Package contains complete execution documentation:
# packages/content-2025-01-18-17-30/logs/
#   ├── prompts_audit.log      # All prompts used
#   ├── processing.log         # Pipeline execution
#   ├── execution_summary.md   # Human-readable summary
#   └── metadata.json          # Structured metadata
```

## 🚨 Risks & Mitigation

### 1. Log File Size
- **Risk**: Large prompt logs may bloat packages
- **Mitigation**: Implement log compression, configurable verbosity levels

### 2. Performance Impact
- **Risk**: Log capture may slow down pipeline
- **Mitigation**: Async log copying, minimal overhead design

### 3. Session Tracking Complexity
- **Risk**: Session management adds complexity
- **Mitigation**: Simple UUID-based sessions, graceful fallback

## 📝 Documentation Requirements

### 1. User Documentation
- [ ] Package structure documentation with logs/ directory
- [ ] Execution summary interpretation guide
- [ ] Debugging workflow using packaged logs

### 2. Developer Documentation
- [ ] Session management implementation guide
- [ ] Log capture architecture documentation
- [ ] Performance impact analysis

## 🔗 Dependencies

### Internal
- [ ] `src/lyfe_kt/content_packager.py` (existing)
- [ ] `src/lyfe_kt/openai_client.py` (prompt auditing)
- [ ] `src/lyfe_kt/logging_config.py` (logging system)

### External
- [ ] No new external dependencies required

---

**Approval Required From:**
- [ ] Engineering Lead
- [ ] Product Manager

**Estimated Effort:** 1-2 days  
**Team Size:** 1 engineer  
**Priority:** MEDIUM (Improves debugging and audit capabilities)

---

*This PRD enhances the content packaging system to provide complete execution documentation, enabling better debugging, audit trails, and understanding of how content was generated.* 