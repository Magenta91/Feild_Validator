# Test Data Documentation

This directory contains synthetic test datasets to fully test the Xeno Validator system.

## Test Files Overview

### 1. `test_data_comprehensive.csv` (20 rows)
**Purpose**: Mixed valid and invalid records to test all validation rules

**Valid Records**: 10 rows (ORD001-ORD010, ORD019-ORD020)
**Invalid Records**: 10 rows

**Error Types Covered**:
- Invalid payment mode (ORD011)
- Invalid phone number - too short (ORD011, ORD012)
- Invalid date format (ORD011, ORD013)
- Negative amount (ORD011, ORD018)
- Bad email format (ORD011, ORD013)
- Missing email (ORD012)
- Missing payment mode (ORD014)
- Zero amount (ORD014)
- Alphabetic phone number (ORD015)
- Duplicate order_id (ORD016 - duplicate of ORD001)
- Missing phone number (ORD017)
- Negative amount (ORD018)

**Expected Results**:
- Total: 20 rows
- Valid: 10 rows
- Invalid: 10 rows
- Integrity errors: ~8
- Phone errors: ~5
- Date errors: ~2

---

### 2. `test_data_international.csv` (20 rows)
**Purpose**: Test phone validation across different countries

**Countries Tested**:
- **US** (United States): 10-digit, various area codes
- **SG** (Singapore): 8-digit
- **GB** (United Kingdom): 10-digit
- **AE** (UAE): 9-digit, prefix 5X
- **AU** (Australia): 9-digit

**Valid Records**: 15 rows (US001-US003, SG001-SG003, GB001-GB003, AE001-AE003, AU001-AU003)
**Invalid Records**: 5 rows

**Error Types Covered**:
- Short phone numbers (US004, SG004)
- Invalid dates (SG004, GB004)
- Negative amounts (US004)
- Bad email (US004, GB004)
- Missing email (SG004)
- Missing payment mode (AE004)
- Zero amount (AE004)
- Alphabetic phone (AU004)

**Expected Results**:
- Total: 20 rows
- Valid: 15 rows
- Invalid: 5 rows
- Tests country-specific phone validation rules

---

### 3. `test_data_edge_cases.csv` (25 rows)
**Purpose**: Test boundary conditions and edge cases

**Test Cases**:
- **Amount boundaries**: 0.01, 999999.99, 0, negative, million
- **Date edges**: End of year (12-31), New year (01-01), Leap year (02-29)
- **Email formats**: Uppercase, lowercase, mixed case, special chars (+tag)
- **Missing fields**: phone, email, date, amount, payment_mode
- **Phone edge cases**: Empty, too short (123), too long (98765432101234)
- **Date validity**: Future dates (2025), old dates (2020)
- **Email edge cases**: no TLD, multiple @ signs

**Valid Records**: ~6 rows (EDGE001-EDGE010)
**Invalid Records**: ~19 rows

**Expected Results**:
- Total: 25 rows
- Valid: ~6 rows
- Invalid: ~19 rows
- Tests system robustness with edge cases

---

### 4. `test_data_all_valid.csv` (20 rows)
**Purpose**: Baseline test with 100% valid records

**All Fields Valid**:
- Proper Indian phone numbers (10 digits, starting with 6-9)
- Valid payment modes (upi, credit_card, debit_card, wallet, cash)
- Valid dates (YYYY-MM-DD format, 2024)
- Positive amounts with decimals
- Properly formatted emails
- Unique order IDs

**Expected Results**:
- Total: 20 rows
- Valid: 20 rows
- Invalid: 0 rows
- All validators: PASS
- No error details

---

### 5. `test_data_all_invalid.csv` (10 rows)
**Purpose**: Stress test with 100% invalid records

**All Records Have Multiple Errors**:
- Invalid payment modes
- Invalid phone numbers (too short, alphabetic, too long)
- Invalid dates (month > 12, day > 31, invalid format)
- Negative amounts
- Bad email formats
- Duplicate order_id (INV001 appears twice)

**Expected Results**:
- Total: 10 rows
- Valid: 0 rows
- Invalid: 10 rows (or 9 after duplicate removal)
- All validators: FAIL
- Multiple errors per row

---

## How to Test

### Test Sequence Recommendation:

1. **Start with `test_data_all_valid.csv`**
   - Verify system handles perfect data correctly
   - Check that no false positives occur
   - Validate cleaned output matches input

2. **Test with `test_data_comprehensive.csv`**
   - Verify mixed valid/invalid detection
   - Check all error types are caught
   - Validate report generation for all three outputs

3. **Test with `test_data_international.csv`**
   - Change country_code in sidebar (IN, US, SG, GB, AE, AU)
   - Verify country-specific phone validation works
   - Check that same phone fails/passes based on country

4. **Test with `test_data_edge_cases.csv`**
   - Verify system handles boundary conditions
   - Check for crashes or unexpected behavior
   - Validate error messages are clear

5. **Test with `test_data_all_invalid.csv`**
   - Verify system handles worst-case scenario
   - Check that all errors are caught
   - Validate cleaned output is empty or minimal

### Testing Checklist:

For each file:
- [ ] Upload file successfully
- [ ] Run validation completes without crashes
- [ ] Summary stats are accurate
- [ ] Validator table shows correct PASS/FAIL
- [ ] Error details expand and show specific errors
- [ ] Validation Report preview shows all records with status
- [ ] Failed Records preview shows only invalid records
- [ ] Clean Data preview shows only valid records
- [ ] All three download buttons work
- [ ] Downloaded files contain expected data

### Expected Validation Times:

- Small files (10-25 rows): < 2 seconds
- Medium files (100-300 rows): 2-5 seconds
- Large files (1000+ rows): 5-15 seconds

---

## Validation Rules Reference

### Phone Validation (by country):
- **IN**: 10 digits, must start with 6-9
- **US**: 10 digits, various prefixes
- **SG**: 8 digits, prefix 8 or 9
- **GB**: 10 digits
- **AE**: 9 digits, prefix 5X
- **AU**: 9 digits, prefix 4

### Date Validation:
- Format: YYYY-MM-DD (default)
- Valid month: 01-12
- Valid day: 01-31 (month-dependent)
- Valid year: Reasonable range

### Email Validation:
- Must contain single @ symbol
- Must have domain and TLD
- Standard email format validation

### Payment Mode Validation:
Valid modes: `upi`, `credit_card`, `debit_card`, `wallet`, `cash`

### Amount Validation:
- Must be positive (> 0)
- Can have decimals
- Cannot be negative

### Integrity Checks:
- No duplicate order_ids
- No missing critical fields
- Proper data types

---

## File Statistics

| File | Total Rows | Valid | Invalid | Size |
|------|------------|-------|---------|------|
| comprehensive | 20 | 10 | 10 | ~1.5 KB |
| international | 20 | 15 | 5 | ~1.4 KB |
| edge_cases | 25 | 6 | 19 | ~1.8 KB |
| all_valid | 20 | 20 | 0 | ~1.5 KB |
| all_invalid | 10 | 0 | 10 | ~0.8 KB |

---

## Notes

- All test data is synthetic and does not represent real transactions
- Phone numbers follow country-specific format rules
- Email addresses use common domain names
- Dates are in YYYY-MM-DD format (unless testing invalid formats)
- Amounts are in decimal format with 2 decimal places

---

## Quick Test Command (Backend Direct)

Test any file directly with curl:

```bash
curl -X POST http://localhost:8000/validate \
  -F "file=@test_data_comprehensive.csv" \
  -F "country_code=IN" \
  -F "date_format=%Y-%m-%d" \
  -F "chunk_size=1000" \
  -F "split_output=false"
```
