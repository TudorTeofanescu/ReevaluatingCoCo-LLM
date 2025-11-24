# CoCo Analysis: hoieipnjbkghbcmcaiiakfacmillicbg

## Summary

- **Overall Assessment:** TRUE POSITIVE
- **Total Sinks Detected:** 2

---

## Sink 1: bg_external_port_onMessage → chrome_storage_sync_set_sink

**CoCo Trace:**
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/hoieipnjbkghbcmcaiiakfacmillicbg/opgen_generated_files/bg.js
Line 1043    let fgn = message.editorFontGroupName, reply = {
    message.editorFontGroupName

**Code:**

```javascript
// Line 1321 - External connection listener
chrome.runtime.onConnectExternal.addListener(connectionListener);

// Line 1276-1279 - Connection handler
function connectionListener (port) {
    console.log('New connection');
    port.onMessage.addListener(messageListener);
}

// Line 1212-1254 - Message handler
function messageListener (message, port) {
    console.log('New request:', message.request);
    switch (message.request) {
        case 'fontConfig':
            // Handle font configuration request
            fontConfig(message, port); // ← attacker-controlled message
            break;
        // ... other cases
    }
}

// Line 1041-1092 - Font configuration handler
function fontConfig (message, port) {
    chrome.storage.sync.get({ editorFontGroupName: '', fontInfo: [], fontPicks: [], fontGroups: {} }, data => {
        let fgn = message.editorFontGroupName, reply = { // ← attacker-controlled
            fontGroupNames: Object.keys(data.fontGroups || {}).sort(),
        }, css, product = licenseManager && licenseManager.getProduct(),
            hasEditFonts = licenseManager && licenseManager.hasFeature('EDIT-FONT');

        // Use the saved font group if no font group was requested
        if (undefined === fgn) fgn = data.editorFontGroupName;

        // ... processing logic ...

        // Update saved font group name if changing
        if (fgn !== data.editorFontGroupName) chrome.storage.sync.set({ editorFontGroupName: fgn }); // Line 1092

        try { port.postMessage(reply); } catch (err) {}
    });
}
```

**Classification:** TRUE POSITIVE

**Attack Vector:** External port connection (chrome.runtime.onConnectExternal)

**Attack:**

```javascript
// From any whitelisted domain (app.kartra.com, app.kartra-beta.com, *.kartradev.com)
// or from any other extension that knows this extension's ID
const port = chrome.runtime.connect('hoieipnjbkghbcmcaiiakfacmillicbg');

port.postMessage({
    request: 'fontConfig',
    editorFontGroupName: 'malicious_font_group_name'
});
```

**Impact:** Storage poisoning vulnerability. An external attacker (from whitelisted domains or other extensions) can arbitrarily set the `editorFontGroupName` value in chrome.storage.sync, potentially disrupting the extension's font configuration functionality or causing unexpected behavior.

---

## Sink 2: bg_external_port_onMessage → chrome_storage_local_set_sink

**CoCo Trace:**
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/hoieipnjbkghbcmcaiiakfacmillicbg/opgen_generated_files/bg.js
Line 1215    console.log('New request:', message.request);
    message.request
Line 1260    newVer = message.request.substring(4);
    message.request.substring(4)

**Code:**

```javascript
// Line 1321 - External connection listener
chrome.runtime.onConnectExternal.addListener(connectionListener);

// Line 1276-1279 - Connection handler
function connectionListener (port) {
    console.log('New connection');
    port.onMessage.addListener(messageListener);
}

// Line 1212-1266 - Message handler
function messageListener (message, port) {
    let newVer;
    try {
        console.log('New request:', message.request);
        switch (message.request) { // ← attacker-controlled
            case 'kver6':
            case 'kver7':
                // On-page report of Kartra version
                newVer = message.request.substring(4); // ← attacker-controlled
                if (newVer !== kver) {
                    kver = newVer;
                    // Update version for pop-up
                    chrome.storage.local.set({ kver }); // Line 1264
                }
                break;
            // ... other cases
        }
    } catch (err) {
        console.error('Error during request: ' + err);
    }
}
```

**Classification:** TRUE POSITIVE

**Attack Vector:** External port connection (chrome.runtime.onConnectExternal)

**Attack:**

```javascript
// From any whitelisted domain or other extension
const port = chrome.runtime.connect('hoieipnjbkghbcmcaiiakfacmillicbg');

// Poison the Kartra version stored in chrome.storage.local
port.postMessage({
    request: 'kver_malicious_payload'
});
// The code will store '_malicious_payload' (substring from position 4) in kver
```

**Impact:** Storage poisoning vulnerability. An external attacker can set arbitrary values in the extension's `kver` (Kartra version) field in chrome.storage.local by sending a message with a request starting with 'kver'. This could disrupt version-dependent logic or cause the extension to behave incorrectly.
