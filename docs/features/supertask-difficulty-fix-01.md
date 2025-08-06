# Supertask Difficulty Parameter Fix - Feature Document

**Feature ID**: `supertask-difficulty-fix-01`  
**Priority**: HIGH - Critical Bug Fix  
**Status**: ANALYSIS COMPLETE - Ready for Implementation  
**Discovered**: August 5, 2025 during difficulty parameter testing

---

## 🚨 **Problem Statement**

The `--difficulty` parameter in the CLI is **completely broken**:

```bash
# Both commands generate identical "beginner" output
python -m lyfe_kt.cli generate template input.md output/ --difficulty beginner  
python -m lyfe_kt.cli generate template input.md output/ --difficulty advanced  
```

**Root Cause**: CLI only passes `generate_both_difficulties=True/False` but never specifies which single difficulty to generate.

---

## 🎯 **Success Criteria**

1. **`--difficulty beginner`** → generates ONLY beginner version
2. **`--difficulty advanced`** → generates ONLY advanced version  
3. **`--difficulty both`** → generates BOTH versions (current behavior)
4. **Generated content shows clear difficulty differentiation**
5. **All existing functionality preserved**

---

## 🔧 **Simplest Implementation That Could Possibly Work**

### **Step 1: Fix CLI Parameter Passing**

**File**: `src/lyfe_kt/cli.py`

**Current Code** (Lines 638-646):
```python
# Determine difficulty settings
generate_both = difficulty == 'both'

result = generate_from_template(
    template_file,
    output_dir,
    generate_both_difficulties=generate_both,
    progress_callback=progress_callback if progress else None
)
```

**Fixed Code**:
```python
# Determine difficulty settings
if difficulty == 'both':
    generate_both = True
    specific_difficulty = None
else:
    generate_both = False
    specific_difficulty = difficulty

result = generate_from_template(
    template_file,
    output_dir,
    generate_both_difficulties=generate_both,
    specific_difficulty=specific_difficulty,
    progress_callback=progress_callback if progress else None
)
```

### **Step 2: Update Generation Function Signature**

**File**: `src/lyfe_kt/stage3_generation.py`

**Current Function** (Line 1457):
```python
def generate_from_template(template_path: str, output_dir: str, 
                          generate_both_difficulties: bool = True,
                          progress_callback=None) -> Dict[str, Any]:
```

**Fixed Function**:
```python
def generate_from_template(template_path: str, output_dir: str, 
                          generate_both_difficulties: bool = True,
                          specific_difficulty: str = None,
                          progress_callback=None) -> Dict[str, Any]:
```

### **Step 3: Update Pipeline Process Method**

**File**: `src/lyfe_kt/stage3_generation.py`

**Current Method** (around line 1170):
```python
def process_template(self, template_path: str, output_dir: str, 
                    generate_both_difficulties: bool = True) -> Dict[str, Any]:
```

**Fixed Method**:
```python
def process_template(self, template_path: str, output_dir: str, 
                    generate_both_difficulties: bool = True,
                    specific_difficulty: str = None) -> Dict[str, Any]:
```

### **Step 4: Update Generation Logic**

**File**: `src/lyfe_kt/stage3_generation.py`

**Current Logic** (inside `process_template`):
```python
if generate_both_difficulties:
    # Generate both beginner and advanced
    for difficulty in ['beginner', 'advanced']:
        # ... generate each difficulty
else:
    # Currently defaults to beginner - THIS IS THE BUG
    difficulty = 'beginner'
    # ... generate only beginner
```

**Fixed Logic**:
```python
if generate_both_difficulties:
    # Generate both beginner and advanced
    difficulties = ['beginner', 'advanced']
else:
    # Use specific difficulty (defensive default to beginner)
    difficulties = [specific_difficulty or 'beginner']

for difficulty in difficulties:
    # ... generate for each difficulty
```

---

## 🛡️ **Defensive Tests**

### **Test 1: CLI Parameter Validation**

```python
def test_difficulty_parameter_beginner():
    """Test --difficulty beginner generates only beginner version."""
    # Setup test template
    template_file = "test_template.md"
    output_dir = "test_output"
    
    # Run command
    result = runner.invoke(cli, [
        'generate', 'template', template_file, output_dir, 
        '--difficulty', 'beginner'
    ])
    
    # Assertions
    assert result.exit_code == 0
    assert "beginner.json" in os.listdir(output_dir)
    assert "advanced.json" not in os.listdir(output_dir)
    
    # Verify content
    with open(f"{output_dir}/test_template_beginner.json") as f:
        data = json.load(f)
        assert data['metadata']['difficulty_level'] == 'beginner'
        assert data['estimatedDuration'] <= 600  # Max 10 min for beginner
        assert data['coinsReward'] <= 15  # Max 15 coins for beginner
```

### **Test 2: Advanced Parameter Test**

```python
def test_difficulty_parameter_advanced():
    """Test --difficulty advanced generates only advanced version."""
    # Setup test template
    template_file = "test_template.md"
    output_dir = "test_output"
    
    # Run command
    result = runner.invoke(cli, [
        'generate', 'template', template_file, output_dir, 
        '--difficulty', 'advanced'
    ])
    
    # Assertions
    assert result.exit_code == 0
    assert "advanced.json" in os.listdir(output_dir)
    assert "beginner.json" not in os.listdir(output_dir)
    
    # Verify content
    with open(f"{output_dir}/test_template_advanced.json") as f:
        data = json.load(f)
        assert data['metadata']['difficulty_level'] == 'advanced'
        assert data['estimatedDuration'] >= 600  # Min 10 min for advanced
        assert data['coinsReward'] >= 15  # Min 15 coins for advanced
```

### **Test 3: Both Parameter Test (Regression)**

```python
def test_difficulty_parameter_both():
    """Test --difficulty both generates both versions (existing behavior)."""
    # Setup test template
    template_file = "test_template.md"
    output_dir = "test_output"
    
    # Run command
    result = runner.invoke(cli, [
        'generate', 'template', template_file, output_dir, 
        '--difficulty', 'both'
    ])
    
    # Assertions
    assert result.exit_code == 0
    assert "beginner.json" in os.listdir(output_dir)
    assert "advanced.json" in os.listdir(output_dir)
    
    # Verify both files have correct difficulty
    with open(f"{output_dir}/test_template_beginner.json") as f:
        beginner_data = json.load(f)
        assert beginner_data['metadata']['difficulty_level'] == 'beginner'
    
    with open(f"{output_dir}/test_template_advanced.json") as f:
        advanced_data = json.load(f)
        assert advanced_data['metadata']['difficulty_level'] == 'advanced'
```

### **Test 4: Content Differentiation Test**

```python
def test_difficulty_content_differentiation():
    """Test that beginner and advanced content are actually different."""
    template_file = "test_template.md"
    output_dir = "test_output"
    
    # Generate both versions
    result = runner.invoke(cli, [
        'generate', 'template', template_file, output_dir, 
        '--difficulty', 'both'
    ])
    
    # Load both files
    with open(f"{output_dir}/test_template_beginner.json") as f:
        beginner = json.load(f)
    with open(f"{output_dir}/test_template_advanced.json") as f:
        advanced = json.load(f)
    
    # Verify differentiation
    assert beginner['title'] != advanced['title']
    assert beginner['estimatedDuration'] < advanced['estimatedDuration']
    assert beginner['coinsReward'] <= advanced['coinsReward']
    
    # Verify content complexity differences (simple heuristic)
    beginner_content = ' '.join([item['content'] for item in beginner['flexibleItems'] if item['type'] == 'content'])
    advanced_content = ' '.join([item['content'] for item in advanced['flexibleItems'] if item['type'] == 'content'])
    
    # Advanced should have longer or more complex content
    assert len(advanced_content) >= len(beginner_content)
```

### **Test 5: Defensive Default Test**

```python
def test_difficulty_defensive_default():
    """Test that invalid difficulty defaults to beginner safely."""
    # This tests the defensive programming aspect
    pipeline = create_generation_pipeline()
    
    # Test with None
    result = pipeline.process_template(
        "test_template.md", 
        "test_output", 
        generate_both_difficulties=False,
        specific_difficulty=None
    )
    
    assert result['status'] == 'success'
    # Should default to beginner
    files = os.listdir("test_output")
    assert any("beginner" in f for f in files)
```

---

## 🔄 **Implementation Steps**

### **Phase 1: Core Fix (30 minutes)**
1. Update CLI parameter passing logic
2. Update function signatures  
3. Update generation logic with defensive defaults

### **Phase 2: Testing (45 minutes)**
4. Add 5 defensive tests above
5. Run full test suite to ensure no regressions
6. Manual testing with all 3 parameter values

### **Phase 3: Validation (15 minutes)**
7. Test with real templates
8. Verify output files are correctly named and differentiated
9. Update documentation

---

## 📋 **Files to Modify**

1. **`src/lyfe_kt/cli.py`** - Lines ~638-646 (3 CLI commands)
2. **`src/lyfe_kt/stage3_generation.py`** - Lines ~1170, ~1457, ~1480 (3 functions)
3. **`tests/test_difficulty_parameter.py`** - New test file (5 tests)

---

## 🚦 **Risk Assessment**

**Risk Level**: **LOW**
- Minimal code changes
- Defensive defaults prevent breaking existing behavior
- Comprehensive test coverage
- Easy to rollback if issues arise

**Mitigation**:
- Extensive testing before deployment
- Defensive programming with safe defaults
- Preserve existing `--difficulty both` behavior

---

## ✅ **Acceptance Criteria Checklist**

**Before Implementation:**
- [ ] Understand current broken behavior
- [ ] Identify all affected files and functions
- [ ] Plan defensive test strategy

**During Implementation:**
- [ ] Fix CLI parameter passing
- [ ] Update function signatures
- [ ] Update generation logic
- [ ] Add defensive defaults
- [ ] Write comprehensive tests

**After Implementation:**
- [ ] `--difficulty beginner` works correctly
- [ ] `--difficulty advanced` works correctly  
- [ ] `--difficulty both` still works (regression test)
- [ ] Generated content shows clear differentiation
- [ ] All tests pass
- [ ] Manual validation successful

---

## 🎯 **Expected Outcome**

After this fix:

```bash
# Will generate ONLY beginner version
python -m lyfe_kt.cli generate template input.md output/ --difficulty beginner
# → output/input_beginner.json (3-6 min, 10-15 coins)

# Will generate ONLY advanced version  
python -m lyfe_kt.cli generate template input.md output/ --difficulty advanced
# → output/input_advanced.json (10-15 min, 15-25 coins)

# Will generate BOTH versions (existing behavior preserved)
python -m lyfe_kt.cli generate template input.md output/ --difficulty both
# → output/input_beginner.json + output/input_advanced.json
```

**This simple fix enables proper difficulty testing and lays the foundation for the 3 content quality improvements (playfulness, sequencing, differentiation).**

---

## 🚀 **Ready for Implementation**

**Estimated Time**: 90 minutes  
**Complexity**: LOW  
**Impact**: HIGH (fixes critical CLI bug)  
**Testing Strategy**: Defensive with 5 comprehensive tests

**Next Steps**: Implement fix → Test thoroughly → Validate with real content → Document results