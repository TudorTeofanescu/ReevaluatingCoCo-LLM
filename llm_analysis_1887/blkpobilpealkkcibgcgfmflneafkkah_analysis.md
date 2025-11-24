# CoCo Analysis: blkpobilpealkkcibgcgfmflneafkkah

## Summary

- **Overall Assessment:** FALSE POSITIVE
- **Total Sinks Detected:** 4 (all the same pattern)

---

## Sink: document_body_innerText → chrome_storage_local_set_sink

**CoCo Trace:**
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/blkpobilpealkkcibgcgfmflneafkkah/opgen_generated_files/cs_0.js
Line 29    Document_element.prototype.innerText = new Object();
Line 474   var emails = allText.match(emailRegex);
Line 477   if (allEmails.indexOf(emails[i]) == -1) {

$FilePath$/home/teofanescu/cwsCoCo/extensions_local/blkpobilpealkkcibgcgfmflneafkkah/opgen_generated_files/bg.js
Line 972   chrome.storage.local.set({emails: request.emails,urlTab:request.urlTab}, function() {

**Code:**

```javascript
// Content script (cs_0.js) - Lines 467-492
var allEmails = [];
var emailRegex = /\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b/g;
var allText = document.body.innerText; // Extract text from webpage
var emails = allText.match(emailRegex);
if (emails) {
    for (var i = 0; i < emails.length; i++) {
        if (allEmails.indexOf(emails[i]) == -1) {
            allEmails.push(emails[i]);
        }
    }
}
// Send extracted emails to background
chrome.runtime.sendMessage({message: "finded", emails: allEmails, urlTab: urlTab});

// Background script (bg.js) - Lines 966-974
chrome.runtime.onMessage.addListener(function(request, sender, sendResponse) {
    if (request.message === "finded") {
        // Store emails in chrome.storage.local
        chrome.storage.local.set({emails: request.emails,urlTab:request.urlTab}, function() {
            console.log("Emails saved to local storage");
        });
    }
});
```

**Classification:** FALSE POSITIVE

**Reason:** Storage poisoning without complete exploitation chain. While an attacker can poison `document.body.innerText` on their webpage to inject malicious email addresses into storage, the stored data is only retrieved and displayed in the extension's own popup UI (popup.js lines 8-19), which is NOT attacker-accessible. The attacker cannot retrieve the poisoned storage data back. According to the methodology, storage poisoning alone without a retrieval path to the attacker is NOT exploitable.
