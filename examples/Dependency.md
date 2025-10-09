
# Agent 依赖注入（Dependency Injection）设计与开发/使用指南

本文件详细介绍了 `Agent` 智能体的依赖注入（Dependency Injection, DI）设计思想、开发者与使用者的分工，以及如何高效协作。

---

## 角色分工概览

- **Agent开发者**：负责定义依赖结构、Agent本体、工具与指令的实现，保证可扩展性和灵活性。
- **Agent使用者**：负责在实际业务中实例化Agent，注入具体依赖，实现个性化和上下文定制。

---


## 一、什么是依赖注入？


依赖注入是一种软件设计模式，指的是将组件所依赖的对象（如配置、上下文、外部资源等）在外部创建好后，通过参数传递、属性赋值等方式注入到组件内部，而不是在组件内部直接创建依赖。这样可以实现：

- **解耦**：业务逻辑与依赖对象分离，便于维护和扩展。
- **灵活性**：可根据不同场景动态切换依赖。
- **可测试性**：便于 mock 或替换依赖进行单元测试。

---


## 二、Agent依赖注入的开发与使用流程

本节分为两部分：

- **A. Agent开发者要做什么？**
- **B. Agent使用者要做什么？**

---

### A. Agent开发者要做什么？

### 1. 定义依赖数据结构


依赖通常用 Python 的 `dataclass` 数据类定义。例如：

```python
from dataclasses import dataclass

@dataclass
class Dependency:
	agent_name: str = "Peter Pan"
```

该类用于描述 Agent 运行所需的上下文信息（如 agent 的名字），可以根据实际需求扩展更多字段。

---


### 2. Agent 注册依赖类型

在创建 Agent 时，通过 `deps_type` 参数声明依赖类型：

```python
agent = Agent(model, deps_type=Dependency)
```

这样 Agent 就知道后续会注入什么类型的依赖对象。

---


### 3. 在指令与工具中访问依赖


Agent 的 instructions（指令）和 tool（工具）函数都可以通过 `ctx.deps` 访问依赖对象。例如：

```python
@agent.instructions
def get_instruction(ctx: RunContext):
	return f"你是一个乐于助人的助手，你的名字是 {ctx.deps.agent_name}。"
```


在工具函数中访问依赖的推荐例子：

```python
@agent.tool
def get_agent_signature(ctx: RunContext) -> str:
    """返回带有 agent_name 的签名。"""
    return f"-- 由智能体 {ctx.deps.agent_name} 服务"
```
这样，工具可以根据依赖中的 agent_name 字段动态生成不同的行为或响应。

> **开发者注意：**
> - 所有需要依赖上下文的指令/工具，均应通过 `ctx.deps` 获取依赖。
> - 依赖结构应尽量简洁明了，便于使用者理解和传参。

---


---

### B. Agent使用者要做什么？

#### 1. 实例化依赖并注入

在实际运行时，可以为每个 AgentRunner 注入不同的依赖实例，实现上下文定制：

```python
agent_runner = AgentRunner(agent=agent, dependency=Dependency(agent_name="Alice"))
```

这样，Agent 在本次会话中就会以 "Alice" 作为名字。

---

### 5. 依赖注入的完整流程示例

```python
from dataclasses import dataclass
from pydantic_ai import Agent, RunContext

@dataclass
class Dependency:
	agent_name: str = "Peter Pan"

agent = Agent(model, deps_type=Dependency)

@agent.instructions
def get_instruction(ctx: RunContext):
	return f"你好，我叫 {ctx.deps.agent_name}，很高兴为你服务。"

agent_runner = AgentRunner(agent=agent, dependency=Dependency(agent_name="Alice"))
response = agent_runner.run("你是谁？")
```

---

## 三、依赖注入的优势

- **关注点分离**：业务逻辑与上下文配置解耦，代码更清晰。
- **灵活扩展**：可根据不同用户/场景动态注入不同依赖。
- **便于测试**：可轻松 mock 依赖，进行单元测试。
- **可维护性强**：依赖结构统一，便于后期维护和升级。

---

## 四、常见用法与建议

1. **依赖字段建议用 dataclass 明确声明类型和默认值。**（开发者）
2. **如需多种上下文信息，可在依赖类中扩展更多字段。**（开发者）
3. **在工具函数、指令函数中均可通过 ctx.deps 访问依赖。**（开发者）
4. **建议每次会话（AgentRunner）都注入新的依赖实例，避免状态污染。**（使用者）
5. **使用者应根据业务实际，正确传递依赖参数。**

---

## 五、总结

Agent 的依赖注入机制极大提升了智能体的灵活性、可扩展性和可维护性。开发者专注于定义依赖和实现功能，使用者专注于业务注入和上下文定制，二者协作可实现高效、可维护的智能体开发与应用。
