import axios from "axios";

const api = axios.create({
  baseURL: "https://realstatechatbot.onrender.com", // your backend endpoint
});

export default api;



