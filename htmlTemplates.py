css = '''
<style>
.header-container {
  display: flex;
  background-color: #A20066;
  justify-content: space-between;
  height: 80px;
  width: 100%;
  padding: 0;
  position: sticky;
  top: 0;
  margin-bottom: 1rem;
}
.header-logo {
  color: #fff;
  justify-self: flex-start;
  cursor: pointer;
  font-size: 1.8rem;
  display: flex;
  align-items: center;
  margin-left: 5%;
  font-weight: bold;
  text-decoration: none;
}
.header-img {
  width: 150px;
  height: auto;
}
.chat-message {
  display: flex;
  align-items: flex-start;
  border-radius: 0.5rem;
  padding: 1.5rem;
  margin-bottom: 1rem;
}
.chat-message.user {
    background-color: #2b313e;
}
.chat-message.bot {
  background-color: #475063;
}
.message-documents {
  display: flex; /* Make this also a flex container */
  flex-direction: column; /* Stack children (message and documents) vertically */
  align-items: flex-start; /* Align children to the start of the flex container */
  margin-left: 1.5rem; /* Space between avatar and text */
  flex: 1; /* Take up remaining space */
}
.chat-message .avatar {
  margin-right: 1.5rem; /* Adds space between the avatar and the message */
  
}
.chat-message .avatar img {
  max-width: 78px;
  max-height: 78px;
  border-radius: 50%;
  object-fit: cover;
}
.chat-message .message {
  color: #fff;
  font-size: 18px;
}
.documents {
  font-size: 16px; /* Same font size as the chatbot's response */
  color: #fff; /* Same color as the chatbot's response */
  margin-top: 1rem; /* Space between message and document links */
  padding: 0;
  margin: 0;
}
.documents a {
  color: #E91E63; /* A pleasant blue shade for links, adjust as needed */
  text-decoration: none; /* Removes underline from links */
  display: block; /* Each link on a new line */
  margin-bottom: 0.1rem; /* Space between links */
  padding: 0;
  margin: 0;
}
.documents a:hover {
  text-decoration: underline; /* Underline on hover for better user experience */
}

/* Style for the dividing line */
.documents-divider {
  border: 1px solid #ffffff; /* Sets a top border to white */
  width: 90%;
  opacity: 1; /* Full opacity */
  visibility: visible; /* Ensures the line is not hidden */
  margin: 1rem 0; /* Add some margin above and below the line */
  z-index: 1; /* Ensure it's above other elements */
}

/* Adjust the width of the message so it doesn't stretch too wide */
.chat-message .message {
  max-width: 90%; /* Adjust the percentage as needed */
  word-wrap: break-word; /* Ensures long words don't overflow */
}

/* Apply flex column direction to stack message and documents vertically */
.chat-message .message-documents {
  flex-direction: column;
  align-items: flex-start; /* Aligns content to the left */
}

.footer-container {
  display: flex;
  position: fixed;
  bottom: 0;
  right: 0;
  background-color:#f8e6f7;
  height: 5%;
  width: 100%;
  z-index: 999;
  padding-left: 2rem;
}

.footer-text{
  font-size: 13px;
  color: black;
  font-style: italic;
  align-self: center;
  padding: 0;
  margin:0
}
'''

bot_template = '''
<div class="chat-message bot">
    <div class="avatar">
        <img src="https://i.ibb.co/f2h6BQb/3-robot.jpg">
    </div>
    <div class="message-documents">
        <div class="message">{{MSG}}</div>
        <div class="documents-divider"></div>
        <div class="documents">You may want to check the following documents:<br>{{DOCS}}</div>
    </div>
</div>
'''

user_template = '''
<div class="chat-message user">
    <div class="avatar">
        <img src="https://i.ibb.co/Dbnp4mn/Screenshot-2023-10-17-at-10-40-18.png">
    </div>    
    <div class="message-documents">
      <div class="message">{{MSG}}</div>
    </div>
</div>
'''

banner = '''
<div class="header-container">  
    <a class="header-logo">    
        <img class="header-img" src="https://i.ibb.co/74Sk7KW/Python-logo-notext-svg.png" alt="Logo">  
    </a>
</div>
'''

footer = '''
<div class="footer-container">
    <p class="footer-text"> This is a footer. </p>

</div>
'''
