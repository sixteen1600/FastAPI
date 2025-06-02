// firebaseConfig.js
import { initializeApp } from "https://www.gstatic.com/firebasejs/9.6.1/firebase-app.js";
import { getAuth } from "https://www.gstatic.com/firebasejs/9.6.1/firebase-auth.js";

// Firebase 設定（可依環境變數調整）
const firebaseConfig = {
    
};

// 初始化 Firebase App
const app = initializeApp(firebaseConfig);

// 匯出 Auth 物件
const auth = getAuth(app);

export { auth };
