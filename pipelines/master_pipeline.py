from pipelines.names_pipeline import run_name_pipeline
# from pipeline.email_pipeline import run_email_pipeline
# from pipeline.address_pipeline import run_address_pipeline

def run_full_quality_pipeline(df):
    df = run_name_pipeline(df)
    # df = run_email_pipeline(df)
    # df = run_address_pipeline(df)
    # df = run_phone_pipeline(df)
    return df
