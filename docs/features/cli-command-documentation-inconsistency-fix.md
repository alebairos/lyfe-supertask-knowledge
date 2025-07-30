# CLI Command Documentation Inconsistency Fix - PRD

**Feature Name**: CLI Command Documentation Standardization  
**Version**: 1.0.0  
**Priority**: HIGH  
**Target Release**: Immediate (Critical for usability)  
**Owner**: Engineering Team  

## 📋 Problem Statement

**Critical Issue Discovered**: Documentation contains conflicting CLI command formats that prevent users from successfully executing pipeline commands.

### Current Inconsistencies Found
1. **README.md** shows: `python -m lyfe_kt preprocess`
2. **Feature docs** show: `python -m src.lyfe_kt.cli preprocess`
3. **Work directory manual** shows: `lyfe-kt preprocess work/01_raw/`

### Impact
- Users cannot execute documented commands
- `zsh: command not found: lyfe-kt` error when following manual
- Pipeline execution blocked by documentation inconsistency
- Missing setup instructions for virtual environment activation
- `ModuleNotFoundError: No module named 'click'` when dependencies not installed

## 🎯 Proposed Solution

### 1. Standardize CLI Command Format
- **Decision**: Use `python -m src.lyfe_kt.cli` as the standard format
- **Rationale**: Most specific and accurate to actual module structure

### 2. Update All Documentation
- **README.md**: Update all command examples to use standard format
- **Work directory manual**: Replace `lyfe-kt` with `python -m src.lyfe_kt.cli`
- **Feature docs**: Ensure consistency across all PRDs

### 3. Add CLI Alias Setup (Optional)
```bash
# Add to installation instructions
alias lyfe-kt="python -m src.lyfe_kt.cli"
```

## 📋 Functional Requirements

### Must Fix Immediately
1. **README.md**: Lines 112-114 command examples
2. **docs/manual/work-directory-and-package-system.md**: Lines 38-42 usage commands
3. **All feature docs**: Standardize to `python -m src.lyfe_kt.cli`

### Correct Command Format
```bash
# Current (broken)
lyfe-kt preprocess work/01_raw/
lyfe-kt generate work/02_preprocessed/
lyfe-kt package

# Fixed (working)
python -m src.lyfe_kt.cli preprocess work/01_raw/
python -m src.lyfe_kt.cli generate work/02_preprocessed/
python -m src.lyfe_kt.cli package
```

## 🚨 Priority Justification

**HIGH PRIORITY** because:
- Blocks all pipeline usage following documentation
- Creates immediate user frustration
- Critical for work directory system functionality
- Simple fix with high impact

## ✅ Acceptance Criteria

- [ ] All documentation uses consistent `python -m src.lyfe_kt.cli` format
- [ ] README.md commands updated
- [ ] Work directory manual commands updated
- [ ] All feature docs commands standardized
- [ ] Commands execute successfully when copied from documentation

## 🔧 Implementation

**Estimated Effort**: 30 minutes (find and replace across docs)  
**Impact**: Critical - enables pipeline usage
**Risk**: None - pure documentation fix

---

*Critical fix required for pipeline functionality. All CLI commands in documentation must be standardized to working format.* 