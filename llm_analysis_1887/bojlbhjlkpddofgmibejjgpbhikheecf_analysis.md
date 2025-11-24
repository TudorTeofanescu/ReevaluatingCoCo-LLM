# CoCo Analysis: bojlbhjlkpddofgmibejjgpbhikheecf

## Summary

- **Overall Assessment:** FALSE POSITIVE
- **Total Sinks Detected:** 1

---

## Sink: document_body_innerText → jQuery_post_data_sink (referenced only CoCo framework code)

**CoCo Trace:**
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/bojlbhjlkpddofgmibejjgpbhikheecf/opgen_generated_files/cs_0.js
Line 29: `Document_element.prototype.innerText = new Object();`

Note: CoCo only detected the flow in framework code (Line 29). The actual extension code is after line 7548. Analysis of actual extension code is required.

**Code:**

```javascript
// Content script - cs_0.js (Lines 7665-7705, 7723-7742)
function checkPageContent() {
    // ... page checking logic ...

    if (shouldCheckPage) {
        if (shouldTakeSnapshotOfPage()) {
            html2canvas(document.body).then(function (canvas) {
                var postData = {
                    base64: canvas.toDataURL("image/jpg"),
                    url: location.href,
                    lucidWebOptions: lucidWebOptions,
                    pageTitle: document.pageTitle,
                    pageContent: document.body.innerText,  // ← Contains webpage content
                    loginPage: loginPage,
                    entryPage: entryPage,
                    hasPasswordField: hasPasswordField,
                    hasLoginThrough: hasLoginThrough,
                    sellSomething: sellSomething,
                    hasEmailAndNext: hasEmailAndNext,
                    rating: rating
                };
                consultServer(postData);  // ← Sends to background
            });
        } else {
            var postData = {
                base64: "",
                url: location.href,
                lucidWebOptions: lucidWebOptions,
                pageTitle: document.pageTitle,
                pageContent: document.body.innerText,  // ← Contains webpage content
                loginPage: loginPage,
                entryPage: entryPage,
                hasPasswordField: hasPasswordField,
                hasLoginThrough: hasLoginThrough,
                sellSomething: sellSomething,
                hasEmailAndNext: hasEmailAndNext,
                rating: rating
            };
            consultServer(postData);  // ← Sends to background
        }
    }
}

function consultServer(postData) {
    chrome.runtime.sendMessage({postData: postData}, function (response) {
        // ... handle response ...
    });
}

// Background script - bg.js (Lines 985-1004)
var prodhostURL = "https://the-shadow.com/aphish/findMatch";  // ← Hardcoded backend URL
var localhostURL = "http://localhost:9103/findMatch";
var serverURL = prodhostURL;  // ← Defaults to production server

chrome.runtime.onMessage.addListener(function(message, sender, sendResponse) {
    if (message.postData) {
        var postData = message.postData;
        lucidWebOptions = postData.lucidWebOptions;
        if (lucidWebOptions && lucidWebOptions.debug && lucidWebOptions.debug == true) {
            serverURL = localhostURL;  // ← Debug mode uses localhost
        }
        $.post(serverURL, postData, function(result){  // ← POST to hardcoded backend
            sendResponse(result);
        });
    }
    return true;
});
```

**Classification:** FALSE POSITIVE

**Reason:** Hardcoded backend URL (trusted infrastructure). The extension sends `document.body.innerText` (which contains webpage content) to a hardcoded developer backend URL `https://the-shadow.com/aphish/findMatch` (line 985 in bg.js). According to the methodology, data TO hardcoded backend URLs is considered trusted infrastructure. The extension developer trusts their own backend server for legitimate anti-phishing functionality; compromising this backend is a separate infrastructure security issue, not an extension vulnerability. The extension is designed to analyze page content for phishing detection, and sending page content to the developer's backend is the intended functionality, not a vulnerability.
