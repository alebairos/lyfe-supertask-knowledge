# Configurable Narrative Sequence Feature

**Feature ID**: CNS-001  
**Priority**: High  
**Type**: Enhancement  
**Target Release**: v1.2  
**Estimated Effort**: 1-2 weeks  

---

## 🎯 **Executive Summary**

Enable users to customize the narrative flow sequence of supertask content through a configurable parameter. Instead of the hardcoded `content → quiz → content → quote → content → quiz` pattern, users can specify their own storytelling sequences to optimize for different learning objectives, content types, and audience preferences.

## 🔍 **Problem Statement**

### **Current Limitations**
- **Fixed Narrative**: All supertasks follow the same `content → quiz → content → quote → content → quiz` pattern
- **No Flexibility**: Different content types (educational vs motivational vs practical) may benefit from different sequences
- **Audience Constraints**: Beginner vs advanced learners may need different pacing and engagement patterns
- **Content Type Mismatch**: Some topics work better with inspiration-first (quote-led) or assessment-first (quiz-led) approaches

### **Use Cases Requiring Different Sequences**

**1. Motivation-First Pattern** (`quote → content → quiz → content → quiz → quote`)
- **When**: Inspirational content, personal development, overcoming challenges
- **Why**: Start with inspiration to create emotional engagement before diving into concepts

**2. Assessment-First Pattern** (`quiz → content → quote → content → quiz → content`)
- **When**: Skills assessment, knowledge validation, diagnostic learning
- **Why**: Test existing knowledge first, then provide targeted content

**3. Deep Learning Pattern** (`content → content → quiz → quote → content → quiz`)
- **When**: Complex technical topics, academic subjects, detailed explanations
- **Why**: Build solid conceptual foundation before testing understanding

**4. Rapid Engagement Pattern** (`quiz → quote → content → quiz → quote → content`)
- **When**: Short attention spans, mobile-first users, quick wins
- **Why**: Alternate between interaction and inspiration for maximum engagement

## 💡 **Proposed Solution**

### **Core Feature: Narrative Sequence Parameter**

Add a new CLI parameter `--sequence` that accepts a string defining the desired narrative flow:

```bash
# Default behavior (current)
lyfe-kt generate template input.md output/ --difficulty beginner

# Custom sequence examples
lyfe-kt generate template input.md output/ --sequence "quote → content → quiz → content → quiz → quote"
lyfe-kt generate template input.md output/ --sequence "quiz → content → quote → content → quiz → content"
lyfe-kt generate template input.md output/ --sequence "content → content → quiz → quote → content → quiz"
```

### **Sequence String Format**

**Syntax**: `"type → type → type → ..."`
- **Separators**: ` → ` (space-arrow-space) for maximum readability
- **Types**: `content`, `quiz`, `quote`
- **Length**: 3-8 items (matching mobile schema limits)
- **Validation**: Must include at least 1 of each type for balanced learning

### **Configuration Integration**

**1. CLI Parameter**
```bash
--sequence "content → quiz → content → quote → content → quiz"
```

**2. Template Frontmatter** (optional override)
```yaml
---
title: "Finding Meaning in Life"
difficulty: beginner
sequence: "quote → content → quiz → content → quiz → quote"
---
```

**3. Configuration File** (global defaults)
```yaml
# config/generation_prompts.yaml
narrative_sequences:
  default: "content → quiz → content → quote → content → quiz"
  motivational: "quote → content → quiz → content → quiz → quote"
  assessment: "quiz → content → quote → content → quiz → content"
  deep_learning: "content → content → quiz → quote → content → quiz"
  rapid_engagement: "quiz → quote → content → quiz → quote → content"
```

## 🏗️ **Technical Implementation**

### **Phase 1: Core Infrastructure (Week 1)**

**1. Sequence Parser**
```python
class SequenceParser:
    def parse_sequence(self, sequence_str: str) -> List[str]:
        """Parse sequence string into list of item types."""
        
    def validate_sequence(self, sequence: List[str]) -> bool:
        """Validate sequence meets requirements."""
        
    def get_default_sequence(self) -> List[str]:
        """Return default sequence pattern."""
```

**2. CLI Integration**
```python
@click.option('--sequence', 
              help='Narrative sequence pattern (e.g., "content → quiz → quote")')
def generate_template(template_file, output_dir, difficulty, sequence, progress):
    # Parse and validate sequence
    # Pass to generation pipeline
```

**3. Enhanced Narrative Creator**
```python
def _create_narrative_sequence(self, content_items, quiz_items, quote_items, 
                              custom_sequence=None):
    """Create narrative flow with configurable sequence."""
    sequence = custom_sequence or self.default_sequence
    # Apply custom pattern instead of hardcoded pattern
```

### **Phase 2: Advanced Features (Week 2)**

**4. Preset Sequences**
```python
PRESET_SEQUENCES = {
    'default': 'content → quiz → content → quote → content → quiz',
    'motivational': 'quote → content → quiz → content → quiz → quote',
    'assessment': 'quiz → content → quote → content → quiz → content',
    'deep_learning': 'content → content → quiz → quote → content → quiz',
    'rapid_engagement': 'quiz → quote → content → quiz → quote → content'
}
```

**5. Smart Validation**
```python
def validate_sequence_requirements(sequence):
    """Ensure balanced learning experience."""
    # Must have at least 1 content, 1 quiz, 1 quote
    # Must be 3-8 items total
    # Should not have more than 2 consecutive items of same type
```

**6. Template Override Support**
```python
def extract_sequence_from_template(frontmatter):
    """Allow template-level sequence customization."""
```

## 📋 **User Experience Design**

### **CLI Usage Examples**

**Basic Usage** (backward compatible)
```bash
lyfe-kt generate template content.md output/
# Uses default: content → quiz → content → quote → content → quiz
```

**Custom Sequence**
```bash
lyfe-kt generate template content.md output/ --sequence "quote → content → quiz → content → quiz → quote"
```

**Preset Sequences**
```bash
lyfe-kt generate template content.md output/ --sequence motivational
# Expands to: quote → content → quiz → content → quiz → quote
```

**Combined with Other Options**
```bash
lyfe-kt generate template content.md output/ --difficulty advanced --sequence "quiz → content → quote → content → quiz → content" --progress
```

### **Error Handling & User Feedback**

**Validation Errors**
```bash
❌ Invalid sequence: "content → content → content → content"
   Reason: Must include at least one quiz and one quote item
   
❌ Invalid sequence: "content quiz quote"
   Reason: Use ' → ' separator (space-arrow-space)
   
❌ Invalid sequence: "content → quiz → unknown → quote"
   Reason: Unknown item type 'unknown'. Valid types: content, quiz, quote
```

**Success Feedback**
```bash
✅ Using custom sequence: quote → content → quiz → content → quiz → quote
📊 Generated 6 items following motivational pattern
```

## 🧪 **Testing Strategy**

### **Unit Tests**
```python
def test_sequence_parser_valid_patterns():
    """Test parsing of valid sequence strings."""
    
def test_sequence_parser_invalid_patterns():
    """Test rejection of invalid sequences."""
    
def test_narrative_sequence_creation():
    """Test creation of items following custom sequence."""
    
def test_preset_sequence_expansion():
    """Test expansion of preset sequence names."""
```

### **Integration Tests**
```python
def test_cli_custom_sequence():
    """Test CLI with custom sequence parameter."""
    
def test_template_sequence_override():
    """Test template frontmatter sequence override."""
    
def test_sequence_with_different_difficulties():
    """Test custom sequences work with beginner/advanced."""
```

### **Quality Assurance**
- Test all preset sequences produce valid, engaging content
- Verify mobile optimization works with all sequence patterns
- Ensure schema compliance regardless of sequence
- Validate learning effectiveness of different patterns

## 📊 **Success Metrics**

### **Technical Metrics**
- ✅ All sequence patterns generate valid JSON (100% schema compliance)
- ✅ Performance remains under 100ms for sequence parsing
- ✅ Memory usage doesn't increase significantly with custom sequences
- ✅ Backward compatibility maintained (existing commands work unchanged)

### **User Experience Metrics**
- 📈 Adoption rate of custom sequences vs default
- 📈 User satisfaction with sequence flexibility
- 📈 Content engagement scores by sequence type
- 📉 Support requests related to narrative flow

### **Content Quality Metrics**
- 🎯 Learning objective achievement by sequence pattern
- 🎯 User completion rates by sequence type
- 🎯 Content coherence scores across different patterns

## 🚀 **Implementation Plan**

### **Week 1: Core Infrastructure**
- **Day 1-2**: Sequence parser and validation
- **Day 3-4**: CLI parameter integration
- **Day 5**: Enhanced narrative sequence creator
- **Weekend**: Unit tests and documentation

### **Week 2: Advanced Features**
- **Day 1-2**: Preset sequences and smart validation
- **Day 3-4**: Template frontmatter override support
- **Day 5**: Integration tests and error handling
- **Weekend**: QA, performance optimization, and final polish

## 🔮 **Future Enhancements**

### **Phase 3: AI-Powered Sequence Optimization**
- **Smart Sequence Suggestions**: AI analyzes content and suggests optimal sequence
- **A/B Testing Integration**: Automatically test different sequences for effectiveness
- **Learning Analytics**: Track which sequences work best for different content types

### **Phase 4: Advanced Customization**
- **Conditional Sequences**: Different sequences based on user progress or preferences
- **Dynamic Length**: Sequences that adapt length based on content complexity
- **Micro-Interactions**: Custom transitions and animations between sequence items

## 💭 **Discussion Points**

### **🎯 Strategic Value**
1. **Differentiation**: This feature sets us apart from static learning platforms
2. **Flexibility**: Supports diverse content creators and learning styles
3. **Scalability**: Foundation for future AI-powered content optimization
4. **User Empowerment**: Gives creators control over their storytelling approach

### **🤔 Design Considerations**

**1. Default Behavior**
- Should we change the current default sequence based on research?
- How do we ensure backward compatibility while encouraging exploration?

**2. Sequence Validation**
- How strict should validation be? (e.g., max consecutive items of same type)
- Should we allow sequences without certain item types?

**3. User Interface**
- CLI-only or should we add config file support?
- Visual sequence builder for future web interface?

**4. Performance Impact**
- Caching strategies for frequently used sequences
- Memory optimization for complex sequence patterns

### **🔍 Research Questions**
1. **Learning Science**: Which sequences are most effective for different content types?
2. **User Behavior**: How will users discover and adopt custom sequences?
3. **Content Analysis**: Can we automatically suggest optimal sequences based on content analysis?

## 🎉 **Expected Impact**

### **For Content Creators**
- ✅ **Creative Freedom**: Full control over narrative pacing and flow
- ✅ **Content Optimization**: Match sequence to content type and audience
- ✅ **Experimentation**: A/B test different approaches easily

### **For Learners**
- ✅ **Personalized Experience**: Sequences optimized for their learning style
- ✅ **Better Engagement**: Appropriate pacing and interaction patterns
- ✅ **Improved Outcomes**: Sequences designed for specific learning objectives

### **For Platform**
- ✅ **Competitive Advantage**: Unique storytelling flexibility
- ✅ **Data Insights**: Rich analytics on sequence effectiveness
- ✅ **Scalable Foundation**: Platform for future AI-powered optimizations

---

**This feature transforms the Lyfe Supertask Knowledge Generator from a fixed-pattern content creator into a flexible storytelling platform, empowering users to craft the perfect learning journey for their audience.** 🎯✨