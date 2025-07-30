# Markdown File Processing Feature PRD

## Overview
Enable the Stage 1 preprocessing pipeline to process markdown files (.md) in addition to JSON files, allowing content extraction and conversion to the expected analysis format.

## Problem Statement
Currently, the Stage 1 CLI command `lyfe-kt stage1 process-file` fails when processing markdown files because:
- The pipeline expects JSON input but receives markdown
- `ContentAnalyzer.analyze_single_file()` calls `process_raw_file()` which uses `load_raw_json()`
- `load_raw_json()` attempts to parse markdown as JSON, causing "Invalid JSON" errors

## Success Criteria
- ✅ `lyfe-kt stage1 process-file work/01_raw/file.md work/02_preprocessed/file.json` works
- ✅ Markdown content is extracted and converted to expected analysis format
- ✅ Existing JSON file processing continues to work unchanged
- ✅ No breaking changes to current API

## Technical Approach

### Simplest Solution: File Type Detection in ContentAnalyzer

**Location**: `src/lyfe_kt/content_analyzer.py`

**Changes**:
1. Modify `ContentAnalyzer.analyze_single_file()` to detect file type
2. Use existing `ContentExtractor` for non-JSON files
3. Convert extracted content to expected format before analysis

### Implementation Details

#### Step 1: Add File Type Detection
```python
def analyze_single_file(self, file_path: str, include_ai_analysis: bool = True) -> Dict[str, Any]:
    """
    Analyze a single file with comprehensive content analysis.
    Supports JSON, markdown, PDF, text, and DOCX files.
    """
    try:
        logger.info(f"Analyzing single file: {file_path}")
        
        # Detect file type and extract content accordingly
        file_extension = Path(file_path).suffix.lower()
        
        if file_extension == '.json':
            # Existing JSON processing
            processed_data = process_raw_file(file_path)
        else:
            # New: Use ContentExtractor for other formats
            from .stage1_preprocessing import ContentExtractor
            extractor = ContentExtractor()
            extracted_content = extractor.extract_content(file_path)
            processed_data = self._convert_extracted_to_analysis_format(extracted_content)
        
        # Rest of the method remains unchanged...
```

#### Step 2: Add Content Conversion Helper
```python
def _convert_extracted_to_analysis_format(self, extracted_content: Dict[str, Any]) -> Dict[str, Any]:
    """
    Convert ContentExtractor output to format expected by analysis pipeline.
    
    Args:
        extracted_content: Output from ContentExtractor
        
    Returns:
        Dictionary in format expected by existing analysis code
    """
    # Create minimal structure that matches JSON processing expectations
    return {
        "content": [
            {
                "type": "text",
                "content": extracted_content.get("text_content", ""),
                "metadata": {
                    "file_type": extracted_content.get("file_type", "unknown"),
                    "file_path": extracted_content.get("file_path", ""),
                    "extraction_timestamp": extracted_content.get("extraction_timestamp", "")
                }
            }
        ],
        "quiz": [],  # Empty for non-JSON files
        "metadata": {
            "source": extracted_content.get("file_path", ""),
            "file_type": extracted_content.get("file_type", "unknown"),
            "file_size": extracted_content.get("file_size", 0)
        }
    }
```

## Dependencies
- Existing `ContentExtractor` class (already implemented)
- No new external dependencies required
- Uses existing YAML frontmatter parsing (already imported)

## Testing Strategy

### Unit Tests
1. **Test markdown file processing**:
   - Create sample markdown file
   - Verify successful processing without JSON errors
   - Validate output structure

2. **Test existing JSON processing still works**:
   - Ensure no regression in JSON file handling
   - Verify same output format maintained

3. **Test other file types**:
   - Basic validation for PDF, TXT, DOCX processing

### Integration Tests
1. **CLI end-to-end test**:
   - `lyfe-kt stage1 process-file sample.md output.json`
   - Verify successful completion and valid output

## Implementation Plan

### Phase 1: Core Implementation (2-3 hours)
1. ✅ Modify `ContentAnalyzer.analyze_single_file()` for file type detection
2. ✅ Add `_convert_extracted_to_analysis_format()` helper method
3. ✅ Basic unit tests for markdown processing

### Phase 2: Testing & Validation (1-2 hours)
1. ✅ Comprehensive test cases
2. ✅ Integration testing with CLI
3. ✅ Regression testing for JSON files

### Phase 3: Documentation (30 minutes)
1. ✅ Update CLI help text to mention supported formats
2. ✅ Add example usage for markdown files

## Risk Mitigation

### Low Risk Items
- **Breaking changes**: Minimal - only adding functionality
- **Performance**: No impact - same processing for JSON files
- **Dependencies**: None - uses existing code

### Potential Issues
- **Content format differences**: Markdown structure differs from JSON
  - *Mitigation*: Simple conversion to expected format
- **Frontmatter parsing**: YAML parsing might fail
  - *Mitigation*: Graceful fallback to plain text content

## Success Metrics
- ✅ Zero JSON parsing errors for markdown files
- ✅ Successful generation of preprocessed JSON from markdown input
- ✅ All existing tests pass
- ✅ New tests for markdown processing pass

## Future Considerations
- Support for more complex markdown structures
- Better handling of markdown metadata
- Integration with existing template generation pipeline

---

**Estimated Effort**: 4-5 hours
**Priority**: High (blocks current workflow)
**Complexity**: Low (leverages existing components) 