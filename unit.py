import numpy as np
import polars as pl
from typing import List, Optional
from dataclasses import dataclass
import warnings

@dataclass
class BHFResult:
    est: Optional[dict] = None
    mse: Optional[pl.DataFrame] = None

def pbmseBHF(formula: str,
             dom: pl.Series,
             selectdom: Optional[List] = None,
             meanxpop: pl.DataFrame = None,
             popnsize: pl.DataFrame = None,
             B: int = 200,
             method: str = "REML",
             data: pl.DataFrame = None) -> BHFResult:
    """
    Parametric bootstrap MSE estimation for EBLUP under Battese-Harter-Fuller (BHF) model.
    """
    import patsy

    result = BHFResult()
    if data is None:
        raise ValueError("`data` must be provided as a DataFrame.")

    # Convert Polars DataFrame to Pandas for patsy compatibility
    data_pd = data.to_pandas()
    y, X = patsy.dmatrices(formula, data_pd, return_type="dataframe")
    y = y.iloc[:, 0]
    dom_series = dom.to_pandas().reset_index(drop=True)
    X = X.reset_index(drop=True)

    if selectdom is None:
        selectdom = dom_series.unique()
    else:
        selectdom = np.unique(selectdom)
        
    valid_domains = [d for d in dom_series.unique() if (dom_series == d).sum() > 1]
    selectdom = np.intersect1d(selectdom, valid_domains)

    # Add intercept if necessary
    intercept = "Intercept" in X.columns
    p = X.shape[1]

    if intercept and p == meanxpop.shape[1]:
        meanxpop = pl.concat([
            meanxpop[:, 0].to_frame(),
            pl.DataFrame(np.ones((meanxpop.shape[0], 1))),
            meanxpop[:, 1:]
        ], how="horizontal")

    # Initial model fit (simulate eblupBHF)
    beta_est = np.linalg.lstsq(X, y, rcond=None)[0].reshape(-1, 1)
    residuals = y.values - (X.to_numpy() @ beta_est).flatten()
    sigma_e2 = np.var(residuals)
    sigma_u2 = 1.0  # Placeholder

    unique_doms = dom_series.unique()
    D = len(unique_doms)
    nd = np.array([(dom_series == d).sum() for d in unique_doms])
    I = len(selectdom)

    # Prepare population means and sizes
    Ni = popnsize.filter(popnsize[popnsize.columns[0]].is_in(selectdom)).select(popnsize.columns[1]).to_numpy().flatten()
    meanx_selected = meanxpop.filter(meanxpop[meanxpop.columns[0]].is_in(selectdom)).select(meanxpop.columns[1:]).to_numpy()
    if intercept and p == meanx_selected.shape[1] + 1:
        meanx_selected = np.concatenate([np.ones((I, 1)), meanx_selected], axis=1)

    mud_B = np.dot(meanx_selected, beta_est).flatten()
    SampSize_selectdom = np.array([nd[list(unique_doms).index(d)] if d in unique_doms else 0 for d in selectdom])
    valid_domains = np.intersect1d(selectdom, popnsize[popnsize.columns[0]].to_numpy())
    selectdom = valid_domains

    # Recalculate `Ni` and `SampSize_selectdom` with the updated `selectdom`
    Ni = popnsize.filter(popnsize[popnsize.columns[0]].is_in(selectdom)).select(popnsize.columns[1]).to_numpy().flatten()
    SampSize_selectdom = np.array([nd[list(unique_doms).index(d)] if d in unique_doms else 0 for d in selectdom])

    # Ensure `Ni` and `SampSize_selectdom` have the same shape
    rd = Ni - SampSize_selectdom

    mse_B = np.zeros(I)
    true_mean_B = np.zeros(I)

    print(f"\nBootstrap procedure with B = {B} iterations starts.")
    b = 0
    while b < B:
        ys_B = y.copy()
        ud_B = np.random.normal(0, np.sqrt(sigma_u2), size=D)
        esd_mean_B = []

        for i, d in enumerate(unique_doms):
            rows = (dom_series == d)
            esd = np.random.normal(0, np.sqrt(sigma_e2), size=nd[i])
            # Ensure the right-hand side is flattened to match the shape of ys_B.loc[rows]
            ys_B.loc[rows] = (X.loc[rows].values @ beta_est).flatten() + ud_B[i] + esd
            esd_mean_B.append(np.mean(esd))

        for i, d in enumerate(selectdom):
            if d in unique_doms:
                posd = list(unique_doms).index(d)
                erd_mean_B = np.random.normal(0, np.sqrt(sigma_e2 / rd[i])) if rd[i] > 0 else 0
                ed_mean_B = esd_mean_B[posd] * nd[posd] / Ni[i] + erd_mean_B * rd[i] / Ni[i]
                true_mean_B[i] = mud_B[i] + ud_B[posd] + ed_mean_B
            else:
                true_mean_B[i] = mud_B[i] + np.random.normal(0, np.sqrt(sigma_u2))

        beta_boot = np.linalg.lstsq(X, ys_B, rcond=None)[0].reshape(-1, 1)
        mean_EB = np.dot(meanx_selected, beta_boot).flatten()

        mse_B += (mean_EB - true_mean_B) ** 2
        b += 1
        print(f"b = {b}")

    mse_df = pl.DataFrame({
        "domain": selectdom,
        "mse": mse_B / B
    })

    result.mse = mse_df
    return result

def main():
    # Load data from pseudo.csv
    data = pl.read_csv("peudo.csv")
    dom = data["County"]
    meanxpop = data.select(["CountyIndex", "MeanCornPixPerSeg", "MeanSoyBeansPixPerSeg"])
    popnsize = data.select(["CountyIndex", "PopnSegments"])

    # Example usage of pbmseBHF
    formula = "CornHec ~ CornPix + SoyBeansPix"
    result = pbmseBHF(
        formula=formula,
        dom=dom,
        meanxpop=meanxpop,
        popnsize=popnsize,
        data=data
    )

    print(result)

if __name__ == "__main__":
    main()