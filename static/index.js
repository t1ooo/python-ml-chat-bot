const { createApp, ref } = Vue;

createApp({
  data() {
    return {
      userInput: "",
      messages: [],
      isDisabled: false,
    };
  },

  created() {
    this._handleMessageResponse(_startChatRequest());
  },

  methods: {
    _handleMessageResponse(responsePromise) {
      this.$nextTick(this._scrollToEnd);
      responsePromise
        .then((response) => {
          console.log("response", response);
          if ("error" in response) {
            this.messages.push(_errorMessage(response.error));
            return;
          }

          this.messages.push(_botMessage(response.text));
        })
        .catch((error) => {
          console.error("Error fetching data:", error);

          this.messages.push(_errorMessage("Something went wrong :("));
        })
        .finally(() => {
          this.$nextTick(this._scrollToEnd);
          this.isDisabled = false;
        });
    },

    sendMessage() {
      if (this.isDisabled) {
        return;
      }
      this.userInput = this.userInput.trim();
      if (this.userInput !== "") {
        this.isDisabled = true;

        const userMessage = _userMessage(this.userInput);
        this.userInput = "";
        this.messages.push(userMessage);

        this._handleMessageResponse(_chatRequest(userMessage));
      }
    },
    _scrollToEnd: function () {
      const container = this.$refs.chatMessages;
      container.scrollTop = container.scrollHeight;
    },
  },
}).mount("#app");

function _userMessage(text) {
  return _message(text, false);
}

function _botMessage(text) {
  return _message(text, true);
}

function _errorMessage(text) {
  return _message(`ERROR: ${text}`, true);
}

function _message(text, isBot) {
  return { text: text, isBot: isBot, id: Date.now() };
}

function _startChatRequest() {
  return fetch("/startchat", {
    method: "GET",
  }).then((response) => response.json());
}

function _chatRequest(userMessage) {
  return fetch("/chat", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(userMessage),
  }).then((response) => response.json());
}

function _fakeChatRequest(userMessage) {
  return new Promise((resolve, reject) =>
    setTimeout(() => {
      if (_rand(2) == 0) {
        reject("error");
        return;
      }
      resolve({
        id: Date.now(),
        text: `you send me this message: ${userMessage.text}`,
        isBot: true,
      });
    }, 1000)
  );
}

function _rand(max) {
  return Math.floor(Math.random() * max);
}

function _randomString(n) {
  chars =
    "ABCDEFGHIJKLMNOPQRSTUVWXYZ" + "abcdefghijklmnopqrstuvwxyz" + "0123456789";
  buf = "";
  for (let i = 0; i < n; i++) {
    buf += chars.charAt(_rand(chars.length));
  }
  return buf;
}
