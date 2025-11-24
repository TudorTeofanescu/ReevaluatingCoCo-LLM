# CoCo Analysis: mheppnpebcmghdfflplanpkngijpcabk

## Summary

- **Overall Assessment:** TRUE POSITIVE
- **Total Sinks Detected:** 1

---

## Sink: document_eventListener_cfc_auth → chrome_storage_sync_set_sink

**CoCo Trace:**
```
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/mheppnpebcmghdfflplanpkngijpcabk/opgen_generated_files/cs_0.js
Line 467	document.addEventListener("cfc_auth", (data) => {
Line 468	  chrome.runtime.sendMessage({ message: "cfc_auth_finish", data: data.detail });
```

**Code:**

```javascript
// Content script (cs_0.js / content.js) - Entry point
document.addEventListener("cfc_auth", (data) => { // ← attacker can dispatch custom event
  chrome.runtime.sendMessage({ message: "cfc_auth_finish", data: data.detail }); // ← attacker-controlled
});

// Background script (bg.js / background.js) - Message handler
chrome.runtime.onMessage.addListener((req, sender, res) => {
  if (req.message === "cfc_auth_start") {
    chrome.windows.create({
      type: "popup",
      url: req.authUrl,
      width: 600,
      height: 650,
      focused: true,
    }, (w) => {
      if (w && w.id) {
        authWindowID = w.id;
      }
    });
  } else if (req.message === "cfc_auth_finish") {
    chrome.storage.sync.set({ cfc_token: req.data }, function () { // ← storage sink with attacker data
      console.log("cfc_token saved");
    });

    // Close auth popup windows
    chrome.windows.getCurrent({ windowTypes: ["popup"] }, (w) => {
      if (w.id === authWindowID) {
        chrome.windows.remove(w.id);
        authWindowID = null;
      }
    });
  }
});
```

**Classification:** TRUE POSITIVE

**Attack Vector:** DOM event (document.addEventListener)

**Attack:**

```javascript
// Malicious webpage code - any page can dispatch this event
const maliciousToken = "attacker_controlled_token_12345";
const event = new CustomEvent("cfc_auth", {
  detail: maliciousToken
});
document.dispatchEvent(event);

// This will cause the extension to store the attacker's token in chrome.storage.sync
// The attacker can poison the stored authentication token
```

**Impact:** Storage poisoning vulnerability. An attacker on any webpage can dispatch a custom "cfc_auth" event to poison the extension's stored authentication token (cfc_token). While this is storage.set without immediate retrieval, the poisoned token could be used by the extension later for authentication with api.pipedrive.com, potentially allowing the attacker to hijack the user's Pipedrive session or inject their own credentials. The extension runs on all HTTP/HTTPS pages ("matches": ["http://*/*", "https://*/*"]), making this exploitable from any malicious website.

**Note:** While the manifest.json has `"externally_connectable": {"matches": ["http://localhost/*"]}`, this only restricts chrome.runtime.sendMessage from external web pages, NOT document.addEventListener which is used here. Any webpage can dispatch DOM events that the content script listens for.
