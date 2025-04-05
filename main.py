from pipelines.names_pipeline import DataQualityPipeline

GURS_file_path = 'src/raw_data/RN_SLO_NASLOVI_register_naslovov_20240929.csv'

pipeline = DataQualityPipeline(GURS_file_path, dataset_size=10000)
pipeline.run()

df = pipeline.get_data()
print(df.head())
