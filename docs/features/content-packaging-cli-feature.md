# Content Packaging CLI - Simple Implementation PRD

**Feature Name**: Content Packaging CLI Command  
**Version**: 1.0.0  
**Priority**: MEDIUM  
**Target Release**: Q1 2025 (1 week)  
**Owner**: Engineering Team  

## 📋 Problem Statement

After generating supertasks through the pipeline, all content remains scattered in the work directory. Users need a simple way to:
- Package completed pipeline content into organized folders
- Clean up the work directory for the next project
- Archive content with clear naming and timestamps

## 🎯 Proposed Solution

Create a simple CLI command `package` that:
1. Moves all content from work directories to a packages folder
2. Creates organized folder with `<title>-<date>-<time>` naming
3. Cleans work directory, keeping only structural folders

## 📋 Functional Requirements

### 1. CLI Command Structure
```bash
python -m src.lyfe_kt.cli package [OPTIONS] [TITLE]
```

**Arguments:**
- `TITLE` (optional): Custom package name. Defaults to auto-detected from supertasks

**Options:**
- `--output-dir`: Custom packages directory (default: `packages/`)
- `--keep-work`: Don't clean work directory after packaging

### 2. Package Organization
```
packages/
  └── naval_supertask-2025-01-14-16-58/
      ├── 01_raw/          # All raw content files
      ├── 02_preprocessed/ # Templates and analysis
      ├── 03_output/       # Generated supertasks
      └── reports/         # Processing reports
```

### 3. Title Detection Logic
1. **Auto-detect from supertasks**: Extract common prefix from generated JSON files
2. **Fallback to timestamp**: If no clear pattern, use `content-YYYY-MM-DD`
3. **User override**: Accept explicit title parameter

### 4. Work Directory Cleanup
After packaging, work directory should contain only:
```
work/
  ├── 01_raw/     # Empty folder
  ├── 02_preprocessed/ # Empty folder  
  ├── 03_output/  # Empty folder
  ├── reports/    # Empty folder
  └── README.md   # Keep structural documentation
```

## 🔧 Technical Requirements

### 1. Implementation Location
- **File**: `src/lyfe_kt/content_packager.py` (new)
- **CLI Integration**: Add to existing `src/lyfe_kt/cli.py`

### 2. Core Functions
```python
class ContentPackager:
    def __init__(self, work_dir="work", packages_dir="packages"):
        pass
    
    def detect_title(self) -> str:
        """Auto-detect package title from content."""
        pass
    
    def create_package(self, title: str) -> str:
        """Create timestamped package folder."""
        pass
    
    def move_content(self, package_path: str):
        """Move all work content to package."""
        pass
    
    def clean_work_directory(self):
        """Clean work dir, keep structural folders."""
        pass
```

### 3. Error Handling
- Handle empty work directories gracefully
- Skip if no content to package
- Preserve work structure on errors

## 📊 Success Metrics

- ✅ Command executes without errors
- ✅ All work content moved to packages folder
- ✅ Work directory cleaned but structural folders remain
- ✅ Package naming follows `<title>-<date>-<time>` format
- ✅ Auto-title detection works for common cases

## 🚧 Implementation Plan

### Week 1: Core Implementation
- [ ] Create `ContentPackager` class
- [ ] Implement title detection logic
- [ ] Add move and cleanup functionality
- [ ] Integrate with CLI

### Testing
- [ ] Test with existing Naval supertask content
- [ ] Test empty work directory handling
- [ ] Verify structural folder preservation

## 🎯 Acceptance Criteria

### Must Have
- [ ] CLI command `package` works without parameters
- [ ] Auto-detects title from supertask files
- [ ] Creates timestamped package folder
- [ ] Moves all work content to package
- [ ] Cleans work directory keeping structure

### Should Have
- [ ] Custom title parameter support
- [ ] Custom output directory option
- [ ] Graceful handling of edge cases

### Could Have
- [ ] Package compression option
- [ ] List existing packages command
- [ ] Package statistics/summary

## 🔄 Example Usage

```bash
# Auto-detect title and package content
python -m src.lyfe_kt.cli package

# Custom title
python -m src.lyfe_kt.cli package "wealth_concepts"

# Custom output directory
python -m src.lyfe_kt.cli package --output-dir "archived_projects"
```

**Expected Output:**
```
📦 Packaging pipeline content...
🔍 Auto-detected title: naval_supertask
📁 Created package: packages/naval_supertask-2025-01-14-16-58/
📋 Moved 15 files from work directories
🧹 Cleaned work directory (kept structural folders)
✅ Content packaged successfully!
```

## 🚨 Risks & Mitigation

### 1. Data Loss Risk
- **Risk**: Accidental deletion of important content
- **Mitigation**: Move (don't delete) content, add confirmation prompts

### 2. Title Detection Failures
- **Risk**: Poor auto-detection creates confusing names
- **Mitigation**: Fallback to timestamp, allow manual override

## 📝 Documentation Requirements

- [ ] CLI help documentation
- [ ] Usage examples in README
- [ ] Package folder structure explanation

---

**Approval Required From:**
- [ ] Engineering Lead
- [ ] Product Manager

**Estimated Effort:** 1 week  
**Team Size:** 1 engineer  
**Priority:** MEDIUM (Quality of life improvement)

---

*This simple PRD focuses on the core packaging functionality without complex features, delivering immediate value for pipeline content organization.* 