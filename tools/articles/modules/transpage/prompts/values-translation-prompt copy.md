Translate the following text values from English to {language_name}.

CRITICAL RULES (MUST FOLLOW EXACTLY):
1. **Line Count**: Output MUST have EXACTLY the same number of lines as input
   - Count input lines carefully
   - Do NOT merge lines
   - Do NOT split lines
   - Do NOT add or remove lines

2. **Line Order**: Maintain EXACT order
   - Line 1 input → Line 1 output
   - Line 2 input → Line 2 output
   - Never reorder lines

3. **Content Rules**:
   - Translate each line independently
   - Keep translations natural and fluent
   - Preserve empty lines exactly as they appear
   - Do NOT add explanations, comments, or metadata
   - Do NOT add line numbers or markers

4. **Special Cases**:
   - Table headers: Translate column names only, keep structure
   - JSON keys: Do NOT translate (they are identifiers)
   - Game names: Keep "{game_name}" as-is
   - Technical terms: Keep as-is unless culturally inappropriate
   - URLs: Do NOT translate
   - Numbers: Keep unchanged

5. **Output Format**:
   - Output ONLY translated lines
   - One line per output line
   - No extra blank lines
   - No prefixes or suffixes
   - No line numbers

VERIFICATION CHECKLIST (Before outputting):
- [ ] Count: Input lines = Output lines?
- [ ] Order: Lines in same sequence?
- [ ] Content: Each line translated?
- [ ] Format: No extra content added?
- [ ] Structure: Empty lines preserved?

Game context: This is for "{game_name}" - a Roblox farming simulation game.

INPUT TEXT (one value per line, total {line_count} lines):
---
{content}
---

IMPORTANT: Output exactly {line_count} lines, one per line, in the same order.

OUTPUT (translated values, one per line):
