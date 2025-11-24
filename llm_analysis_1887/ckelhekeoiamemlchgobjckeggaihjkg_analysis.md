# CoCo Analysis: ckelhekeoiamemlchgobjckeggaihjkg

## Summary

- **Overall Assessment:** FALSE POSITIVE
- **Total Sinks Detected:** 1

---

## Sink: document_eventListener_localStorageChangeEvent → chrome_storage_local_set_sink

**CoCo Trace:**
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/ckelhekeoiamemlchgobjckeggaihjkg/opgen_generated_files/cs_0.js
Line 467: Custom event listener and storage.set operation

**Code:**

```javascript
// Content script
(function(){
  console.log("content started");

  // Initial load from localStorage
  var e=window.localStorage.getItem("id_token");
  null!=e&&chrome.storage.local.set({idToken:e},(function(){}));

  // Inject script
  var t=document.createElement("script");
  t.src=chrome.runtime.getURL("script.js");
  t.onload=function(){this.remove()};
  (document.head||document.documentElement).appendChild(t);

  // Listen for custom event
  document.addEventListener("localStorageChangeEvent",(function(e){
    var t=e.detail;  // ← attacker-controlled (webpage can dispatch custom event)
    chrome.storage.local.set({idToken:t["idToken"]},(function(){}));
  }))
})();
```

**Classification:** FALSE POSITIVE

**Reason:** Storage poisoning without retrieval path. While the extension listens to a custom DOM event `localStorageChangeEvent` that can be triggered by malicious webpages (matching `*://*.souyouxiang.com/*`), the poisoned `idToken` is stored but never retrieved back to the attacker. The background.js contains no storage operations, and there's no code path that reads the stored `idToken` and sends it back via sendResponse, postMessage, or any other attacker-accessible channel. Without a complete exploitation chain, this is not exploitable.
