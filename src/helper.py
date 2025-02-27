"""Helper functions"""

def calculate_change(old, new):
    """
    Compute the percentage change from old to new value.
    
    Args:
        old (float): Initial Gini value.
        new (float): New Gini value.
    
    Returns:
        float or None: Percentage change if both values exist, otherwise None.
    """
    if not old or not new:
        return None
    return ((new - old) / old) * 100
