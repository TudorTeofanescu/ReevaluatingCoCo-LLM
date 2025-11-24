# CoCo Analysis: ehkmngnolihelcgloljbcpghfngagcpj

## Summary

- **Overall Assessment:** FALSE POSITIVE
- **Total Sinks Detected:** 1

---

## Sink: jQuery_ajax_result_source → chrome_storage_local_set_sink (referenced only CoCo framework code)

**CoCo Trace:**
```
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/ehkmngnolihelcgloljbcpghfngagcpj/opgen_generated_files/bg.js
Line 291	var jQuery_ajax_result_source = 'data_form_jq_ajax';
```

Note: Line 291 is in CoCo framework code (before the 3rd "// original" marker at line 963). The actual extension code implementing this flow is in the original extension files after line 963.

**Code:**

```javascript
// Content script (content.js) - Lines 9-19
// Listener for when Youtube page reloads
window.addEventListener("yt-navigate-finish", function(){
  setTimeout(function() {
    const domElements = getDOMElements();
    const totalTime = getTotalTime();
    // Send message to background to make request
    chrome.runtime.sendMessage({
      totalTime: totalTime,
      title: domElements.title  // ← Video title from document.title
    });
  }, 1000);
});

// Get video title (content.js lines 128-136)
function getYoutubeVideoTitle() {
  var videoTitle = document.title;  // ← From YouTube's document.title
  const youtubeSuffix = " - YouTube";
  if (videoTitle.length >= youtubeSuffix.length) {
    videoTitle = videoTitle.substring(0, videoTitle.length - youtubeSuffix.length);
  }
  return videoTitle;
}

// Background script - API client (apiclient.js lines 965-990)
const BASE_URL = "http://ec2-52-13-122-43.us-west-2.compute.amazonaws.com:3000/";

function request(type, parameters, url, callback){
  $.ajax({
    type: type,
    url: url,  // ← Hardcoded backend URL
    data: JSON.stringify(parameters),
    dataType: 'json',
    contentType: 'application/json',
    success: function (data) {
      callback(true, data);  // ← Response from backend
    },
    error: function (data) {
      callback(false, data);
    }
  });
}

function requestVideoTracklist(videoTitle, callback) {
  const sanitizedTitle = encodeURI(videoTitle.replace('&',' ').replace('#', ' '));
  request(GET, null, BASE_URL + "?v=" + sanitizedTitle, callback);
}

// Background script - Storage (tracklist_fetcher.js lines 994-1022)
function getTracklist(videoTitle, callback) {
  chrome.storage.local.get([videoTitle], function(items) {
    if (items[videoTitle] === undefined) {
      // Fetch remotely from hardcoded backend
      requestVideoTracklist(videoTitle, function(success, response) {
        if (success) {
          // Store response from backend
          chrome.storage.local.set({[videoTitle]: response}, function() {
            console.log('Value is set to', response);
            chrome.storage.local.get([videoTitle], function(items) {
              callback(true, items[videoTitle]);
            })
          });
        } else {
          callback(false, undefined);
        }
      });
    } else {
      callback(true, items[videoTitle]);
    }
  });
}

// Background message listener (background.js lines 1031-1046)
chrome.runtime.onMessage.addListener(
  function(request, sender, sendResponse) {
    if (request.totalTime > TOTAL_TIME_THRESHOLD) {
      getTracklist(request.title, function(success, tracklist) {
        if (success) {
          console.log("Success fetching tracklist!");
        } else {
          console.log("Error getting video tracklist");
        }
      });
    }
    return true;
  });
```

**Manifest content_scripts:**
```json
{
  "matches": [
    "*://*.youtube.com/*",
    "*://*.soundcloud.com/*",
    "*://*.mixcloud.com/*"
  ],
  "js": ["jquery-3.2.1.min.js", "content.js"]
}
```

**Classification:** FALSE POSITIVE

**Reason:** Data flows from hardcoded backend URL to storage, which is trusted infrastructure. The flow is: YouTube video title → AJAX request to hardcoded backend `http://ec2-52-13-122-43.us-west-2.compute.amazonaws.com:3000/` → backend response → storage. Per methodology Rule #3, "Hardcoded backend URLs are still trusted infrastructure" and "Data FROM hardcoded backend" is a false positive pattern. The video title comes from legitimate websites (YouTube, SoundCloud, Mixcloud) where the attacker cannot directly control document.title. Even if the title could be influenced, the actual stored data is the response from the developer's trusted backend server, not attacker-controlled input. There is no evidence of a retrieval path that sends this data back to an external attacker.
