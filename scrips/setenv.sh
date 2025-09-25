#!/usr/bin/env bash
set -e

echo "=== 检查依赖 (zsh, git, curl, tmux) ==="

sudo apt-get update
sudo apt-get install -y zsh git curl tmux silversearcher-ag

# ========== 安装 Oh My Zsh ==========
if [ -d "$HOME/.oh-my-zsh" ]; then
    echo "Oh My Zsh 已安装，跳过"
else
    echo "=== 安装 Oh My Zsh ==="
    sh -c "$(curl -fsSL https://raw.githubusercontent.com/ohmyzsh/ohmyzsh/master/tools/install.sh)" "" --unattended
fi

# 设置 zsh 为默认 shell
if [ "$SHELL" != "$(which zsh)" ]; then
    echo "=== 设置 zsh 为默认 shell ==="
    chsh -s "$(which zsh)"
else
    echo "zsh 已是默认 shell"
fi

# ========== 安装 Zsh 插件 ==========
ZSH_CUSTOM=${ZSH_CUSTOM:-$HOME/.oh-my-zsh/custom}

echo "=== 安装 zsh-autosuggestions 插件 ==="
if [ ! -d "$ZSH_CUSTOM/plugins/zsh-autosuggestions" ]; then
    git clone https://github.com/zsh-users/zsh-autosuggestions \
        "$ZSH_CUSTOM/plugins/zsh-autosuggestions"
else
    echo "zsh-autosuggestions 已存在，跳过"
fi

echo "=== 安装 zsh-syntax-highlighting 插件 ==="
if [ ! -d "$ZSH_CUSTOM/plugins/zsh-syntax-highlighting" ]; then
    git clone https://github.com/zsh-users/zsh-syntax-highlighting.git \
        "$ZSH_CUSTOM/plugins/zsh-syntax-highlighting"
else
    echo "zsh-syntax-highlighting 已存在，跳过"
fi

# ========== 自动修改 ~/.zshrc ==========
echo "=== 配置 ~/.zshrc 启用插件 ==="
if grep -q '^plugins=' ~/.zshrc; then
    # 替换已有 plugins 行
    sed -i 's/^plugins=(.*)/plugins=(git zsh-autosuggestions zsh-syntax-highlighting)/' ~/.zshrc
else
    echo 'plugins=(git zsh-autosuggestions zsh-syntax-highlighting)' >> ~/.zshrc
fi

# 确保最后一行加载 syntax-highlighting
if ! grep -q 'source $ZSH_CUSTOM/plugins/zsh-syntax-highlighting/zsh-syntax-highlighting.zsh' ~/.zshrc; then
    echo 'source $ZSH_CUSTOM/plugins/zsh-syntax-highlighting/zsh-syntax-highlighting.zsh' >> ~/.zshrc
fi

# ========== 安装 tmux 插件管理器 ==========
echo "=== 安装 tmux 插件管理器 TPM ==="
if [ ! -d "$HOME/.tmux/plugins/tpm" ]; then
    git clone https://github.com/tmux-plugins/tpm ~/.tmux/plugins/tpm
else
    echo "TPM 已存在，跳过"
fi

# ========== 写入 tmux 配置文件 ==========
TMUX_CONF="$HOME/.tmux.conf"
echo "=== 写入默认 tmux 配置 ==="
cat <<'EOF' > "$TMUX_CONF"
# List of plugins
set -g @plugin 'tmux-plugins/tpm'
set -g @plugin 'tmux-plugins/tmux-sensible'

# Other examples:
# set -g @plugin 'github_username/plugin_name'
# set -g @plugin 'github_username/plugin_name#branch'
# set -g @plugin 'git@github.com:user/plugin'
# set -g @plugin 'git@bitbucket.com:user/plugin'

# Initialize TMUX plugin manager (keep this line at the very bottom of tmux.conf)
run '~/.tmux/plugins/tpm/tpm'

# Catppuccin 主题
set -g @plugin 'catppuccin/tmux'
set -g @catppuccin_flavour 'mocha'

# 终端设置
set -g default-terminal 'tmux-256color'
set -g base-index 1
set -g pane-base-index 1
set -g renumber-windows on

# 使用 alt + 方向键控制 pane
bind -n M-Left select-pane -L
bind -n M-Right select-pane -R
bind -n M-Up select-pane -U
bind -n M-Down select-pane -D

# 使用鼠标点击控制 pane
set-option -g mouse on

# 修改分屏快捷键，v 垂直分屏，h 水平分屏
unbind '"'
unbind %
bind-key h split-window -h
bind-key v split-window -v

# 设置前景背景颜色框
set -g default-terminal "screen-256color"
EOF

echo "=== 所有步骤完成 ==="
echo "1. 重新登录或执行 'exec zsh'"
echo "2. 启动 tmux 后按下 'prefix + I' (Ctrl+b 再按大写 I) 安装 tmux 插件"
