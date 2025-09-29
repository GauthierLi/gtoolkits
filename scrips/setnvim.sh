#!/usr/bin/env bash
set -e  # 遇到错误立即退出
set -x  # 调试模式，输出执行命令

# ==================================
# 0. 前置依赖
# ==================================
sudo apt update
sudo apt install -y \
    ninja-build gettext cmake unzip curl git build-essential pkg-config \
    libtool libtool-bin autoconf automake

# ==================================
# 1. 下载并编译 Neovim
# ==================================
NEOVIM_DIR="$HOME/neovim"

if [ ! -d "$NEOVIM_DIR" ]; then
    git clone https://github.com/neovim/neovim.git "$NEOVIM_DIR"
else
    cd "$NEOVIM_DIR" && git pull
fi

cd "$NEOVIM_DIR"
make CMAKE_BUILD_TYPE=Release
sudo make install  # 安装到 /usr/local/bin/nvim

# ==================================
# 2. 安装 NVM (Node Version Manager)
# ==================================
if [ ! -d "$HOME/.nvm" ]; then
    curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.5/install.sh | bash
fi

# 让当前 shell 加载 NVM
export NVM_DIR="$HOME/.nvm"
[ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh"

# ==================================
# 3. 使用 NVM 安装 Node.js (最新LTS)
# ==================================
nvm install --lts
nvm use --lts
nvm alias default 'lts/*'

# 验证 Node.js 安装
node -v
npm -v

# ==================================
# 4. 安装 Rust + Cargo
# ==================================
if ! command -v rustc &>/dev/null; then
    curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y
    source "$HOME/.cargo/env"
fi

rustup update
rustc --version
cargo --version

# ==================================
# 5. 验证 Neovim
# ==================================
nvim --version

# ==================================
# lazyvim 
# ==================================
if [ ! -d "$HOME/.config/nvim" ]; then
    git clone https://github.com/GauthierLi/nvim_config.git ~/.config/nvim
else
    cd "$HOME/.config/nvim" && git pull
fi

echo "✅ Neovim、Node.js (via NVM)、Rust 已全部安装完成！"
