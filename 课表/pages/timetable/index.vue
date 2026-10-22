<template>
	<view class="container">
		<view class="header">
			<text class="title">课程表</text>
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
				
				<view class="control-item">
					<text class="label">周数</text>
					<picker mode="selector" :range="weeks" @change="onWeekChange">
						<view class="picker">
							<text>第{{ currentWeek }}周</text>
							<text class="arrow">▼</text>
						</view>
					</picker>
				</view>
			</view>
			
			<button class="query-btn" @click="queryTimetable" :disabled="loading">
				<text v-if="!loading">查询课表</text>
				<text v-else>查询中...</text>
			</button>
		</view>
		
		<scroll-view class="table-container" scroll-y scroll-x>
			<view class="timetable">
				<view class="table-header">
					<view class="header-cell">节次</view>
					<view class="header-cell" v-for="day in days" :key="day">{{ day }}</view>
				</view>
				
				<view class="table-body">
					<view class="table-row" v-for="slot in timeSlots" :key="slot">
						<view class="cell cell-slot">{{ slot }}</view>
						<view class="cell" v-for="day in 7" :key="day">
							<view class="course-cell" v-if="getCourse(slot, day)">
								<text class="course-name">{{ getCourse(slot, day).name }}</text>
								<text class="course-location">{{ getCourse(slot, day).location }}</text>
								<text class="course-teacher">{{ getCourse(slot, day).teacher }}</text>
							</view>
						</view>
					</view>
				</view>
			</view>
		</scroll-view>
		
		<view class="empty-state" v-if="courses.length === 0 && !loading">
			<text class="empty-icon">📅</text>
			<text class="empty-text">暂无课程数据</text>
			<text class="empty-hint">请选择学期并查询课表</text>
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
			weeks: [],
			year: '2024',
			term: '1',
			currentWeek: 1,
			days: ['周一', '周二', '周三', '周四', '周五', '周六', '周日'],
			timeSlots: ['第1节', '第2节', '第3节', '第4节', '第5节', '第6节', '第7节', '第8节', '第9节', '第10节', '第11节', '第12节'],
			courses: [],
			loading: false
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
			for (let i = 1; i <= 20; i++) {
				this.weeks.push(i)
			}
		},
		onYearChange(e) {
			this.year = this.years[e.detail.value]
		},
		onTermChange(e) {
			this.term = this.terms[e.detail.value]
		},
		onWeekChange(e) {
			this.currentWeek = this.weeks[e.detail.value]
		},
		async queryTimetable() {
			if (this.loading) return
			
			this.loading = true
			const semester = this.year + this.term.padStart(2, '0')
			
			try {
				await api.login()
				const courses = await api.getCourseData(semester)
				this.courses = courses
				
				if (courses.length === 0) {
					uni.showToast({
						title: '未找到课程数据',
						icon: 'none'
					})
				} else {
					uni.showToast({
						title: '查询成功',
						icon: 'success'
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
		getCourse(slot, day) {
			const slotNum = parseInt(slot.replace('第', '').replace('节', ''))
			for (const course of this.courses) {
				if (course.weeks.includes(this.currentWeek) && course.day === day && course.time.includes(slotNum)) {
					return course
				}
			}
			return null
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
	background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
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
	background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
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

.table-container {
	flex: 1;
	margin: 0 24rpx 24rpx;
	background: #ffffff;
	border-radius: 24rpx;
	box-shadow: 0 4rpx 16rpx rgba(0, 0, 0, 0.08);
	overflow: hidden;
}

.timetable {
	min-width: 100%;
}

.table-header {
	display: flex;
	background: #f8f9fa;
	border-bottom: 2rpx solid #e9ecef;
}

.header-cell {
	flex: 0 0 120rpx;
	padding: 24rpx 16rpx;
	text-align: center;
	font-size: 24rpx;
	font-weight: bold;
	color: #495057;
	border-right: 2rpx solid #e9ecef;
}

.header-cell:first-child {
	flex: 0 0 100rpx;
	background: #667eea;
	color: #ffffff;
}

.table-body {
	display: flex;
	flex-direction: column;
}

.table-row {
	display: flex;
	border-bottom: 2rpx solid #e9ecef;
}

.cell {
	flex: 0 0 120rpx;
	padding: 16rpx;
	text-align: center;
	border-right: 2rpx solid #e9ecef;
	min-height: 120rpx;
	display: flex;
	align-items: center;
	justify-content: center;
}

.cell-slot {
	background: #f8f9fa;
	font-size: 24rpx;
	color: #666666;
	font-weight: bold;
}

.course-cell {
	width: 100%;
	display: flex;
	flex-direction: column;
	gap: 8rpx;
	padding: 12rpx;
	background: linear-gradient(135deg, #667eea15 0%, #764ba215 100%);
	border-radius: 8rpx;
}

.course-name {
	font-size: 22rpx;
	color: #333333;
	font-weight: bold;
	overflow: hidden;
	text-overflow: ellipsis;
	white-space: nowrap;
}

.course-location {
	font-size: 20rpx;
	color: #666666;
	overflow: hidden;
	text-overflow: ellipsis;
	white-space: nowrap;
}

.course-teacher {
	font-size: 20rpx;
	color: #999999;
	overflow: hidden;
	text-overflow: ellipsis;
	white-space: nowrap;
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
