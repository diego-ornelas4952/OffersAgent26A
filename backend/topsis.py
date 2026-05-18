import numpy as np
import pandas as pd

def topsis(data, weights, impacts):
    """
    Executes the TOPSIS algorithm with numerical stability checks.
    """
    # 1. Normalization
    matrix = data.values.astype(float)
    
    # Calculate norm, add tiny epsilon to avoid division by zero if all values are 0
    norm = np.sqrt(np.sum(matrix**2, axis=0))
    norm = np.where(norm == 0, 1e-9, norm) 
    
    norm_matrix = matrix / norm
    
    # 2. Weighted Normalization
    weighted_matrix = norm_matrix * weights
    
    # 3. Identify Ideal Positive and Negative Solutions
    ideal_best = []
    ideal_worst = []
    
    for i in range(len(impacts)):
        if impacts[i] == '+':
            ideal_best.append(np.max(weighted_matrix[:, i]))
            ideal_worst.append(np.min(weighted_matrix[:, i]))
        else:
            ideal_best.append(np.min(weighted_matrix[:, i]))
            ideal_worst.append(np.max(weighted_matrix[:, i]))
            
    ideal_best = np.array(ideal_best)
    ideal_worst = np.array(ideal_worst)
    
    # 4. Calculate Euclidean Distances
    dist_best = np.sqrt(np.sum((weighted_matrix - ideal_best)**2, axis=1))
    dist_worst = np.sqrt(np.sum((weighted_matrix - ideal_worst)**2, axis=1))
    
    # 5. Calculate Performance Score (Ci*)
    # Avoid division by zero if dist_best + dist_worst is zero
    denominator = dist_best + dist_worst
    scores = np.where(denominator == 0, 0.5, dist_worst / np.where(denominator == 0, 1, denominator))
    
    # 6. Ranking
    results = data.copy()
    results['topsis_score'] = scores
    # Use rank with method='min' and handle potential NaN if any (though epsilon prevents it)
    results['rank'] = results['topsis_score'].rank(ascending=False, method='min').fillna(1).astype(int)
    
    return results.sort_values(by='rank')
