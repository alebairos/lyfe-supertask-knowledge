# Supertask Narrative Flow & Content Coverage - Feature Document

**Feature ID**: `supertask-narrative-01`  
**Priority**: HIGH - Core Learning Experience  
**Status**: ANALYSIS COMPLETE - Ready for Implementation  
**Discovered**: August 5, 2025 during content quality analysis

---

## 🚨 **Problem Statement**

The current supertask generation **lacks storytelling integration and comprehensive content coverage**:

### **Current Broken Behavior:**
```json
// Generated sequence (WRONG)
"content → content → content → content → quiz → quiz → quote → quote"

// Configured sequence (CORRECT)  
"content → quiz → content → quote → content → quiz"
```

### **Content Coverage Issues:**
- **Raw content has**: 5 specific areas of meaning (amor, transcendência, serviço, beleza, sofrimento)
- **Generated supertask covers**: Generic mentions without deep exploration
- **Quizzes test**: Random concepts instead of specific content areas
- **No narrative flow**: Items are independent chunks with no connection

### **Evidence:**
```json
{
  "type": "quiz",
  "question": "Qual é o conceito principal sobre Encontrando Sentido na Vida?",
  "options": ["Desenvolvimento pessoal", "Ciência comportamental"]
}
```
**↑ Quiz tests generic concepts, not the 5 specific areas from raw content**

---

## 🎯 **Success Criteria**

1. **Narrative Sequencing**: Items follow configured flow pattern `content → quiz → content → quote → content → quiz`
2. **Content Coverage**: All key concepts from raw content are covered in flexible items
3. **Connected Learning**: Each item builds logically on the previous one
4. **Specific Testing**: Quizzes test the actual content areas, not generic concepts
5. **Story Coherence**: User experiences a coherent learning journey through the material

---

## 🔧 **Simplest Implementation That Could Possibly Work**

### **Step 1: Fix Item Sequencing (Narrative Flow)**

**File**: `src/lyfe_kt/stage3_generation.py`

**Current Code** (Lines 155-170):
```python
def _generate_flexible_items(self, template_data: Dict[str, Any], difficulty: str) -> List[Dict[str, Any]]:
    flexible_items = []
    
    # Groups by type (WRONG)
    content_items = self._extract_and_split_content(template_data, difficulty)
    flexible_items.extend(content_items)
    
    quiz_items = self._generate_quiz_items(template_data, difficulty)
    flexible_items.extend(quiz_items)
    
    quote_items = self._generate_quote_items(template_data, difficulty)
    flexible_items.extend(quote_items)
```

**Fixed Code**:
```python
def _generate_flexible_items(self, template_data: Dict[str, Any], difficulty: str) -> List[Dict[str, Any]]:
    # Generate all item types first
    content_items = self._extract_and_split_content(template_data, difficulty)
    quiz_items = self._generate_quiz_items(template_data, difficulty)
    quote_items = self._generate_quote_items(template_data, difficulty)
    
    # Apply narrative sequencing
    flexible_items = self._create_narrative_sequence(content_items, quiz_items, quote_items)
    
    return flexible_items
```

### **Step 2: Implement Narrative Sequencing**

**File**: `src/lyfe_kt/stage3_generation.py`

**New Method**:
```python
def _create_narrative_sequence(self, content_items: List[Dict], quiz_items: List[Dict], quote_items: List[Dict]) -> List[Dict]:
    """Create narrative flow following: content → quiz → content → quote → content → quiz"""
    try:
        narrative_items = []
        
        # Target pattern: content → quiz → content → quote → content → quiz
        # Minimum: 3 items, Maximum: 8 items
        
        # Ensure we have items to work with
        if not content_items:
            content_items = [self._create_default_content_item("beginner", 0)]
        if not quiz_items:
            quiz_items = [self._create_default_quiz_item("beginner")]
        if not quote_items:
            quote_items = [self._create_default_quote_item("beginner")]
        
        # Create iterators to cycle through items
        content_iter = iter(content_items)
        quiz_iter = iter(quiz_items)
        quote_iter = iter(quote_items)
        
        # Build narrative sequence
        pattern = ['content', 'quiz', 'content', 'quote', 'content', 'quiz']
        
        for i, item_type in enumerate(pattern):
            if len(narrative_items) >= 8:  # Max mobile limit
                break
                
            try:
                if item_type == 'content':
                    narrative_items.append(next(content_iter))
                elif item_type == 'quiz':
                    narrative_items.append(next(quiz_iter))
                elif item_type == 'quote':
                    narrative_items.append(next(quote_iter))
            except StopIteration:
                # If we run out of items of this type, skip
                continue
        
        # Ensure minimum of 3 items
        while len(narrative_items) < 3:
            narrative_items.append(self._create_default_content_item("beginner", len(narrative_items)))
        
        logger.info(f"Created narrative sequence with {len(narrative_items)} items following story pattern")
        return narrative_items
        
    except Exception as e:
        logger.error(f"Failed to create narrative sequence: {e}")
        # Fallback to original behavior
        return content_items + quiz_items + quote_items
```

### **Step 3: Implement Content Coverage Mapping**

**File**: `src/lyfe_kt/stage3_generation.py`

**Enhanced Content Extraction**:
```python
def _extract_and_split_content(self, template_data: Dict[str, Any], difficulty: str) -> List[Dict[str, Any]]:
    """Extract content ensuring comprehensive coverage of raw material."""
    sections = template_data.get('sections', {})
    content_items = []
    
    # Map key concepts from template
    key_concepts = self._extract_key_concepts(template_data)
    
    # Ensure each key concept gets coverage
    for i, concept in enumerate(key_concepts):
        concept_content = self._generate_concept_content(concept, sections, difficulty)
        if concept_content:
            content_items.append({
                "type": "content",
                "content": concept_content,
                "author": "Ari",
                "concept_focus": concept  # Track what this item covers
            })
    
    # Add overview if we have multiple concepts
    if len(key_concepts) > 1:
        overview_content = self._generate_overview_content(key_concepts, sections, difficulty)
        content_items.insert(0, {
            "type": "content", 
            "content": overview_content,
            "author": "Ari",
            "concept_focus": "overview"
        })
    
    return content_items[:4]  # Max 4 content items for mobile
```

### **Step 4: Implement Specific Content Testing**

**File**: `src/lyfe_kt/stage3_generation.py`

**Enhanced Quiz Generation**:
```python
def _generate_quiz_items(self, template_data: Dict[str, Any], difficulty: str) -> List[Dict[str, Any]]:
    """Generate quizzes that test specific content areas, not generic concepts."""
    key_concepts = self._extract_key_concepts(template_data)
    quiz_items = []
    
    # Generate specific quizzes for key concepts
    for concept in key_concepts[:2]:  # Max 2 quizzes for mobile
        quiz_content = self._generate_concept_quiz(concept, template_data, difficulty)
        if quiz_content:
            quiz_items.append(quiz_content)
    
    # If no specific concepts, create one quiz about main topic
    if not quiz_items:
        main_topic = template_data.get('frontmatter', {}).get('title', 'this topic')
        quiz_items.append({
            "type": "quiz",
            "question": f"What is the main focus of {main_topic.lower()}?",
            "options": ["Personal growth", "Behavioral change", "Skill development", "Knowledge building"],
            "correctAnswer": 0,
            "explanation": "This content focuses on personal growth and development."
        })
    
    return quiz_items
```

### **Step 5: Add Helper Methods**

**File**: `src/lyfe_kt/stage3_generation.py`

**New Helper Methods**:
```python
def _extract_key_concepts(self, template_data: Dict[str, Any]) -> List[str]:
    """Extract key concepts that need coverage from template data."""
    concepts = []
    sections = template_data.get('sections', {})
    
    # Look for numbered content items
    main_content = sections.get('main_content', '')
    
    # Extract concepts from content items (Content Item 1, Content Item 2, etc.)
    import re
    content_items = re.findall(r'### Content Item \d+\s*(.+?)(?=###|$)', main_content, re.DOTALL)
    
    for item in content_items:
        # Extract first sentence as concept focus
        first_sentence = item.split('.')[0].strip()
        if first_sentence and len(first_sentence) > 10:
            concepts.append(first_sentence[:50])  # Truncate for focus
    
    # Look for key themes mentioned in overview
    overview = sections.get('overview', '')
    if 'cinco áreas' in overview.lower():
        concepts.append("cinco áreas de significado")
    if 'amor, transcendência, serviço' in overview.lower():
        concepts.extend(["amor e relacionamentos", "transcendência e conexão", "serviço aos outros"])
    
    return concepts[:4]  # Max 4 concepts for mobile

def _generate_concept_content(self, concept: str, sections: Dict, difficulty: str) -> str:
    """Generate content focused on a specific concept."""
    # Use AI to generate focused content for this concept
    content = f"Understanding {concept} is essential for personal growth."
    
    # Enhance with difficulty-appropriate insights
    if difficulty == "advanced":
        content += " This involves deep self-reflection and consistent practice."
    else:
        content += " Start with small, daily practices to build this understanding."
    
    return self._ai_enhance_content(content, difficulty)

def _generate_concept_quiz(self, concept: str, template_data: Dict, difficulty: str) -> Dict[str, Any]:
    """Generate a quiz specifically testing this concept."""
    return {
        "type": "quiz",
        "question": f"How can you apply {concept.lower()} in daily life?",
        "options": [
            "Daily reflection",
            "Ignore it completely", 
            "Only think about it",
            "Wait for motivation"
        ],
        "correctAnswer": 0,
        "explanation": f"Daily reflection and practice help integrate {concept.lower()} into your life."
    }
```

---

## 🛡️ **Defensive Tests**

### **Test 1: Narrative Sequencing**

```python
def test_narrative_sequencing():
    """Test that items follow content → quiz → content → quote pattern."""
    template_data = load_test_template()
    generator = StructuralJSONGenerator()
    
    result = generator.generate_supertask(template_data, "beginner")
    items = result['flexibleItems']
    
    # Check pattern compliance
    expected_pattern = ['content', 'quiz', 'content', 'quote', 'content', 'quiz']
    actual_pattern = [item['type'] for item in items]
    
    # Allow partial pattern if fewer than 6 items
    for i, expected_type in enumerate(expected_pattern):
        if i < len(actual_pattern):
            assert actual_pattern[i] == expected_type, f"Item {i} should be {expected_type}, got {actual_pattern[i]}"
```

### **Test 2: Content Coverage**

```python
def test_content_coverage():
    """Test that key concepts from raw content are covered."""
    template_data = load_test_template_with_concepts()
    generator = StructuralJSONGenerator()
    
    result = generator.generate_supertask(template_data, "beginner")
    
    # Extract all content from flexible items
    all_content = ' '.join([
        item.get('content', '') + ' ' + item.get('question', '')
        for item in result['flexibleItems']
    ]).lower()
    
    # Verify key concepts are mentioned
    key_concepts = ["amor", "transcendência", "serviço", "beleza", "sofrimento"]
    covered_concepts = [concept for concept in key_concepts if concept in all_content]
    
    assert len(covered_concepts) >= 3, f"Should cover at least 3 key concepts, only covered: {covered_concepts}"
```

### **Test 3: Specific Testing**

```python
def test_specific_content_testing():
    """Test that quizzes test actual content, not generic concepts."""
    template_data = load_test_template_with_specific_content()
    generator = StructuralJSONGenerator()
    
    result = generator.generate_supertask(template_data, "beginner")
    
    # Find quiz items
    quiz_items = [item for item in result['flexibleItems'] if item['type'] == 'quiz']
    
    assert len(quiz_items) >= 1, "Should have at least one quiz"
    
    # Check that quiz questions reference specific content
    for quiz in quiz_items:
        question = quiz['question'].lower()
        explanation = quiz['explanation'].lower()
        
        # Should not be completely generic
        generic_terms = ['conceito principal', 'desenvolvimento pessoal', 'ciência comportamental']
        is_generic = any(term in question for term in generic_terms)
        
        # Should reference specific content elements
        specific_terms = ['amor', 'transcendência', 'serviço', 'significado', 'sentido']
        is_specific = any(term in question or term in explanation for term in specific_terms)
        
        assert not is_generic or is_specific, f"Quiz should test specific content: {question}"
```

### **Test 4: Story Coherence**

```python
def test_story_coherence():
    """Test that items create a coherent learning progression."""
    template_data = load_test_template()
    generator = StructuralJSONGenerator()
    
    result = generator.generate_supertask(template_data, "beginner")
    items = result['flexibleItems']
    
    # First item should be introductory
    first_content = items[0]['content'].lower()
    assert any(word in first_content for word in ['neste', 'aprenderá', 'você', 'vamos']), \
        "First item should be introductory"
    
    # Quiz should test content that appeared before it
    content_before_quiz = ' '.join([item['content'] for item in items[:2] if item['type'] == 'content']).lower()
    first_quiz = next((item for item in items if item['type'] == 'quiz'), None)
    
    if first_quiz:
        quiz_question = first_quiz['question'].lower()
        # Quiz should reference concepts mentioned in prior content
        has_connection = any(word in content_before_quiz and word in quiz_question 
                           for word in ['sentido', 'significado', 'vida', 'amor', 'serviço'])
        assert has_connection, "Quiz should test concepts from previous content"
```

### **Test 5: Mobile Optimization**

```python
def test_mobile_narrative_optimization():
    """Test that narrative flow works within mobile constraints."""
    template_data = load_test_template()
    generator = StructuralJSONGenerator()
    
    result = generator.generate_supertask(template_data, "beginner")
    items = result['flexibleItems']
    
    # Should have 3-8 items (mobile constraint)
    assert 3 <= len(items) <= 8, f"Should have 3-8 items, got {len(items)}"
    
    # Should have variety (not all same type)
    types = [item['type'] for item in items]
    unique_types = set(types)
    assert len(unique_types) >= 2, f"Should have at least 2 different types, got: {unique_types}"
    
    # Each content item should respect character limits
    for item in items:
        if item['type'] == 'content':
            content_length = len(item['content'])
            assert 50 <= content_length <= 300, f"Content should be 50-300 chars, got {content_length}"
```

---

## 📋 **Files to Modify**

1. **`src/lyfe_kt/stage3_generation.py`** - Main implementation (5 new methods, 2 enhanced methods)
2. **`tests/test_narrative_flow.py`** - New test file (5 comprehensive tests)

---

## 🔄 **Implementation Steps**

### **Phase 1: Core Narrative Flow (45 minutes)**
1. Add `_create_narrative_sequence()` method
2. Update `_generate_flexible_items()` to use narrative sequencing
3. Add defensive fallbacks for missing items

### **Phase 2: Content Coverage (60 minutes)**
4. Add `_extract_key_concepts()` method
5. Enhance `_extract_and_split_content()` for concept coverage
6. Add `_generate_concept_content()` helper

### **Phase 3: Specific Testing (30 minutes)**
7. Enhance `_generate_quiz_items()` for concept-specific quizzes
8. Add `_generate_concept_quiz()` helper
9. Update quiz generation to test actual content

### **Phase 4: Testing & Validation (45 minutes)**
10. Write 5 comprehensive defensive tests
11. Run full test suite to ensure no regressions
12. Manual testing with real templates

---

## 🚦 **Risk Assessment**

**Risk Level**: **MEDIUM**
- More complex than simple parameter fix
- Changes core generation logic
- Could affect existing content quality

**Mitigation**:
- Defensive fallbacks preserve existing behavior if narrative flow fails
- Comprehensive test coverage
- Step-by-step implementation with validation at each phase

---

## ✅ **Acceptance Criteria Checklist**

**Before Implementation:**
- [ ] Understand current broken sequencing behavior
- [ ] Identify all concepts that need coverage in test content
- [ ] Plan narrative flow pattern implementation

**During Implementation:**
- [ ] Implement narrative sequencing logic
- [ ] Add content coverage mapping
- [ ] Enhance quiz generation for specific testing
- [ ] Add defensive fallbacks
- [ ] Write comprehensive tests

**After Implementation:**
- [ ] Items follow `content → quiz → content → quote → content → quiz` pattern
- [ ] Key concepts from raw content are covered in generated items
- [ ] Quizzes test specific content areas, not generic concepts
- [ ] Story creates coherent learning progression
- [ ] Mobile constraints respected (3-8 items, character limits)
- [ ] All tests pass
- [ ] Manual validation with real content successful

---

## 🎯 **Expected Outcome**

**Before (Current Broken State):**
```json
{
  "flexibleItems": [
    {"type": "content", "content": "Generic intro..."},
    {"type": "content", "content": "Generic content..."},
    {"type": "content", "content": "Generic content..."},
    {"type": "content", "content": "Broken formatting..."},
    {"type": "quiz", "question": "What is the main concept?"},
    {"type": "quiz", "question": "How to apply in daily life?"},
    {"type": "quote", "content": "Generic quote..."},
    {"type": "quote", "content": "Generic quote..."}
  ]
}
```

**After (Narrative Flow with Content Coverage):**
```json
{
  "flexibleItems": [
    {"type": "content", "content": "Você aprenderá sobre cinco áreas de significado: amor, transcendência, serviço, beleza e sofrimento.", "concept_focus": "overview"},
    {"type": "quiz", "question": "Qual das cinco áreas de significado ressoa mais com você?", "options": ["Amor e relacionamentos", "Transcendência espiritual", "Serviço aos outros", "Apreciação da beleza"]},
    {"type": "content", "content": "O amor como fonte de significado envolve tanto dar quanto receber...", "concept_focus": "amor e relacionamentos"},
    {"type": "quote", "content": "O propósito da vida é viver uma vida com propósito.", "author": "Richard Leider"},
    {"type": "content", "content": "A transcendência pode ser encontrada em momentos de profunda conexão...", "concept_focus": "transcendência e conexão"},
    {"type": "quiz", "question": "Como você pode praticar transcendência no dia a dia?", "options": ["Meditação diária", "Ignorar os outros", "Focar apenas no trabalho", "Evitar conexões"]}
  ]
}
```

---

## 🚀 **Ready for Implementation**

**Estimated Time**: 3 hours  
**Complexity**: MEDIUM  
**Impact**: HIGH (transforms learning experience)  
**Testing Strategy**: Defensive with 5 comprehensive tests covering sequencing, coverage, specificity, coherence, and mobile optimization

**This simple narrative feature will transform supertasks from fragmented content chunks into coherent, engaging learning stories that comprehensively cover the raw material!** 🎯

---

## 💡 **Future Enhancements (Beyond Scope)**

After this basic implementation succeeds:
- **Dynamic flow patterns** based on content type
- **Adaptive difficulty progression** within the narrative
- **Emotional engagement curves** with strategic quote placement
- **Multi-supertask story arcs** for complex topics
- **Personalized narrative paths** based on user archetype

**But for now: Simple narrative sequencing + content coverage = Massive improvement!** ✨