# CoCo Analysis: eijeghjmolnfcjfhcjkhcmdiancaifdd

## Summary

- **Overall Assessment:** FALSE POSITIVE
- **Total Sinks Detected:** 2 (duplicate detection)

---

## Sink: XMLHttpRequest_responseText_source → XMLHttpRequest_url_sink

**CoCo Trace:**
```
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/eijeghjmolnfcjfhcjkhcmdiancaifdd/opgen_generated_files/bg.js
Line 332: XMLHttpRequest.prototype.responseText = 'sensitive_responseText';
Line 998: var data1 = JSON.parse(xhr1.responseText)
Line 999: streamerID = data1.users[0]._id;
Line 1001: xhr.open("GET", "https://api.twitch.tv/kraken/streams/" + streamerID, true);
```

**Classification:** FALSE POSITIVE

**Reason:** This extension is a Twitch stream notification tool for AlexCrilo. The flow involves fetching data exclusively from hardcoded Twitch API endpoints (`https://api.twitch.tv/kraken/users` and `https://api.twitch.tv/kraken/streams/`). The data flows from the first Twitch API response to construct the URL for the second Twitch API request. Both source and sink involve the developer's trusted infrastructure (Twitch API). There is no external attacker trigger - the extension simply polls Twitch's API every 2 minutes via `setInterval(checkstream, 120000)` to check if the streamer is online. Per the methodology, data to/from hardcoded developer backend URLs is considered trusted infrastructure and not a vulnerability.

**Code:**
```javascript
// Line 991 - checkstream function (internal polling)
function checkstream(){
  var xhr1 = new XMLHttpRequest();
  xhr1.open("GET", "https://api.twitch.tv/kraken/users?login=" + streamerURL, true); // hardcoded Twitch API
  xhr1.setRequestHeader("Accept", "application/vnd.twitchtv.v5+json");
  xhr1.setRequestHeader("Client-ID", "s9qt2epst6li0ihjgzx8lxpt283nzl");
  xhr1.onreadystatechange = function (channel) {
    if(xhr1.readyState == 4) {
      var data1 = JSON.parse(xhr1.responseText) // Twitch API response
      streamerID = data1.users[0]._id;
      var xhr = new XMLHttpRequest();
      xhr.open("GET", "https://api.twitch.tv/kraken/streams/" + streamerID, true); // hardcoded Twitch API
      xhr.setRequestHeader("Accept", "application/vnd.twitchtv.v5+json");
      xhr.setRequestHeader("Client-ID", "s9qt2epst6li0ihjgzx8lxpt283nzl");
      xhr.onreadystatechange = function(channel) {
        if(xhr.readyState == 4) {
          var data = JSON.parse(xhr.responseText)
          // Check stream status and update icon
          if(data["stream"] === null){
            chrome.browserAction.setIcon({path: "../img/icon_off.png"});
          }else{
            onlineStream(data);
          }
        }
      }
      xhr.send()
    }
  }
  xhr1.send()
}

// Line 1022 - Automatic polling (no external trigger)
checkstream();
setInterval(checkstream, 120000);
```
