# CoCo Analysis: cohkdbccofoniobcnbjkhfmndggddbmf

## Summary

- **Overall Assessment:** FALSE POSITIVE
- **Total Sinks Detected:** 2 (same flow pattern)

---

## Sink: XMLHttpRequest_responseText_source → chrome_storage_local_set_sink

**CoCo Trace:**
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/cohkdbccofoniobcnbjkhfmndggddbmf/opgen_generated_files/bg.js
Line 332: XMLHttpRequest.prototype.responseText = 'sensitive_responseText' (CoCo framework code)
Line 981: var data = JSON.parse(xhr.responseText);
Line 982: var count = data.items.length;

**Code:**

```javascript
// Background script - CheckYoutube() function (bg.js Line 978-996)
var xhr = new XMLHttpRequest();
xhr.onreadystatechange = function () {
    if (xhr.readyState == 4  && xhr.status == 200) {
        var data = JSON.parse(xhr.responseText);
        var count = data.items.length;
        // Flow detected by CoCo: data.items.length → storage
        chrome.storage.local.set({'count': count});
        if (count > 0) {
            chrome.storage.local.get({"notif-youtube": true}, function(item) {
                if (item["notif-youtube"])
                    doNotification(notifYoutube, messageYoutube);
            });
        }
    }
}

// HARDCODED URL - trusted Google/YouTube API infrastructure
var dateenc = encodeURIComponent(lastDate2);
xhr.open("GET","https://www.googleapis.com/youtube/v3/search?part=snippet&channelId=UC8v1wzqXGNksNl3XKIsGhPA&order=date&maxResults=50&publishedAfter="+dateenc+"&key=AIzaSyBpEoqKFNwMeU_GmS1BId-nYCZ7V3TLMG0", true);
xhr.send();
```

**Classification:** FALSE POSITIVE

**Reason:** Both detected flows originate from XMLHttpRequest responses to a hardcoded Google/YouTube API URL (`https://www.googleapis.com/youtube/v3/search`). This is trusted infrastructure. Attackers cannot control the response data from Google's YouTube API endpoint. The extension fetches video count information from YouTube's official API and stores it locally. There are no external message listeners or other attacker-controlled entry points. Per the methodology, data from hardcoded developer/trusted backend URLs is classified as FALSE POSITIVE.

---
