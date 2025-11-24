# CoCo Analysis: nkpnfhfaabjfnfabmecmfdedkeoldogp

## Summary

- **Overall Assessment:** FALSE POSITIVE
- **Total Sinks Detected:** 1

---

## Sink: cs_window_eventListener_message → fetch_resource_sink

**CoCo Trace:**
```
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/nkpnfhfaabjfnfabmecmfdedkeoldogp/opgen_generated_files/cs_0.js
Line 467	(minified code with eventListener and sendLoginDataToBg)
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/nkpnfhfaabjfnfabmecmfdedkeoldogp/opgen_generated_files/bg.js
Line 965	var o=e.social?"https://api.filestream.me/rest/Clients/"+e.social:"https://api.filestream.me/rest/Clients/Auth"
```

**Code:**

```javascript
// Content script - cs_0.js (Line 467 - minified, reformatted for clarity)
function eventListener(e) {
  if (-1 !== e.origin.indexOf("filestream.me")) { // ← Check origin contains "filestream.me"
    message = e.data; // ← attacker-controlled data
    switch(message.function) {
      case "loginToFs":
        sendLoginDataToBg(message); // ← flows to background
        break;
      // ... other cases
    }
  }
}

function sendLoginDataToBg(e) {
  var n = {
    function: "login",
    login: e.login,
    password: e.password,
    social: e.social, // ← attacker-controlled
    remember: e.remember,
    url: container.dUrl,
    type: container.dType,
    tabId: container.tabId,
    action: container.action,
    linkData: container.linkData
  };
  chrome.runtime.sendMessage(n, function(e) { /* ... */ });
}

function main() {
  window.addEventListener("message", eventListener, false); // ← Entry point
  chrome.runtime.onMessage.addListener(messageListener);
}

// Background script - bg.js (Line 968)
chrome.runtime.onMessage.addListener(function(e, t, o) {
  switch(e.function) {
    case "login":
      return authAndDownload(e, o), true; // ← Receives message
  }
});

function authAndDownload(e, t) {
  if (null == engine) {
    engine = new FsEngine(e.login, e.password, null);
  }
  engine.authorizeAndDownload(e, t); // ← Calls engine method
}

// FsEngine.authorizeAndDownload (Line 965 - within FsEngine constructor)
this.authorizeAndDownload = function(e, t) {
  // Constructs URL with attacker-controlled e.social in path
  var o = e.social
    ? "https://api.filestream.me/rest/Clients/" + e.social // ← attacker-controlled path segment
    : "https://api.filestream.me/rest/Clients/Auth";

  var a = e.social
    ? {login: n.username, token: n.password}
    : {login: n.username, password: n.password};

  // ... encode parameters ...

  fetch(o, c) // ← Fetch to hardcoded domain with attacker-controlled path
    .then(n.checkStatus)
    .then(n.toText)
    .then(n.authorizeAndDownloadOk.bind(null, e, t))
    .catch(n.authorizeAndDownloadError.bind(null, t));
};
```

**Classification:** FALSE POSITIVE

**Reason:** Hardcoded backend URL (trusted infrastructure). While the attacker can control the `social` parameter which affects the URL path (`https://api.filestream.me/rest/Clients/[social]`), the domain is hardcoded to the developer's own backend server (`api.filestream.me`). The attacker can only make requests to different paths on the developer's trusted infrastructure. Compromising developer infrastructure is separate from extension vulnerabilities.
