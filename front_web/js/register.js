var vm = new Vue({
	el: '#app',
	data: {
		error_name: false,
		error_password: false,
		error_check_password: false,
		error_phone: false,
		error_allow: false,
		error_sms_code: false,
		sending_flag: false,
		username: '',
		password: '',
		password2: '',
		mobile: '',
		sms_code: '',
		allow: false,
		sms_code_tip: '获取短信验证码', // a标签显示文字
		error_sms_code_message: '', // 错误信息
		error_name_message: '',
		error_phone_message: ''
	},
	methods: {
		check_username: function () {
			var len = this.username.length;
			if (len < 5 || len > 20) {
				this.error_name_message = '请输入5-20个字符的用户名';
				this.error_name = true;
			} else {
				this.error_name = false;
			}
			// 检查重名
			if (this.error_name == false) {
				axios.get(host + '/auth/users/' + this.username + '/', {
					responseType: 'json'
				})
					.then(response => {
						if (response.data.count > 0) {
							this.error_name_message = '用户名已存在';
							this.error_name = true;
						} else {
							this.error_name = false;
						}
					})
					.catch(error => {
						console.log(error.response.data);
					})
			}
		},
		check_pwd: function () {
			var len = this.password.length;
			if (len < 8 || len > 20) {
				this.error_password = true;
			} else {
				this.error_password = false;
			}
		},
		check_cpwd: function () {
			if (this.password != this.password2) {
				this.error_check_password = true;
			} else {
				this.error_check_password = false;
			}
		},
		check_phone: function () {
			var re = /^1[345789]\d{9}$/;
			if (re.test(this.mobile)) {
				this.error_phone = false;
			} else {
				this.error_phone_message = '您输入的手机号格式不正确';
				this.error_phone = true;
			}
			if (this.error_phone == false) {
				axios.get(host + '/auth/mobile/' + this.mobile + '/', {
					responseType: 'json'
				})
					.then(response => {
						if (response.data.count > 0) {
							this.error_phone_message = '手机号已存在';
							this.error_phone = true;
						} else {
							this.error_phone = false;
						}
					})
					.catch(error => {
						console.log(error.response.data);
					})
			}
		},
		check_sms_code: function () {
			if (!this.sms_code) {
				this.error_sms_code = true;
			} else {
				this.error_sms_code = false;
			}
		},
		check_allow: function () {
			if (!this.allow) {
				this.error_allow = true;
			} else {
				this.error_allow = false;
			}
		},
		send_sms_code: function () {

			// 重新发送短信后，隐藏提示信息
			this.error_sms_code = false;

			if (this.sending_flag == true) {
				return;
			}
			this.sending_flag = true;

			// 校验参数，保证输入框有数据填写
			this.check_phone();

			if (this.error_phone == true) {
				this.sending_flag = false;
				return;
			}

			// 向后端接口发送请求，让后端发送短信验证码
			axios.get(host + '/smscode/' + this.mobile + '/', {
				responseType: 'json'
			})
				.then(response => {
					// 表示后端发送短信成功
					// 倒计时60秒，60秒后允许用户再次点击发送短信验证码的按钮
					var num = 60;
					// 设置一个计时器
					var t = setInterval(() => {
						if (num == 1) {
							// 如果计时器到最后, 清除计时器对象
							clearInterval(t);
							// 将点击获取验证码的按钮展示的文本回复成原始文本
							this.sms_code_tip = '获取短信验证码';
							// 将点击按钮的onclick事件函数恢复回去
							this.sending_flag = false;
						} else {
							num -= 1;
							// 展示倒计时信息
							this.sms_code_tip = num + '秒';
						}
					}, 1000, 60)
				})
				.catch(error => {
					if (error.response.status == 400) {
						// 展示发送短信错误提示
						this.error_sms_code = true;
						this.error_sms_code_message = error.response.data.message;
					} else {
						console.log(error.response.data);
					}
					this.sending_flag = false;
				})
		},
		// 注册
		on_submit: function () {
			this.check_username();
			this.check_pwd();
			this.check_cpwd();
			this.check_phone();
			this.check_sms_code();
			this.check_allow();

			if (this.error_name == false && this.error_password == false && this.error_check_password == false
				&& this.error_phone == false && this.error_sms_code == false && this.error_allow == false) {
				axios.post(host + '/auth/register/', {
					username: this.username,
					password: this.password,
					password2: this.password2,
					mobile: this.mobile,
					sms_code: this.sms_code,
					allow: this.allow.toString()
				}, {
					responseType: 'json'
				})
					.then(response => {
						// 记录用户的登录状态
						sessionStorage.clear();
						localStorage.clear();
						localStorage.token = response.data.token;
						localStorage.username = response.data.username;
						localStorage.user_id = response.data.id;
						location.href = '/index.html';
					})
					.catch(error => {
						if (error.response.status == 400) {
							if ('non_field_errors' in error.response.data) {
								this.error_sms_code_message = error.response.data.non_field_errors[0];
							} else {
								this.error_sms_code_message = '数据有误';
							}
							this.error_sms_code = true;
						} else {
							console.log(error.response.data);
						}
					})
			}
		}
	}
});
