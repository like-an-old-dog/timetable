<template>
	<view class="container">
		<view class="header">
			<view class="logo">
				<text class="logo-text">广油</text>
			</view>
			<text class="title">课程成绩查询系统</text>
		</view>
		
		<view class="content">
			<view class="welcome-card">
				<text class="welcome-text">欢迎使用课程成绩查询系统</text>
				<text class="sub-text">快速查看您的课程表和成绩信息</text>
			</view>
			
			<view class="menu-list">
				<view class="menu-item" @click="goToTimetable">
					<view class="menu-icon timetable-icon">
						<text class="icon">📅</text>
					</view>
					<view class="menu-info">
						<text class="menu-title">查看课表</text>
						<text class="menu-desc">查看每周课程安排</text>
					</view>
					<text class="arrow">›</text>
				</view>
				
				<view class="menu-item" @click="goToScore">
					<view class="menu-icon score-icon">
						<text class="icon">📊</text>
					</view>
					<view class="menu-info">
						<text class="menu-title">查看成绩</text>
						<text class="menu-desc">查看学期成绩和绩点</text>
					</view>
					<text class="arrow">›</text>
				</view>
			</view>
		</view>
		
		<view class="footer">
			<text class="footer-text">© 2024 广油课程成绩查询系统</text>
		</view>
	</view>
</template>

<script>
export default {
	data() {
		return {
			
		}
	},
	methods: {
		goToTimetable() {
			uni.navigateTo({
				url: '/pages/timetable/index'
			})
		},
		goToScore() {
			uni.navigateTo({
				url: '/pages/score/index'
			})
		}
	}
}
</script>

<style scoped>
.container {
	min-height: 100vh;
	background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
	display: flex;
	flex-direction: column;
}

.header {
	padding: 80rpx 40rpx 40rpx;
	display: flex;
	align-items: center;
	gap: 20rpx;
}

.logo {
	width: 100rpx;
	height: 100rpx;
	background: rgba(255, 255, 255, 0.2);
	border-radius: 20rpx;
	display: flex;
	align-items: center;
	justify-content: center;
	backdrop-filter: blur(10rpx);
}

.logo-text {
	font-size: 40rpx;
	font-weight: bold;
	color: #ffffff;
}

.title {
	font-size: 48rpx;
	font-weight: bold;
	color: #ffffff;
	text-shadow: 0 4rpx 8rpx rgba(0, 0, 0, 0.1);
}

.content {
	flex: 1;
	padding: 40rpx;
	display: flex;
	flex-direction: column;
	gap: 40rpx;
}

.welcome-card {
	background: rgba(255, 255, 255, 0.15);
	border-radius: 24rpx;
	padding: 40rpx;
	backdrop-filter: blur(10rpx);
	border: 2rpx solid rgba(255, 255, 255, 0.2);
}

.welcome-text {
	display: block;
	font-size: 36rpx;
	font-weight: bold;
	color: #ffffff;
	margin-bottom: 16rpx;
}

.sub-text {
	display: block;
	font-size: 28rpx;
	color: rgba(255, 255, 255, 0.8);
}

.menu-list {
	display: flex;
	flex-direction: column;
	gap: 24rpx;
}

.menu-item {
	background: #ffffff;
	border-radius: 24rpx;
	padding: 32rpx;
	display: flex;
	align-items: center;
	gap: 24rpx;
	box-shadow: 0 8rpx 24rpx rgba(0, 0, 0, 0.1);
	transition: all 0.3s ease;
}

.menu-item:active {
	transform: scale(0.98);
	box-shadow: 0 4rpx 12rpx rgba(0, 0, 0, 0.15);
}

.menu-icon {
	width: 100rpx;
	height: 100rpx;
	border-radius: 20rpx;
	display: flex;
	align-items: center;
	justify-content: center;
}

.timetable-icon {
	background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.score-icon {
	background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
}

.icon {
	font-size: 48rpx;
}

.menu-info {
	flex: 1;
	display: flex;
	flex-direction: column;
	gap: 8rpx;
}

.menu-title {
	font-size: 32rpx;
	font-weight: bold;
	color: #333333;
}

.menu-desc {
	font-size: 24rpx;
	color: #999999;
}

.arrow {
	font-size: 60rpx;
	color: #cccccc;
	font-weight: 300;
}

.footer {
	padding: 40rpx;
	text-align: center;
}

.footer-text {
	font-size: 24rpx;
	color: rgba(255, 255, 255, 0.6);
}
</style>
