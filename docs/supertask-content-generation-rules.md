# Supertask Content Generation Rules

## 📐 JSON Schema Compliance

The system uses **Supertask Schema v1.1 (Mobile-Optimized)** which enforces strict content rules:

### **Required Fields Structure**
```json
{
  "title": "string (1-200 chars)",
  "dimension": "physicalHealth|mentalHealth|relationships|work|spirituality",
  "archetype": "warrior|explorer|sage|ruler",
  "relatedToType": "HABITBP|GENERIC",
  "relatedToId": "string (min 1 char)",
  "estimatedDuration": "integer (180-600 seconds)",
  "coinsReward": "integer (1-1000 coins)",
  "flexibleItems": "array (3-8 items)",
  "metadata": "object with required fields"
}
```

### **Metadata Requirements**
```json
{
  "language": "portuguese|english|spanish",
  "region": "string (min 1 char)",
  "created_at": "ISO 8601 datetime",
  "updated_at": "ISO 8601 datetime",
  "version": "semantic version (e.g., 1.0.0)",
  "generated_by": "string (optional)",
  "generation_timestamp": "ISO 8601 datetime (optional)",
  "ari_persona_applied": "boolean (optional)",
  "difficulty_level": "beginner|intermediate|advanced (optional)",
  "source_template": "string (optional)",
  "mobile_optimization_score": "number 0.0-1.0 (optional)"
}
```

---

## 📱 Mobile-First Content Constraints (v1.1)

### **FlexibleItems Content Limits**

#### **1. Content Items**
```json
{
  "type": "content",
  "content": "50-300 characters (mobile optimized)",
  "author": "1-100 characters (optional)",
  "tips": ["20-150 characters each, max 5 tips (optional)"]
}
```

#### **2. Quote Items**
```json
{
  "type": "quote",
  "content": "20-200 characters (mobile optimized)",
  "author": "1-100 characters (required)"
}
```

#### **3. Quiz Items**
```json
{
  "type": "quiz",
  "question": "15-120 characters (mobile optimized)",
  "options": ["3-60 characters each", "2-5 options total"],
  "correctAnswer": "0-based index",
  "explanation": "30-250 characters (mobile optimized)"
}
```

### **Supertask Structure Limits**
- **Total Items**: 3-8 items per supertask (mobile-friendly)
- **Duration**: 180-600 seconds (3-10 minutes for mobile)
- **Minimum Content**: At least 1 content item
- **Recommended Quiz**: 1-3 quiz items for engagement

### **Character Limit Comparison (v1.0 → v1.1)**
| Content Type | v1.0 Limits | v1.1 Mobile Limits | Reduction |
|--------------|-------------|-------------------|-----------|
| Content items | 10-5000 chars | 50-300 chars | 94% reduction |
| Quiz questions | 10-500 chars | 15-120 chars | 76% reduction |
| Quiz options | 1-200 chars | 3-60 chars | 70% reduction |
| Quotes | 10-1000 chars | 20-200 chars | 80% reduction |
| Explanations | 10-1000 chars | 30-250 chars | 75% reduction |
| Total items | 1-20 items | 3-8 items | 60% reduction |
| Duration | 60-7200 seconds | 180-600 seconds | 92% reduction |

---

## 🎯 Content Quality Standards

### **Educational Effectiveness**
- **Learning Progression**: Gradual, step-by-step approach
- **Practical Application**: High focus on actionable content
- **Behavioral Focus**: Mandatory integration of behavioral science
- **Evidence-Based**: All content must be grounded in evidence

### **Content Composition Guidelines**
- **Minimum Content Items**: 3 items
- **Maximum Content Items**: 8 items
- **Minimum Quiz Items**: 2 questions
- **Maximum Quiz Items**: 4 questions
- **Variety Requirement**: Mix of content, quote, and quiz types

### **Recommended Flow Pattern**
```
Content → Quiz → Content → Quote → Content → Quiz
```

### **Quality Metrics Targets**
```json
{
  "content_metrics": {
    "total_word_count": {"min": 50, "max": 250},
    "reading_time_seconds": {"min": 30, "max": 120},
    "mobile_optimization_score": {"min": 0.8, "max": 1.0}
  }
}
```

---

## 🗣️ Ari Persona Voice Requirements

### **Language Requirements**
- **Language**: Portuguese (Brazilian)
- **Gender Forms**: Masculine forms required
- **Tone**: Encouraging but realistic
- **Style**: Brief intelligence (6-15 words per sentence)
- **Approach**: Evidence-based coaching

### **Content Voice Guidelines**
- Concise, intelligent, motivating communication
- Natural integration of behavioral science frameworks
- TARS-inspired brevity with engagement progression
- Cultural sensitivity for Brazilian context

### **Quiz Voice Integration**
- **Explanations**: Connect with behavioral principles
- **Coaching Language**: Use positive reinforcement
- **Learning Focus**: Celebrate incremental progress
- **Reflection Prompts**: Questions that stimulate thinking

### **Voice Markers**
```yaml
Language Markers:
  - "Use português masculino brasileiro"
  - "Prefira frases concisas (6-15 palavras)"
  - "Aplique ciência comportamental naturalmente"
  - "Mantenha tom motivador mas prático"

Coaching Integration:
  - "Celebre o progresso incremental"
  - "Foque em mudanças sustentáveis"
  - "Use perguntas que estimulem reflexão"
  - "Mantenha esperança realista"
```

---

## 🚦 Difficulty-Specific Rules

### **Beginner Level**
```yaml
Title Suffix: " - Beginner"
Duration: 180-360 seconds (3-6 minutes)
Coins: 10-15
Characteristics:
  - Simple, accessible language
  - Fundamental concepts
  - Basic, universal examples
  - Small, gradual steps
  - Detailed quiz explanations
Max Items: 6 (mobile friendly)
Quiz Style:
  - Direct questions
  - Clear, distinct options
  - Didactic and encouraging explanations
```

### **Advanced Level**
```yaml
Title Suffix: " - Advanced"
Duration: 600-900 seconds (10-15 minutes)
Coins: 15-25
Characteristics:
  - Sophisticated concepts
  - Nuances and complexities
  - Multi-concept integration
  - Advanced strategies
  - Challenging practical application
Quiz Style:
  - Analytical questions
  - Subtle, differentiated options
  - Deep insight explanations
```

---

## ✅ Validation Rules

### **Input Validation**
- **File Size**: Maximum 10MB
- **File Extensions**: `.md`, `.markdown`, `.json`
- **Required Template Fields**: title, description, target_audience, difficulty_level, learning_objectives

### **Content Validation**
- **Min Content Length**: 50 characters
- **Max Content Length**: 50,000 characters
- **Required Sections**: overview, main_content, key_concepts, examples, summary

### **Output Validation**
- **Schema Compliance**: 100% adherence to v1.1 schema
- **Character Limits**: Strict enforcement of mobile constraints
- **JSON Validity**: Valid JSON structure required
- **Ari Voice Check**: Consistency with persona guidelines

### **Validation Process**
```mermaid
graph LR
    A[Input Template] --> B[Content Validation]
    B --> C[Structure Generation]
    C --> D[Schema Validation]
    D --> E[Voice Consistency Check]
    E --> F[Mobile Optimization Score]
    F --> G[Final JSON Output]
    
    style D fill:#ff6b6b
    style E fill:#4ecdc4
    style F fill:#45b7d1
```

---

## 🔧 Generation Configuration

### **OpenAI Settings**
```yaml
openai:
  model: "gpt-4"
  max_tokens: 4000
  temperature: 0.7
  timeout: 60
```

### **Processing Limits**
```yaml
processing:
  retry_attempts: 3
  retry_delay: 1.0
  batch_size: 5
```

### **Generation Presets**
```yaml
default_beginner:
  target_difficulty: "beginner"
  estimated_duration: 360
  suggested_coins: 12
  
default_advanced:
  target_difficulty: "advanced"
  estimated_duration: 720
  suggested_coins: 20
```

---

## 🚨 Critical Rules Summary

### **Never Break These Rules**
1. **✋ Preserve All Required Fields**: All schema-required fields must be present
2. **📏 Respect Character Limits**: Mobile constraints are non-negotiable
3. **🗣️ Maintain Ari Persona**: Consistent voice throughout all content
4. **🇧🇷 Use Brazilian Portuguese**: Masculine forms required
5. **🏷️ Generate Unique Titles**: Include difficulty level in title
6. **🚫 Never Invent Data**: Only use information present in source templates
7. **✅ Validate Structure**: All output must pass v1.1 schema validation

### **Quality Assurance Checklist**
- ✅ JSON structure matches schema exactly
- ✅ All content within character limits (50-300 for content, 15-120 for quiz questions)
- ✅ Ari persona voice consistent
- ✅ Brazilian Portuguese with masculine forms
- ✅ Educational progression logical
- ✅ Mobile optimization score > 0.8
- ✅ Difficulty level appropriate
- ✅ Behavioral science integration present
- ✅ 3-8 flexibleItems total
- ✅ Duration 180-600 seconds
- ✅ At least 1 content item and 2 quiz items

### **Common Validation Errors to Avoid**
```yaml
Content Errors:
  - Content exceeding 300 characters
  - Quiz questions shorter than 15 characters
  - Quiz options longer than 60 characters
  - Missing required author in quotes
  
Structure Errors:
  - Less than 3 or more than 8 flexibleItems
  - Duration outside 180-600 second range
  - Missing required metadata fields
  - Invalid enum values for dimension/archetype
  
Voice Errors:
  - Using feminine Portuguese forms
  - Sentences longer than 15 words
  - Missing behavioral science integration
  - Inconsistent coaching tone
```

---

## 📊 Success Metrics

### **Technical Metrics**
- **Schema Compliance**: 100% of generated content passes v1.1 validation
- **Mobile Optimization Score**: Average score > 0.85
- **Generation Success Rate**: > 95% successful generations
- **Character Limit Compliance**: 100% adherence to mobile limits

### **Content Quality Metrics**
- **Content Consistency**: < 10% variation in supertask lengths
- **Educational Flow**: Logical progression in 100% of content
- **Ari Voice Consistency**: Maintained across all generated content
- **Behavioral Integration**: Present in 100% of explanations

This comprehensive rule set ensures all generated supertasks are mobile-optimized, educationally effective, and maintain the consistent Ari persona voice while adhering to strict technical requirements. 