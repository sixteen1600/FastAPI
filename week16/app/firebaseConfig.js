// firebaseConfig.js
import { initializeApp } from "https://www.gstatic.com/firebasejs/9.6.1/firebase-app.js";
import { getAuth } from "https://www.gstatic.com/firebasejs/9.6.1/firebase-auth.js";

// Firebase 設定（可依環境變數調整）
const firebaseConfig = {
    apiKey: "AIzaSyBeS4QmyFlY1kGk4wjJeEKA1OqZ9hsRw2k",
    authDomain: "project-4744833769401526445.firebaseapp.com",
    projectId: "project-4744833769401526445",
    storageBucket: "project-4744833769401526445.appspot.com",
    messagingSenderId: "942642616229",
    appId: "1:942642616229:web:1cd1a43ac9f56691d2ba4c"
};

// 初始化 Firebase App
const app = initializeApp(firebaseConfig);

// 匯出 Auth 物件
const auth = getAuth(app);

export { auth };
