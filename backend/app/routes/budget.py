
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.database.connection import get_db
from app.core.dependencies import get_current_user
from app.models.budget import Budget
from app.models.category import Category
from app.models.user import User
from app.schemas.budget import BudgetCreate, BudgetResponse, BudgetUpdate


router = APIRouter(
    prefix="/budgets",
    tags=["Budgets"]
)


@router.post("/", response_model=BudgetResponse, status_code=status.HTTP_201_CREATED)
def create_budget(
    budget_data: BudgetCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    category = db.query(Category).filter(
        Category.id == budget_data.category_id,
        Category.user_id == current_user.id
    ).first()

    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Category not found"
        )

    if category.type.lower() != "expense":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Budget can only be created for expense categories"
        )

    existing_budget = db.query(Budget).filter(
        Budget.user_id == current_user.id,
        Budget.category_id == budget_data.category_id,
        Budget.month == budget_data.month
    ).first()

    if existing_budget:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Budget already exists for this category and month"
        )

    new_budget = Budget(
        name=budget_data.name,
        amount=budget_data.amount,
        month=budget_data.month,
        category_id=budget_data.category_id,
        user_id=current_user.id
    )

    db.add(new_budget)

    try:
        db.commit()
        db.refresh(new_budget)
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Budget already exists for this category and month"
        )

    return new_budget


@router.get("/", response_model=list[BudgetResponse])
def get_budgets(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    budgets = db.query(Budget).filter(
        Budget.user_id == current_user.id
    ).order_by(
        Budget.month.desc(),
        Budget.id.desc()
    ).all()

    return budgets




@router.put("/{budget_id}", response_model=BudgetResponse)
def update_budget(
    budget_id: int,
    budget_data: BudgetUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    budget = db.query(Budget).filter(
        Budget.id == budget_id,
        Budget.user_id == current_user.id
    ).first()

    if not budget:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Budget not found"
        )

    category = db.query(Category).filter(
        Category.id == budget_data.category_id,
        Category.user_id == current_user.id
    ).first()

    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Category not found"
        )

    if category.type.lower() != "expense":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Budget can only be assigned to expense categories"
        )

    duplicate_budget = db.query(Budget).filter(
        Budget.user_id == current_user.id,
        Budget.category_id == budget_data.category_id,
        Budget.month == budget_data.month,
        Budget.id != budget_id
    ).first()

    if duplicate_budget:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Budget already exists for this category and month"
        )

    budget.name = budget_data.name
    budget.amount = budget_data.amount
    budget.month = budget_data.month
    budget.category_id = budget_data.category_id

    try:
        db.commit()
        db.refresh(budget)
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Budget already exists for this category and month"
        )

    return budget



@router.delete("/{budget_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_budget(
    budget_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    budget = db.query(Budget).filter(
        Budget.id == budget_id,
        Budget.user_id == current_user.id
    ).first()

    if not budget:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Budget not found"
        )

    db.delete(budget)
    db.commit()

    return None
