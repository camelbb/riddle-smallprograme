//app.js
App({
  globalData: {
    score: 0,
    currentQuestionIndex: 0,
    riddles: [],
    currentTheme: ''
  },
  onLaunch: function () {
    // 初始化全局数据
    this.globalData.score = 0;
  }
});