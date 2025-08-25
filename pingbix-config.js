// pingbix-config.js
(function(){
  window.PingbixWebchat.init({
    apiUrl: "http://127.0.0.1:8000/chat",  // 👈 your FastAPI backend
    botName: "Pingbix Assistant"
  });
})();
