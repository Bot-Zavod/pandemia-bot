import requests
from pprint import PrettyPrinter

pp = PrettyPrinter()


def get_hospital_needs():
    hospitals = pre_config()
    hospitals_data = final_format(hospitals)
    return hospitals_data


def pre_config():
    url = "https://api.pandemiia.in.ua/hospitals/needs/"
    needs = requests.get(url).json()
    # pp.pprint(needs)

    hospitals = dict()

    """
    PRE-CONFIGURE
    {
        hospital_id:{
            hospital_name: text,
            region: int,
            needs: [
                {
                    need_name: text,
                    needed: int,
                    recived: int
                }
            ]
        }
    }
    """

    for need in needs["results"]:
        if need["quantity"]["needed"]>0:
            if need["hospital"] not in hospitals:
                h = requests.get(f"https://api.pandemiia.in.ua/hospitals/{need['hospital']}/").json()
                hospital_name = h["name"]
                region = h['region']
                hospitals[need["hospital"]] = {
                                                "hospital_name": hospital_name,
                                                "region": region,
                                                "needs": []
                                            }
            hospitals[need["hospital"]]["needs"].append({
                "need_name": need["solution_type"]["name"],
                "needed": need["quantity"]["needed"],
                "received": need["quantity"]["received"]
            })
    # pp.pprint(hospitals)
    
    return hospitals


def final_format(hospitals):
    hospitals_data = dict()
    region_ids = {r["region"] for r in hospitals.values()}

    regions = requests.get("https://api.pandemiia.in.ua/hospitals/regions/").json()
    regions = {r["key"]: r["name"] for r in regions}

    """
    FINAL FORMAT
    {
        region_id: {
            region_name: text, 
            hospitals: [
                {
                    hospital_name: text,
                    needs: [
                        {
                            need_name: text,
                            needed: int,
                            recived: int
                        }
                    ]
                }
            ]
        }
    }
    """

    for region_id in region_ids:
        if region_id not in hospitals_data:
            hospitals_data[region_id] = {
                "region_name": regions[region_id], 
                "hospitals": []
            }
            
    for hospital in hospitals.values():
        hospitals_data[hospital["region"]]["hospitals"].append(
            {
                "hospital_name": hospital["hospital_name"],
                "needs": hospital["needs"]
            }
        )
        
    # pp.pprint(hospitals_data)
    return hospitals_data


if __name__=="__main__":
    data = pre_config()
    pp.pprint(data)