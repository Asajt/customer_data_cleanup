# pipeline/controller.py

import pandas as pd
import phonenumbers
from utils.customer_data_generator import generate_synthetic_customer_data
from utils.chaos_engineering import apply_errors
from detection.detect_phone import detect_phone_errors
from detection.detect_email import detect_email_errors
from detection.detect_address import detect_address_errors
from detection.detect_names import detect_name_errors
from validation.validate_address import validate_full_address
from validation.validate_name import validate_name
from correction.correct_address import correct_address_errors
# from correction.correct_name import correct_name_errors
# from evaluation.metrics import evaluate_pipeline
import phonenumbers
import re


class DataQualityPipeline:
    def __init__(self, gurs_file_path: str, dataset_size=10000, seed=42):
        self.gurs_file_path = gurs_file_path
        self.dataset_size = dataset_size
        self.seed = seed
        self.df = None

    def generate_data(self):
        print("✅ Step 1: Generating synthetic data...")
        self.df = generate_synthetic_customer_data(self.gurs_file_path, self.dataset_size, self.seed)

    def inject_errors(self):
        print("⚠️ Step 2: Injecting errors...")
        self.df = apply_errors(self.df)

    def build_full_address(self):
        self.df["FULL_ADDRESS"] = (
            self.df["STREET"].str.strip() + " " +
            self.df["HOUSE_NUMBER"].str.strip() + ", " +
            self.df["POSTAL_CODE"].str.strip() + " " +
            self.df["POSTAL_CITY"].str.strip()
        )

    def validate_data(self):
        print("🔍 Step 3: Validating address and name data...")
        self.build_full_address()

        self.df["IS_ADDRESS_VALID"] = validate_full_address(
            customer_full_address=self.df["FULL_ADDRESS"],
            path_to_gurs_RN_csv=self.gurs_file_path
        )

        self.df["IS_NAME_VALID"] = self.df.apply(
            lambda row: validate_name(row["FIRST_NAME"], row["LAST_NAME"]),
            axis=1
        )

        self.df["IS_EMAIL_VALID"] = self.df["EMAIL"].apply(self.validate_email_format)
        self.df["IS_PHONE_VALID"] = self.df["PHONE"].apply(self.validate_phone_number)

    def detect_errors(self):
        print("🧪 Step 4: Detecting errors for invalid rows...")

        # Detect only for invalid rows
        detect_address_errors(self.df[~self.df["IS_ADDRESS_VALID"]])
        detect_name_errors(self.df[~self.df["IS_NAME_VALID"]])
        detect_email_errors(self.df[~self.df["IS_EMAIL_VALID"]])
        detect_phone_errors(self.df[~self.df["IS_PHONE_VALID"]])

    def correct_errors(self):
        print("🛠 Step 5: Correcting errors for invalid rows...")

        # Address corrections
        corrected_addresses = correct_address_errors(self.df[~self.df["IS_ADDRESS_VALID"]])
        self.df.update(corrected_addresses)
        self.df["WAS_ADDRESS_CORRECTED"] = False
        self.df.loc[~self.df["IS_ADDRESS_VALID"], "WAS_ADDRESS_CORRECTED"] = True

        # Name corrections
        corrected_names = correct_name_errors(self.df[~self.df["IS_NAME_VALID"]])
        self.df.update(corrected_names)
        self.df["WAS_NAME_CORRECTED"] = False
        self.df.loc[~self.df["IS_NAME_VALID"], "WAS_NAME_CORRECTED"] = True

    def create_report(self):
        print("📊 Step 6: Creating report...")
        # Just printing stats for now
        print("Valid addresses:", self.df["IS_ADDRESS_VALID"].sum())
        print("Corrected addresses:", self.df["WAS_ADDRESS_CORRECTED"].sum())
        print("Valid names:", self.df["IS_NAME_VALID"].sum())
        print("Corrected names:", self.df["WAS_NAME_CORRECTED"].sum())

    def evaluate(self):
        print("📈 Step 7: Evaluating pipeline performance...")
        evaluate_pipeline(self.df)  # you can define precision/recall here

    def run(self):
        self.generate_data()
        self.inject_errors()
        self.validate_data()
        self.detect_errors()
        self.correct_errors()
        self.create_report()
        self.evaluate()

    def get_data(self):
        return self.df

    # ========== UTILITIES ==========

    def validate_email_format(self, email: str) -> bool:
        email_regex = re.compile(r"(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)")
        return bool(email_regex.match(email))

    def validate_phone_number(self, phone: str, region: str = "SI") -> bool:
        try:
            number = phonenumbers.parse(phone, region)
            return phonenumbers.is_possible_number(number) and phonenumbers.is_valid_number(number)
        except phonenumbers.NumberParseException:
            return False
