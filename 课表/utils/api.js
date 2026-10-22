const BASE_URL = '/jwxt'
const LOGIN_URL = BASE_URL + '/login!doLogin.action'
const COURSE_URL = BASE_URL + '/xsgrkbcx!xsAllKbList.action'
const LOGIN2 = BASE_URL + '/login'
const SCORE_URL = BASE_URL + '/xskccjxx!getDataList.action'

const FIXED_USERNAME = '24034530116'
const FIXED_PASSWORD = 'LiYuhan060317@@'

const headers = {
	'Content-Type': 'application/x-www-form-urlencoded'
}

function base64Encode(str) {
	return uni.arrayBufferToBase64(new TextEncoder().encode(str).buffer)
}

function login() {
	return new Promise((resolve, reject) => {
		uni.request({
			url: LOGIN2,
			method: 'GET',
			header: headers,
			success: (res) => {
				const encodedPwd = base64Encode(FIXED_PASSWORD)
				const loginData = {
					account: FIXED_USERNAME,
					pwd: encodedPwd,
					verifycode: ''
				}
				
				uni.request({
					url: LOGIN_URL,
					method: 'POST',
					data: loginData,
					header: headers,
					success: (loginRes) => {
						if (loginRes.data && typeof loginRes.data === 'string' && loginRes.data.includes('不正确')) {
							reject(new Error('账号或密码错误'))
						} else {
							resolve(true)
						}
					},
					fail: (err) => {
						reject(new Error('登录失败: ' + err.errMsg))
					}
				})
			},
			fail: (err) => {
				reject(new Error('网络错误: ' + err.errMsg))
			}
		})
	})
}

function getCourseData(semester) {
	return new Promise((resolve, reject) => {
		uni.request({
			url: COURSE_URL,
			method: 'POST',
			data: {
				xnxqdm: semester
			},
			header: headers,
			success: (res) => {
				try {
					const courses = parseCourseInfo(res.data)
					resolve(courses)
				} catch (e) {
					reject(new Error('数据解析失败: ' + e.message))
				}
			},
			fail: (err) => {
				reject(new Error('获取课表失败: ' + err.errMsg))
			}
		})
	})
}

function parseCourseInfo(htmlContent) {
	const courses = []
	const scriptRegex = /var kbxx = (\[.*?\]);/
	const match = htmlContent.match(scriptRegex)
	
	if (!match) {
		return courses
	}
	
	try {
		const courseData = JSON.parse(match[1])
		
		for (const course of courseData) {
			const weeks = parseWeeks(course.zcs || '')
			const timeSlots = course.jcdm2 ? course.jcdm2.split(',').map(s => parseInt(s)) : []
			
			courses.push({
				name: course.kcmc || '',
				code: course.kcbh || '',
				class: course.jxbmc || '',
				weeks: weeks,
				day: parseInt(course.xq || 0),
				time: timeSlots,
				location: course.jxcdmcs || '',
				teacher: course.teaxms || ''
			})
		}
	} catch (e) {
		console.error('解析课程数据失败:', e)
	}
	
	return courses
}

function parseWeeks(weekStr) {
	const weeks = []
	if (!weekStr) return weeks
	
	const parts = weekStr.split(',')
	for (const part of parts) {
		if (part.includes('-')) {
			const [start, end] = part.split('-').map(s => parseInt(s))
			for (let i = start; i <= end; i++) {
				weeks.push(i)
			}
		} else {
			weeks.push(parseInt(part))
		}
	}
	return weeks
}

function getScoreData(semester) {
	return new Promise((resolve, reject) => {
		const scoreData = {
			xnxqdm: semester,
			jhlxdm: '',
			page: 1,
			rows: 20,
			sort: 'xnxqdm,kcbh,ksxzdm',
			order: 'asc'
		}
		
		uni.request({
			url: SCORE_URL,
			method: 'POST',
			data: scoreData,
			header: headers,
			success: (res) => {
				try {
					resolve(res.data)
				} catch (e) {
					reject(new Error('数据解析失败: ' + e.message))
				}
			},
			fail: (err) => {
				reject(new Error('获取成绩失败: ' + err.errMsg))
			}
		})
	})
}

function calculateGPA(score) {
	try {
		const scoreNum = parseFloat(score)
		if (scoreNum >= 90) return 4.0
		if (scoreNum >= 85) return 3.7
		if (scoreNum >= 80) return 3.3
		if (scoreNum >= 75) return 3.0
		if (scoreNum >= 70) return 2.7
		if (scoreNum >= 65) return 2.3
		if (scoreNum >= 60) return 2.0
		return 0.0
	} catch (e) {
		return 0.0
	}
}

export default {
	login,
	getCourseData,
	getScoreData,
	calculateGPA
}
