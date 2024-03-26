import json
import datetime
from typing import Union, List
from fastapi import APIRouter
from fastapi import Request
from pydantic import BaseModel
import pandas as pd
from icecream import ic


router = APIRouter()



@router.post("/process")
async def process(request: Request):
    
    body_dict = await request.json()
    print(body_dict)
    
    summary = body_dict.get("issue", {}).get("fields", {}).get("summary", None)
    
    with open(f"temp_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.json", "w") as f:
        json.dump(body_dict, f)

    return {"summary": summary}




@router.post("/calculate_roof_price_per_quarter")
async def calculate_roof_price_per_quarter(request: Request):
    body_dict = await request.json()
    
    df = pd.json_normalize(body_dict.get("time_series_data"))

    ev_comfort_charge_capacity_kwh = int(body_dict.get("ev_comfort_charge_capacity_kwh"))
    ev_max_charge_capacity_kwh = int(body_dict.get("ev_max_charge_capacity_kwh"))
    buffer = float(body_dict.get("buffer"))
    
    with open(f"data_request_body_jsons/temp_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.json", "w") as f:
        json.dump(body_dict, f)
    

    ev_pmax = 22  # kW
    ev_charged_per_quarter = ev_pmax / 4  # kWh


    ev_charging_quarters_count_comfort = ev_comfort_charge_capacity_kwh / ev_charged_per_quarter
    ev_charging_quarters_count_max = ev_max_charge_capacity_kwh / ev_charged_per_quarter

    ic(ev_charging_quarters_count_comfort)
    ic(ev_charging_quarters_count_max)

    total_quarters_count = len(df)

    percent_of_quarters_needed_comfort = ev_charging_quarters_count_comfort / total_quarters_count
    percent_of_quarters_needed_max = ev_charging_quarters_count_max / total_quarters_count

    ic(percent_of_quarters_needed_comfort)
    ic(percent_of_quarters_needed_max)

    df['is_in_lowest_quarters_comfort'] = df['Negative imbalance price'] <= df['Negative imbalance price'].quantile(percent_of_quarters_needed_comfort)
    df['is_in_lowest_quarters_max'] = df['Negative imbalance price'] <= df['Negative imbalance price'].quantile(percent_of_quarters_needed_max)

    pd.set_option('display.max_rows', None)
    print(df)

    highest_price_in_lowest_quarters_comfort = df[df['is_in_lowest_quarters_comfort']]['Negative imbalance price'].max()
    highest_price_in_lowest_quarters_max = df[df['is_in_lowest_quarters_max']]['Negative imbalance price'].max()

    # TODO room for improvement here, it could be somewhere between highest_price_in_lowest_quarters_comfort
    #      (if that's below 0) and highest_price_in_lowest_quarters_max
    if highest_price_in_lowest_quarters_max > 0:
        highest_price_in_lowest_quarters_max = highest_price_in_lowest_quarters_comfort

    return {
        "roof_comfort": highest_price_in_lowest_quarters_comfort,
        "roof_max": highest_price_in_lowest_quarters_max
    }