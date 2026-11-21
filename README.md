# 流式 Agent 聊天演示

这是一个使用模拟数据的 Agent 聊天应用，演示由服务端驱动的搜索、人工确认、SVG 占位图生成和逐字回复流程。项目不会调用真实大语言模型、搜索服务或图片生成模型。

## 环境要求与安装

需要 Python 3.11 或更新版本，以及 Node.js 和 npm。

在项目根目录下，先在选定的 Python 环境中安装后端依赖：

```bash
python -m pip install -r backend/requirements.txt
```

安装前端依赖：

```bash
cd frontend
npm ci
```

返回项目根目录，使用一条命令启动前后端：

```bash
python dev.py
```

如果使用本机已有的 Conda 环境 `agent_test`，也可以在项目根目录执行：

```powershell
conda run -n agent_test python dev.py
```

打开 `http://127.0.0.1:5173`，或使用 Vite 输出的实际地址。后端监听 18000 端口，前端将 `/health` 和 `/api` 请求代理到后端。按 `Ctrl+C` 停止启动脚本。如果端口已被占用，请先停止对应的旧开发进程。

也可以分别启动前后端：

```bash
python -m uvicorn backend.app.main:app --host 127.0.0.1 --port 18000
```

在另一个终端运行：

```bash
cd frontend
npm run dev
```

在 `frontend` 目录执行 `npm run build` 可以进行 TypeScript 检查并构建前端。`GET /health` 返回 `{"status":"ok"}`。

## 项目结构

- `backend/app/main.py`：HTTP 和 SSE 接口。
- `backend/app/store.py`：会话与事件日志。
- `backend/app/agent.py`：Agent 状态机和模拟执行流程。
- `backend/app/svg.py`：生成包含转义文本的 SVG 占位图。
- `frontend/src/main.tsx`：将事件渲染为聊天内容和调试控件。
- `dev.py`：同时启动前后端开发服务。
- `CHANGES.md`：项目修改记录。

## 事件与状态

每个业务事件都包含 `seq`、`type`、`sessionId`、`turnId`、`timestamp` 和 `data`。同一会话内的序号递增。SSE 使用 `id`、`event` 和 JSON 格式的 `data`。

| 事件 | 主要数据 | 触发时机 |
| --- | --- | --- |
| `user_message` | `text` | 用户消息被接受 |
| `turn_started` | `message` | 创建新一轮对话 |
| `tool_started` | `tool`、`status` | 搜索或图片生成开始 |
| `tool_finished` | `tool`、`status`、`result?`、`error?` | 工具完成、失败或被取消 |
| `confirmation_required` | `confirmationId`、`prompt` | 搜索完成，需要用户确认 |
| `confirmation_resolved` | `confirmationId`、`decision`、`finalPrompt` | 确认决定被接受 |
| `image_generated` | `imageUrl`、`prompt` | SVG 生成完成 |
| `text_delta` | `delta` | 输出回复中的一个字符 |
| `turn_ended` | `reason` | 对话轮次结束，原因包括 `completed`、`rejected`、`cancelled` 或 `failed` |

正常状态转换为 `idle → searching → waiting_confirmation → generating_image → streaming_reply → completed`。用户拒绝后进入 `rejected`；图片生成失败后进入 `failed`；在任意活跃状态取消后进入 `cancelled`。进入终态后可以开始新一轮对话。

会话锁保护状态转换和事件追加。同一会话同时只能运行一个 Agent 流程：忙碌期间发送新消息会返回 HTTP 409，等待确认时也一样。每张确认卡片只能接受一次决定。取消会停止任务并产生一个终止事件。模拟图片失败只对下一次生成生效，不自动重试；失败后用户可以开始新一轮对话。

Agent 执行与 SSE 连接相互独立。服务端按顺序保存事件，追加事件和等待新事件使用同一把条件锁，避免从历史重放切换到实时接收时漏事件。断线重连时，客户端请求最后一个已收到序号之后的事件，并忽略已处理的序号。刷新页面时，浏览器复用保存的会话 ID，从序号 0 重放事件来恢复界面。

会话仅保存在**服务端内存**中：后端进程重启后会话会丢失，需要创建新会话。浏览器刷新或网络断线不会导致服务端任务停止。

## 七个演示场景

1. **普通批准**：输入消息，点击 **Send**，然后点击 **Approve**。依次出现搜索、确认卡片、图片和流式回复，最终状态为 `completed`。
2. **修改后批准**：发送消息，在确认卡片中修改 Prompt，然后点击 **Edit and approve**。SVG 应显示修改后的文本。
3. **生成中取消**：批准消息后，在图片生成进行期间点击 **Cancel**。对话以 `cancelled` 结束，不出现成功生成的图片。
4. **断线重放**：回复逐字输出时点击 **Disconnect**。几秒后自动重连，最终回复完整显示，字符没有重复。
5. **模拟图片失败**：勾选 **Image generation fails**，发送消息并批准。下一次图片生成失败，工具状态和错误可见，对话以 `failed` 结束，不自动重试。
6. **运行中重复发送**：在当前对话进行时点击 **Send again**。界面显示 409 提示，不会启动第二个并行流程。
7. **等待确认时发送新消息**：确认卡片等待处理时，输入另一条消息并点击 **Send**。新请求被拒绝并显示提示，原确认卡片仍可使用。

还应检查 **Reject**、重复批准、在其他活跃状态取消，以及等待确认时刷新页面。

## AI 使用与已知限制

项目使用 Codex 进行实现和检查。原始会话导出与使用记录的状态见 `ai-logs/README.md`。

工作流程和搜索结果均由规则模拟，SVG 是占位图。项目使用单个内存服务进程，不支持多进程共享会话或持久化恢复，也未提供身份认证。七个场景的 UI 验收和外部提交情况需要单独核对；未经实际验证的项目不应标记为通过。
