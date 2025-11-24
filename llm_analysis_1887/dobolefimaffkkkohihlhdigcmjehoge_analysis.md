# CoCo Analysis: dobolefimaffkkkohihlhdigcmjehoge

## Summary

- **Overall Assessment:** FALSE POSITIVE
- **Total Sinks Detected:** 2 (chrome_storage_local_set_sink and XMLHttpRequest_post_sink, with multiple duplicate detections)

---

## Sink 1: Document_element_href → chrome_storage_local_set_sink (referenced only CoCo framework code)

**CoCo Trace:**
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/dobolefimaffkkkohihlhdigcmjehoge/opgen_generated_files/cs_0.js
Line 20	    this.href = 'Document_element_href';

**Classification:** FALSE POSITIVE

**Reason:** CoCo only detected flows in framework code (Line 20 is CoCo's Document_element mock). The actual extension does store user email from Google Classroom, but this is user's own data on the page they're viewing, not attacker-controlled data.

---

## Sink 2: Document_element_href → XMLHttpRequest_post_sink (referenced only CoCo framework code)

**CoCo Trace:**
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/dobolefimaffkkkohihlhdigcmjehoge/opgen_generated_files/cs_0.js
Line 20	    this.href = 'Document_element_href';
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/dobolefimaffkkkohihlhdigcmjehoge/opgen_generated_files/bg.js
Line 977	encodeURI(a)
Line 977	c="userLogged="+encodeURI(a)

**Code:**

```javascript
// Content script (cs_0.js line 476):
function sendInfo() {
    var a = window.location.href;
    if (a && a.includes("classroom")) {
        a = $('[aria-label*="@"]'); // ← reads user's email from Classroom page
        if (a) {
            a = a.attr("aria-label");
            chrome.storage.local.set({userLogged: a}); // ← stores user email
            chrome.runtime.sendMessage({url: window.location.href, user: a}); // ← sends to bg
        }
    }
}

// Background script (bg.js lines 977-978):
function checkLicense(a) {
    if (void 0 != a) try {
        var b = new XMLHttpRequest;
        var c = a;
        c = "userLogged=" + encodeURI(a); // ← user email from content script
        b.open("POST", "https://www.razorsparrow.com/licensing.php", !0); // ← hardcoded backend
        b.setRequestHeader("Content-type", "application/x-www-form-urlencoded");
        b.onreadystatechange = function() {
            if (4 == b.readyState && 200 == b.status) {
                // ... handles response
            }
        };
        b.send(c); // ← sends user email to backend
    } catch(d) {
        alert("an error occurred: " + d.stack);
    }
}

// Triggered from message listener:
chrome.runtime.onMessage.addListener(function(a, b, c) {
    if (a.url) {
        tabToCheck = a.url;
        userLogged = a.user; // ← receives user email from content script
        chrome.storage.local.get("power", function(a) {
            if (1 == a.power && tabToCheck.includes("classroom")) {
                checkLicense(userLogged); // ← POSTs to backend
            }
        });
    }
});
```

**Classification:** FALSE POSITIVE

**Reason:** While CoCo detected a flow from Document_element_href (framework code only) to XMLHttpRequest POST, the actual extension flow is:
1. Content script reads user's own email from Google Classroom page DOM
2. Sends to background script via internal message (not external attacker)
3. Background POSTs to hardcoded backend URL (https://www.razorsparrow.com/licensing.php)

Per methodology rule: "Hardcoded backend URLs are trusted infrastructure - data TO hardcoded backend is FALSE POSITIVE." The user's email is their own data being sent to the developer's licensing server, not attacker-controlled data. There is no external attacker trigger (only internal chrome.runtime.onMessage, not onMessageExternal).
