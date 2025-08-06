# Supertask Testing UI - Fix 01: Content Generation Issues

**Date**: 2025-08-05  
**Priority**: 🔴 HIGH  
**Component**: Stage 3 Generation (Content Enhancement)  
**Impact**: User Experience & Content Quality

## 🐛 **Issues Identified During UI Testing**

### **Issue 1: Content Type Label Bleeding**
**Problem**: The word "Content" appears incorrectly in the actual content text.

**Current Output**:
```
"Content Neste supertask, você aprenderá sobre cinco áreas principais..."
```

**Expected Output**:
```
"Neste supertask, você aprenderá sobre cinco áreas principais..."
```

**Root Cause**: Content enhancement function is prepending type labels to the actual content.

---

### **Issue 2: "Supertask" Term in User Content**
**Problem**: The internal term "supertask" appears in user-facing content.

**Current Output**:
```
"Neste supertask, você aprenderá sobre..."
```

**Expected Output**:
```
"Neste exercício, você aprenderá sobre..." 
# OR
"Nesta atividade, você aprenderá sobre..."
```

**Root Cause**: Generation prompts not filtering out internal terminology.

---

### **Issue 3: Author/Tips Formatting Broken**
**Problem**: Author and tips are rendered as plain text instead of structured format.

**Current Output**:
```
Author: Equipe Lyfe Tips: - Tente identificar em quais dessas áreas você encontra mais sentido. - Crie micro-hábitos para se envolver mais nessas áreas. - Permita que o sentido evolua e mude com o tempo.
— Ari
```

**Expected Output**:
```json
{
  "type": "content",
  "content": "O sentido na vida é uma busca pessoal...",
  "author": "Equipe Lyfe",
  "tips": [
    "Tente identificar em quais dessas áreas você encontra mais sentido.",
    "Crie micro-hábitos para se envolver mais nessas áreas.", 
    "Permita que o sentido evolua e mude com o tempo."
  ]
}
```

**Root Cause**: Content parsing not properly separating author and tips into structured fields.

---

### **Issue 4: Difficulty Level in Quiz Questions**
**Problem**: Difficulty level ("Iniciante") appears in quiz questions.

**Current Output**:
```
"Qual é o conceito principal sobre Encontrando Sentido na Vida - Iniciante?"
"Como aplicar Encontrando Sentido na Vida - Iniciante no dia a dia?"
```

**Expected Output**:
```
"Qual é o conceito principal sobre Encontrando Sentido na Vida?"
"Como aplicar Encontrando Sentido na Vida no dia a dia?"
```

**Root Cause**: Quiz generation prompts including difficulty metadata in questions.

---

## 🔧 **Required Fixes**

### **Fix 1: Content Enhancement Function**
**File**: `src/lyfe_kt/stage3_generation.py`  
**Method**: `_ai_enhance_content()`

```python
# BEFORE:
def _ai_enhance_content(self, content: str, difficulty: str) -> str:
    # Current logic prepends "Content" 

# AFTER:
def _ai_enhance_content(self, content: str, difficulty: str) -> str:
    # Remove type labels from content
    content = re.sub(r'^(Content|Quiz|Quote)\s+', '', content, flags=re.IGNORECASE)
    # Continue with enhancement...
```

### **Fix 2: User-Facing Terminology**
**File**: `src/config/generation_prompts.yaml`  
**Section**: Content enhancement prompts

**Add Filtering Rules**:
```yaml
content_terminology_rules: |
  - Replace "supertask" with "exercício" or "atividade" 
  - Replace "flexibleItems" with user-friendly terms
  - Remove internal system terminology
  - Use Brazilian Portuguese equivalents
```

### **Fix 3: Structured Content Parsing**
**File**: `src/lyfe_kt/stage3_generation.py`  
**Method**: `_extract_and_split_content()`

**Enhanced Parsing Logic**:
```python
def _parse_content_structure(self, content_text: str) -> Dict[str, Any]:
    """Extract author, tips, and main content separately"""
    
    # Parse author line
    author_match = re.search(r'Author:\s*([^\n]+)', content_text)
    author = author_match.group(1).strip() if author_match else None
    
    # Parse tips section  
    tips_match = re.search(r'Tips:\s*(.+?)(?:\n—|$)', content_text, re.DOTALL)
    tips = []
    if tips_match:
        tips_text = tips_match.group(1)
        tips = [tip.strip('- ').strip() for tip in tips_text.split('\n') if tip.strip().startswith('-')]
    
    # Extract main content (remove author/tips sections)
    main_content = re.sub(r'Author:.*?$', '', content_text, flags=re.MULTILINE | re.DOTALL)
    main_content = re.sub(r'Tips:.*?$', '', main_content, flags=re.MULTILINE | re.DOTALL)
    
    return {
        'content': main_content.strip(),
        'author': author,
        'tips': tips if tips else None
    }
```

### **Fix 4: Quiz Question Enhancement**
**File**: `src/lyfe_kt/stage3_generation.py`  
**Method**: `_ai_enhance_question()`

```python
def _ai_enhance_question(self, question: str, difficulty: str) -> str:
    # Remove difficulty level from questions
    question = re.sub(r'\s*-\s*(Iniciante|Avançado|Beginner|Advanced)\s*', '', question)
    question = re.sub(r'\s*\((Iniciante|Avançado|Beginner|Advanced)\)\s*', '', question)
    
    # Continue with character limit enforcement...
```

---

## 🧪 **Testing Strategy**

### **Test Cases**:
1. **Content Items**: Verify no "Content" prefix, no "supertask" mentions
2. **Author/Tips**: Confirm proper JSON structure with separate fields  
3. **Quiz Questions**: Ensure no difficulty level in question text
4. **Character Limits**: All fixes maintain mobile optimization

### **Validation Steps**:
1. Run generation on sample content
2. Load output in Testing UI
3. Verify content formatting in debug panel
4. Check character counts remain compliant

---

## 📋 **Implementation Priority**

| Fix | Priority | Impact | Effort |
|-----|----------|---------|---------|
| Fix 1: Content Labels | 🔴 HIGH | User Experience | Low |
| Fix 2: Terminology | 🔴 HIGH | User Experience | Medium |
| Fix 3: Structure Parsing | 🟡 MEDIUM | Data Quality | High |
| Fix 4: Quiz Questions | 🔴 HIGH | User Experience | Low |

---

## ✅ **Acceptance Criteria**

**Content Items**:
- ❌ No "Content" prefix in content text
- ❌ No "supertask" mentions in user content  
- ✅ Proper author field separation
- ✅ Tips as structured array

**Quiz Items**:
- ❌ No difficulty level in questions
- ✅ Character limits maintained (15-120 chars)
- ✅ Clean, user-friendly language

**Overall**:
- ✅ Mobile optimization score ≥ 80%
- ✅ All character limits respected
- ✅ Structured JSON format maintained
- ✅ User-friendly Brazilian Portuguese

---

## 🎯 **Next Steps**

1. **Implement fixes in generation logic**
2. **Update generation prompts**  
3. **Test with Arthur Brooks content**
4. **Validate in Testing UI**
5. **Update TODO_RC.md with results**

**Testing Reference**: Load generated JSON in UI at `http://localhost:8080/index.html` to verify fixes.