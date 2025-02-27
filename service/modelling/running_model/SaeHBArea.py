import polars as pl
from PyQt6.QtWidgets import QMessageBox
from service.modelling.running_model.convert_df import convert_df

def run_model_hb_area(parent):
    import rpy2.robjects as ro
    parent.activate_R()
    df = parent.model1.get_data()
    df = df.drop_nulls()
    convert_df(df, parent)
    try:
        ro.r('suppressMessages(library(saeHB))')
        ro.r('data <- as.data.frame(r_df)')
        ro.r('attach(data)')
        ro.r(parent.r_script)
        ro.r('estimated_value <- model$Est')
        ro.r('sd <- model$sd')
        ro.r('refVar <- model$refVar')
        ro.r('coefficient <- model$coefficient')
        
        result_str = "Estimated Value:\n" + "\n".join(ro.r('capture.output(print(estimated_value))')) + "\n\n"
        result_str += "Standard Deviation:\n" + "\n".join(ro.r('capture.output(print(sd))')) + "\n\n"
        result_str += "Reference Variance:\n" + "\n".join(ro.r('capture.output(print(refVar))')) + "\n\n"
        result_str += "Coefficient:\n" + "\n".join(ro.r('capture.output(print(coefficient))')) + "\n"
        parent.result = result_str
        estimated_value = ro.conversion.rpy2py(ro.globalenv['estimated_value'])
        hb_mean = estimated_value["MEAN"]
        hb_25 = estimated_value["25%"]
        hb_50 = estimated_value["50%"]
        hb_75 = estimated_value["75%"]
        hb_97_5 = estimated_value["97.5%"]
        hb_sd = estimated_value["SD"]
        df = pl.DataFrame({
            'HB_Mean': hb_mean,
            'HB_25%': hb_25,
            'HB_50%': hb_50,
            'HB_75%': hb_75,
            'HB_97.5%': hb_97_5,
            'SD': hb_sd,})
        ro.r("detach(data)")
        parent.model2.set_data(df)
        
    except Exception as e:
        error_dialog = QMessageBox()
        error_dialog.setIcon(QMessageBox.Icon.Critical)
        error_dialog.setText("Error")
        error_dialog.setInformativeText(str(e))