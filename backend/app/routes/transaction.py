
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_user
from app.database.connection import get_db
from app.models.category import Category
from app.models.transaction import Transaction
from app.models.user import User
from app.schemas.transaction import TransactionCreate, TransactionResponse, TransactionUpdate


router = APIRouter(
    prefix="/transactions",
    tags=["Transactions"]
)


@router.post(
    "/",
    response_model=TransactionResponse,
    status_code=status.HTTP_201_CREATED
)
def create_transaction(
    transaction_data: TransactionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if transaction_data.category_id is not None:
        category = (
            db.query(Category)
            .filter(
                Category.id == transaction_data.category_id,
                Category.user_id == current_user.id
            )
            .first()
        )

        if category is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Category not found"
            )

        if category.type != transaction_data.type:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Category type must match transaction type"
            )

    transaction = Transaction(
        title=transaction_data.title,
        amount=transaction_data.amount,
        type=transaction_data.type,
        category_id=transaction_data.category_id,
        transaction_date=transaction_data.transaction_date,
        description=transaction_data.description,
        user_id=current_user.id
    )

    db.add(transaction)
    db.commit()
    db.refresh(transaction)

    return transaction


@router.get(
    "/",
    response_model=list[TransactionResponse]
)
def get_transactions(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    transactions = (
        db.query(Transaction)
        .filter(Transaction.user_id == current_user.id)
        .order_by(Transaction.transaction_date.desc())
        .all()
    )

    return transactions


@router.put(
    "/{transaction_id}",
    response_model=TransactionResponse
)
def update_transaction(
    transaction_id: int,
    transaction_data: TransactionUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    transaction = (
        db.query(Transaction)
        .filter(
            Transaction.id == transaction_id,
            Transaction.user_id == current_user.id
        )
        .first()
    )

    if transaction is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Transaction not found"
        )

    if transaction_data.category_id is not None:
        category = (
            db.query(Category)
            .filter(
                Category.id == transaction_data.category_id,
                Category.user_id == current_user.id
            )
            .first()
        )

        if category is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Category not found"
            )

        if category.type != transaction_data.type:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Category type must match transaction type"
            )

    transaction.title = transaction_data.title
    transaction.amount = transaction_data.amount
    transaction.type = transaction_data.type
    transaction.category_id = transaction_data.category_id
    transaction.transaction_date = transaction_data.transaction_date
    transaction.description = transaction_data.description

    db.commit()
    db.refresh(transaction)

    return transaction



@router.delete(
    "/{transaction_id}",
    status_code=status.HTTP_204_NO_CONTENT
)
def delete_transaction(
    transaction_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    transaction = (
        db.query(Transaction)
        .filter(
            Transaction.id == transaction_id,
            Transaction.user_id == current_user.id
        )
        .first()
    )

    if transaction is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Transaction not found"
        )

    db.delete(transaction)
    db.commit()

    return None
