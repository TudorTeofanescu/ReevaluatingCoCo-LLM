# CoCo Analysis: fdlkdmjhccmacajafcfcoffjmkkkkfib

## Summary

- **Overall Assessment:** FALSE POSITIVE
- **Total Sinks Detected:** 6 (3 unique flows, duplicated)

---

## Sink: XMLHttpRequest_responseText_source → chrome_storage_local_set_sink

**CoCo Trace:**
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/fdlkdmjhccmacajafcfcoffjmkkkkfib/opgen_generated_files/bg.js
Line 332: XMLHttpRequest.prototype.responseText = 'sensitive_responseText';
Line 988: var data = JSON.parse(xhr.responseText);
Line 1001: chrome.storage.local.set({"title": data.stream.channel.status}, function() {
Line 1004: chrome.storage.local.set({"viewers": data.stream.viewers}, function() {
Line 1007: chrome.storage.local.set({"game": data.stream.game}, function() {

**Code:**

```javascript
// Background script - XMLHttpRequest to hardcoded Twitch API
xhr.open("GET", "https://api.twitch.tv/kraken/streams/23138164");  // ← Hardcoded Twitch API
xhr.setRequestHeader("Client-Id", "yecpql8r59bwp1yl2fu3dfsqgeweqi");
xhr.setRequestHeader("Accept", "application/vnd.twitchtv.v5+json");
xhr.onreadystatechange = function()
{
    if(xhr.readyState == 4)
    {
        var data = JSON.parse(xhr.responseText);  // ← Data from Twitch API
        if(data["stream"] == null)
        {
            chrome.browserAction.setTitle({title: "ZANKIOH - Offline"});
            chrome.browserAction.setIcon({path: {"48": "../Assets/Logo/Logo_Offline_48x48.png"}});
            chrome.browserAction.setPopup({popup: "../HTML-CSS/page_offline.html"});
            onStream = false;
        }
        else
        {
            chrome.browserAction.setTitle({title: "ZANKIOH - Online"});
            chrome.browserAction.setIcon({path: {"48": "../Assets/Logo/Logo_Online_48x48.png"}});

            // Store Twitch stream data
            chrome.storage.local.set({"title": data.stream.channel.status}, function() {
                console.log('Title: ' +  data.stream.channel.status);
            });
            chrome.storage.local.set({"viewers": data.stream.viewers}, function() {
                console.log('Viewers: ' +  data.stream.channel.status);
            });
            chrome.storage.local.set({"game": data.stream.game}, function() {
                console.log('Game: ' +  data.stream.game);
                game = data.stream.game;
            });

            let stream_date = new Date(data.stream.created_at)
            let timer = Date.now() - stream_date;
            chrome.storage.local.set({"time": timer}, function() {
                console.log('Time: ' +  new Date(data.stream.created_at) - new Date());
            });

            chrome.browserAction.setPopup({popup: "../HTML-CSS/page_online.html"});
            onStream = true;
        }
    }
}
xhr.send(null);
```

**Classification:** FALSE POSITIVE

**Reason:** Data flows from hardcoded Twitch API endpoint (https://api.twitch.tv/kraken/streams/23138164) to storage. The Twitch API is trusted infrastructure - the extension is designed to monitor a specific Twitch streamer's status and display it to users. According to the methodology, "Data FROM hardcoded backend" is FALSE POSITIVE because compromising external APIs (like Twitch) is an infrastructure issue, not an extension vulnerability. There is no attacker-controlled input - the XHR request goes to a hardcoded URL with hardcoded headers.
