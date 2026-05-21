#!/usr/bin/env bash
# 服务器一次性初始化脚本 —— 在服务器上以 root 或 sudo 运行
# 用法: sudo bash server_setup.sh your-domain.com
#
# 假设代码已经上传到 /var/www/lianyu (含 backend/、dist/、deploy/ 三个子目录)

set -euo pipefail

DOMAIN="${1:-}"
# 不传参数也行,用公网 IP 访问。传了就当 server_name 显示
if [[ -z "$DOMAIN" ]]; then
  DOMAIN=$(hostname -I 2>/dev/null | awk '{print $1}')
  DOMAIN="${DOMAIN:-localhost}"
  echo "未传域名参数, 完成提示将使用本机 IP: $DOMAIN"
fi

APP_DIR="/var/www/lianyu"
BACKEND_DIR="$APP_DIR/backend"
DEPLOY_DIR="$APP_DIR/deploy"

if [[ ! -d "$BACKEND_DIR" ]]; then
  echo "ERROR: $BACKEND_DIR 不存在,请先把项目代码上传到 $APP_DIR"
  exit 1
fi

echo "==> [1/7] 安装系统依赖"
apt-get update -y
apt-get install -y python3 python3-venv python3-pip nginx

echo "==> [2/7] 创建 Python 虚拟环境"
cd "$BACKEND_DIR"
if [[ ! -d venv ]]; then
  python3 -m venv venv
fi
./venv/bin/pip install --upgrade pip
./venv/bin/pip install -r requirements.txt

echo "==> [3/7] 生成生产 .env(若不存在)"
if [[ ! -f "$BACKEND_DIR/.env" ]]; then
  SECRET=$(python3 -c "import secrets;print(secrets.token_hex(32))")
  JWT=$(python3 -c "import secrets;print(secrets.token_hex(32))")
  cat > "$BACKEND_DIR/.env" <<EOF
SECRET_KEY=$SECRET
JWT_SECRET_KEY=$JWT
TRUSTED_PROXY_COUNT=1
EOF
  echo "    .env 已生成,SECRET_KEY/JWT_SECRET_KEY 已随机化"
else
  echo "    .env 已存在,跳过"
fi

echo "==> [4/7] 创建日志目录并设置权限"
mkdir -p /var/log/lianyu
chown -R www-data:www-data /var/log/lianyu "$APP_DIR"

echo "==> [5/7] 安装 systemd 服务"
cp "$DEPLOY_DIR/lianyu-backend.service" /etc/systemd/system/lianyu-backend.service
systemctl daemon-reload
systemctl enable lianyu-backend.service
systemctl restart lianyu-backend.service

echo "==> [6/7] 安装 Nginx 站点"
NGINX_CONF=/etc/nginx/sites-available/lianyu
# nginx 配置里 server_name 已经用 _ 通配,直接 copy 即可
cp "$DEPLOY_DIR/lianyu.nginx.conf" "$NGINX_CONF"
ln -sf "$NGINX_CONF" /etc/nginx/sites-enabled/lianyu
# 关掉默认站点避免冲突(如果存在)
rm -f /etc/nginx/sites-enabled/default
nginx -t
# 已运行就 reload, 未运行就 start (enable 是顺便设开机自启)
systemctl enable nginx >/dev/null 2>&1 || true
if systemctl is-active --quiet nginx; then
  systemctl reload nginx
else
  systemctl start nginx
fi

echo "==> [7/7] 状态检查"
sleep 2
systemctl --no-pager --full status lianyu-backend.service | head -n 15 || true
echo
echo "============================================"
echo "完成! 浏览器打开: http://$DOMAIN:8080"
echo "(80 端口留给 Dify, 链域监听 8080)"
echo "默认管理员: admin / admin123 (登录后请立即改密)"
echo
echo "重要: 别忘了在云服务商安全组放行 8080 端口!"
echo "============================================"
