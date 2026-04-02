import sys, logging
logging.basicConfig(level=logging.INFO)
from website.backend.pipeline import predict_for_district

district = sys.argv[1]
date     = sys.argv[2]

results_df, rmse_df = predict_for_district(district, date)
print(results_df.to_string(index=False))
