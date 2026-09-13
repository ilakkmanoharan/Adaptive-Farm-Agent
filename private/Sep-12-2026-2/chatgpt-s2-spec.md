```markdown
# Submission 2 Specification

## Diagnosis of v1 Losses
- **Production Scale**: The current strategy is too conservative, focusing on minimal production with limited crop types and livestock. This results in lower revenue compared to opponents who scale aggressively.
- **Idle Actions**: A significant number of `PASS` actions indicate inefficient worker routing and underutilization of available resources.
- **Market Strategy**: Lack of diversification in market actions, especially in selling high-value products like milk and strawberries, limits income potential.

## Target Portfolio and Timing
- **Crops**:
  - **Wheat**: Increase planting to support both feed and market sales. Aim for 15-20 wheat plants by day 10.
  - **Melons**: Maintain initial planting of 5 melons but focus on selling them earlier to free up space.
  - **Strawberries**: Introduce strawberries by day 5, aiming for 10-15 plants by day 15 to capitalize on their high market value.
- **Livestock**:
  - **Cows**: Acquire the first cow by day 5 and aim for 5 cows by day 15. Use `BUY_PRODUCT WHEAT` to ensure consistent feed supply.
  - **Sheep**: Limit to 2 sheep to focus resources on cows, which have higher milk output.
- **Land Expansion**: Purchase additional land by day 10 to accommodate increased crop and livestock production.
- **Hires**: Increase hires to 10 by day 15 to support expanded operations and reduce idle time.

## Feed Pipeline
- Implement a consistent feed supply using `BUY_PRODUCT WHEAT` to ensure cows are fed even if wheat production is insufficient.

## Worker Routing
- Optimize worker actions to minimize `PASS` actions. Prioritize tasks such as watering, harvesting, and feeding to ensure continuous production flow.

## Market Order Rules
- **Milk**: Prioritize selling milk daily to capitalize on its consistent demand.
- **Wool**: Sell wool as it becomes available, but do not prioritize increasing sheep numbers.
- **Melons**: Sell melons early to free up space for more profitable crops.
- **Strawberries**: Focus on selling strawberries once production scales, as they have high market value.

## What NOT to Change
- **Crash Safety**: Maintain current safety checks to prevent crashes.
- **Same-Turn Market Delay**: Avoid actions that require immediate market responses to prevent delays.

## Acceptance Tests
- **Performance**: Test against v1 and starter agent to ensure improved coin accumulation and reduced idle actions.
- **Stability**: Ensure no crashes occur during test runs.
- **Market Efficiency**: Validate that market actions result in increased revenue without causing resource shortages.

## Implementation Plan
- Update `main.py` to incorporate the above strategies using standard library functions. Focus on optimizing existing code to handle increased complexity without introducing new dependencies.
```
