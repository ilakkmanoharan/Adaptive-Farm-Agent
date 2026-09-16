# Kaggriculture Next Submission Plan

## Ladder Facts from Recent Games
- **Record:** 0 Wins, 0 Ties, 0 Losses
- **Mean Bank:** Not applicable as no games have been played yet.
- **Opponents:** No opponents have been faced yet; thus, no data on who beat us or how.

## Root Causes to Fix
Since no games have been played, we will focus on optimizing our initial strategy based on common pitfalls:
1. **Inventory Management:** Avoid unnecessary DROP actions that lead to loss of inventory.
2. **Herd Size Management:** Ensure optimal herd size to maximize milk production without overburdening resources.
3. **Wheat Purchases:** Balance wheat purchases to maintain a steady supply without overstocking.
4. **Weed Management:** Implement timely weed removal to prevent crop loss.
5. **Land Utilization Timing:** Optimize the timing of land use to maximize crop yield.

## Exact S1 Policy Table vs Previous Bot
Since this is our first submission, we will establish a baseline policy:
- **Initial Setup:**
  - Purchase 2 cows and 1 sheep for a balanced start in milk and wool production.
  - Buy 10 units of wheat to ensure initial feed supply.
- **Daily Actions:**
  - **Morning:** 
    - Feed animals with available wheat.
    - Harvest any mature crops.
  - **Midday:**
    - Sell harvested goods immediately to free up inventory space.
    - Purchase seeds if inventory space allows and funds are sufficient.
  - **Evening:**
    - Plant seeds on available land.
    - Remove weeds if present.

## Task Priority
1. **Implement Initial Setup Strategy:** Ensure the initial purchase of animals and wheat is coded correctly.
2. **Daily Action Routine:** Code the daily routine for feeding, harvesting, selling, and planting.
3. **Weed Management:** Implement a check for weeds and remove them as needed.
4. **Inventory Management:** Ensure no DROP actions are coded; focus on selling and using items efficiently.

## Local Acceptance Gates Before Kaggle Upload
1. **Simulation Test:** Run a local simulation to ensure the initial setup and daily actions execute without errors.
2. **Inventory Check:** Verify that no DROP actions are present in the code.
3. **Resource Utilization:** Ensure that resources (wheat, land, inventory space) are utilized efficiently.
4. **Error Handling:** Implement basic error handling to manage unexpected scenarios.

## Non-Goals
- **Opponent Shop Denial:** Do not focus on denying resources to opponents; prioritize our own strategy.
- **Reinforcement Learning (RL):** Avoid complex RL strategies; stick to a rule-based approach.
- **Advanced Market Predictions:** Do not attempt to predict market trends; focus on consistent execution of the strategy.

This plan should be implemented in one `main.py` file located in the `2026-09-16-s1/` folder. Ensure all code is thoroughly tested locally before submission to Kaggle.