#!/usr/bin/env python3
"""
Fix name table for Strichpunkt Sans variable font (post-build).

- Sets nameID 1 (Font Family) to "Strichpunkt Sans" for all existing records.
- Removes nameID 16 (Typographic Family) if present.
- Does not modify the STAT table.
- Normalizes nameID 4/6 so "Strichpunkt " -> "Strichpunkt Sans " where needed.

Use:
    python3 scripts/fix_STAT_and_name_STRICH.py
"""

from fontTools.ttLib import TTFont
from fontTools.ttLib.tables._n_a_m_e import NameRecord

FAMILY_NAME = "Strichpunkt Sans"
FONT_PATH = "fonts/variable/StrichpunktSans[wdth,wght].ttf"

font = TTFont(FONT_PATH)
name_table = font["name"]

def set_all_name_records(name_id: int, value: str):
    """Set all existing records of name_id to value; return count updated."""
    updated = 0
    for rec in name_table.names:
        if rec.nameID == name_id:
            rec.string = value.encode(rec.getEncoding())
            updated += 1
    return updated

print(f'✏️ Setting nameID 1 to "{FAMILY_NAME}" (all records)...')
count = set_all_name_records(1, FAMILY_NAME)

# If there were no existing nameID 1 records (unlikely), add a standard Win record
if count == 0:
    rec = NameRecord()
    rec.nameID = 1
    rec.platformID = 3
    rec.platEncID = 1
    rec.langID = 0x409
    rec.string = FAMILY_NAME.encode("utf-16-be")
    name_table.names.append(rec)
    print("➕ Added nameID 1 Windows record (platform 3).")

# Remove nameID 16 entirely
before = len(name_table.names)
name_table.names = [r for r in name_table.names if r.nameID != 16]
after = len(name_table.names)
print(f"🗑️ Removed nameID 16 records: {before - after}")

# Normalize nameID 4/6
prefix = "Strichpunkt "
prefix_len = len(prefix)

for rec in name_table.names:
    if rec.nameID not in (4, 6):
        continue
    try:
        s = rec.toUnicode()
        if s.startswith(prefix) and not s.startswith(FAMILY_NAME + " "):
            s = FAMILY_NAME + " " + s[prefix_len:]
            rec.string = s.encode(rec.getEncoding())
    except (UnicodeDecodeError, UnicodeEncodeError):
        continue

font.save(FONT_PATH)
print(f"💾 Saved: {FONT_PATH}")
print("🎉 Done!")
