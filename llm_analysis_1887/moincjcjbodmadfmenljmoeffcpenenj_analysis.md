# CoCo Analysis: moincjcjbodmadfmenljmoeffcpenenj

## Summary

- **Overall Assessment:** FALSE POSITIVE
- **Total Sinks Detected:** 2 (both identical flows)

---

## Sink: XMLHttpRequest_responseText_source → XMLHttpRequest_url_sink

**CoCo Trace:**
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/moincjcjbodmadfmenljmoeffcpenenj/opgen_generated_files/bg.js
Line 332: XMLHttpRequest.prototype.responseText = 'sensitive_responseText';
Line 1000: var data1 = JSON.parse(xhr1.responseText)
Line 1001: streamerID = data1.users[0]._id;
Line 1003: xhr.open("GET", "https://api.twitch.tv/kraken/streams/" + streamerID, true);

**Code:**

```javascript
// Background script - Check stream status (lines 993-1022)
var streamerURL = "samuse"; // ← Hardcoded value

function checkstream(){
  var xhr1 = new XMLHttpRequest();
  xhr1.open("GET", "https://api.twitch.tv/kraken/users?login=" + streamerURL, true); // ← Hardcoded backend URL
  xhr1.setRequestHeader("Accept", "application/vnd.twitchtv.v5+json");
  xhr1.setRequestHeader("Client-ID", "s9qt2epst6li0ihjgzx8lxpt283nzl");
  xhr1.onreadystatechange = function (channel) {
    if(xhr1.readyState == 4) {
      var data1 = JSON.parse(xhr1.responseText) // ← Response from Twitch API
      streamerID = data1.users[0]._id; // ← Extracts user ID from response
      var xhr = new XMLHttpRequest();
      xhr.open("GET", "https://api.twitch.tv/kraken/streams/" + streamerID, true); // ← Uses ID in another Twitch API call
      xhr.setRequestHeader("Accept", "application/vnd.twitchtv.v5+json");
      xhr.setRequestHeader("Client-ID", "s9qt2epst6li0ihjgzx8lxpt283nzl");
      xhr.onreadystatechange = function(channel) {
        if(xhr.readyState == 4) {
          var data = JSON.parse(xhr.responseText)
          var elm  = document.getElementById("info")
          if(data["stream"] === null){
            chrome.browserAction.setIcon({path: "../img/icon_off2.png"});
            alreadyCheck = false;
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

checkstream();
setInterval(checkstream, 120000);
```

**Classification:** FALSE POSITIVE

**Reason:** This is a FALSE POSITIVE because it involves only hardcoded backend URLs (Twitch API - trusted infrastructure). The flow is:

1. Extension makes XHR request to hardcoded Twitch API: `https://api.twitch.tv/kraken/users?login=samuse`
2. Response from Twitch API contains user ID
3. That user ID is used in a second XHR request to another hardcoded Twitch API endpoint: `https://api.twitch.tv/kraken/streams/[ID]`

There is no attacker control in this flow:
- The initial request goes to a hardcoded Twitch API URL (not attacker-controlled)
- The streamerURL variable is hardcoded as "samuse" (line 967)
- The response comes from Twitch's infrastructure (trusted backend)
- The extracted ID is only used to make another request to the same Twitch API (hardcoded domain)

According to the methodology, "Data FROM hardcoded backend: fetch('https://api.myextension.com') → response → subsequent request" is classified as FALSE POSITIVE because the developer trusts the backend infrastructure (in this case, Twitch API). There is no external attacker trigger, and all URLs involved are hardcoded to the legitimate Twitch API. This is internal extension logic for checking if a specific Twitch streamer is online, with no exploitable path for an attacker.

The CoCo detection is purely about data flowing from one XHR response (XMLHttpRequest_responseText_source) to another XHR URL parameter (XMLHttpRequest_url_sink), but both requests are to the same trusted Twitch API infrastructure with hardcoded domains.

---

## Sink 2: XMLHttpRequest_responseText_source → XMLHttpRequest_url_sink (Duplicate)

**Classification:** FALSE POSITIVE

**Reason:** This is a duplicate detection of the same flow described above. CoCo detected the same vulnerability pattern twice.
