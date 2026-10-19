# Trista Codex Skills

## 用途

Trista Codex Skills 是一个小型的 Codex 原生技能集合，包含三种彼此独立的软件工程模式和剧情类动画短片规划。工程技能区分实现、只读审查与独立验证；规划技能将故事整理为角色资产、场景资产和分镜文档，不生成媒体。各技能均保留用户授权范围与已有工作。

`README.md` 是规范的英文文档。[README.zh-CN.md](README.zh-CN.md) 是完整的中文对应文档。

## 技能表

| 技能 | 使用场景 | 修改权限 |
| --- | --- | --- |
| `codex-implement-change` | 用户明确要求修复、添加、更改、删除、迁移或重构仓库文件。 | 可以——仅限用户授权的仓库范围。 |
| `codex-readonly-review` | 用户要求审查代码、差异、分支或拉取请求，或进行审计或风险评估，但未授权编辑。 | 不可以——严格只读；不修复发现的问题。 |
| `codex-verify-change` | 用户要求根据现有证据判断变更是否有效、是否修复问题、是否满足验收标准或是否就绪。 | 不可以——严格只读；不修复失败。 |
| `story-to-film-planner` | 用户希望从创意、故事、剧本、素材或已有分镜规划剧情类动画短片。 | 仅限规划文档；不生成媒体、不剪辑、不上传或发布。 |

在三个工程技能中，只有 `codex-implement-change` 可以修改文件，并且仅限用户授权的仓库范围。`codex-readonly-review` 和 `codex-verify-change` 均为严格只读。`story-to-film-planner` 可以创建或修改已授权的规划文档，不授权修改仓库代码或执行媒体制作。

验证结果必须以且仅以一个结论开头：所有重要标准都有充分正面证据且不存在矛盾时为 `VERIFIED`；观察到的证据与至少一个重要标准矛盾或表明存在相关失败时为 `NOT_VERIFIED`；所需证据、访问权限、环境或标准不可用或存在实质歧义时为 `BLOCKED`。

## 路由示例

| 请求 | 路由 | 最终权限 |
| --- | --- | --- |
| “修复失败的解析器测试。” | `codex-implement-change` | 只能编辑请求涉及的仓库范围。 |
| “审查这个拉取请求；不要编辑文件。” | `codex-readonly-review` | 只读地报告发现。 |
| “验证此修复是否满足验收标准。” | `codex-verify-change` | 只读地提供证据和一个结论。 |
| “审查变更，然后只修复确认的 P1 问题。” | 先使用 `codex-readonly-review`，再使用 `codex-implement-change` | 先完成审查；只有在独立且明确授权的修复阶段才能开始修改。 |
| “解释这个函数为什么慢；不要修改它。” | 不使用本技能包中的任何技能 | 解释过程保持只读。 |
| “为这部动画短片规划角色、场景和分镜，不生成媒体。” | `story-to-film-planner` | 可编写请求的规划文档，并检查已授权素材。 |

对于工程任务，仅分析或规划并不授权实现。验证失败不会触发修复。任何技能都不会自动调用另一个技能；当请求措辞混合时，在修改意图明确前采用更严格的权限。

规划技能保留已验收的中文正文与规则：大纲、风格、时长、画幅、声音及字幕由用户选择或确认，默认交付一份项目工作表，仅在明确需要时附平台无关的提示词草案，片段分组按需启用。当前规划文档已验收并完成静态检查；本次分发不代表已做故事试用或验证媒体效果。

## 安装

规范的技能源是 `skills/` 下的各目录。只安装需要的技能。支持的目标位置为：

- 仓库级：`.agents/skills/<skill-name>`
- 个人级：`~/.agents/skills/<skill-name>`

如果 Codex 环境提供技能安装器，请选择 `skills/<skill-name>` 作为源，并选择上述目标位置之一。不同环境的安装器界面可能不同。也可以从仓库根目录直接复制；将 `skill_name` 设置为技能表中的准确名称。

仓库级安装：

```bash
skill_name=codex-implement-change
mkdir -p ".agents/skills/$skill_name"
cp -R "skills/$skill_name/." ".agents/skills/$skill_name/"
```

个人级安装：

```bash
skill_name=codex-implement-change
mkdir -p "$HOME/.agents/skills/$skill_name"
cp -R "skills/$skill_name/." "$HOME/.agents/skills/$skill_name/"
```

根据需要将其替换为 `codex-readonly-review`、`codex-verify-change` 或 `story-to-film-planner` 并重复执行。直接复制只会更改所选目标位置，不需要更改无关的 Codex 配置。

## 验证

在仓库根目录运行以下两个不依赖第三方包的检查：

```bash
python scripts/validate_skills.py
python -m unittest discover -s tests -p 'test_*.py' -v
```

验证器检查准确的技能清单、必需文件、frontmatter、本地引用、Codex 元数据和未完成标记。单元测试覆盖仓库结构和验证器拒绝无效结构的情形。`evals/` 下的路由和行为夹具是可供审查的预期，不是自动化模型评估框架。

## 边界与非目标

本技能包不是通用智能体框架。V1 不提供编排运行时或状态机，不提供自动模型选择或路由，不提供自动子智能体路由或委派，也不提供拉取请求创建、合并、发布或部署自动化。它也不提供外部治理适配器、插件市场包、特定语言的测试预设、审查或验证过程中的自动修复，以及从只读工作到修改操作的隐藏升级。

技术能力绝不代表已经获得权限。现有的已跟踪和未跟踪工作均归用户所有；除非用户另行授权，否则实现技能不允许进行破坏性清理、扩大到无关范围、发布、合并、部署、发送消息或更改外部系统。

## 贡献与公共安全规则

- 在用户明确要求新增技能时，同步维护文档清单、验证器清单、测试与权限矩阵。
- 实现变更必须处于用户明确授权的范围内；审查和验证必须保持严格只读。
- 将已跟踪和未跟踪工作视为用户所有，不得删除或吸收无关变更。
- 每个技能必须独立提交，并在发布前运行两个验证命令。
- 公共行为或安装方式发生变化时，同时更新 `README.md` 和 `README.zh-CN.md`。
- 不得提交凭据、令牌、Cookie、认证产物、客户数据、私有日志、专有源代码、私有仓库名称、私有基础设施拓扑、本地机器路径或特定环境标识符。
- 示例必须通用且可复现。不得声称不存在的关联或认可关系。

仓库策略请参阅 [AGENTS.md](AGENTS.md)，V1 契约与规划技能扩展请参阅[设计规范](docs/superpowers/specs/2026-09-04-trista-codex-skills-design.md)。

## 致谢

本技能包的结构受到公共仓库 [`multica-ai/andrej-karpathy-skills`](https://github.com/multica-ai/andrej-karpathy-skills) 的启发。本仓库的文字、契约、测试以及针对 Codex 对实现、审查和验证权限所作的划分均为原创。本项目与该仓库的作者、Andrej Karpathy 或 OpenAI 不存在关联，也未获得其认可。

## 许可证

本仓库采用 [MIT License](LICENSE)。Copyright 2026 Trista。
