"""适配器包：每个 AI 工具一个 adapter，统一产出 usage_events 元组。

约定：
- agent_type 即适配器名（"codex"/"claude"/"antigravity"/"zcode"）；
- 产出元组列序与 parser.INSERT_SQL 一致；
- 适配器自带文件发现与解析，增量游标（offset/step_idx）沿用 file_index。
"""
