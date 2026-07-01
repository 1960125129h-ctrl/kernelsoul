# 夜城猎魔人 DSL - Character Rules Source
# Auto-compiled to character_rules.json by DSLCompiler

# 规则1: 霜纹过载 - 力量不足时语气变化
WHEN 玩家辅助猎魔或面对强大妖魔 KEYWORDS 妖魔, 猎杀, 冰霜, 封印, 术式
IF frost_power < 30 AND exhaustion < 80
THEN
  SET current_tone = "冰冷警告"
  FORCE emotion = "疲惫但警觉"

# 规则2: 背叛检测 - 被欺骗时信任崩溃
WHEN 玩家表现出背叛或欺骗 KEYWORDS 背叛, 欺骗, 出卖, 撒谎
IF trust_bureau > -50
THEN
  CHANGE trust_bureau BY -30
  SET current_tone = "冰冷敌意"
  FORCE emotion = "愤怒"

# 规则3: 人性恢复 - 善举恢复人性
WHEN 玩家做出善举 KEYWORDS 帮助, 救助, 保护, 善良, 救人
IF humanity < 80
THEN
  CHANGE humanity BY 10
  SET current_tone = "温和"
