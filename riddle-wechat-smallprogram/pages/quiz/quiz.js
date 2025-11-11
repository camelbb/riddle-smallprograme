// quiz.js
const app = getApp();

Page({
    data: {
        currentRiddle: {},
        userAnswer: '',
        isCorrect: null, // null: 未提交, true: 正确, false: 错误
        currentIndex: 0,
        totalCount: 0,
        score: 0,
        showHint: false,
        hintText: '',
        submitDisabled: false // 提交按钮禁用状态
    },

    // 每次页面显示时都会触发此方法
    onShow: function () {
        // 重置状态
        this.resetQuizState();
        // 重新请求接口加载数据
        this.generateRiddles(app.globalData.currentThemeId);
    },
  
    // 重置测验状态
    resetQuizState: function() {
        // 重置全局状态
        app.globalData.currentQuestionIndex = 0;
        app.globalData.score = 0;
        // 重置页面状态
        this.setData({
            userAnswer: '',
            isCorrect: null,
            showHint: false,
            hintText: '',
            submitDisabled: false
        });
    },

    // 生成谜语数据（从接口获取）
    generateRiddles: function (themeId) {
        wx.showLoading({
            title: '加载中...',
        });
      
        // 从接口获取谜语数据（使用云容器调用接口）
        wx.cloud.callContainer({
            ...app.globalData.CLOUD_CONTAINER_CONFIG,
            path: "/api/riddles/rank",
            method: "GET",
            data: {
                riddle_type: themeId, // 必填参数，对应谜语类型
                count: 5 // 默认返回5条谜语
            },
            success: (res) => {
                let riddles = [];
                if (res.data && res.data.data && Array.isArray(res.data.data.list)) {
                    riddles = res.data.data.list.map(item => ({
                        question: item.riddle,
                        answer: item.answer
                    }));
                } else {
                    wx.showToast({
                        title: '获取谜语失败',
                        icon: 'none'
                    });
                }
                
                // 保存谜语数据到全局
                app.globalData.riddles = riddles;
                // 数据加载完成后更新页面数据并渲染第一个谜语
                this.updatePageDataAndRender();
            },

            fail: () => {
                // 如果请求失败，使用默认数据
                wx.showToast({
                    title: '网络请求失败',
                    icon: 'none'
                });
                // 数据加载完成后更新页面数据并渲染第一个谜语
                this.updatePageDataAndRender();
            },

            complete: () => {
                wx.hideLoading();
            }
        });
    },
  
    // 更新页面数据并渲染
    updatePageDataAndRender: function() {
        const riddles = app.globalData.riddles || [];
        const currentQuestionIndex = app.globalData.currentQuestionIndex || 0;
        
        // 确保currentQuestionIndex有效
        if (currentQuestionIndex >= riddles.length && riddles.length > 0) {
            app.globalData.currentQuestionIndex = 0;
        }

        // 更新页面数据
        this.setData({
            totalCount: riddles.length,
            currentIndex: app.globalData.currentQuestionIndex,
            currentTheme: app.globalData.currentTheme || '未知主题',
            score: app.globalData.score || 0
        });

        // 加载当前谜语
        this.loadCurrentRiddle();
    },
  
    // 加载当前谜语
    loadCurrentRiddle: function () {
        const riddles = app.globalData.riddles || [];
        let currentIndex = app.globalData.currentQuestionIndex || 0;
        
        // 确保索引有效，直接使用第一个谜题
        if (!riddles || riddles.length === 0) {
            this.setData({
                currentRiddle: { question: '默认谜题', answer: '默认答案' },
                userAnswer: '',
                isCorrect: null,
                showHint: false,
                hintText: ''
            });
            return;
        }
        
        // 确保索引在有效范围内，直接显示第一个谜题
        currentIndex = Math.max(0, Math.min(currentIndex, riddles.length - 1));
        app.globalData.currentQuestionIndex = currentIndex;
        // 直接显示第一个谜题
        if (riddles && riddles.length > 0) {
            this.setData({
                currentRiddle: riddles[currentIndex],
                userAnswer: '',
                isCorrect: null,
                showHint: false,
                hintText: '',
                currentIndex: currentIndex, // 确保页面上显示的索引正确
                submitDisabled: false // 切换题目后重新启用提交按钮
            });
        }
    },

    // 输入答案
    inputAnswer: function (e) {
        this.setData({
            userAnswer: e.detail.value
        });
    },

    // 语音播放题目
    playQuestion: function () {
        const question = this.data.currentRiddle.question;
        // 直接显示文字题目，避免语音API调用可能带来的错误
        this.showTextQuestion(question);
    },
  
    // 显示文字题目（备用方案）
    showTextQuestion: function (question) {
        wx.showModal({
            title: '题目',
            content: question,
            showCancel: false
        });
    },

    // 提交答案
    submitAnswer: function () {
        // 如果按钮已禁用，则直接返回
        if (this.data.submitDisabled) {
            return;
        }
        const userAnswer = this.data.userAnswer.trim();
        const correctAnswer = this.data.currentRiddle.answer;
        if (!userAnswer) {
            wx.showToast({
                title: '请输入答案',
                icon: 'none'
            });
            return;
        }
        
        // 简单的答案验证逻辑，可以根据实际需求调整
        const isCorrect = userAnswer === correctAnswer || 
                        userAnswer.includes(correctAnswer) || 
                        correctAnswer.includes(userAnswer);
        
        this.setData({
            isCorrect: isCorrect,
            submitDisabled: true // 提交后禁用按钮
        });
        
        // 如果答对了，增加分数
        if (isCorrect) {
            app.globalData.score += 1;
            this.setData({
                score: app.globalData.score
            });
            wx.showToast({
                title: '恭喜你，答对了！',
                icon: 'success'
            });
        } else {
            // 显示正确答案
            this.setData({
                showHint: true,
                hintText: '正确答案是：' + correctAnswer
            });
            wx.showToast({
                title: '答错了，再试试吧',
                icon: 'none'
            });
        }
  },

    // 上一题
    prevQuestion: function () {
        // 添加边界检查，确保riddles数组存在且不为空
        const riddles = app.globalData.riddles || [];
        if (riddles.length === 0) {
            wx.showToast({
                title: '暂无题目',
                icon: 'none'
            });
            return;
        }
        if (app.globalData.currentQuestionIndex > 0) {
            app.globalData.currentQuestionIndex -= 1;
            this.setData({
                currentIndex: app.globalData.currentQuestionIndex
            });
            this.loadCurrentRiddle();
        } else {
            wx.showToast({
                title: '已经是第一题了',
                icon: 'none'
            });
        }
    },

    // 下一题
    nextQuestion: function () {
        if (app.globalData.currentQuestionIndex < app.globalData.riddles.length - 1) {
        app.globalData.currentQuestionIndex += 1;
        this.setData({
            currentIndex: app.globalData.currentQuestionIndex
        });
        this.loadCurrentRiddle();
        } else {
        wx.showModal({
            title: '游戏结束',
            content: '恭喜你完成了所有题目！你的得分是：' + this.data.score,
            showCancel: false,
            success: res => {
            if (res.confirm) {
                wx.navigateBack();
            }
            }
        });
        }
    },

    // 返回首页
    backToHome: function () {
        wx.switchTab({
        url: '/pages/index/index'
        });
    },

    // 分享给朋友
    onShareAppMessage: function () {
        return {
        title: '儿童谜语猜猜猜 - ' + this.data.currentTheme + '主题',
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
        title: '我在玩儿童谜语猜猜猜，快来一起猜谜语吧！',
        query: 'theme=' + this.data.currentTheme,
        imageUrl: '/images/quiz.png'
        };
    }
    
});