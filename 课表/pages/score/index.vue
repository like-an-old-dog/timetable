<template>
	<view class="container">
		<view class="header">
			<text class="title">成绩查询</text>
		</view>
		
		<view class="control-panel">
			<view class="control-row">
				<view class="control-item">
					<text class="label">年份</text>
					<picker mode="selector" :range="years" @change="onYearChange">
						<view class="picker">
							<text>{{ year }}</text>
							<text class="arrow">▼</text>
						</view>
					</picker>
				</view>
				
				<view class="control-item">
					<text class="label">学期</text>
					<picker mode="selector" :range="terms" @change="onTermChange">
						<view class="picker">
							<text>{{ term }}</text>
							<text class="arrow">▼</text>
						</view>
					</picker>
				</view>
			</view>
			
			<button class="query-btn" @click="queryScores" :disabled="loading">
				<text v-if="!loading">查询成绩</text>
				<text v-else>查询中...</text>
			</button>
		</view>
		
		<view class="gpa-card" v-if="scores.length > 0">
			<view class="gpa-info">
				<text class="gpa-label">平均绩点</text>
				<text class="gpa-value">{{ averageGPA }}</text>
			</view>
			<view class="gpa-detail">
				<view class="detail-item">
					<text class="detail-label">总学分</text>
					<text class="detail-value">{{ totalCredits }}</text>
				</view>
				<view class="detail-item">
					<text class="detail-label">课程数</text>
					<text class="detail-value">{{ scores.length }}</text>
				</view>
			</view>
		</view>
		
		<scroll-view class="score-list" scroll-y v-if="scores.length > 0">
			<view class="score-item" v-for="(score, index) in scores" :key="index">
				<view class="score-header">
					<view class="course-info">
						<text class="course-name">{{ score.kcmc }}</text>
						<text class="course-type">{{ score.kcdlmc }}</text>
					</view>
					<view class="score-value" :class="getScoreClass(score.zcj)">
						<text class="score-number">{{ score.zcj }}</text>
						<text class="score-label">分</text>
					</view>
				</view>
				<view class="score-detail">
					<view class="detail-row">
						<text class="detail-label">学分</text>
						<text class="detail-value">{{ score.xf }}</text>
					</view>
					<view class="detail-row">
						<text class="detail-label">绩点</text>
						<text class="detail-value">{{ score.cjjd }}</text>
					</view>
					<view class="detail-row">
						<text class="detail-label">序号</text>
						<text class="detail-value">{{ index + 1 }}</text>
					</view>
				</view>
			</view>
		</scroll-view>
		
		<view class="empty-state" v-if="scores.length === 0 && !loading">
			<text class="empty-icon">📊</text>
			<text class="empty-text">暂无成绩数据</text>
			<text class="empty-hint">请选择学期并查询成绩</text>
		</view>
	</view>
</template>

<script>
import api from '@/utils/api.js'

export default {
	data() {
		return {
			years: [],
			terms: ['1', '2'],
			year: '2024',
			term: '2',
			scores: [],
			loading: false,
			totalCredits: 0,
			averageGPA: '--'
		}
	},
	onLoad() {
		this.initData()
	},
	methods: {
		initData() {
			const currentYear = new Date().getFullYear()
			for (let i = currentYear - 5; i <= currentYear + 5; i++) {
				this.years.push(String(i))
			}
		},
		onYearChange(e) {
			this.year = this.years[e.detail.value]
		},
		onTermChange(e) {
			this.term = this.terms[e.detail.value]
		},
		async queryScores() {
			if (this.loading) return
			
			this.loading = true
			const semester = this.year + this.term.padStart(2, '0')
			
			try {
				await api.login()
				const scoreData = await api.getScoreData(semester)
				
				if (scoreData && scoreData.rows) {
					this.scores = scoreData.rows.sort((a, b) => {
						const gpaA = parseFloat(a.cjjd) || 0
						const gpaB = parseFloat(b.cjjd) || 0
						return gpaB - gpaA
					})
					
					this.calculateGPA()
					
					if (this.scores.length === 0) {
						uni.showToast({
							title: '未找到成绩数据',
							icon: 'none'
						})
					} else {
						uni.showToast({
							title: '查询成功',
							icon: 'success'
						})
					}
				} else {
					this.scores = []
					uni.showToast({
						title: '未找到成绩数据',
						icon: 'none'
					})
				}
			} catch (error) {
				console.error('查询失败:', error)
				uni.showToast({
					title: error.message || '查询失败',
					icon: 'none'
				})
			} finally {
				this.loading = false
			}
		},
		calculateGPA() {
			let totalCredits = 0
			let totalGPA = 0
			
			for (const score of this.scores) {
				const credits = parseFloat(score.xf) || 0
				const gpa = parseFloat(score.cjjd) || 0
				totalCredits += credits
				totalGPA += gpa * credits
			}
			
			this.totalCredits = totalCredits.toFixed(1)
			
			if (totalCredits > 0) {
				this.averageGPA = (totalGPA / totalCredits).toFixed(2)
			} else {
				this.averageGPA = '--'
			}
		},
		getScoreClass(score) {
			const scoreNum = parseFloat(score)
			if (scoreNum >= 90) return 'score-excellent'
			if (scoreNum >= 80) return 'score-good'
			if (scoreNum >= 70) return 'score-medium'
			if (scoreNum >= 60) return 'score-pass'
			return 'score-fail'
		}
	}
}
</script>

<style scoped>
.container {
	min-height: 100vh;
	background: #f5f7fa;
	display: flex;
	flex-direction: column;
}

.header {
	background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
	padding: 40rpx;
}

.title {
	font-size: 48rpx;
	font-weight: bold;
	color: #ffffff;
}

.control-panel {
	background: #ffffff;
	padding: 32rpx;
	margin: 24rpx;
	border-radius: 24rpx;
	box-shadow: 0 4rpx 16rpx rgba(0, 0, 0, 0.08);
}

.control-row {
	display: flex;
	justify-content: space-between;
	gap: 16rpx;
	margin-bottom: 24rpx;
}

.control-item {
	flex: 1;
	display: flex;
	flex-direction: column;
	gap: 12rpx;
}

.label {
	font-size: 24rpx;
	color: #666666;
}

.picker {
	background: #f5f7fa;
	border-radius: 12rpx;
	padding: 20rpx 24rpx;
	display: flex;
	justify-content: space-between;
	align-items: center;
}

.picker text:first-child {
	font-size: 28rpx;
	color: #333333;
}

.arrow {
	font-size: 20rpx;
	color: #999999;
}

.query-btn {
	background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
	color: #ffffff;
	border-radius: 12rpx;
	padding: 24rpx;
	font-size: 32rpx;
	font-weight: bold;
	border: none;
}

.query-btn[disabled] {
	opacity: 0.6;
}

.gpa-card {
	background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
	margin: 0 24rpx 24rpx;
	padding: 32rpx;
	border-radius: 24rpx;
	box-shadow: 0 4rpx 16rpx rgba(0, 0, 0, 0.08);
}

.gpa-info {
	text-align: center;
	margin-bottom: 24rpx;
}

.gpa-label {
	display: block;
	font-size: 24rpx;
	color: rgba(255, 255, 255, 0.8);
	margin-bottom: 8rpx;
}

.gpa-value {
	display: block;
	font-size: 64rpx;
	font-weight: bold;
	color: #ffffff;
}

.gpa-detail {
	display: flex;
	justify-content: space-around;
	padding-top: 24rpx;
	border-top: 2rpx solid rgba(255, 255, 255, 0.2);
}

.detail-item {
	text-align: center;
}

.detail-label {
	display: block;
	font-size: 24rpx;
	color: rgba(255, 255, 255, 0.8);
	margin-bottom: 8rpx;
}

.detail-value {
	display: block;
	font-size: 32rpx;
	font-weight: bold;
	color: #ffffff;
}

.score-list {
	flex: 1;
	margin: 0 24rpx 24rpx;
	display: flex;
	flex-direction: column;
	gap: 16rpx;
}

.score-item {
	background: #ffffff;
	border-radius: 16rpx;
	padding: 24rpx;
	box-shadow: 0 2rpx 8rpx rgba(0, 0, 0, 0.06);
}

.score-header {
	display: flex;
	justify-content: space-between;
	align-items: flex-start;
	margin-bottom: 16rpx;
}

.course-info {
	flex: 1;
	display: flex;
	flex-direction: column;
	gap: 8rpx;
}

.course-name {
	font-size: 28rpx;
	font-weight: bold;
	color: #333333;
}

.course-type {
	font-size: 22rpx;
	color: #999999;
}

.score-value {
	display: flex;
	align-items: baseline;
	gap: 4rpx;
}

.score-number {
	font-size: 48rpx;
	font-weight: bold;
}

.score-label {
	font-size: 20rpx;
}

.score-excellent .score-number {
	color: #52c41a;
}

.score-good .score-number {
	color: #1890ff;
}

.score-medium .score-number {
	color: #faad14;
}

.score-pass .score-number {
	color: #ff7a45;
}

.score-fail .score-number {
	color: #f5222d;
}

.score-detail {
	display: flex;
	justify-content: space-around;
	padding-top: 16rpx;
	border-top: 2rpx solid #f0f0f0;
}

.detail-row {
	display: flex;
	flex-direction: column;
	align-items: center;
	gap: 4rpx;
}

.detail-row .detail-label {
	font-size: 22rpx;
	color: #999999;
}

.detail-row .detail-value {
	font-size: 24rpx;
	color: #666666;
	font-weight: bold;
}

.empty-state {
	flex: 1;
	display: flex;
	flex-direction: column;
	align-items: center;
	justify-content: center;
	padding: 80rpx 40rpx;
}

.empty-icon {
	font-size: 120rpx;
	margin-bottom: 32rpx;
}

.empty-text {
	font-size: 32rpx;
	color: #333333;
	margin-bottom: 16rpx;
}

.empty-hint {
	font-size: 24rpx;
	color: #999999;
}
</style>
