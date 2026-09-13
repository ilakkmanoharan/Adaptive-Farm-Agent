```markdown
# Kaggriculture S3 Agent Specification

## Objective
Develop a single-file stdlib agent for Kaggriculture S3 that addresses the issues observed in S2 and improves performance against stronger opponents. The agent should focus on efficient logistics, strategic resource allocation, and optimal market interactions.

## Key Improvements

### 1. Logistics Optimization
- **DROP/PICKUP Fixes**: 
  - Implement a check to ensure that DROP does not dump the entire inventory. Only DROP items that are intended for sale or storage.
  - Limit PICKUP actions to essential items only, aiming for a count significantly lower than 400 per game.

### 2. Pasture and Herd Management
- **Day 0 Pasture Reservation**:
  - Reserve a specific number of tiles (e.g., 10) for pasture immediately on Day 0 to ensure space for animal growth.
- **Animal Scaling**:
  - Prioritize scaling SHEEP initially, as they proved effective in Neo's strategy. Aim to place at least 4 animals (sheep and cows) by Day 3.
  - Gradually introduce cows as resources allow, targeting a balanced herd that can be sustained with available feed.

### 3. Market Interactions
- **Wheat Purchase for Feed**:
  - Implement a strategy to regularly BUY_PRODUCT WHEAT from the market, aiming for a range of 300-700 purchases per game to ensure sufficient feed for animals.
- **Market Delay**:
  - Maintain the same-turn market delay to avoid market timing issues and ensure transactions are processed correctly.

### 4. Plant Management
- **Cap Planting**:
  - Limit the number of plants to what can be effectively watered with available labor. This will prevent overplanting and reduce weed growth.
  - Monitor water availability and adjust planting accordingly to maintain a low weed count.

### 5. Financial Management
- **Land Purchase Delay**:
  - Delay purchasing additional land until cash reserves recover to a safer threshold (e.g., $500+). This will prevent early cash depletion and allow for strategic expansion.

## Acceptance Criteria
- The agent must consistently beat the S2 agent in local tests.
- The first 4 animals should be placed by Day 3.
- Maintain a low weed count throughout the game.
- Ensure PICKUP count remains significantly below 400 per game.

## Implementation Notes
- Retain the crash wrapper to handle unexpected errors gracefully.
- Continuously monitor and adjust strategies based on in-game performance and opponent behavior.

By implementing these strategies, the S3 agent should demonstrate improved performance, particularly against stronger opponents, while maintaining efficient resource management and logistics.
```