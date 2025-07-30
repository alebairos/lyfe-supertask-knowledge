# Mobile-Optimized Schema v1.1 - Simple Implementation PRD

## 📋 Feature Overview

**Feature Name**: Mobile-Optimized Supertask Schema v1.1  
**Version**: 1.1.0  
**Priority**: HIGH  
**Target Release**: Q1 2025 (2-3 weeks)  
**Owner**: Engineering Team  
**Stakeholders**: Product, UX, Content Team  

## 🎯 Problem Statement

### Current Issues
1. **Schema v1.0 Mismatch**: Current schema allows content 10-50x larger than mobile screens can display
2. **Poor UX**: Content requiring excessive scrolling, inconsistent supertask lengths
3. **Validation Gaps**: Schema passes validation but creates unusable mobile content

### Impact on Users
- **Poor Mobile Experience**: Users face content that doesn't fit screens properly
- **Inconsistent Engagement**: Supertasks vary wildly in length and complexity

## 🚀 Proposed Solution

### High-Level Approach
Replace **Schema v1.0** with **Mobile-First Schema v1.1** with strict content size limits for optimal mobile experience.

### Core Components
1. **New JSON Schema v1.1** with mobile-optimized limits
2. **Pipeline Integration** for v1.1 validation
3. **Basic Quality Metrics** for mobile optimization

## 📋 Functional Requirements

### 1. Schema Enhancements (v1.1)

#### 1.1 Content Size Optimization
- **Content items**: 50-300 characters (was 10-5000)
- **Quiz questions**: 15-120 characters (was 10-500)
- **Quiz options**: 3-60 characters each (was 1-200)
- **Quotes**: 20-200 characters (was 10-1000)
- **Explanations**: 30-250 characters (was 10-1000)

#### 1.2 Supertask Structure Constraints
- **Total items**: 3-8 items per supertask (was 1-20)
- **Duration**: 180-600 seconds (was 60-7200)
- **Minimum requirements**: At least 1 content item, recommended 1-3 quiz items



### 2. Pipeline Integration

#### 2.1 Schema Validation Updates
- **Stage 3 Generation**: Replace v1.0 with v1.1 schema validation
- **Output Validation**: Strict enforcement of mobile character limits

#### 2.2 Generation Prompt Updates
```yaml
generation_prompts:
  mobile_constraints:
    content_guidance: "Keep content items between 50-300 characters for optimal mobile display"
    quiz_guidance: "Quiz questions should be 15-120 characters, options 3-60 characters"
    quote_guidance: "Quotes should be 20-200 characters for mobile readability"
```

### 3. Basic Quality Metrics

#### 3.1 Content Quality Metrics
```json
{
  "content_metrics": {
    "total_word_count": {"min": 50, "max": 250},
    "reading_time_seconds": {"min": 30, "max": 120},
    "mobile_optimization_score": {"min": 0.8, "max": 1.0}
  }
}
```

## 🔧 Technical Requirements

### 1. Schema Implementation

#### 1.1 New Schema File
- **Location**: `src/config/supertask_schema_v1.1.json`
- **Validation**: JSON Schema Draft-07 compliant
- **Replaces**: `supertask_schema_v1.0.json` completely

### 2. Pipeline Updates

#### 2.1 Stage 3 Generation Update
```python
class StructuralJSONGenerator:
    def __init__(self, format_version="v1.1"):
        self.format_version = format_version
        # Load v1.1 schema instead of v1.0
        self.schema_path = f"src/config/supertask_schema_{format_version}.json"
    
    def _validate_structure(self, json_data):
        # Use v1.1 schema validation
        import jsonschema
        with open(self.schema_path, 'r') as f:
            schema = json.load(f)
        jsonschema.validate(json_data, schema)
        return True
```



## 📊 Success Metrics

### 1. Technical Metrics
- **Schema Compliance**: 100% of generated content passes v1.1 validation
- **Mobile Optimization Score**: Average mobile score > 0.85
- **Generation Success Rate**: > 95% successful generations with v1.1
- **Pipeline Performance**: No degradation in processing time

### 2. Content Quality Metrics
- **Character Limit Compliance**: 100% adherence to mobile limits
- **Content Consistency**: < 10% variation in supertask lengths

### 3. User Experience Metrics (Post-Implementation)
- **Mobile Scroll Reduction**: 80% reduction in excessive scrolling
- **Content Engagement**: Consistent engagement across all supertasks

## 🚧 Implementation Plan

### Week 1: Schema Development
- [ ] Create `supertask_schema_v1.1.json` with mobile constraints
- [ ] Replace v1.0 schema in pipeline

### Week 2: Pipeline Integration
- [ ] Update `StructuralJSONGenerator` to use v1.1 schema
- [ ] Test generation with mobile limits

### Week 3: Testing & Validation
- [ ] Test with `solidao_cronica.md` sample
- [ ] Validate mobile compliance
- [ ] Performance testing

## 🔄 Implementation Approach

### Simple Replacement Strategy
- **Direct Replacement**: v1.1 schema replaces v1.0 completely
- **No Migration Needed**: No legacy content to migrate
- **Clean Start**: All new supertasks use mobile-optimized schema

## 🎯 Acceptance Criteria

### Must Have
- [ ] Schema v1.1 enforces mobile-optimized content limits
- [ ] Pipeline generates 100% compliant v1.1 content
- [ ] Basic testing with sample content

### Should Have
- [ ] Performance metrics for mobile optimization
- [ ] Content quality validation

### Could Have
- [ ] Advanced layout pattern support (future iteration)
- [ ] AI-powered content optimization suggestions

## 🚨 Risks & Mitigation

### 1. Content Quality Degradation
- **Risk**: Strict limits may reduce content richness
- **Mitigation**: Test with sample content, validate mobile experience

### 2. Pipeline Performance Impact
- **Risk**: Schema validation may slow generation
- **Mitigation**: Simple schema replacement, minimal code changes

## 📚 Documentation Requirements

### 1. Technical Documentation
- [ ] Schema v1.1 specification document
- [ ] Pipeline integration changes

### 2. Testing Documentation
- [ ] Basic test plan for mobile validation
- [ ] Sample content testing results

## 🔗 Dependencies

### Internal
- [ ] `src/config/supertask_schema_v1.0.json` (to be replaced)
- [ ] `src/lyfe_kt/stage3_generation.py` (generation pipeline)
- [ ] `tests/test_cli_full_pipeline.py` (testing framework)

### External
- [ ] JSON Schema validation library (jsonschema)

---

**Approval Required From:**
- [ ] Engineering Lead
- [ ] Product Manager
- [ ] UX Design Lead
- [ ] Content Strategy Lead

**Estimated Effort:** 3 weeks  
**Team Size:** 1 engineer  
**Priority:** HIGH (Mobile-first initiative critical for user experience)

---

*This simplified PRD focuses on immediate mobile optimization through schema replacement, delivering core mobile-first functionality quickly.* 