import React from "react";

function Message({ sender, text }) {
  return (
    <div className={`message ${sender}`}>
      <p>{text}</p>
    </div>
  );
}

export default Message;
