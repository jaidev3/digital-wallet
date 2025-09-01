from fastapi import APIRouter
from controllers import create_user, get_user, update_user, create_transaction

router = APIRouter()

router.post("/create-user")(create_user)
router.get("/get-user/{user_id}")(get_user)
router.put("/update-user/{user_id}")(update_user)
router.post("/create-transaction")(create_transaction)