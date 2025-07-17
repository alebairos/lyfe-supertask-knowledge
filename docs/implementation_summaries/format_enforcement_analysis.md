# Format Enforcement Analysis - Stage 3 JSON Generation

**Analysis Date**: July 16, 2025  
**Issue**: Ensuring AI-generated supertasks strictly follow the required JSON format  
**Status**: CRITICAL - Current gaps identified, solutions proposed  
**Context**: Stage 3 CLI generation working but format compliance inconsistent  

## Executive Summary

The current Stage 3 generation pipeline has **partial format enforcement** but lacks robust mechanisms to **guarantee** strict JSON structure compliance. While basic validation exists, the system relies heavily on AI "following instructions" rather than **forcing** compliance through technical constraints.

## Current Format Enforcement Mechanisms

### ✅ Existing Safeguards

#### 1. JSON Structure Validation (`generation_prompts.yaml` lines 197-227)
```yaml
json_structure_validation:
  required_fields: ["title", "dimension", "archetype", "relatedToType", "relatedToId", "estimatedDuration", "coinsReward", "flexibleItems", "metadata"]
  metadata_required: ["language", "region", "created_at", "updated_at", "version"]
  flexibleitems_validation:
    allowed_types: ["content", "quote", "quiz"]
    content_required: ["type", "content"]
    quote_required: ["type", "content", "author"]
    quiz_required: ["type", "question", "options", "correctAnswer", "explanation"]
```

#### 2. Generation Prompts with Structure Examples
- System message emphasizes strict JSON structure compliance
- Includes target JSON structure in prompts
- Critical rules highlighted in prompts

#### 3. Post-Processing Validation (`stage3_generation.py`)
- JSON parsing with markdown code block handling ✅
- Metadata enhancement after generation ✅
- Structure validation using `validate_generated_json_structure()` ✅

#### 4. Raw JSON Format Reference
Based on `work/01_raw/levantar_da_cama_raw.json`:
```json
{
  "title": "Levantar da Cama",
  "dimension": "physicalHealth",
  "archetype": "warrior", 
  "relatedToType": "HABITBP",
  "relatedToId": "wake-up-early",
  "estimatedDuration": 300,
  "coinsReward": 15,
  "flexibleItems": [
    {
      "type": "content",
      "content": "...",
      "author": "Optional"
    },
    {
      "type": "quiz",
      "question": "...",
      "options": ["...", "...", "...", "..."],
      "correctAnswer": 1,
      "explanation": "..."
    }
  ],
  "metadata": {...}
}
```

## ❌ Critical Gaps & Issues Identified

### Issue 1: Validation Logic Inconsistencies

**Problem**: Current validation config expects incorrect fields for quiz items.

**Evidence**: 
- Validation expects `content` field for quiz items
- Raw JSON shows quiz items have: `question`, `options`, `correctAnswer`, `explanation` (NO `content`)
- This causes validation failures: "flexibleItems[4] missing required field: content"

**Root Cause**: Inconsistency between validation rules and actual raw JSON structure.

### Issue 2: Weak AI Constraint Enforcement

**Problem**: System relies on AI "following instructions" rather than technical enforcement.

**Gaps**:
- No JSON Schema validation to guarantee structure
- No retry mechanism for failed validations
- No corrective feedback loop for format violations
- AI can generate valid JSON that doesn't match exact structure

### Issue 3: Missing Format Enforcement Tools

**Current Limitations**:
- No comprehensive JSON Schema definition
- No structural template enforcement
- No pre-generation constraint validation
- No automatic correction mechanisms

## 🔧 Proposed Solution: Hybrid Approach (Template + Schema)

### **RECOMMENDED: Simple Structural Hybrid - v1.0**

For evolving formats, the best approach combines **template-based structure** with **schema validation**:

1. **Template guarantees structure** → Zero format violations
2. **AI fills content** → Intelligent, contextual generation  
3. **Schema validates output** → Catches any edge cases
4. **Version support** → Easy format evolution

### **v1.0 Implementation: Simple Structure Template**

#### Phase 1: Structure Template (Immediate Implementation)

```python
class StructuralJSONGenerator:
    """Hybrid generator with guaranteed structure compliance."""
    
    def __init__(self, format_version="v1.0"):
        self.format_version = format_version
        self.schema = self._load_schema(format_version)
    
    def generate_supertask(self, template_data: Dict[str, Any], difficulty: str) -> Dict[str, Any]:
        """Generate supertask with guaranteed structure + AI content."""
        
        # Step 1: Create guaranteed base structure (template-based)
        base_structure = self._create_base_structure(template_data, difficulty)
        
        # Step 2: AI generates flexibleItems content within structure
        base_structure["flexibleItems"] = self._generate_flexible_items(template_data, difficulty)
        
        # Step 3: Add metadata with proper format
        base_structure["metadata"] = self._generate_metadata()
        
        # Step 4: Validate against schema
        self._validate_structure(base_structure)
        
        return base_structure
    
    def _create_base_structure(self, template_data: Dict[str, Any], difficulty: str) -> Dict[str, Any]:
        """Create guaranteed compliant base structure."""
        frontmatter = template_data.get('frontmatter', {})
        
        return {
            "title": f"{frontmatter.get('title', 'Knowledge Task')} - {difficulty.capitalize()}",
            "dimension": frontmatter.get('dimension', 'physicalHealth'),
            "archetype": frontmatter.get('archetype', 'warrior'),
            "relatedToType": frontmatter.get('relatedToType', 'HABITBP'),
            "relatedToId": frontmatter.get('relatedToId', 'generic'),
            "estimatedDuration": int(frontmatter.get('estimatedDuration', 300)),
            "coinsReward": int(frontmatter.get('coinsReward', 15)),
            "flexibleItems": [],  # Will be filled by AI
            "metadata": {}        # Will be filled by metadata generator
        }
    
    def _generate_flexible_items(self, template_data: Dict[str, Any], difficulty: str) -> List[Dict[str, Any]]:
        """AI generates content within guaranteed item structures."""
        content_sections = self._extract_content_sections(template_data)
        quiz_sections = self._extract_quiz_sections(template_data)
        
        flexible_items = []
        
        # Generate content items with guaranteed structure
        for section in content_sections:
            content_item = {
                "type": "content",
                "content": self._ai_enhance_content(section, difficulty),
                "author": "Ari"  # Can be AI-generated or default
            }
            flexible_items.append(content_item)
        
        # Generate quiz items with guaranteed structure  
        for quiz in quiz_sections:
            quiz_item = {
                "type": "quiz",
                "question": self._ai_enhance_question(quiz.get('question', ''), difficulty),
                "options": self._ai_enhance_options(quiz.get('options', []), difficulty),
                "correctAnswer": quiz.get('correctAnswer', 0),
                "explanation": self._ai_enhance_explanation(quiz.get('explanation', ''), difficulty)
            }
            flexible_items.append(quiz_item)
        
        return flexible_items
```

#### Phase 2: Simple Schema Validation

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "Supertask Format v1.0",
  "type": "object",
  "required": ["title", "dimension", "archetype", "relatedToType", "relatedToId", "estimatedDuration", "coinsReward", "flexibleItems", "metadata"],
  "properties": {
    "title": {"type": "string", "minLength": 1},
    "dimension": {
      "type": "string", 
      "enum": ["physicalHealth", "mentalHealth", "relationships", "work", "spirituality"]
    },
    "archetype": {
      "type": "string",
      "enum": ["warrior", "explorer", "sage", "ruler"]
    },
    "relatedToType": {
      "type": "string",
      "enum": ["HABITBP", "GENERIC"]
    },
    "relatedToId": {"type": "string"},
    "estimatedDuration": {"type": "integer", "minimum": 60},
    "coinsReward": {"type": "integer", "minimum": 1},
    "flexibleItems": {
      "type": "array",
      "minItems": 1,
      "items": {
        "oneOf": [
          {
            "type": "object",
            "required": ["type", "content"],
            "properties": {
              "type": {"const": "content"},
              "content": {"type": "string", "minLength": 10},
              "author": {"type": "string"}
            }
          },
          {
            "type": "object",
            "required": ["type", "content", "author"],
            "properties": {
              "type": {"const": "quote"},
              "content": {"type": "string", "minLength": 10},
              "author": {"type": "string", "minLength": 1}
            }
          },
          {
            "type": "object",
            "required": ["type", "question", "options", "correctAnswer", "explanation"],
            "properties": {
              "type": {"const": "quiz"},
              "question": {"type": "string", "minLength": 10},
              "options": {
                "type": "array",
                "minItems": 2,
                "maxItems": 5,
                "items": {"type": "string", "minLength": 1}
              },
              "correctAnswer": {"type": "integer", "minimum": 0},
              "explanation": {"type": "string", "minLength": 10}
            }
          }
        ]
      }
    },
    "metadata": {"type": "object"}
  }
}
```

#### Phase 3: Future Evolution Support

```python
class FormatVersionManager:
    """Manages different format versions for evolution."""
    
    SUPPORTED_VERSIONS = {
        "v1.0": {
            "schema_file": "supertask_schema_v1.0.json",
            "generator_class": "StructuralJSONGenerator_v1_0",
            "deprecated": False
        },
        "v1.1": {  # Future version
            "schema_file": "supertask_schema_v1.1.json", 
            "generator_class": "StructuralJSONGenerator_v1_1",
            "deprecated": False,
            "migration_from": ["v1.0"]
        }
    }
    
    def get_generator(self, version: str) -> StructuralJSONGenerator:
        """Get appropriate generator for format version."""
        version_config = self.SUPPORTED_VERSIONS.get(version)
        if not version_config:
            raise ValueError(f"Unsupported format version: {version}")
        
        return globals()[version_config["generator_class"]](version)
    
    def migrate_format(self, content: Dict[str, Any], from_version: str, to_version: str) -> Dict[str, Any]:
        """Migrate content between format versions."""
        # Implementation for future format migrations
        pass
```

## Immediate Action Items

### 🔥 Critical Fix Required
1. **Fix Quiz Validation Logic** - Remove incorrect `content` field requirement for quiz items
2. **Update validation config** in `generation_prompts.yaml`
3. **Test with Portuguese content** to verify advanced difficulty generation

### 📋 Implementation Roadmap: Hybrid v1.0

#### Phase 1: Immediate Fixes (30 minutes)
- [ ] Fix quiz validation logic in `generation_prompts.yaml`
- [ ] Test current CLI with corrected validation

#### Phase 2: Simple Structure Template (1-2 hours)
- [ ] Create `StructuralJSONGenerator` class in `stage3_generation.py`
- [ ] Implement `_create_base_structure()` method
- [ ] Implement `_generate_flexible_items()` with guaranteed structure
- [ ] Replace current JSON generation with hybrid approach

#### Phase 3: Schema Validation (1 hour)
- [ ] Create `src/config/supertask_schema_v1.0.json`
- [ ] Add schema validation to `StructuralJSONGenerator`
- [ ] Integrate schema loading into config system

#### Phase 4: Testing & Validation (1 hour)
- [ ] Test with Portuguese content template
- [ ] Verify both beginner and advanced generation
- [ ] Confirm 100% format compliance

#### Phase 5: Future Evolution Foundation (30 minutes)
- [ ] Create `FormatVersionManager` skeleton
- [ ] Add version configuration structure
- [ ] Document evolution process

## Technical Implementation Details - v1.0

### Files to Create/Modify

1. **`src/config/supertask_schema_v1.0.json`** (NEW)
   - Simple JSON Schema for format v1.0
   - Validation rules matching raw JSON structure exactly

2. **`src/lyfe_kt/stage3_generation.py`** (MODIFY)
   - Add `StructuralJSONGenerator` class
   - Replace current `JSONGenerator.generate_supertask()` method
   - Add schema loading and validation

3. **`src/config/generation_prompts.yaml`** (FIX)
   - Fix `quiz_required` field list (remove incorrect content requirement)
   - Update system prompts for hybrid approach

4. **`src/lyfe_kt/config_loader.py`** (MINOR UPDATE)
   - Add schema loading function
   - Update validation to use schema

### Implementation Strategy

#### Structure First, Content Second
```python
# Current approach (risky):
ai_generates_entire_json()  # Can deviate from structure

# New hybrid approach (safe):
base_structure = create_guaranteed_structure()  # 100% compliant
base_structure["flexibleItems"] = ai_generates_content_only()  # Within structure
validate_against_schema(base_structure)  # Final safety check
```

#### Minimal AI Scope
- **AI Only Generates**: Content text, questions, explanations
- **Template Guarantees**: Field names, structure, data types, required fields
- **Schema Validates**: Final output compliance

### Evolution Benefits

When format evolves from v1.0 → v1.1:

```python
# v1.0 generator (current)
class StructuralJSONGenerator_v1_0:
    def _create_base_structure(self, ...):
        return {"title": "...", "flexibleItems": []}

# v1.1 generator (future)  
class StructuralJSONGenerator_v1_1:
    def _create_base_structure(self, ...):
        return {"title": "...", "flexibleItems": [], "newField": "..."}  # Easy evolution
```

**Migration**: Old v1.0 content can be automatically migrated to v1.1 structure.

## Risk Assessment

### High Risk
- **Format Violations**: Current gaps could produce non-compliant JSON
- **Validation Failures**: Incorrect logic blocks valid content generation

### Medium Risk  
- **Performance Impact**: Additional validation adds processing time
- **AI Hallucination**: Free-form generation can deviate from structure

### Low Risk
- **Schema Evolution**: JSON Schema can adapt to format changes
- **Backward Compatibility**: Current outputs mostly compliant

## Success Metrics

### Immediate Goals
- [ ] 100% validation success for quiz items
- [ ] Advanced difficulty generation working
- [ ] CLI generation completing without validation errors

### Long-term Goals
- [ ] 99%+ JSON Schema compliance rate
- [ ] <3 retry attempts average for successful generation
- [ ] Zero manual intervention required for format corrections

## Conclusion

The current Stage 3 generation pipeline has solid foundations but requires **immediate fixes** for validation logic and **strategic enhancements** for guaranteed format compliance. The proposed JSON Schema approach provides the most robust solution for ensuring strict structure adherence while maintaining flexibility for content generation.

The immediate priority is fixing the quiz validation logic to unblock current CLI generation, followed by implementing comprehensive JSON Schema validation for long-term format enforcement reliability. 