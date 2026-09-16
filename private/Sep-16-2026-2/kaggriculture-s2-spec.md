# Kaggriculture Submission 2 Specification
Date: 2026-09-16 · Slot: s2 · Folder: `2026-09-16-s2/`

Previous Kaggle id: 56273013
Sources: pulled live episodes + ChatGPT (`gpt-4o`).

# Kaggriculture Next Submission Plan

## 1. Ladder Facts from Previous Games
- **Record:** 0 Wins - 0 Ties - 0 Losses
- **Mean Our Bank:** Not available (no games completed)
- **Opponents:** No data on who beat us or how, as no games have been completed.

## 2. Root Causes We Must Fix
Since we have no completed games, we will focus on potential issues based on common pitfalls:
- **Inventory Management:** Avoid unnecessary DROP/PICKUP actions that can lead to thrashing and wasted turns.
- **Animal Management:** Ensure optimal herd size to maximize production without overextending resources.
- **Crop Purchases:** Balance wheat buys to maintain a steady supply without overstocking.
- **Weed Management:** Prioritize weed removal to prevent crop yield penalties.
- **Land Utilization:** Optimize land usage timing to ensure maximum productivity.

## 3. Exact S2 Policy Table vs Previous Bot
- **Inventory Management:**
  - Prioritize PLACE actions for harvest goods to avoid inventory overflow.
  - Avoid DROP actions entirely; manage inventory through strategic PLACE and SELL actions.
  
- **Animal Management:**
  - Maintain a balanced herd size based on available resources and land capacity.
  - Focus on high-yield animals and avoid over-purchasing.

- **Crop Purchases:**
  - Implement a threshold for wheat purchases to prevent overstocking (e.g., maintain a maximum of 100 units in inventory).
  - Prioritize purchasing seeds that align with current land and resource availability.

- **Weed Management:**
  - Schedule regular weed removal actions to maintain crop health and yield.

- **Land Utilization:**
  - Plan land expansions based on current and projected resource availability.
  - Ensure land is always utilized for either crops or animals to maximize productivity.

## 4. Task Priority
1. Implement inventory management improvements to prevent DROP/PICKUP thrash.
2. Optimize animal management to maintain a productive herd size.
3. Balance crop purchases to avoid overstocking and ensure steady supply.
4. Schedule regular weed management actions.
5. Plan land utilization to maximize productivity.

## 5. Local Acceptance Gates Before Kaggle Upload
- **Simulation Testing:** Run local simulations to ensure the new policy table leads to improved inventory management and resource utilization.
- **Performance Metrics:** Verify that the new strategy maintains or improves bank balance over multiple simulated games.
- **Code Review:** Ensure the main.py implementation adheres to the outlined policy table and task priorities.

## 6. Non-Goals
- **Reinforcement Learning (RL):** Do not implement RL strategies in this submission.
- **Opponent Shop Denial:** Avoid strategies focused on denying opponents access to shop items.

---

Implement the above strategy in the `2026-09-16-s2/` folder, ensuring all changes are confined to a single `main.py` file. Focus on improving resource management and productivity without introducing complex algorithms or opponent-focused strategies.
