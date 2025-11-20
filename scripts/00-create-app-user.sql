-- Chú ý: Script này chạy dưới user admin (postgres)
-- 1. Tạo user ứng dụng với mật khẩu mà backend mong muốn
-- (Backend mong muốn app_password, nếu bạn dùng 123456 thì thay vào)
CREATE ROLE app_user WITH LOGIN PASSWORD 'app_password';

-- 2. Đặt user này là owner của database mặc định (file2learning)
ALTER DATABASE file2learning OWNER TO app_user;