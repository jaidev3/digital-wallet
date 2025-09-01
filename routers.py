from fastapi import APIRouter
from controllers import create_user, get_user, update_user, create_transaction, get_wallet_balance, add_wallet_balance, withdraw_wallet_balance

router = APIRouter()

router.post("/create-user")(create_user)
router.get("/get-user/{user_id}")(get_user)
router.put("/update-user/{user_id}")(update_user)
router.get("/get-wallet-balance/{user_id}")(get_wallet_balance)
router.post("/add-wallet-balance/{user_id}")(add_wallet_balance)
router.post("/withdraw-wallet-balance/{user_id}")(withdraw_wallet_balance)


router.post("/create-transaction")(create_transaction)
