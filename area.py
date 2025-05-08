import numpy as np
from scipy.stats import norm
from numpy.linalg import inv, solve
import polars as pl

def eblupFH(formula, vardir, method="REML", MAXITER=100, PRECISION=1e-4, B=0, data=None):
    """
    Empirical Best Linear Unbiased Prediction (EBLUP) based on Fay-Herriot model.

    Parameters:
    - formula: Patsy formula describing the model (e.g., 'y ~ x1 + x2').
    - vardir: Array-like, sampling variances for each domain.
    - method: Estimation method ('REML', 'ML', or 'FH').
    - MAXITER: Maximum number of iterations for convergence.
    - PRECISION: Convergence threshold.
    - B: Number of bootstrap iterations (not implemented in this version).
    - data: polars DataFrame containing the variables in the formula.

    Returns:
    - Dictionary containing EBLUP estimates, model coefficients, variance estimates, and goodness-of-fit measures.
    """
    import patsy

    if method not in ["REML", "ML", "FH"]:
        raise ValueError(f"method='{method}' must be 'REML', 'ML', or 'FH'.")

    # Prepare design matrix X and response vector y
    y, X = patsy.dmatrices(formula, data.to_pandas(), return_type='dataframe')
    y = y.values.flatten()
    X = X.values
    vardir = np.asarray(vardir)

    m = len(y)  # Number of areas
    p = X.shape[1]  # Number of predictors

    # Initialize variance component A
    A_est = [np.median(vardir)]
    k = 0
    diff = PRECISION + 1

    while diff > PRECISION and k < MAXITER:
        Vi = 1 / (A_est[k] + vardir)
        XtVi = X.T * Vi
        Q = inv(XtVi @ X)
        P = np.diag(Vi) - XtVi.T @ Q @ XtVi
        Py = P @ y

        if method == "ML":
            s = -0.5 * np.sum(Vi) + 0.5 * Py.T @ Py
            F = 0.5 * np.sum(Vi ** 2)
        elif method == "REML":
            s = -0.5 * np.trace(P) + 0.5 * Py.T @ Py
            F = 0.5 * np.trace(P @ P)
        elif method == "FH":
            beta_aux = Q @ XtVi @ y
            res_aux = y - X @ beta_aux
            s = np.sum((res_aux ** 2) * Vi) - (m - p)
            F = np.sum(Vi)

        A_new = A_est[k] + s / F
        A_est.append(A_new)
        diff = abs((A_est[k + 1] - A_est[k]) / A_est[k])
        k += 1

    A_final = max(A_est[-1], 0)

    # Check convergence
    convergence = k < MAXITER or diff < PRECISION

    # Compute beta estimates
    Vi = 1 / (A_final + vardir)
    XtVi = X.T * Vi
    Q = inv(XtVi @ X)
    beta_hat = Q @ XtVi @ y

    # Compute standard errors, t-values, and p-values
    std_error_beta = np.sqrt(np.diag(Q))
    t_values = beta_hat / std_error_beta
    p_values = 2 * norm.sf(np.abs(t_values))

    # Compute EBLUP
    X_beta = X @ beta_hat
    resid = y - X_beta
    eblup = X_beta + A_final * Vi * resid

    # Compute goodness-of-fit measures
    loglike = -0.5 * np.sum(np.log(2 * np.pi * (A_final + vardir)) + (resid ** 2) / (A_final + vardir))
    AIC = -2 * loglike + 2 * (p + 1)
    BIC = -2 * loglike + (p + 1) * np.log(m)
    min2loglike = -2 * loglike
    KIC = min2loglike + 3 * (p + 1)

    # Compile results
    coef_table = {
        'beta': beta_hat,
        'std.error': std_error_beta,
        'tvalue': t_values,
        'pvalue': p_values
    }

    result = {
        'eblup': eblup,
        'fit': {
            'method': method,
            'convergence': convergence,
            'iterations': k,
            'estcoef': coef_table,
            'refvar': A_final,
            'goodness': {
                'loglike': loglike,
                'AIC': AIC,
                'BIC': BIC,
                'KIC': KIC
            }
        }
    }

    return result


def mseFH(formula, vardir_col, method="REML", MAXITER=100, PRECISION=1e-4, B=0, data=None):
    result = {"est": None, "mse": None}

    if data is not None:
        y = data.select(formula.split('~')[0].strip()).to_numpy().flatten()
        X_cols = [col.strip() for col in formula.split('~')[1].split('+')]
        X = data.select(X_cols).to_numpy()
        vardir = data[vardir_col].to_numpy()
    else:
        raise ValueError("Data must be provided as a polars DataFrame.")

    if np.any(np.isnan(y)) or np.any(np.isnan(vardir)):
        raise ValueError("NA values found in response or vardir.")

    # Estimation step (you must provide this function)
    result["est"] = eblupFH(formula, vardir, method, MAXITER, PRECISION, B, data)
    if not result["est"]["fit"]["convergence"]:
        print("Warning: The fitting method does not converge.")
        return result

    A = result["est"]["fit"]["refvar"]
    m, p = X.shape
    Vi = 1 / (A + vardir)
    Bd = vardir / (A + vardir)
    SumAD2 = np.sum(Vi**2)
    XtVi = (Vi[:, np.newaxis] * X).T
    Q = solve(XtVi @ X, np.eye(p))

    g1d = vardir * (1 - Bd)
    g2d = np.array([(Bd[d]**2) * X[d:d+1] @ Q @ X[d:d+1].T for d in range(m)]).flatten()
    g3d = (Bd**2) * (2 / SumAD2) / (A + vardir)

    if method == "REML" or method == "ML":
        VarA = 2 / SumAD2
        if method == "ML":
            b = -np.trace(Q @ (XtVi @ (Vi[:, np.newaxis] * X))) / SumAD2
            mse2d = g1d + g2d + 2 * g3d - b * (Bd**2)
        else:
            mse2d = g1d + g2d + 2 * g3d
    else:  # FH
        SumAD = np.sum(Vi)
        VarA = 2 * m / (SumAD**2)
        b = 2 * (m * SumAD2 - SumAD**2) / (SumAD**3)
        g3d = (Bd**2) * VarA / (A + vardir)
        mse2d = g1d + g2d + 2 * g3d - b * (Bd**2)

    result["mse"] = mse2d
    return result

if __name__ == "__main__":
    # Import the data using polars
    data = pl.read_csv("data.csv")

    # Define the formula, vardir_col, and other parameters
    formula = "y ~ x1 + x2"  # Replace with your actual formula
    vardir_col = "vardir"  # Replace with your actual variance column name

    # Call the mseFH function
    result = mseFH(formula=formula, vardir_col=vardir_col, method="REML", data=data)

    # Print the results
    print("Estimation Results:", result["est"])
    print("MSE Results:", result["mse"])