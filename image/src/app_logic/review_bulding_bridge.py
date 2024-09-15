from models.building_model import BuildingModel, BuildingCreate, BuildingResponse
from models.review_model import ReviewModel, ReviewCreate, ReviewResponse
import requests

def main(review: BuildingCreate):
    
    
    review_dict = review.model_dump()
    
    building_name = review_dict["buildingName"]
    base_url = "https://rksm5pqdlaltlgj5pf6du4glwa0ahmao.lambda-url.us-east-1.on.aws/api/buildings"
    buildingName = review_dict["buildingName"]

    # Construct the full URL
    url = f"{base_url}/{buildingName}"
    response = requests.get(url)    
    
    if response == -1:
        mobility_accessibility_count = 0
        cognitive_accessibility_count = 0
        hearing_accessibility_count = 0
        vision_accessibility_count = 0
        bathroom_accessibility_count = 0
        lgbtq_inclusivity_count = 0
        sensory_considerations_count = 0
        overall_inclusivity_count = 0
        
        mobility_accessibility_rating = 0
        cognitive_accessibility_rating = 0
        hearing_accessibility_rating = 0
        vision_accessibility_rating = 0
        bathroom_accessibility_rating = 0
        lgbtq_inclusivity_rating = 0
        sensory_considerations_rating = 0
        overall_inclusivity_rating = 0
        
        if review_dict["mobility_accessibility_rating"] != 0:
            mobility_accessibility_count = 1
            mobility_accessibility_rating = review_dict["mobility_accessibility_rating"]      
        if review_dict["cognitive_accessibility_rating"] != 0:
            cognitive_accessibility_count = 1
            cognitive_accessibility_rating = review_dict["cognitive_accessibility_rating"] 
        if review_dict["hearing_accessibility_rating"] != 0:
            hearing_accessibility_count = 1
            hearing_accessibility_rating = review_dict["hearing_accessibility_rating"]
        if review_dict["vision_accessibility_rating"] != 0:
            vision_accessibility_count = 1
            vision_accessibility_rating = review_dict["vision_accessibility_rating"]
        if review_dict["bathroom_accessibility_rating"] != 0:
            bathroom_accessibility_count = 1
            bathroom_accessibility_rating = review_dict["bathroom_accessibility_rating"]
        if review_dict["lgbtq_inclusivity_rating"] != 0:
            lgbtq_inclusivity_count = 1
            lgbtq_inclusivity_rating = review_dict["lgbtq_inclusivity_rating"]         
        if review_dict["sensory_considerations_rating"] != 0:
            sensory_considerations_count = 1
            sensory_considerations_rating = review_dict["sensory_considerations_rating"]        
        if review_dict["overall_inclusivity_rating"] != 0:
            overall_inclusivity_count = 1
            overall_inclusivity_rating = review_dict["overall_inclusivity_rating"]
            
            
        building_input_dict = {
            "buildingName": building_name,
            "category":  review_dict["category"],
            "GID":  review_dict["GID"],
            "address":  review_dict["address"],
            "latitude": review_dict["latitude"],
            "longitude": review_dict["longitude"],
            
            "mobility_accessibility_dict": {},
            "cognitive_accessibility_dict": {},
            "hearing_accessibility_dict": {},
            "vision_accessibility_dict": {},
            "bathroom_accessibility_dict": {},
            "lgbtq_inclusivity_dict": {},
            "sensory_considerations_dict": {},
            "overall_inclusivity_dict": {},            
            
            "mobility_accessibility_text_aggregate": "string",
            "cognitive_accessibility_text_aggregate": "string",
            "hearing_accessibility_text_aggregate": "string",
            "vision_accessibility_text_aggregate": "string",
            "bathroom_accessibility_text_aggregate": "string",
            "lgbtq_inclusivity_text_aggregate": "string",
            "sensory_considerations_text_aggregate": "string",
            "overall_inclusivity_text_aggregate": "string",
            
            "mobility_accessibility_rating": mobility_accessibility_rating,
            "cognitive_accessibility_rating": cognitive_accessibility_rating,
            "hearing_accessibility_rating": hearing_accessibility_rating,
            "vision_accessibility_rating": vision_accessibility_rating,
            "bathroom_accessibility_rating": bathroom_accessibility_rating,
            "lgbtq_inclusivity_rating": lgbtq_inclusivity_rating,
            "sensory_considerations_rating": sensory_considerations_rating,
            "overall_inclusivity_rating": overall_inclusivity_rating,
            
            "mobility_accessibility_count": mobility_accessibility_count,
            "cognitive_accessibility_count": cognitive_accessibility_count,
            "hearing_accessibility_count": hearing_accessibility_count,
            "vision_accessibility_count": vision_accessibility_count,
            "bathroom_accessibility_count": bathroom_accessibility_count,
            "lgbtq_inclusivity_count": lgbtq_inclusivity_count,
            "sensory_considerations_count": sensory_considerations_count,
            "overall_inclusivity_count":overall_inclusivity_count
}
                
        createBuilding(building_input_dict)
        
    else:
        building_dict = response.model_dump()
                
        mobility_accessibility_count = building_dict["mobility_accessibility_count"]
        cognitive_accessibility_count = building_dict["cognitive_accessibility_count"]
        hearing_accessibility_count = building_dict["hearing_accessibility_count"]
        vision_accessibility_count = building_dict["vision_accessibility_count"]
        bathroom_accessibility_count = building_dict["bathroom_accessibility_count"]
        lgbtq_inclusivity_count = building_dict["lgbtq_inclusivity_count"]
        sensory_considerations_count = building_dict["sensory_considerations_count"]
        overall_inclusivity_count = building_dict["overall_inclusivity_count"]
        
        mobility_accessibility_rating = building_dict["mobility_accessibility_rating"]
        cognitive_accessibility_rating = building_dict["cognitive_accessibility_rating"]
        hearing_accessibility_rating = building_dict["hearing_accessibility_rating"]
        vision_accessibility_rating = building_dict["vision_accessibility_rating"]
        bathroom_accessibility_rating = building_dict["bathroom_accessibility_rating"]
        lgbtq_inclusivity_rating = building_dict["lgbtq_inclusivity_rating"]
        sensory_considerations_rating = building_dict["sensory_considerations_rating"]
        overall_inclusivity_rating = building_dict["overall_inclusivity_rating"]
        
        
        if review_dict["mobility_accessibility_rating"] != 0:
            mobility_accessibility_count += 1
        if review_dict["cognitive_accessibility_rating"] != 0:
            cognitive_accessibility_count += 1
        if review_dict["hearing_accessibility_rating"] != 0:
            hearing_accessibility_count += 1
        if review_dict["vision_accessibility_rating"] != 0:
            vision_accessibility_count += 1
        if review_dict["bathroom_accessibility_rating"] != 0:
            bathroom_accessibility_count += 1
        if review_dict["lgbtq_inclusivity_rating"] != 0:
            lgbtq_inclusivity_count += 1
        if review_dict["sensory_considerations_rating"] != 0:
            sensory_considerations_count += 1
        if review_dict["overall_inclusivity_rating"] != 0:
            overall_inclusivity_count += 1
        
        if  mobility_accessibility_count != 0:
            mobility_accessibility_rating = (review_dict["mobility_accessibility_rating"] + mobility_accessibility_rating * (mobility_accessibility_count-1)) / mobility_accessibility_count
        if  cognitive_accessibility_count != 0:
            cognitive_accessibility_rating += (review_dict["cognitive_accessibility_rating"] + cognitive_accessibility_rating * (cognitive_accessibility_count-1)) / cognitive_accessibility_count
        if  hearing_accessibility_count != 0:
            hearing_accessibility_rating = (review_dict["hearing_accessibility_rating"] + hearing_accessibility_rating * (hearing_accessibility_count-1)) / hearing_accessibility_count
        if  vision_accessibility_count != 0:
            vision_accessibility_rating = (review_dict["vision_accessibility_rating"] + vision_accessibility_rating * (vision_accessibility_count-1)) / vision_accessibility_count
        if  bathroom_accessibility_count != 0:
            bathroom_accessibility_rating = (review_dict["bathroom_accessibility_rating"] + bathroom_accessibility_rating * (bathroom_accessibility_count-1)) / bathroom_accessibility_count
        if  lgbtq_inclusivity_count != 0:
            lgbtq_inclusivity_rating = (review_dict["lgbtq_inclusivity_rating"] + lgbtq_inclusivity_rating * (lgbtq_inclusivity_count-1)) / lgbtq_inclusivity_count
        if  sensory_considerations_count != 0:
            sensory_considerations_rating = (review_dict["sensory_considerations_rating"] + sensory_considerations_rating * (sensory_considerations_count-1)) / sensory_considerations_count
        if  overall_inclusivity_count != 0:
            overall_inclusivity_rating = (review_dict["overall_inclusivity_rating"] + overall_inclusivity_rating * (overall_inclusivity_count-1)) / overall_inclusivity_count
        
        building_input_dict = {
            "buildingName": building_name,
            "category":  review_dict["category"],
            "GID":  review_dict["GID"],
            "address":  review_dict["address"],
            "latitude": review_dict["latitude"],
            "longitude": review_dict["longitude"],
            
            "mobility_accessibility_dict": {},
            "cognitive_accessibility_dict": {},
            "hearing_accessibility_dict": {},
            "vision_accessibility_dict": {},
            "bathroom_accessibility_dict": {},
            "lgbtq_inclusivity_dict": {},
            "sensory_considerations_dict": {},
            "overall_inclusivity_dict": {},            
            
            "mobility_accessibility_text_aggregate": "string",
            "cognitive_accessibility_text_aggregate": "string",
            "hearing_accessibility_text_aggregate": "string",
            "vision_accessibility_text_aggregate": "string",
            "bathroom_accessibility_text_aggregate": "string",
            "lgbtq_inclusivity_text_aggregate": "string",
            "sensory_considerations_text_aggregate": "string",
            "overall_inclusivity_text_aggregate": "string",
            
            "mobility_accessibility_rating": mobility_accessibility_rating,
            "cognitive_accessibility_rating": cognitive_accessibility_rating,
            "hearing_accessibility_rating": hearing_accessibility_rating,
            "vision_accessibility_rating": vision_accessibility_rating,
            "bathroom_accessibility_rating": bathroom_accessibility_rating,
            "lgbtq_inclusivity_rating": lgbtq_inclusivity_rating,
            "sensory_considerations_rating": sensory_considerations_rating,
            "overall_inclusivity_rating": overall_inclusivity_rating,
            
            "mobility_accessibility_count": mobility_accessibility_count,
            "cognitive_accessibility_count": cognitive_accessibility_count,
            "hearing_accessibility_count": hearing_accessibility_count,
            "vision_accessibility_count": vision_accessibility_count,
            "bathroom_accessibility_count": bathroom_accessibility_count,
            "lgbtq_inclusivity_count": lgbtq_inclusivity_count,
            "sensory_considerations_count": sensory_considerations_count,
            "overall_inclusivity_count":overall_inclusivity_count
}

        updateBuilding(building_input_dict)
        


def updateBuilding(building_input_dict):           
    url = "https://rksm5pqdlaltlgj5pf6du4glwa0ahmao.lambda-url.us-east-1.on.aws/api/buildings/update-building"
    requests.post(url, json=building_input_dict)    

def createBuilding(building_input_dict):
    url = "https://rksm5pqdlaltlgj5pf6du4glwa0ahmao.lambda-url.us-east-1.on.aws/api/buildings/create-building"
    requests.post(url, json=building_input_dict)    

    
    
