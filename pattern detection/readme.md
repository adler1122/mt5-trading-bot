

Pattern Types 

Fixed Setup Patterns
These patterns represent complete trade setups. Once detected, the only question is whether the market will hit TP or SL.  
This is treated as a binary classification problem.

Key traits:
Defined entry, TP, and SL
No need for prior trend context
Label: success = True/False

Modeling goal:
Predict the probability of TP being hit

Market Movement Patterns
These patterns indicate a change in market structure, such as trend reversal or breakout.  
They do not define a full setup, so the modeling task is regression.

Key traits:
Directional bias (up/down)
Magnitude of movement
Often context-dependent

Modeling goal:
Predict how far the market will move after the pattern appears

Why This Separation Matters

Fixed setups are clean, repeatable, and ideal for supervised classification
Market movement patterns are contextual, requiring deeper modeling and feature engineering
This separation allows us to build specialized models for each task

