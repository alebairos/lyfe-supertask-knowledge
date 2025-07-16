# Supertask Analysis Report
**Generated**: 2025-07-15 15:49:41
**Input Directory**: work/01_raw/levantar_da_cama
**Output Directory**: work/02_preprocessed/levantar_da_cama

## Summary
- **Total Files Processed**: 1
- **Supertasks Created**: 1
- **Format Compliant**: 0/1
- **Success Rate**: 100.0%

## Supertasks Created
### 1. "Levantar da Cama"
- **Source**: `work/01_raw/levantar_da_cama/test.json`
- **Output**: `work/02_preprocessed/levantar_da_cama/test.json`
- **Topic**: Levantar da Cama
- **Content Items**: 7
- **Learning Objectives**: 5

**Learning Objectives**:
- Understand the benefits of waking up early
- Learn how to establish a consistent morning routine
- Recognize the health benefits of proper sleep habits
- Apply morning habits to improve daily productivity
- Develop motivation to maintain healthy habits

## Format Compliance Analysis

### ❌ Non-Compliant Files: 1

**test.json** - Missing fields:

- `relatedToType`
- `relatedToId`
- `estimatedDuration`
- `coinsReward`
- `flexibleItems`

## Recommendations

### Critical Issues
- **Fix JSON Format**: Output files must maintain exact input structure
- **Preserve Required Fields**: Keep all original metadata fields
- **Enhance Within Structure**: Transform content inside `flexibleItems` array

### Next Steps
1. Review format compliance issues
2. Test with multiple input files
3. Validate content quality
4. Ensure template structure consistency
