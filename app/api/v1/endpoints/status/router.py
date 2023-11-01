from os import path
from fastapi import APIRouter,  HTTPException


router = APIRouter()


@router.get("/")
def get_status():
    """
    Check server up and authorized to access data
    """
    checkServiceAccount()
    return 'Server Up'


def checkServiceAccount():
    # check for service-account.json file relative to project root
    serviceJsonPath = path.abspath('./service-account.json')
    print('path',serviceJsonPath)
    if path.exists(serviceJsonPath):
        return True
    else:
        raise HTTPException(status_code=401,detail="service-account.json missing from local files. Endpoints will not be able to access climate data")