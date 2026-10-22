module.exports = {
	devServer: {
		proxy: {
			'/jwxt': {
				target: 'https://jwxt.gdupt.edu.cn',
				changeOrigin: true,
				secure: true,
				pathRewrite: {
					'^/jwxt': ''
				}
			}
		}
	}
}
