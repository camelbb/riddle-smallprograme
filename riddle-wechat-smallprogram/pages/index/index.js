// index.js
const app = getApp();

// 定义云容器调用的公共配置，方便后续统一修改
app.globalData.CLOUD_CONTAINER_CONFIG = {
  config: {
    env: "prod-5grn5sv6c732c805"
  },
  header: {
    "X-WX-SERVICE": "riddle-smallprogram"
  }
};

// 定义默认主题数据（作为备份）
const DEFAULT_THEMES = [
    { name: '植物11', icon: 'plant.png', id: 1 },
    { name: '动物22', icon: 'animal.png', id: 2 },
    { name: '水果33', icon: 'fruit.png', id: 3 },
    { name: '蔬菜44', icon: 'vegetable.png', id: 4 },
    { name: '交通工具55', icon: 'transport.png', id: 5 },
    { name: '日常用品66', icon: 'daily.png', id: 6 }
];

// 初始化云函数容器
wx.cloud.init()

Page({
    data: {
        themes: [] // 初始为空，将在onLoad中从接口获取
    },
  
    // 页面加载时获取谜语类型数据
    onLoad: function() {
        this.fetchRiddleTypes();
    },
  
    // 从外部服务器获取谜语类型数据
    fetchRiddleTypes: function() {
        wx.showLoading({
            title: '加载主题中...',
        });
    
        wx.cloud.callContainer({
            ...app.globalData.CLOUD_CONTAINER_CONFIG,
            path: "/api/riddles/types",
            method: "GET",
            success: (res) => {
                let themes = [];
                
                // 检查接口返回的数据格式并转换
                if (res.data && res.data.data && Array.isArray(res.data.data.list)) {
                    // 根据接口返回的数据结构映射到主题列表
                    themes = res.data.data.list.map(item => {
                        return {
                            name: item.type,
                            icon: item.image,
                            id: item.id // 确保有ID
                        };
                    });
                    // 如果接口返回的数据为空数组，则使用默认主题
                    if (themes.length === 0) {
                        themes = DEFAULT_THEMES;
                    }
                } else {
                    // 如果接口数据格式不正确，使用默认主题
                    themes = DEFAULT_THEMES;
                }
                
                // 更新页面数据
                this.setData({
                    themes: themes
                });
            },

            fail: () => {
                // 如果请求失败，使用默认主题
                wx.showToast({
                    title: '获取主题失败，使用默认主题',
                    icon: 'none'
                });
                
                this.setData({
                    themes: DEFAULT_THEMES
                });
            },

            complete: () => {
                wx.hideLoading();
            }
        });
    },

    // 选择预设主题
    selectTheme: function (e) {
        const theme = e.currentTarget.dataset.theme;
        const themeId = e.currentTarget.dataset.themeid;
        this.startQuiz(theme, themeId);
    },

    // 开始猜谜游戏
    startQuiz: function (theme, themeId) {
        // 保存当前主题
        app.globalData.currentTheme = theme;
        app.globalData.currentThemeId = themeId;
        app.globalData.score = 0;
        app.globalData.currentQuestionIndex = 0;
        // 跳转到猜谜页面（由于是tabBar页面，使用switchTab）
        wx.switchTab({
        url: '/pages/quiz/quiz',
        success: () => {
            console.log('成功跳转到猜谜页面');
            // 可以在这里添加额外的页面跳转后处理逻辑

        }
        });
    },

    // 分享给朋友
    onShareAppMessage: function () {
        return {
        title: '儿童谜语猜猜猜 - 有趣的儿童谜语游戏',
        path: '/pages/index/index',
        imageUrl: '/images/quiz.png',
        success: function (res) {
            wx.showToast({
            title: '分享成功',
            icon: 'success'
            });
        }
        };
    },

    // 分享到朋友圈
    onShareTimeline: function () {
        return {
        title: '儿童谜语猜猜猜，一起来挑战有趣的谜语吧！',
        query: '',
        imageUrl: '/images/quiz.png'
        };
    }

});