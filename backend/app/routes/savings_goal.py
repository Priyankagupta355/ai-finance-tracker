
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database.connection import get_db
from app.core.dependencies import get_current_user
from app.models.savings_goal import SavingGoal
from app.models.user import User
from app.schemas.savings_goal import (
    SavingsGoalCreate,
    SavingsGoalResponse,
    SavingsGoalUpdate
)

router = APIRouter(
    prefix="/savings-goals",
    tags=["Savings Goals"]
)


@router.post(
    "/",
    response_model=SavingsGoalResponse,
    status_code=status.HTTP_201_CREATED
)
def create_savings_goal(
    goal_data: SavingsGoalCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if goal_data.current_amount > goal_data.target_amount:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Current amount cannot exceed target amount"
        )

    new_goal = SavingGoal(
        name=goal_data.name,
        target_amount=goal_data.target_amount,
        current_amount=goal_data.current_amount,
        target_date=goal_data.target_date,
        user_id=current_user.id
    )

    db.add(new_goal)
    db.commit()
    db.refresh(new_goal)

    return new_goal



@router.get("/", response_model=list[SavingsGoalResponse])
def get_savings_goals(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    goals = db.query(SavingGoal).filter(
        SavingGoal.user_id == current_user.id
    ).order_by(
        SavingGoal.created_at.desc()
    ).all()

    return goals



@router.put("/{goal_id}", response_model=SavingsGoalResponse)
def update_savings_goal(
    goal_id: int,
    goal_data: SavingsGoalUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    goal = db.query(SavingGoal).filter(
        SavingGoal.id == goal_id,
        SavingGoal.user_id == current_user.id
    ).first()

    if not goal:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Savings goal not found"
        )

    if goal_data.current_amount > goal_data.target_amount:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Current amount cannot exceed target amount"
        )

    goal.name = goal_data.name
    goal.target_amount = goal_data.target_amount
    goal.current_amount = goal_data.current_amount
    goal.target_date = goal_data.target_date

    db.commit()
    db.refresh(goal)

    return goal


@router.delete("/{goal_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_savings_goal(
    goal_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    goal = db.query(SavingGoal).filter(
        SavingGoal.id == goal_id,
        SavingGoal.user_id == current_user.id
    ).first()

    if not goal:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Savings goal not found"
        )

    db.delete(goal)
    db.commit()

    return None
