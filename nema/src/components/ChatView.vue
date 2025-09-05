<template>
  <div class="app-layout">
    <aside class="sidebar">
      <div class="sidebar-header">
        <div class="user-info">
          <span>👨‍🔬 科研助手</span>
        </div>
      </div>
      <ul class="menu">
        <li @click="clearChat" :class="{active: activeMenu === 'clear'}">
          <span class="icon">🧹</span>
          <span class="text">清除对话</span>
        </li>
        <li @click="toggleHistory" :class="{active: activeMenu === 'history'}">
          <span class="icon">📜</span>
          <span class="text">对话历史</span>
        </li>
        <li @click="triggerUpload" :class="{active: activeMenu === 'upload'}">
          <span class="icon">🖼️</span>
          <span class="text">上传图片</span>
        </li>
        <li @click="clearAllHistory" :class="{active: activeMenu === 'clearAll'}">
  <span class="icon">🗑️</span>
  <span class="text">清空历史</span>
</li>
      </ul>

      <div v-if="showHistory" class="history-panel">
        <div class="panel-header">
          <h3>历史记录</h3>
          <button @click="toggleHistory" class="close-btn">×</button>
        </div>
        <div class="history-list">
          <div v-for="(record, idx) in history" :key="idx"
               class="history-item"
               @click="loadHistory(idx)"
               :class="{selected: selectedHistory === idx}">
            <div class="history-title">{{ record.title || "未命名对话" }}</div>
            <div class="history-preview">{{ record.preview }}</div>
            <div class="history-time">{{ formatTime(record.time) }}</div>
          </div>
        </div>
      </div>
    </aside>

    <main class="main-content">
      <header class="chat-header">
        <h1>线虫分析系统</h1>
        <div class="upload-status" v-if="uploading">
          <span class="spinner"></span>
          上传中...
        </div>
      </header>

      <div class="chat-container">
        <div id="chat" class="chat-box">
          <div v-for="(msg, index) in messages" :key="index" class="message" :class="msg.sender">
            <div v-if="msg.sender === 'user' && msg.imageUrl" class="message-image">
              <img :src="msg.imageUrl" alt="上传的图片" @click="showFullImage(msg.imageUrl)"/>
              <div class="image-caption" v-if="msg.text">{{ msg.text }}</div>
            </div>
            <div v-else class="message-content" v-html="msg.text"></div>
          </div>
        </div>

        <div class="input-area">
          <div class="image-preview" v-if="tempImageUrl">
            <img :src="tempImageUrl" alt="待发送图片"/>
            <button @click="removeImage" class="remove-btn">×</button>
          </div>
          <form @submit.prevent="sendMessage" class="message-form">
            <input
              v-model="userInput"
              type="text"
              placeholder="请输入关于线虫的问题..."
              :disabled="uploading"
              @keydown.enter.exact.prevent="sendMessage"
            />
            <div class="action-buttons">
              <button type="button" @click="triggerUpload" class="upload-btn" :disabled="uploading">
                <span class="icon">📷</span>
              </button>
              <button type="submit" class="send-btn" :disabled="uploading || (!userInput && !tempImageUrl)">
                <span v-if="!uploading">发送</span>
                <span v-else class="spinner"></span>
              </button>
            </div>
            <input type="file" ref="fileInput" style="display: none" @change="uploadImage" accept="image/*"/>
          </form>
        </div>
      </div>
    </main>

    <div v-if="fullImageUrl" class="image-modal" @click="fullImageUrl = null">
      <div class="modal-content">
        <img :src="fullImageUrl" alt="全屏图片"/>
        <div class="image-meta">
          <a :href="fullImageUrl" target="_blank" download>下载原图</a>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { marked } from 'marked';
import DOMPurify from 'dompurify';

export default {
  name: 'ChatView',
  data() {
    return {
      userInput: '',
      messages: [],
      history: [],
      showHistory: false,
      activeMenu: null,
      selectedHistory: null,
      tempImageUrl: null,
      uploading: false,
      fullImageUrl: null
    };
  },
  created() {
    // 初始化一些示例历史记录
    this.history = [
    ];
  },
  methods: {
    appendMessage(text, sender, imageUrl = null) {
      const parsedText = sender === 'ai'
        ? DOMPurify.sanitize(marked.parse(text))
        : DOMPurify.sanitize(text);

      this.messages.push({
        text: parsedText,
        sender,
        imageUrl
      });

      this.$nextTick(() => {
        this.scrollToBottom();
      });
    },

scrollToBottom() {
  this.$nextTick(() => {
    const chatBox = this.$el.querySelector('#chat');
    if (chatBox) {
      // 检查是否已经接近底部（50px容差范围）
      const isNearBottom = chatBox.scrollHeight - chatBox.scrollTop - chatBox.clientHeight < 50;

      // 只有当前在底部附近时才自动滚动
      if (isNearBottom) {
        chatBox.scrollTo({
          top: chatBox.scrollHeight,
          behavior: 'smooth'
        });
      }
    }
  });
},

    async sendMessage() {
      const prompt = this.userInput.trim();
      if (!prompt && !this.tempImageUrl) return;

      // 如果有图片，先发送图片消息
      if (this.tempImageUrl) {
        this.appendMessage('', 'user', this.tempImageUrl);
        if (prompt) {
          this.appendMessage(prompt, 'user');
        }
      } else {
        this.appendMessage(prompt, 'user');
      }

      this.userInput = '';

      const aiMessage = {
        text: DOMPurify.sanitize(marked.parse('<div class="thinking">正在分析中...</div>')),
        sender: 'ai'
      };
      this.messages.push(aiMessage);
      this.scrollToBottom();

      try {
        const response = await fetch('http://127.0.0.1:5000/api', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            user_input: prompt,
            image_url: this.tempImageUrl
          })
        });

        if (!response.ok) throw new Error('网络错误');

        const reader = response.body.getReader();
        const decoder = new TextDecoder('utf-8');
        let result = '';

        const read = () => {
          reader.read().then(({ done, value }) => {
            if (done) {
              this.saveToHistory(prompt);
              this.tempImageUrl = null;
              return;
            }

            const chunk = decoder.decode(value, { stream: true });
            chunk.split('\n').forEach(line => {
              if (line.startsWith('data:')) {
                const data = line.replace(/^data:\s*/, '');
                if (data === '[DONE]') return;
                result += data;
                aiMessage.text = DOMPurify.sanitize(marked.parse(result));
                this.scrollToBottom();
              }
            });
            read();
          });
        };

        read();
      } catch (error) {
        console.error(error);
        aiMessage.text = DOMPurify.sanitize(marked.parse('❌ **请求失败，请重试**'));
        this.scrollToBottom();
      }
    },

    saveToHistory(prompt) {
      this.history.unshift({
        title: prompt.slice(0, 30) || "图片分析",
        preview: this.messages.slice(-1)[0].text.replace(/<[^>]*>/g, "").slice(0, 50),
        time: new Date(),
        messages: [...this.messages]
      });

      // 限制历史记录数量
      if (this.history.length > 10) {
        this.history.pop();
      }
    },

    clearChat() {
      this.activeMenu = 'clear';
      this.messages = [];
      this.tempImageUrl = null;
    },

    toggleHistory() {
      this.activeMenu = this.showHistory ? null : 'history';
      this.showHistory = !this.showHistory;
      this.selectedHistory = null;
    },

    loadHistory(index) {
      this.selectedHistory = index;
      this.messages = [...this.history[index].messages];
      this.showHistory = false;
      this.activeMenu = null;
      this.$nextTick(() => {
        this.scrollToBottom();
      });
    },

    triggerUpload() {
      this.activeMenu = 'upload';
      this.$refs.fileInput.click();
    },
clearAllHistory() {
  if (confirm('确定要清空所有历史记录吗？此操作不可恢复！')) {
    // 清空前端历史
    this.history = [];

    // 调用后端API清空历史
    fetch('http://127.0.0.1:5000/clear-history', {
      method: 'POST'
    }).catch(err => {
      console.error('清空历史记录失败:', err);
    });

    this.showHistory = false;
    this.activeMenu = null;
  }
},
    async uploadImage(event) {
      const file = event.target.files[0];
      if (!file) return;
  // 添加图片大小限制（5MB）
  const MAX_SIZE = 5 * 1024 * 1024; // 5MB
  if (file.size > MAX_SIZE) {
    this.appendMessage('❌ 图片大小超过5MB限制，请上传更小的图片', 'ai');
    event.target.value = ''; // 清除文件选择
    return;
  }
      this.uploading = true;
      this.appendMessage('📷 正在上传图像：' + file.name, 'user');
      this.scrollToBottom();

      try {
        const formData = new FormData();
        formData.append('file', file);
        formData.append('filename', file.name);

        const uploadRes = await fetch('http://127.0.0.1:5000/upload-to-oss', {
          method: 'POST',
          body: formData
        });

        if (!uploadRes.ok) throw new Error('上传失败');

        const result = await uploadRes.json();
        this.tempImageUrl = result.url;

        this.appendMessage('✅ 图像已上传成功，请输入问题后发送', 'ai');
      } catch (err) {
        console.error(err);
        this.appendMessage('❌ 图像上传失败，请重试', 'ai');
      } finally {
        this.uploading = false;
        event.target.value = ''; // 重置文件输入
      }
    },

    removeImage() {
      this.tempImageUrl = null;
    },

    showFullImage(url) {
      this.fullImageUrl = url;
    },

    formatTime(date) {
      if (!date) return '';
      const now = new Date();
      const diff = now - date;

      if (diff < 60000) return '刚刚';
      if (diff < 3600000) return `${Math.floor(diff / 60000)}分钟前`;
      if (diff < 86400000) return `${Math.floor(diff / 3600000)}小时前`;

      return date.toLocaleDateString();
    }
  }
};
</script>

<style scoped>
/* 基础样式重置 */
* {
  box-sizing: border-box;
  margin: 0;
  padding: 0;
}

:root {
  --primary-color: #42b983;
  --secondary-color: #35495e;
  --accent-color: #ff7e67;
  --light-bg: #f8f9fa;
  --dark-bg: #2c3e50;
  --text-color: #333;
  --text-light: #777;
  --border-radius: 8px;
  --box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
}

body {
  font-family: 'Segoe UI', 'PingFang SC', 'Microsoft YaHei', sans-serif;
  color: var(--text-color);
  line-height: 1.6;
}

.app-layout {
  display: flex;
  min-height: 100vh;
  background-color: var(--light-bg);
}

/* 侧边栏样式 */
.sidebar {
  width: 280px;
  background-color: var(--dark-bg);
  color: #101010;
  display: flex;
  flex-direction: column;
  transition: all 0.3s ease;
}

.sidebar-header {
  padding: 20px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.sidebar h2 {
  font-size: 1.5rem;
  margin-bottom: 10px;
  color: black;
}

.user-info {
  display: flex;
  align-items: center;
  font-size: 0.9rem;
  opacity: 0.8;
}

.menu {
  list-style: none;
  padding: 10px 0;
  flex-grow: 1;
}

.menu li {
  padding: 12px 20px;
  cursor: pointer;
  display: flex;
  align-items: center;
  transition: all 0.2s;
}

.menu li:hover {
  background-color: rgba(255, 255, 255, 0.1);
}

.menu li.active {
  background-color: rgba(255, 255, 255, 0.2);
}

.menu .icon {
  margin-right: 12px;
  font-size: 1.2rem;
}

.menu .text {
  font-size: 1rem;
}

/* 历史记录面板 */
.history-panel {
  background-color: rgba(0, 0, 0, 0.2);
  padding: 15px;
  border-top: 1px solid rgba(255, 255, 255, 0.1);
}

.panel-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 10px;
}

.panel-header h3 {
  font-size: 1.1rem;
}

.close-btn {
  background: none;
  border: none;
  color: #00fd35;
  font-size: 1.5rem;
  cursor: pointer;
  opacity: 0.7;
}

.history-list {
  max-height: 400px;
  overflow-y: auto;
}

.history-item {
  padding: 12px;
  margin-bottom: 8px;
  background-color: rgba(255, 255, 255, 0.05);
  border-radius: var(--border-radius);
  cursor: pointer;
  transition: all 0.2s;
}

.history-item:hover {
  background-color: rgba(255, 255, 255, 0.1);
}

.history-item.selected {
  background-color: var(--primary-color);
}

.history-title {
  font-weight: 500;
  margin-bottom: 4px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.history-preview {
  font-size: 0.8rem;
  opacity: 0.8;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
/* 自定义滚动条 */
.chat-box::-webkit-scrollbar {
  width: 8px;
}

.chat-box::-webkit-scrollbar-track {
  background: #f1f1f1;
  border-radius: 4px;
}

.chat-box::-webkit-scrollbar-thumb {
  background: #c1c1c1;
  border-radius: 4px;
}

.chat-box::-webkit-scrollbar-thumb:hover {
  background: #a8a8a8;
}
.history-time {
  font-size: 0.7rem;
  opacity: 0.6;
  margin-top: 4px;
}

/* 主内容区域 */
.main-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.chat-header {
  padding: 20px;
  background-color: white;
  box-shadow: var(--box-shadow);
  z-index: 10;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.chat-header h1 {
  font-size: 1.8rem;
  color: var(--secondary-color);
  margin: 0;
  font-weight: 600;
}

.upload-status {
  display: flex;
  align-items: center;
  font-size: 0.9rem;
  color: var(--text-light);
}

.spinner {
  display: inline-block;
  width: 16px;
  height: 16px;
  border: 2px solid rgba(0, 0, 0, 0.1);
  border-radius: 50%;
  border-top-color: var(--primary-color);
  animation: spin 1s ease-in-out infinite;
  margin-right: 8px;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.chat-container {
  flex: 1;
  display: flex;
  flex-direction: column;
  padding: 20px;
  overflow: hidden;
}

.chat-box {
  flex: 1;
  overflow-y: auto;
  padding: 15px;
  background-color: white;
  border-radius: var(--border-radius);
  box-shadow: var(--box-shadow);
  margin-bottom: 20px;
  display: flex;
  flex-direction: column;
}

.message {
  margin-bottom: 15px;
  max-width: 80%;
  position: relative;
}

.message.user {
  align-self: flex-end;
}

.message.ai {
  align-self: flex-start;
}

.message-content {
  padding: 12px 16px;
  border-radius: 18px;
  line-height: 1.5;
}

.message.user .message-content {
  background-color: #e3f2fd;
  color: #0d47a1;
  border-top-right-radius: 4px;
}

.message.ai .message-content {
  background-color: #f1f8e9;
  color: #2e7d32;
  border-top-left-radius: 4px;
}

.message-image {
  max-width: 300px;
  margin-bottom: 8px;
}

.message-image img {
  max-width: 100%;
  border-radius: var(--border-radius);
  cursor: zoom-in;
  box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1);
  transition: transform 0.2s;
}

.message-image img:hover {
  transform: scale(1.02);
}

.image-caption {
  font-size: 0.9rem;
  color: var(--text-light);
  margin-top: 5px;
}

.thinking {
  color: var(--text-light);
  font-style: italic;
}

/* 输入区域 */
.input-area {
  background-color: white;
  border-radius: var(--border-radius);
  box-shadow: var(--box-shadow);
  padding: 15px;
}

.image-preview {
  position: relative;
  margin-bottom: 15px;
  max-width: 200px;
}

.image-preview img {
  max-width: 100%;
  border-radius: var(--border-radius);
}

.remove-btn {
  position: absolute;
  top: -10px;
  right: -10px;
  width: 24px;
  height: 24px;
  background-color: var(--accent-color);
  color: white;
  border: none;
  border-radius: 50%;
  font-size: 14px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
}

.message-form {
  display: flex;
  align-items: center;
}

.message-form input {
  flex: 1;
  padding: 12px 15px;
  border: 1px solid #ddd;
  border-radius: var(--border-radius);
  font-size: 1rem;
  outline: none;
  transition: border 0.2s;
}

.message-form input:focus {
  border-color: var(--primary-color);
}

.action-buttons {
  display: flex;
  margin-left: 10px;
}

.upload-btn, .send-btn {
  padding: 12px 20px;
  border: none;
  border-radius: var(--border-radius);
  cursor: pointer;
  font-size: 1rem;
  transition: all 0.2s;
  display: flex;
  align-items: center;
  justify-content: center;
}

.upload-btn {
  background-color: #f0f0f0;
  color: var(--secondary-color);
  margin-right: 8px;
  width: 48px;
}

.upload-btn:hover {
  background-color: #e0e0e0;
}

.send-btn {
  background-color: var(--primary-color);
  color: #101010;
  min-width: 80px;
}

.send-btn:hover {
  background-color: #369d6d;
}

.send-btn:disabled {
  background-color: #cccccc;
  cursor: not-allowed;
}

/* 图片模态框 */
.image-modal {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0, 0, 0, 0.8);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  cursor: zoom-out;
}

.modal-content {
  max-width: 90%;
  max-height: 90%;
  position: relative;
}

.modal-content img {
  max-width: 100%;
  max-height: 80vh;
  border-radius: var(--border-radius);
  box-shadow: 0 5px 20px rgba(0, 0, 0, 0.3);
}

.image-meta {
  text-align: center;
  margin-top: 15px;
}

.image-meta a {
  color: white;
  text-decoration: none;
  background-color: var(--primary-color);
  padding: 8px 15px;
  border-radius: var(--border-radius);
  display: inline-block;
}

.image-meta a:hover {
  background-color: #369d6d;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .app-layout {
    flex-direction: column;
  }

  .sidebar {
    width: 100%;
    height: auto;
  }

  .chat-box {
    max-height: 60vh;
  }

  .message {
    max-width: 90%;
  }
}
</style>