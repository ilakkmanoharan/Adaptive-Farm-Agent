# Kaggriculture Submission 5 Specification
Date: 2026-09-15 · Slot: s5 · Folder: `2026-09-15-s5/`

Previous Kaggle id: 56263176
Sources: pulled live episodes + ChatGPT (`gpt-4o`).

# Kaggriculture Next Submission Plan

## 1. Ladder Facts from Previous Games
- **Record:** 0 Wins, 0 Ties, 0 Losses
- **Mean Bank:** Not available (no completed games)
- **Opponents:** No data on who beat us or how, as no games have been completed.

## 2. Root Causes to Fix
Since there are no completed games, we will focus on optimizing our initial strategy based on common pitfalls:
- **Inventory Management:** Avoid unnecessary DROP actions that result in loss of inventory.
- **Animal Management:** Ensure optimal herd size to maximize production without exceeding feed capacity.
- **Crop Management:** Optimize wheat purchases to balance between immediate needs and future growth.
- **Weed Control:** Implement timely weed removal to prevent crop yield reduction.
- **Land Utilization:** Ensure efficient use of land, balancing between crops and animals.

## 3. Exact S5 Policy Table vs Previous Bot
### Inventory Management
- **PLACE item n:** Use this action for harvested goods only. Ensure that all harvested goods are placed in the shed before the market phase.
- **Avoid DROP:** Do not use DROP under any circumstances.

### Animal Management
- **Herd Size:** Maintain a herd size that matches available feed. Prioritize feeding over expanding the herd if feed is limited.
- **Animal Purchases:** Only purchase animals if there is sufficient feed and land available.

### Crop Management
- **Wheat Purchases:** Purchase wheat seeds based on current and projected needs. Avoid over-purchasing to prevent waste.
- **Crop Rotation:** Implement a crop rotation strategy to maximize yield and minimize soil depletion.

### Weed Control
- **Timely Weeding:** Schedule weeding actions to occur just before crops reach maturity to ensure maximum yield.

### Land Utilization
- **Land Allocation:** Allocate land based on a balanced approach between crops and animals. Adjust based on market trends and inventory needs.

## 4. Task Priority
1. **Implement Inventory Management Strategy:** Ensure PLACE item n is used effectively.
2. **Optimize Animal Management:** Adjust herd size and feed strategy.
3. **Refine Crop Management:** Balance wheat purchases and implement crop rotation.
4. **Enhance Weed Control:** Schedule weeding actions effectively.
5. **Improve Land Utilization:** Optimize land allocation for crops and animals.

## 5. Local Acceptance Gates Before Kaggle Upload
- **Simulation Testing:** Run local simulations to ensure the new strategy does not result in inventory loss or inefficient resource use.
- **Performance Metrics:** Ensure that the strategy improves bank balance and resource utilization in test scenarios.
- **Code Review:** Conduct a thorough code review to ensure all changes are correctly implemented and do not introduce errors.

## 6. Non-Goals
- **No Reinforcement Learning (RL):** The strategy will not involve RL techniques.
- **No Opponent Shop Denial:** We will not implement strategies that focus on denying resources to opponents.
- **No Complex Market Predictions:** The strategy will not involve complex market prediction algorithms.

This plan is designed to be implemented in one `main.py` file within the `2026-09-15-s5/` folder, building upon the previous submission's codebase.
