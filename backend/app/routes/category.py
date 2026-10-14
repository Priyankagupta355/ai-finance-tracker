
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_user
from app.database.connection import get_db
from app.models.category import Category
from app.models.user import User
from app.schemas.category import CategoryCreate, CategoryResponse, CategoryUpdate

router = APIRouter(
    prefix="/categories",
    tags=["Categories"]
)


@router.post(
    "/",
    response_model=CategoryResponse,
    status_code=status.HTTP_201_CREATED
)
def create_category(
    category_data: CategoryCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    category = Category(
        name=category_data.name,
        type=category_data.type,
        user_id=current_user.id
    )

    db.add(category)
    db.commit()
    db.refresh(category)

    return category



@router.get(
    "/",
    response_model=list[CategoryResponse]
)
def get_categories(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    categories = (
        db.query(Category)
        .filter(Category.user_id == current_user.id)
        .order_by(Category.id.asc())
        .all()
    )

    return categories

@router.put(
    "/{category_id}",
    response_model=CategoryResponse
)
def update_category(
    category_id: int,
    category_data: CategoryUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    category = (
        db.query(Category)
        .filter(
            Category.id == category_id,
            Category.user_id == current_user.id
        )
        .first()
    )

    if category is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Category not found"
        )

    category.name = category_data.name
    category.type = category_data.type

    db.commit()
    db.refresh(category)

    return category


@router.delete(
    "/{category_id}",
    status_code=status.HTTP_204_NO_CONTENT
)
def delete_category(
    category_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    category = (
        db.query(Category)
        .filter(
            Category.id == category_id,
            Category.user_id == current_user.id
        )
        .first()
    )

    if category is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Category not found"
        )

    db.delete(category)
    db.commit()

    return None
