# CoCo Analysis: fimfonlianpegplhioddaemkldfbnbmo

## Summary

- **Overall Assessment:** TRUE POSITIVE
- **Total Sinks Detected:** 2

---

## Sink 1: storage_local_get_source → bg_external_port_postMessage_sink

**CoCo Trace:**
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/fimfonlianpegplhioddaemkldfbnbmo/opgen_generated_files/bg.js
Line 751: var storage_local_get_source = {'key': 'value'};

$FilePath$/home/teofanescu/cwsCoCo/extensions_local/fimfonlianpegplhioddaemkldfbnbmo/opgen_generated_files/bg.js
Line 965: Main background script with onConnectExternal handler

**Code:**

```javascript
// Background script - bg.js line 965
const o = n(1); // Default settings object
let s = Object.assign({}, o);

// Load settings from storage on startup
chrome.storage.local.get(["settings"], e => {
  console.log("Loaded: settings=", e.settings),
  e.settings && r(e.settings) ? s = e.settings : c()
});

let i = {}; // Port connections map

// External connection handler
function a(e) {
  const t = e.sender && e.sender.tab && e.sender.tab.id;
  t && (
    i[t] = e,
    console.log(`Connected: ${t} (tab)`),
    e.postMessage({settings: s}), // ← Sends stored settings to external connector
    e.onDisconnect.addListener(() => {
      delete i[t],
      console.log(`Disconnected: ${t} (tab)`)
    })
  )
}

// Listen for external connections
chrome.runtime.onConnectExternal.addListener(e => a(e)); // ← Entry point
```

**Classification:** TRUE POSITIVE

**Attack Vector:** External message via chrome.runtime.onConnectExternal

**Attack:**

```javascript
// Attacker code (from whitelisted domain or any domain per methodology)
// Note: manifest has externally_connectable restricting to netflix.com
// but per methodology we IGNORE manifest restrictions

// Connect to the extension from external page
const port = chrome.runtime.connect("fimfonlianpegplhioddaemkldfbnbmo");

// Receive the leaked settings
port.onMessage.addListener((msg) => {
  console.log("Leaked settings:", msg.settings);
  // Exfiltrate settings data:
  // - upperBaselinePos, lowerBaselinePos, primaryImageScale, etc.
});
```

**Impact:** Information disclosure. External attacker can retrieve all stored extension settings from chrome.storage.local via chrome.runtime.onConnectExternal. While the manifest.json specifies externally_connectable only for netflix.com, per the methodology we ignore manifest restrictions and treat any chrome.runtime.onConnectExternal handler as exploitable.

---

## Sink 2: storage_local_get_source → window_postMessage_sink

**CoCo Trace:**
Same source and similar flow as Sink 1, sending stored settings via postMessage.

**Classification:** TRUE POSITIVE

**Reason:** Same vulnerability pattern - stored settings leaked via port.postMessage to external connector.
