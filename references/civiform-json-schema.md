# CiviForm Program Export JSON Schema & Predicate Reference

This reference documents the structure of CiviForm program export JSON files (exported from `/admin/programs` in CiviForm) and the exact transformation rules required to render them as human-readable interactive flowcharts.

---

## 1. Top-Level JSON Structure

A CiviForm program export JSON contains two primary top-level keys:

```json
{
  "program": {
    "id": 440,
    "adminName": "salg-test",
    "adminDescription": "",
    "externalLink": "",
    "displayMode": "PUBLIC",
    "loginOnly": false,
    "programType": "DEFAULT",
    "eligibilityIsGating": true,
    "usesScoring": false,
    "localizedName": {
      "translations": { "en_US": "Test program" },
      "isRequired": true
    },
    "localizedDescription": {
      "translations": { "en_US": "" },
      "isRequired": true
    },
    "localizedShortDescription": {
      "translations": { "en_US": "This is a test problem" },
      "isRequired": true
    },
    "localizedConfirmationMessage": {
      "translations": { "en_US": "" },
      "isRequired": true
    },
    "applicationSteps": [
      {
        "title": { "translations": { "en_US": "Fill out this form" } },
        "description": { "translations": { "en_US": "Description" } }
      }
    ],
    "blockDefinitions": [ ... ]
  },
  "questions": [ ... ],
  "duplicateQuestionHandlingOptions": {}
}
```

### Key Program Metadata Fields

| Field | Type | Visualization Usage |
| :--- | :--- | :--- |
| `program.localizedName` | `LocalizedString` | Main `<h1>` title in the hero header. |
| `program.localizedShortDescription` | `LocalizedString` | Subtitle in the hero header (fall back to `localizedDescription` if empty). |
| `program.adminName` | `string` | **Never display in the UI.** Internal admin identifier only. |
| `program.displayMode` | `string` | Shown in header metadata pill (e.g., `PUBLIC`, `HIDDEN_IN_INDEX`, `TI_ONLY`, `SELECT_TI`). |
| `program.eligibilityIsGating` | `boolean` | When `true` (default), failing an `eligibilityDefinition` stops the applicant from submitting (`⛔ Ineligible — Application Stopped`). When `false`, eligibility is non-gating (`⚠️ Non-Gating Eligibility Warning — Applicant May Continue`). |
| `program.applicationSteps` | `Array` | `applicationSteps[0].title` provides the label for the Start terminal node (`▶ Start Application: ...`). |

---

## 2. Screens / Pages (`program.blockDefinitions[]`)

Each entry in `program.blockDefinitions` represents a screen (page) in the application flow.

> [!IMPORTANT]
> **Block IDs vs. Page Numbers**: `block.id` values are internal database/configuration identifiers and are often non-sequential (e.g., `1, 13, 2, 14, 15, 6, 16, 7, 11, 8, 9`).
> - Display the 1-based array position (`Page ${index + 1}`) to the user as the page badge.
> - Use `block.id` internally to resolve `repeaterId` references and construct unique DOM IDs (`id="flow-node-screen-${block.id}"`).

### Block Definition Fields

| Field | Type | Description & Handling |
| :--- | :--- | :--- |
| `id` | `number` | Internal block ID. Referenced by downstream repeated blocks via `repeaterId`. |
| `localizedName` | `LocalizedString` | Screen title (fall back to `block.name` if `localizedName` is missing). |
| `localizedDescription` | `LocalizedString` | Screen subtitle/description (fall back to `block.description`). |
| `localizedEligibilityMessage` | `LocalizedString` | Custom message shown when an applicant fails this block's `eligibilityDefinition`. Display inside the `.eligibility-stop-card` if non-empty. |
| `hidePredicate` | `PredicateDefinition \| null` | Conditional visibility rule (`HIDE_BLOCK` or `SHOW_BLOCK`). |
| `optionalPredicate` | `PredicateDefinition \| null` | Legacy visibility predicate field; treat as fallback if `hidePredicate` is null. |
| `eligibilityDefinition` | `{ predicate: PredicateDefinition } \| null` | Eligibility gate rule (`ELIGIBLE_BLOCK`). Splits flow into Eligible (continue) vs. Ineligible (stop/warning). |
| `isEnumerator` | `boolean` (optional) | Explicitly marks an enumerator screen when present, but **often omitted** in exports. |
| `repeaterId` | `number \| null` | When non-null, this screen repeats once for each entity created on the enumerator screen with `block.id === repeaterId`. |
| `questionDefinitions` | `Array<{ id, optional, addressCorrectionEnabled }>` | Ordered list of questions on this screen. Cross-reference `id` against `questions[].config.id`. |

### Detecting Enumerator & Repeater Screens Reliably

Because `block.isEnumerator` is optional in CiviForm exports, detect whether a block is an enumerator using all three checks:

```javascript
function isBlockEnumerator(block, questionsMap, allBlocks) {
  if (block.isEnumerator) return true;
  const hasEnumQuestion = (block.questionDefinitions || []).some(qd => {
    const q = questionsMap.get(qd.id);
    return q && q.type === 'enumerator';
  });
  if (hasEnumQuestion) return true;
  return allBlocks.some(other => other.repeaterId === block.id);
}
```

When consecutive blocks share the same non-null `repeaterId`, wrap them in a `.repeater-group-box` container labeled with the parent enumerator's page number and localized `entityType` (from the parent enumerator question's `entityType.translations`).

---

## 3. Questions (`questions[]`)

Each entry in `questions` has:

```json
{
  "type": "multioption",
  "config": {
    "id": 1800,
    "name": "GOLD Age Eligibility",
    "description": "GOLD Age Eligibility",
    "questionText": {
      "translations": {
        "en_US": "To be eligible for the GOLD card, you must be 60 years of age or older"
      }
    },
    "questionHelpText": {
      "translations": {}
    },
    "enumeratorId": null,
    "validationPredicates": { ... }
  },
  "multiOptionQuestionType": "RADIO_BUTTON",
  "questionOptions": [
    {
      "id": 0,
      "adminName": "I am currently 60 years of age or older",
      "localizedOptionText": {
        "translations": { "en_US": "I am currently 60 years of age or older" }
      },
      "displayOrder": 0
    }
  ]
}
```

### Question Display Rules

1. **Never show `config.id` or `config.name`**: Use `getTranslation(q.config.questionText)` for the question prompt and `getTranslation(q.config.questionHelpText)` for the help text.
2. **Question Type Tags**:
   - `currency`, `date` $\rightarrow$ Gold badge (`.q-type-tag--currency`)
   - `multioption` (`RADIO_BUTTON`, `CHECKBOX`, `DROPDOWN`) $\rightarrow$ Teal badge (`.q-type-tag--multioption`)
   - `enumerator` $\rightarrow$ Green badge (`.q-type-tag--enumerator`)
   - `static` $\rightarrow$ Neutral gray badge (`.q-type-tag--static`)
   - `name`, `email`, `phone`, `address`, `text`, `number`, `fileupload`, `id` $\rightarrow$ Blue badge (`.q-type-tag`)
3. **Multi-Option Answer Choices**:
   - Retrieve options via `q.questionOptions || q.displayableOptions || q.options || []`.
   - Render inside an inline `<details class="question-options-details">` element inside the question chip.
   - If the question is referenced by the screen's `eligibilityDefinition`, add the `open` attribute to `<details open>` by default and badge each option pill as `✓ Eligible: <Option Text>` (`.option-pill-item--eligible`) or `⛔ Stops User: <Option Text>` (`.option-pill-item--ineligible`).

---

## 4. CiviForm Predicate AST (`hidePredicate` & `eligibilityDefinition`)

### AST Node Types

A predicate has the shape:

```json
{
  "rootNode": {
    "node": { ... }
  },
  "action": "HIDE_BLOCK" | "SHOW_BLOCK" | "ELIGIBLE_BLOCK"
}
```

The `node` inside `rootNode` (or inside `children[]`) is either:

1. **Leaf Node** (`node.type === "leaf"` or `node.questionId != null`):
   ```json
   {
     "type": "leaf",
     "questionId": 2124,
     "scalar": "CURRENCY_CENTS",
     "operator": "LESS_THAN",
     "value": {
       "value": "10000000",
       "type": "LONG"
     }
   }
   ```
2. **Logical Composite Node** (`node.type === "and"` or `node.type === "or"`):
   ```json
   {
     "type": "and",
     "children": [
       { "node": { "type": "leaf", ... } },
       { "node": { "type": "or", "children": [ ... ] } }
     ]
   }
   ```
   Always traverse `node` recursively so compound `AND` / `OR` conditions render and evaluate properly.

### Action Inversion (`HIDE_BLOCK` vs. `SHOW_BLOCK` vs. `ELIGIBLE_BLOCK`)

- **`HIDE_BLOCK`**: The JSON predicate describes when the block is **hidden**. To display a positive human-readable **"Visible when..."** rule, **invert** the predicate:
  - Leaf operator inversions:
    - `LESS_THAN` (`<`) $\rightarrow$ `≥` (`GREATER_THAN_OR_EQUAL_TO`)
    - `LESS_THAN_OR_EQUAL_TO` (`≤`) $\rightarrow$ `>` (`GREATER_THAN`)
    - `GREATER_THAN` (`>`) $\rightarrow$ `≤` (`LESS_THAN_OR_EQUAL_TO`)
    - `GREATER_THAN_OR_EQUAL_TO` (`≥`) $\rightarrow$ `<` (`LESS_THAN`)
    - `EQUAL_TO` (`=`) $\rightarrow$ `≠` (`NOT_EQUAL_TO`)
    - `NOT_EQUAL_TO` (`≠`) $\rightarrow$ `=` (`EQUAL_TO`)
    - `IN` / `ANY_OF` $\rightarrow$ `is NOT one of`
    - `NOT_IN` / `NONE_OF` $\rightarrow$ `is one of`
    - `AGE_OLDER_THAN` $N$ $\rightarrow$ `age ≤` $N$
    - `AGE_YOUNGER_THAN` $N$ $\rightarrow$ `age ≥` $N$
  - Composite node inversions (De Morgan's laws):
    - `!(A AND B)` $\rightarrow$ `(!A) OR (!B)`
    - `!(A OR B)` $\rightarrow$ `(!A) AND (!B)`
- **`SHOW_BLOCK`**: Do **not** invert. The block is visible when the predicate evaluates to `true`.
- **`ELIGIBLE_BLOCK`**:
  - **Pass branch (`✓ Eligible — Continue Application`)**: Predicate evaluates to `true` (not inverted).
  - **Stop branch (`⛔ Ineligible — Application Stopped`)**: Predicate evaluates to `false` (inverted).

### Scalar Formatting Rules

| Scalar | Raw Value Format | Human-Readable Transformation |
| :--- | :--- | :--- |
| `CURRENCY_CENTS` | Stringified integer in cents (e.g., `"10000000"`) | Divide by `100` and format as USD: `$100,000.00`. |
| `SELECTION` / `SELECTIONS` | Stringified JSON array of option IDs or adminNames (e.g., `"[\"0\"]"`, `"[\"16\",\"17\"]"`) | Parse JSON array, match against target question's `questionOptions` by `String(opt.id)` or `opt.adminName`, and output localized option labels in quotes (`"I am currently 60 years of age or older"`). |
| `DATE` (`AGE_OLDER_THAN`) | Stringified integer years $N$ (e.g., `"59"`) | Pass: `older than ${N} (${N + 1}+ years old)`. Stop: `${N} or younger (< ${N + 1} years old)`. |
| `DATE` (`AGE_YOUNGER_THAN`) | Stringified integer years $N$ | Pass: `younger than ${N} (< ${N} years old)`. Stop: `${N} or older (${N}+ years old)`. |
| `DATE` (`AGE_BETWEEN`) | Array or `value` + `secondValue` `[A, B]` | Pass: `age between ${A} and ${B} years`. Stop: `age outside ${A}–${B} years`. |
| `NUMBER` / `LONG` / `DOUBLE` | Stringified number | Format with locale number separators. |
| `TEXT` / `EMAIL` / `FIRST_NAME` / `LAST_NAME` / `SERVICE_AREA` | String | Display quoted string value. |
