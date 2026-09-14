# Kaggriculture Next Submission Plan

## 1. Ladder Facts from Previous Games
- **Record:** 0 Wins, 0 Ties, 0 Losses
- **Mean Our Bank:** Not available (no completed games)
- **Defeats:** No data on who beat us or how, as no games have been completed.

## 2. Root Causes We Must Fix
- **Inventory Management:** Avoid unnecessary DROP actions that result in loss of inventory.
- **Animal Management:** Ensure optimal herd size to maximize production without exceeding capacity.
- **Resource Allocation:** Balance wheat purchases to maintain a steady supply without overstocking.
- **Land Utilization:** Optimize timing for land expansion to ensure efficient use of resources.
- **Weed Control:** Implement strategies to minimize the impact of weeds on crop yield.

## 3. Exact S2 Policy Table vs the Previous Bot
- **Inventory Management:**
  - Use PLACE item n for harvest goods only when storage is full or near full.
  - Avoid DROP actions unless absolutely necessary.
- **Animal Management:**
  - Maintain a balanced herd size based on current land and resource availability.
  - Prioritize animals that provide the highest yield per resource consumed.
- **Resource Allocation:**
  - Monitor wheat levels closely and purchase only when below a critical threshold.
  - Avoid over-purchasing to prevent resource wastage.
- **Land Utilization:**
  - Expand land only when current capacity is fully utilized and resources allow.
  - Prioritize land expansions that offer the best return on investment.
- **Weed Control:**
  - Implement regular checks for weeds and remove them promptly to maintain crop health.

## 4. Task Priority
1. **Inventory Management Optimization**
2. **Animal Management Strategy**
3. **Resource Allocation Efficiency**
4. **Land Utilization Planning**
5. **Weed Control Implementation**

## 5. Local Acceptance Gates Before Kaggle Upload
- **Simulation Testing:** Run local simulations to ensure the new strategy does not result in negative bank balances or excessive inventory loss.
- **Performance Metrics:** Ensure the bot achieves at least a 70% efficiency in resource utilization and a 50% increase in yield compared to the previous submission.
- **Code Review:** Conduct a thorough review of the code to ensure compliance with the new strategy and absence of logical errors.

## 6. Non-goals
- **Opponent Shop Denial:** Do not implement strategies aimed at denying resources to opponents.
- **Reinforcement Learning (RL):** Avoid using RL techniques; focus on rule-based strategies.
- **Complex Market Predictions:** Do not attempt to predict market trends beyond basic supply and demand principles.

This plan should be implemented in one `main.py` file located in the `2026-09-14-s2/` folder. Ensure all changes are thoroughly tested locally before submission to Kaggle.