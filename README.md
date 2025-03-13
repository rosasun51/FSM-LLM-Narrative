# Bottom Layer

1. narrative state manager判断叙事管理叙事进程：根据playerinteraction/multiagent的选择, 判断 agent 的选择影响故事叙述到故事线的哪一步了（state内；state之间的转换）
2. update消息到middle layer+memory: 完成agent state manager validation+故事线信息的储存

## State Mechanism 判断叙事管理叙事进程：

根据playerinteraction/multiagent的选择, 判断 agent 的选择影响故事叙述到故事线的哪一步了（state内；state之间的转换）

(1) 状态追踪器（State Tracker）：负责跟踪当前剧情状态，判断玩家行为和多agent选择对故事线的影响（即在哪个剧情状态内或从一个状态转换到另一个状态）。
(2) LLM集成（LLM Integration）: 在已有的劇本大致節點上能有i頂靈活性，產生新的節點，對已知的劇情節點進行連接 ; 提供动态内容生成能力，允许系统根据当前剧情状态和上下文生成或修改剧本内容，使剧情更加灵活和生动。
通过与叙事引擎的紧密配合，确保生成的内容符合当前故事状态。


## Update Mechanism：
