# Team Agent 项目环境配置
# 使用方法: source .bashrc_team_agent

# 设置项目根目录
export TEAM_AGENT_ROOT="/home/zhumoore/projects/team-agent"

# 将项目根目录添加到 PYTHONPATH
export PYTHONPATH="${TEAM_AGENT_ROOT}:${PYTHONPATH}"

# 激活虚拟环境（可选）
if [ -f "${TEAM_AGENT_ROOT}/venv/bin/activate" ]; then
    source "${TEAM_AGENT_ROOT}/venv/bin/activate"
fi

echo "✅ Team Agent 环境已加载"
echo "📁 项目根目录: $TEAM_AGENT_ROOT"
echo "🐍 PYTHONPATH: $PYTHONPATH"