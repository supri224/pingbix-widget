// pingbix-webchat.js
(function(){
  window.PingbixWebchat = {
    init: function(config) {
      const chatDiv = document.createElement('div');
      chatDiv.id = 'pingbix-webchat';
      chatDiv.style = 'position:fixed;bottom:20px;right:20px;width:350px;height:400px;border:1px solid #ccc;background:#fff;padding:10px;overflow:auto;box-shadow:0 0 10px rgba(0,0,0,0.2);border-radius:8px;font-family:Arial,sans-serif;';
      document.body.appendChild(chatDiv);

      const messagesDiv = document.createElement('div');
      messagesDiv.style.height='300px';
      messagesDiv.style.overflowY='auto';
      messagesDiv.style.marginBottom='10px';
      chatDiv.appendChild(messagesDiv);

      const input = document.createElement('input');
      input.type='text';
      input.placeholder='Ask me something...';
      input.style.width='80%';
      input.style.padding='5px';
      chatDiv.appendChild(input);

      const btn = document.createElement('button');
      btn.innerText='Send';
      btn.style.width='18%';
      btn.style.padding='5px';
      chatDiv.appendChild(btn);

      async function sendQuestion(){
        const question = input.value.trim();
        if(!question) return;

        // User message
        const userMsg = document.createElement('div');
        userMsg.style.color='blue';
        userMsg.textContent='You: ' + question;
        messagesDiv.appendChild(userMsg);
        input.value='';
        messagesDiv.scrollTop=messagesDiv.scrollHeight;

        try{
          const res = await fetch(config.apiUrl, {
            method:'POST',
            headers:{'Content-Type':'application/json'},
            body: JSON.stringify({ question })
          });

          const data = await res.json();
          const botMsg = document.createElement('div');
          botMsg.style.color='green';
          botMsg.textContent='Bot: ' + (data.answer || "No response");
          messagesDiv.appendChild(botMsg);
          messagesDiv.scrollTop=messagesDiv.scrollHeight;

        } catch(e){
          const errMsg = document.createElement('div');
          errMsg.style.color='red';
          errMsg.textContent='Bot: Error connecting to server.';
          messagesDiv.appendChild(errMsg);
          messagesDiv.scrollTop=messagesDiv.scrollHeight;
        }
      }

      btn.onclick=sendQuestion;
      input.addEventListener('keypress', e=>{ if(e.key==='Enter') sendQuestion(); });
    }
  };
})();
