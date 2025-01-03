// const messages = document.querySelector('.messages-content');
// let d, h, m;
// let i = 0;

// window.addEventListener('load', function () {
//   updateScrollbar();
//   loadMessages();  // Load messages when the page loads
// });

// function updateScrollbar() {
//   messages.scrollTop = messages.scrollHeight;
// }

// function setDate() {
//   d = new Date();
//   if (m !== d.getMinutes()) {
//     m = d.getMinutes();
//     const timestamp = document.createElement('div');
//     timestamp.className = 'timestamp';
//     timestamp.textContent = `${d.getHours()}:${m}`;
//     const lastMessage = messages.querySelector('.message:last-child');
//     if (lastMessage) {
//       lastMessage.appendChild(timestamp);
//     }
//   }
// }

// function insertMessage() {
//   const messageInput = document.querySelector('.message-input');
//   const msg = messageInput.value;
//   if (msg.trim() === '') {
//     return;
//   }

//   // Send the message to the backend (Django) using AJAX
//   sendMessage(msg);

//   // Display the user's message in the chat
//   const messagePersonal = document.createElement('div');
//   messagePersonal.className = 'message message-personal new';
//   messagePersonal.textContent = msg;
//   messages.appendChild(messagePersonal);

//   setDate();
//   messageInput.value = '';
//   updateScrollbar();
// }

// document.querySelector('.message-submit').addEventListener('click', insertMessage);

// window.addEventListener('keydown', function (e) {
//   if (e.key === 'Enter') {
//     insertMessage();
//     e.preventDefault();
//   }
// });

// function loadMessages() {
//   fetch(`/chat/${chatId}/messages/`, {
//     method: 'GET',
//     headers: {
//       'Content-Type': 'application/json',
//     },
//   })
//   .then(response => response.json())
//   .then(data => {
//     data.messages.forEach(msg => {
//       const messageDiv = document.createElement('div');
//       messageDiv.className = `message ${msg.sender === 'user' ? 'message-personal' : 'message-other'} new`;
//       messageDiv.textContent = msg.content;  // Adjust according to the response structure
//       messages.appendChild(messageDiv);
//     });
//     updateScrollbar();
//   })
//   .catch(error => console.log('Error loading messages:', error));
// }

// function sendMessage(msg) {
//   fetch(`/chat/${chatId}/send/`, {
//     method: 'POST',
//     headers: {
//       'Content-Type': 'application/json',
//     },
//     body: JSON.stringify({
//       content: msg,
//       csrfmiddlewaretoken: '{{ csrf_token }}',  // Include CSRF token for security
//     }),
//   })
//   .then(response => response.json())
//   .then(data => {
//     console.log('Message sent successfully:', data);
//     // Optionally handle the response (e.g., display the sent message)
//   })
//   .catch(error => console.log('Error sending message:', error));
// }



document.addEventListener('DOMContentLoaded', () => {
  // Load the initial set of messages
  loadMessages();

  // Scroll chat to the bottom
  function updateScrollbar() {
      const messages = document.getElementById('messages');
      messages.scrollTop = messages.scrollHeight;
  }
  const messagesContainer = document.getElementById('messages');
  if (messagesContainer) {
      messagesContainer.scrollTop = messagesContainer.scrollHeight;
  }
  
  // Load
});
