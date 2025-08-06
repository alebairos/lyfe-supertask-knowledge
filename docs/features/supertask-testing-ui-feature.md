# Supertask Testing UI - Local Development Tool PRD

## 📋 Feature Overview

**Feature Name**: Supertask Testing UI - Local Development Tool  
**Version**: 1.0.0  
**Priority**: MEDIUM  
**Target Release**: Development Tool (1-2 weeks)  
**Owner**: Engineering Team  
**Stakeholders**: Content Team, QA Team  

## 🎯 Problem Statement

### Current Issues
1. **No Visual Testing**: Generated JSON supertasks can't be visually tested/previewed
2. **Manual Validation**: Content creators must mentally parse JSON to understand user experience
3. **Debugging Difficulty**: Hard to validate mobile optimization, character limits, and flow
4. **Content Review Bottleneck**: Content team can't quickly review generated supertasks

### Impact on Development
- **Slow Iteration**: Can't quickly test generated content changes
- **Poor Quality Assurance**: No way to validate mobile experience before deployment
- **Development Friction**: JSON files don't show actual user experience

## 🚀 Proposed Solution

### High-Level Approach
Create a **minimal local testing UI** that renders generated supertask JSON files exactly as users would experience them on mobile devices.

### Architecture Evaluation

#### Option A: Pure TypeScript/Vanilla (Recommended)
**Pros:**
- Zero build dependencies
- Instant startup/refresh
- Minimal complexity
- Easy to debug
- No framework lock-in

**Cons:**
- Manual DOM manipulation
- No component reusability
- Basic state management

#### Option B: React-Based (Alternative)
**Pros:**
- Component-based architecture
- Familiar development experience
- Easy state management
- Reusable components

**Cons:**
- Build pipeline required
- Heavier dependencies
- Slower startup
- Overkill for simple testing

**Recommendation**: **Option A (Pure TypeScript)** - Aligns with "simplest thing that could possibly work" philosophy.

## 📋 Functional Requirements

### 1. JSON File Loading
- **File Selection**: Drag & drop or file picker for JSON files
- **Auto-reload**: Watch for file changes during development
- **Error Handling**: Clear error messages for invalid JSON

### 2. Mobile-First Rendering
- **Mobile Viewport**: 375px width (iPhone SE) default view
- **Responsive Preview**: Toggle between mobile sizes
- **Touch Interactions**: Simulate mobile tap/swipe behavior

### 3. Supertask Flow Simulation
- **Content Display**: Render flexibleItems in sequence
- **Quiz Interaction**: Functional quiz with option selection
- **Progress Tracking**: Show progress through supertask items
- **Completion Flow**: Show completion state with rewards

### 4. Development Features
- **Character Count Display**: Show character counts vs limits
- **Schema Validation**: Real-time validation feedback
- **Performance Metrics**: Show estimated completion time
- **Export Report**: Generate validation report for QA

## 🔧 Technical Implementation

### Pure TypeScript Architecture

```typescript
// Core structure
interface SupertaskTester {
  loadJson(file: File): Promise<void>
  renderSupertask(data: SupertaskData): void
  validateSchema(data: SupertaskData): ValidationResult
  simulateUserFlow(): void
}

// Key modules
- JsonLoader: File handling and parsing
- SchemaValidator: v1.1 schema validation  
- MobileRenderer: Mobile-optimized rendering
- FlowSimulator: User interaction simulation
- DebugPanel: Development tools
```

### File Structure
```
test-ui/
├── index.html          # Single page entry point
├── styles/
│   ├── mobile.css      # Mobile-first styles
│   ├── components.css  # Component styles
│   └── debug.css       # Development tools
├── src/
│   ├── main.ts         # Application entry
│   ├── json-loader.ts  # File loading logic
│   ├── renderer.ts     # Supertask rendering
│   ├── validator.ts    # Schema validation
│   └── flow-sim.ts     # User flow simulation
└── assets/
    └── schema-v1.1.json # Local schema copy
```

### CSS-Based Mobile Simulation
```css
/* Mobile-first approach */
.supertask-container {
  max-width: 375px;
  margin: 0 auto;
  padding: 16px;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto;
}

.flexible-item {
  margin-bottom: 24px;
  padding: 16px;
  border-radius: 12px;
  background: #f8f9fa;
}

.quiz-option {
  padding: 12px 16px;
  margin: 8px 0;
  border: 2px solid #e9ecef;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s ease;
}

.quiz-option:hover {
  border-color: #007bff;
  background: #f0f8ff;
}
```

## 🚦 User Experience Flow

### 1. File Loading
```
1. Open test-ui/index.html in browser
2. Drag & drop JSON file OR click "Choose File"
3. Auto-validation runs → Show validation results
4. If valid → Render supertask preview
```

### 2. Supertask Testing
```
1. Mobile preview loads with first flexibleItem
2. User can navigate: Next/Previous buttons
3. Quiz items: Click options → Show feedback
4. Progress bar shows completion status
5. End screen: Show coins earned, completion time
```

### 3. Development Tools
```
1. Debug panel (toggleable):
   - Character count validation
   - Schema compliance status
   - Mobile optimization score
   - Export validation report
```

## 📱 Mobile Experience Simulation

### Content Rendering
- **Content Items**: Clean typography, proper spacing
- **Quiz Items**: Touch-friendly option buttons
- **Quote Items**: Stylized with author attribution
- **Progress**: Visual progress indicator

### Character Limit Validation
```typescript
interface ValidationFeedback {
  contentItems: Array<{
    index: number
    charCount: number
    isValid: boolean
    limit: [number, number]
  }>
  quizQuestions: Array<{
    index: number
    charCount: number
    isValid: boolean
  }>
  // ... other validations
}
```

## 🔧 Implementation Details

### Minimal Dependencies
- **Zero Build Tools**: Direct TypeScript in browser (ES modules)
- **No Package Manager**: Self-contained HTML/CSS/TS
- **Local Schema**: Copy of v1.1 schema for validation

### Entry Point (index.html)
```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Supertask Testing UI</title>
    <link rel="stylesheet" href="styles/mobile.css">
    <link rel="stylesheet" href="styles/components.css">
    <link rel="stylesheet" href="styles/debug.css">
</head>
<body>
    <div id="app">
        <header>
            <h1>Supertask Testing UI</h1>
            <input type="file" id="jsonFile" accept=".json">
        </header>
        
        <main id="preview-container">
            <!-- Rendered supertask content -->
        </main>
        
        <aside id="debug-panel" class="hidden">
            <!-- Development tools -->
        </aside>
    </div>
    
    <script type="module" src="src/main.ts"></script>
</body>
</html>
```

### Core TypeScript (main.ts)
```typescript
// Main application logic
class SupertaskTester {
    private schema: any
    private currentData: SupertaskData | null = null
    
    async init() {
        await this.loadSchema()
        this.setupFileHandler()
        this.setupUIHandlers()
    }
    
    private async loadSchema() {
        const response = await fetch('./assets/schema-v1.1.json')
        this.schema = await response.json()
    }
    
    private setupFileHandler() {
        const fileInput = document.getElementById('jsonFile') as HTMLInputElement
        fileInput.addEventListener('change', this.handleFileLoad.bind(this))
    }
    
    private async handleFileLoad(event: Event) {
        const file = (event.target as HTMLInputElement).files?.[0]
        if (!file) return
        
        try {
            const text = await file.text()
            const data = JSON.parse(text)
            
            const validation = this.validateSupertask(data)
            if (validation.isValid) {
                this.renderSupertask(data)
            } else {
                this.showValidationErrors(validation.errors)
            }
        } catch (error) {
            this.showError(`Invalid JSON: ${error.message}`)
        }
    }
    
    // ... other methods
}

// Initialize on load
document.addEventListener('DOMContentLoaded', () => {
    const tester = new SupertaskTester()
    tester.init()
})
```

## 📊 Success Metrics

### Functional Validation
- **File Loading**: Supports all generated JSON files
- **Mobile Rendering**: Accurate mobile experience simulation  
- **Character Validation**: Real-time limit checking
- **Schema Compliance**: v1.1 validation accuracy

### Development Experience
- **Startup Time**: < 2 seconds to load and ready
- **File Processing**: < 500ms for typical supertask JSON
- **Refresh Speed**: Instant reload on file changes
- **Error Clarity**: Clear, actionable error messages

## 🚀 Implementation Timeline

### Week 1: Core Implementation
- **Day 1-2**: HTML structure and CSS mobile styles
- **Day 3-4**: TypeScript JSON loading and validation
- **Day 5**: Basic supertask rendering

### Week 2: Enhancement & Polish  
- **Day 1-2**: Quiz interaction simulation
- **Day 3-4**: Debug panel and validation feedback
- **Day 5**: Testing with generated content, documentation

## 🔧 Usage Instructions

### Setup
```bash
# No installation required!
cd lyfe-supertask-knowledge/test-ui
open index.html  # or python3 -m http.server 8000
```

### Testing Generated Content
```bash
# Generate supertask
python -m lyfe_kt.cli generate template work/02_preprocessed/sample.md work/03_output/

# Test in UI
1. Open test-ui/index.html
2. Load work/03_output/sample_beginner.json
3. Review mobile experience
4. Check validation feedback
5. Export QA report if needed
```

## 💡 Future Enhancements (Out of Scope)

- **Difficulty Comparison**: Side-by-side beginner vs advanced view
- **Batch Testing**: Load multiple JSON files for comparison
- **Export to Mobile**: Generate shareable mobile preview links
- **A/B Testing**: Compare different content variations
- **Analytics Simulation**: Mock engagement tracking

## 🎯 Conclusion

This minimal testing UI provides essential validation and preview capabilities without the complexity of a full framework. The pure TypeScript approach ensures:

- **Simplicity**: Single HTML file to get started
- **Speed**: Instant feedback during development  
- **Portability**: Works in any modern browser
- **Maintainability**: Minimal dependencies to manage

Perfect for validating our mobile-optimized supertask generation pipeline!