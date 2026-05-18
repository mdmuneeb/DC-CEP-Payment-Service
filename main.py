from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError
import random
from pydantic import BaseModel, Field
from dotenv import load_dotenv
import os

load_dotenv()

DATABASE_URL = os.getenv("PaymentServiceDeployed")
# DATABASE_URL = os.getenv("PaymentServiceLocal")

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

DATABASE_URL_Local = DATABASE_URL
engine = create_engine(DATABASE_URL_Local)


class PaymentCreate(BaseModel):
    order_id: int = Field(example=1)
    amount: float = Field(gt=0, example=199.99)
    payment_method: str = Field(default="Card", example="Card")


@app.get("/payments")
def get_payments():

    try:
        with engine.connect() as conn:

            result = conn.execute(text("SELECT * FROM Payments"))

            payments = [dict(row._mapping) for row in result]

        return payments

    except SQLAlchemyError:
        raise HTTPException(
            status_code=500,
            detail="Database error while fetching payments"
        )

    except Exception:
        raise HTTPException(
            status_code=500,
            detail="Unexpected server error"
        )


# Process Payment
@app.post("/payments")
def process_payment(payment: PaymentCreate):

    try:
        order_id = payment.order_id
        amount = payment.amount

        # Simulate success/failure
        status = "Success" if random.choice([True, False]) else "Failed"

        with engine.connect() as conn:

            conn.execute(text("""
                INSERT INTO Payments 
                (order_id, amount, status, payment_method)
                VALUES 
                (:order_id, :amount, :status, :payment_method)
            """), {
                "order_id": order_id,
                "amount": amount,
                "status": status,
                "payment_method": payment.payment_method
            })

            conn.commit()

        return {
            "order_id": order_id,
            "payment_status": status
        }

    except SQLAlchemyError:
        raise HTTPException(
            status_code=500,
            detail="Database error while processing payment"
        )

    except Exception:
        raise HTTPException(
            status_code=500,
            detail="Unexpected server error"
        )