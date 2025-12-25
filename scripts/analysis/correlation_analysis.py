#!/usr/bin/env python3
"""
Statistical correlation analysis between MTR proximity and demographic variables.
"""

import pandas as pd
import numpy as np
from pathlib import Path
from scipy import stats
from scipy.stats import pearsonr, spearmanr
import os

def load_analysis_data() -> pd.DataFrame:
    """
    Load combined analysis dataset with MTR proximity and demographics.
    """
    project_root = Path(__file__).parent.parent.parent
    
    # Try to load demographic-integrated data
    demo_file = project_root / 'data' / 'analysis' / 'mtr_impact_analysis.csv'
    
    if demo_file.exists():
        return pd.read_csv(demo_file)
    
    # Fallback to spatial join data
    spatial_file = project_root / 'data' / 'analysis' / 'mtr_tpu_spatial_join_all_years.csv'
    
    if spatial_file.exists():
        return pd.read_csv(spatial_file)
    
    print("Error: No analysis data found")
    return pd.DataFrame()


def calculate_correlations(df: pd.DataFrame, demographic_vars: list = None) -> pd.DataFrame:
    """
    Calculate correlations between MTR proximity and demographic variables.
    """
    if df.empty:
        return pd.DataFrame()
    
    print("Calculating correlations...")
    
    # MTR proximity variables
    mtr_vars = ['nearest_mtr_distance', 'has_mtr_station', 'mtr_stations_count',
                'within_500m_buffer', 'within_1000m_buffer', 'within_2000m_buffer']
    
    # Available demographic variables (to be populated when data is available)
    if demographic_vars is None:
        # Look for demographic columns
        demographic_vars = [col for col in df.columns 
                           if any(keyword in col.lower() for keyword in 
                                 ['population', 'income', 'age', 'education', 'housing', 'employment'])]
    
    if not demographic_vars:
        print("  No demographic variables found in data")
        print("  Available columns:", list(df.columns)[:20])
        return pd.DataFrame()
    
    # Calculate correlations
    correlations = []
    
    for mtr_var in mtr_vars:
        if mtr_var not in df.columns:
            continue
        
        for demo_var in demographic_vars:
            if demo_var not in df.columns:
                continue
            
            # Remove missing values
            data_subset = df[[mtr_var, demo_var]].dropna()
            
            if len(data_subset) < 10:  # Need minimum data points
                continue
            
            # Calculate Pearson correlation
            try:
                if data_subset[mtr_var].dtype in ['object', 'bool']:
                    # For categorical variables, use different approach
                    continue
                
                pearson_r, pearson_p = pearsonr(data_subset[mtr_var], data_subset[demo_var])
                
                correlations.append({
                    'mtr_variable': mtr_var,
                    'demographic_variable': demo_var,
                    'pearson_r': pearson_r,
                    'pearson_p': pearson_p,
                    'n_samples': len(data_subset),
                    'significant': pearson_p < 0.05
                })
            except Exception as e:
                continue
    
    if correlations:
        corr_df = pd.DataFrame(correlations)
        return corr_df.sort_values('pearson_p')
    
    return pd.DataFrame()


def regression_analysis(df: pd.DataFrame, dependent_var: str, 
                       independent_vars: list) -> dict:
    """
    Perform multiple regression analysis.
    """
    try:
        from sklearn.linear_model import LinearRegression
        from sklearn.metrics import r2_score
        
        # Prepare data
        X = df[independent_vars].dropna()
        y = df[dependent_var].loc[X.index]
        
        if len(X) < 10:
            return None
        
        # Fit model
        model = LinearRegression()
        model.fit(X, y)
        
        # Calculate R-squared
        y_pred = model.predict(X)
        r2 = r2_score(y, y_pred)
        
        return {
            'dependent_variable': dependent_var,
            'independent_variables': independent_vars,
            'r_squared': r2,
            'coefficients': dict(zip(independent_vars, model.coef_)),
            'intercept': model.intercept_,
            'n_samples': len(X)
        }
    except Exception as e:
        print(f"  Regression error: {e}")
        return None


def compare_groups(df: pd.DataFrame, demographic_var: str) -> dict:
    """
    Compare demographic variables between MTR-adjacent and non-adjacent TPUs.
    """
    if demographic_var not in df.columns:
        return None
    
    # Define groups
    mtr_adjacent = df[df['within_1000m_buffer'] == True][demographic_var].dropna()
    mtr_non_adjacent = df[df['within_1000m_buffer'] == False][demographic_var].dropna()
    
    if len(mtr_adjacent) == 0 or len(mtr_non_adjacent) == 0:
        return None
    
    # Statistical test (t-test or Mann-Whitney)
    try:
        if len(mtr_adjacent) > 30 and len(mtr_non_adjacent) > 30:
            # Use t-test for large samples
            stat, p_value = stats.ttest_ind(mtr_adjacent, mtr_non_adjacent)
            test_type = 't-test'
        else:
            # Use Mann-Whitney U test for small samples
            stat, p_value = stats.mannwhitneyu(mtr_adjacent, mtr_non_adjacent)
            test_type = 'mann-whitney'
        
        return {
            'demographic_variable': demographic_var,
            'mtr_adjacent_mean': mtr_adjacent.mean(),
            'mtr_adjacent_median': mtr_adjacent.median(),
            'mtr_non_adjacent_mean': mtr_non_adjacent.mean(),
            'mtr_non_adjacent_median': mtr_non_adjacent.median(),
            'difference': mtr_adjacent.mean() - mtr_non_adjacent.mean(),
            'test_statistic': stat,
            'p_value': p_value,
            'significant': p_value < 0.05,
            'test_type': test_type,
            'n_adjacent': len(mtr_adjacent),
            'n_non_adjacent': len(mtr_non_adjacent)
        }
    except Exception as e:
        print(f"  Statistical test error: {e}")
        return None


def correlation_analysis():
    """
    Perform comprehensive correlation analysis.
    """
    project_root = Path(__file__).parent.parent.parent
    
    # Load data
    df = load_analysis_data()
    
    if df.empty:
        print("Error: No data available for analysis")
        return
    
    print("=" * 60)
    print("Correlation Analysis: MTR Proximity vs. Demographics")
    print("=" * 60)
    
    # Calculate correlations
    correlations = calculate_correlations(df)
    
    if not correlations.empty:
        # Save correlations
        output_file = project_root / 'data' / 'analysis' / 'correlation_results.csv'
        correlations.to_csv(output_file, index=False)
        
        print(f"\nSaved correlation results to {output_file}")
        print(f"Total correlations calculated: {len(correlations)}")
        print(f"Significant correlations (p < 0.05): {correlations['significant'].sum()}")
        
        # Show top correlations
        if len(correlations) > 0:
            print("\nTop 10 strongest correlations:")
            top_corr = correlations.nlargest(10, 'pearson_r')
            for idx, row in top_corr.iterrows():
                sig = "*" if row['significant'] else ""
                print(f"  {row['mtr_variable']} vs {row['demographic_variable']}: "
                      f"r={row['pearson_r']:.3f}, p={row['pearson_p']:.3f}{sig}")
    else:
        print("\nNo correlations calculated (demographic data needed)")
    
    # Group comparisons
    print("\nPerforming group comparisons...")
    demographic_vars = [col for col in df.columns 
                       if any(keyword in col.lower() for keyword in 
                             ['population', 'income', 'age', 'education'])]
    
    group_comparisons = []
    for var in demographic_vars[:5]:  # Limit to first 5 for now
        result = compare_groups(df, var)
        if result:
            group_comparisons.append(result)
    
    if group_comparisons:
        comp_df = pd.DataFrame(group_comparisons)
        comp_file = project_root / 'data' / 'analysis' / 'group_comparisons.csv'
        comp_df.to_csv(comp_file, index=False)
        
        print(f"Saved group comparisons to {comp_file}")
        print(f"\nGroup Comparison Summary:")
        for result in group_comparisons:
            sig = "*" if result['significant'] else ""
            print(f"  {result['demographic_variable']}: "
                  f"Adjacent={result['mtr_adjacent_mean']:.2f}, "
                  f"Non-adjacent={result['mtr_non_adjacent_mean']:.2f}, "
                  f"p={result['p_value']:.3f}{sig}")
    else:
        print("  No group comparisons performed (demographic data needed)")
    
    print("\n" + "=" * 60)
    print("Correlation analysis complete!")
    print("=" * 60)
    print("\nNote: Full analysis requires demographic data.")
    print("Once demographic data is integrated, this script will calculate")
    print("correlations and perform regression analysis.")


if __name__ == '__main__':
    correlation_analysis()

