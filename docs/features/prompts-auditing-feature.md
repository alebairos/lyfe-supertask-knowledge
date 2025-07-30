# Prompts Auditing - Simple Implementation PRD

**Feature Name**: Prompts Auditing & Logging  
**Version**: 1.0.0  
**Priority**: HIGH  
**Target Release**: Immediate (1-2 hours)  
**Owner**: Engineering Team  

## 📋 Problem Statement

Currently, we cannot see what prompts are actually being sent to the OpenAI model. This makes it impossible to:
- Debug Ari persona application issues
- Verify prompt composition and content
- Understand why generated content doesn't match expectations
- Troubleshoot generation failures

## 🎯 Proposed Solution

Add simple prompt logging to the OpenAI client that:
1. Logs all system and user prompts before sending to model
2. Logs model responses after receiving
3. Saves detailed audit logs to dedicated files
4. Provides clear visibility into prompt composition

## 📋 Functional Requirements

### 1. Prompt Logging
- **Log all prompts** sent to OpenAI (system + user messages)
- **Log model responses** received from OpenAI
- **Timestamped entries** for chronological tracking
- **Request ID tracking** for correlation

### 2. Audit File Structure
```
logs/
  └── prompts/
      ├── prompts_audit_YYYY-MM-DD.log     # Daily audit log
      └── latest_prompts.log               # Latest session
```

### 3. Log Format (Simple)
```
=== PROMPT REQUEST ===
Timestamp: 2025-01-14 17:30:45
Request ID: req_123456
Model: gpt-4

System Message:
[Full system prompt content]

User Message:
[Full user prompt content]

=== RESPONSE ===
[Full model response]

==========================================
```

## 🔧 Technical Requirements

### 1. Implementation Location
- **File**: `src/lyfe_kt/openai_client.py` (modify existing)
- **Method**: Add logging to existing `make_request()` method
- **No new dependencies**: Use built-in logging

### 2. Simple Implementation
```python
def make_request(self, messages, **kwargs):
    # Log prompt before sending
    self._log_prompt_request(messages, kwargs)
    
    # Make API call
    response = self.client.chat.completions.create(
        model=self.model,
        messages=messages,
        **kwargs
    )
    
    # Log response
    self._log_prompt_response(response)
    
    return response

def _log_prompt_request(self, messages, kwargs):
    """Log prompt details to audit file."""
    pass

def _log_prompt_response(self, response):
    """Log model response to audit file."""
    pass
```

### 3. Configuration Options
- **Enable/disable** via config flag: `enable_prompt_auditing: true`
- **Log level**: Include in DEBUG level logging
- **File rotation**: Daily log files (simple date-based)

## 📊 Success Metrics

- ✅ All prompts logged before sending to model
- ✅ All responses logged after receiving
- ✅ Clear prompt structure visibility
- ✅ Easy debugging of Ari persona issues
- ✅ Minimal performance impact

## 🚧 Implementation Plan

### Phase 1: Basic Logging (1 hour)
- [ ] Add prompt logging methods to OpenAI client
- [ ] Create audit log file structure
- [ ] Log system and user messages

### Phase 2: Response Logging (30 minutes)
- [ ] Log model responses
- [ ] Add request correlation
- [ ] Test with Naval content

## 🎯 Acceptance Criteria

### Must Have
- [ ] System prompts logged with full content
- [ ] User prompts logged with full content  
- [ ] Model responses logged
- [ ] Timestamped entries
- [ ] Works with existing pipeline

### Should Have
- [ ] Request ID correlation
- [ ] Daily file rotation
- [ ] Configurable enable/disable

### Could Have
- [ ] Prompt statistics (token counts)
- [ ] Performance metrics
- [ ] Compressed historical logs

## 🔄 Example Usage

After implementation:
```bash
# Run pipeline with auditing
python -m src.lyfe_kt.cli preprocess file content.md output/

# Check prompts used
cat logs/prompts/latest_prompts.log

# Review specific day
cat logs/prompts/prompts_audit_2025-01-14.log
```

## 🚨 Risks & Mitigation

### 1. Log File Size
- **Risk**: Large prompt logs consume disk space
- **Mitigation**: Daily rotation, simple text format

### 2. Performance Impact
- **Risk**: Logging slows down API calls
- **Mitigation**: Async logging, minimal processing

### 3. Sensitive Content
- **Risk**: API keys or sensitive data in logs
- **Mitigation**: Log content only, not credentials

## 📝 Documentation Requirements

- [ ] Add auditing flag to configuration documentation
- [ ] Example log format in README
- [ ] Troubleshooting guide using prompt logs

---

**Approval Required From:**
- [ ] Engineering Lead

**Estimated Effort:** 1-2 hours  
**Team Size:** 1 engineer  
**Priority:** HIGH (Critical for debugging Ari persona)

---

*This simple PRD focuses on immediate visibility into prompt composition without complex features, enabling quick debugging of the Ari persona application issue.* 